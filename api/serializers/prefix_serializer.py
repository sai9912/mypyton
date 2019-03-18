import re

from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.base_serializers.uploads_serializers import BaseUploadSerializer
from company_organisations.models import CompanyOrganisation
from member_organisations.models import MemberOrganisation
from prefixes.models import Prefix, PrefixStatus
from products.models.product import Product


class PrefixSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False, allow_blank=True)
    member_organisation = serializers.CharField(
        source="member_organisation.slug", required=False, read_only=True
    )
    company_organisation = serializers.CharField(
        source="company_organisation.uuid", required=False, read_only=True
    )
    range = serializers.SerializerMethodField()

    gtins_allocated = serializers.SerializerMethodField()
    gtins_available = serializers.SerializerMethodField()
    gtins_capacity = serializers.SerializerMethodField()

    class Meta:
        model = Prefix
        extra_kwargs = {
            'action': {'required': False},
            'prefix': {'max_length': 12, 'min_length': 5},
            'uuid': {'required': True},
        }
        fields = (
            'prefix', 'status', 'is_suspended', 'is_special', 'starting_from', 'range',
            'starting_from_gln', 'member_organisation', 'company_organisation', 'description',
            'gtins_available', 'gtins_allocated', 'gtins_capacity'
        )
        read_only_fields = ['company_organisation', 'member_organisation']

    def get_gtins_allocated(self, obj):
        request = self.context.get('request')
        if not request:
            return 0

        if request.user.groups.filter(name='GO Admins'):
            products_count = Product.service.filter(gs1_company_prefix=obj.prefix).count()
        else:
            user_company_organisations = CompanyOrganisation.objects.filter(users=request.user)
            products_count = Product.service.filter(
                company_organisation__in=user_company_organisations,
                gs1_company_prefix=obj.prefix
            ).count()

        return products_count

    def get_gtins13_allocated(self, obj):
        try:
            user_company_organisations = CompanyOrganisation.objects.filter(
                users=self.context['request'].user
            )
            products = Product.service.filter(
                company_organisation__in=user_company_organisations,
                gs1_company_prefix=obj.prefix
            )
            gtins = list()
            for product in products:
                gtin = product.gtin[1:-1]
                if not gtin in gtins:
                    gtins.append(gtin)
            ret = len(gtins)
        except:
            return 0
        return ret

    def get_gtins_capacity(self, obj):
        return obj.get_capacity()

    def get_gtins_available(self, obj):
        capacity = obj.get_available_gtins([], len_only=True)
        allocated = self.get_gtins13_allocated(obj)
        return capacity - allocated

    def get_range(self, instance=None):
        return instance.get_range() if instance else None

    def validate(self, data):
        if self.context.get('uuid'):
            company_organisation = self.validate_company_organisation(self.context.get('uuid'))
            data['company_organisation'] = company_organisation
            data['member_organisation'] = company_organisation.member_organisation
        if self.initial_data.get('action'):
            data['action'] = self.initial_data.get('action')
        return data

    def validate_company_organisation(self, uuid):
        queryset = CompanyOrganisation.objects.filter(uuid=uuid)
        if not queryset.exists():
            raise serializers.ValidationError(
                _("Company with this uuid does not exist"))
        elif queryset.count() > 1:
            raise serializers.ValidationError(
                _("More than one company found for this uuid"))
        return queryset.first()

    def validate_prefix(self, prefix):
        gs1_prefix_regex = self.context['request'].user.profile.member_organisation.gs1_prefix_regex
        if not re.match(gs1_prefix_regex, prefix):
            raise serializers.ValidationError(_('Prefix not valid'))
        return prefix

    def create(self, validated_data):
        validated_data['member_organisation'] = validated_data['company_organisation'].member_organisation
        validated_data['company_organisation'] = validated_data['company_organisation']
        return super(PrefixSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        prefix_status = self.get_status_by_action(validated_data.get('action'))
        if prefix_status:
            validated_data['status'] = prefix_status
        # validated_data['company_organisation'] = validated_data.get('company_organisation')
        return super(PrefixSerializer, self).update(instance, validated_data)

    @classmethod
    def get_status_by_action(cls, action):
        action_statuses = {
            'activate': 'ACTIVE',
            'retire': 'EXPIRED',
            'transfer': 'TRANSFERRED',
            'split': 'SPLIT',
            'freeze': 'FROZEN',
            'deactivate': 'INACTIVE',
        }
        action_name = action_statuses.get(action)
        return PrefixStatus.objects.filter(name=action_name).first()


class PrefixUploadSerializer(BaseUploadSerializer):
    class Meta:
        model = MemberOrganisation
        upload_to_serializer = PrefixSerializer
        upload_to_required_fields = ('prefix',)

    def get_extra_context(self, fields_data):
        """
        PrefixSerializer expects uuid as a context item
        """

        return {'uuid': fields_data.get('uuid')}

    def validate_upload_fields_data(self, fields_data):
        try:
            uuid = fields_data.get('uuid')
            CompanyOrganisation.objects.get(uuid=uuid)
        except CompanyOrganisation.DoesNotExist:
            raise ValidationError(f'Company organisation with uuid: "{uuid}" does not exist')

        return {
            field_name: field_value
            for field_name, field_value in fields_data.items()
            if field_value is not None
        }
