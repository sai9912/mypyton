from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from rest_framework import serializers
from django.utils.translation import gettext as _

from api.base_serializers.uploads_serializers import BaseUploadSerializer
from api.serializers.prefix_serializer import PrefixSerializer
from company_organisations.models import CompanyOrganisation
from member_organisations.models import MemberOrganisation
from prefixes.models import Prefix
from users.models import Profile
from services import users_service, prefix_service


class UserSerializer(serializers.ModelSerializer):
    member_organisation = serializers.SerializerMethodField()
    member_organisation_id = serializers.SerializerMethodField(read_only=True)

    company_organisation = serializers.SerializerMethodField()
    advanced_tab = serializers.BooleanField(source="profile.advanced_tab", required=False)
    agreed = serializers.BooleanField(source="profile.agreed", required=False)
    agreed_date = serializers.DateTimeField(source="profile.agreed_date", required=False)
    agreed_version = serializers.CharField(source="profile.agreed_version", required=False)

    # This field optional only for update,
    # when you create this field is required see validate method
    uid = serializers.CharField(source='profile.uid', max_length=124, required=False)
    language = serializers.CharField(source='profile.language', max_length=2, required=False)
    barcode_disclaimer = serializers.CharField(
        source='profile.member_organisation.gs1_barcode_production_disclaimer',
        required=False, read_only=True,
    )
    agreed_barcode_disclaimer = serializers.BooleanField(
        source='profile.agreed_barcode_disclaimer', required=False
    )
    simplified_barcode_generation = serializers.BooleanField(
        source='profile.member_organisation.simplified_barcode_generation',
        required=False, read_only=True
    )

    # nested data is available by a serializer (context['request'] is required there)
    product_active_prefix = PrefixSerializer(
        source='profile.product_active_prefix',
        read_only=False,
        required=False,
    )

    is_staff = serializers.BooleanField(required=False, read_only=True)
    is_superuser = serializers.BooleanField(required=False, read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'uid', 'email', 'first_name', 'last_name', 'member_organisation',
            'member_organisation_id', 'company_organisation', 'advanced_tab', 'agreed',
            'agreed_date', 'agreed_version', 'is_staff', 'is_superuser', 'language',
            'barcode_disclaimer', 'agreed_barcode_disclaimer', 'product_active_prefix',
            'simplified_barcode_generation',
        )
        read_only_fields = (
            'company_organisation', 'member_organisation', 'simplified_barcode_generation',
        )

    def get_member_organisation(self, obj):
        try:
            return MemberOrganisation.objects.get(users=obj).slug
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return None

    def get_member_organisation_id(self, obj):
        try:
            return MemberOrganisation.objects.get(users=obj).pk
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return None

    def get_company_organisation(self, obj):
        try:
            co = CompanyOrganisation.objects.get(users=obj)
            return co.uuid
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return None

    def validate_email(self, value):
        queryset = User.objects.filter(email=value)
        if self.instance:
            queryset = queryset.exclude(email=self.instance.email)

        if queryset.exists():
            raise serializers.ValidationError("User with this email already exists")
        return value

    def validate_uid(self, value):
        queryset = Profile.objects.filter(uid=value)

        if self.instance:
            queryset = queryset.exclude(uid=self.instance.profile.uid)

        if queryset.exists():
            raise serializers.ValidationError("User with this uid already exists")
        return value

    def validate_company_organisation(self, uuid):
        queryset = CompanyOrganisation.objects.filter(uuid=uuid)[0:2]
        if not len(queryset):
            raise serializers.ValidationError("Company with this uuid does not exist")
        elif len(queryset) > 1:
            raise serializers.ValidationError("More than one company found for this uuid")
        return queryset[0]

    def validate(self, data):
        if self.context.get('uuid'):
            company_organisation = self.validate_company_organisation(self.context.get('uuid'))
            data['company_organisation'] = company_organisation
            data['member_organisation'] = company_organisation.member_organisation

        if data.get('email'):
            data['username'] = data['email']

        if not self.instance and not data['profile'].get('uid'):
            # when create user uid is required
            raise serializers.ValidationError({
                'uid': ['This field is required.']
            })

        return data

    def create(self, validated_data):
        uid = self.validated_data.get('profile').get('uid', None)
        email = self.validated_data['email']
        username = self.validated_data['username']
        first_name = self.validated_data.get('first_name', '')
        last_name = self.validated_data.get('last_name', '')
        company_organisation = validated_data['company_organisation']
        member_organisation = validated_data['member_organisation']

        user = users_service.create(
            email=email,
            defaults={
                'uid': uid,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'member_organisation': member_organisation,
                'company_organisation': company_organisation,
            }
        )
        return user

    def update(self, instance, validated_data):
        try:
            profile_data = validated_data.pop("profile")
        except:
            profile_data = None
        instance = super(UserSerializer, self).update(instance, validated_data)
        profile = instance.profile

        if profile_data:
            agreed = profile_data.get("agreed")
            if agreed is not None:
                profile.agreed = agreed
            profile.agreed_version = profile_data.get("agreed_version")
            if profile.agreed:
                profile.agreed_date = profile_data.get("agreed_date")
            profile.save()
        return instance


class UserUpdateSerializer(serializers.ModelSerializer):
    product_active_prefix = serializers.SlugRelatedField(
        source='profile.product_active_prefix',
        slug_field='prefix', queryset=Prefix.objects.all(), required=False
    )
    agreed_barcode_disclaimer = serializers.BooleanField(
        source='profile.agreed_barcode_disclaimer', required=False
    )

    class Meta:
        model = User
        read_only_fields = (
            'email', 'is_staff', 'is_superuser',
        )
        fields = (
            # not allowed to update (must be specified both: here and in "read_only_fields")
            'email', 'is_staff', 'is_superuser',

            # allowed to update
            'first_name', 'last_name', 'product_active_prefix', 'agreed_barcode_disclaimer',
        )

    def validate_product_active_prefix(self, prefix_instance):
        available_prefixes = prefix_service.find(user=self.instance, is_suspended=False)
        if prefix_instance not in available_prefixes:
            raise serializers.ValidationError(_('You can\'t select this prefix.'))

        return prefix_instance

    def update(self, instance, validated_data):
        profile = validated_data.pop('profile', {})

        if 'product_active_prefix' in profile:
            prefix_instance = profile.pop('product_active_prefix')
            instance.profile.product_active_prefix = prefix_instance
        elif 'agreed_barcode_disclaimer' in profile:
            agreed_barcode_disclaimer = profile.pop('agreed_barcode_disclaimer')
            instance.profile.agreed_barcode_disclaimer = agreed_barcode_disclaimer

        instance = super().update(instance, validated_data)
        return instance


class UserUploadSerializer(BaseUploadSerializer):
    class Meta:
        model = MemberOrganisation
        upload_to_serializer = UserSerializer
        upload_to_required_fields = ('uid', 'email', )

    def get_extra_context(self, fields_data):
        """
        PrefixSerializer expects uuid as a context item
        """

        return {'uuid': fields_data.get('uuid')}

    def validate_upload_fields_data(self, fields_data):
        return {
            field_name: field_value
            for field_name, field_value in fields_data.items()
            if field_value is not None
        }
