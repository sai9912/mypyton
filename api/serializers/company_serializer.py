from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from BCM.models import Country
from api.base_serializers.uploads_serializers import BaseUploadSerializer
from company_organisations.models import CompanyOrganisation
from member_organisations.models import MemberOrganisation


class CompanySerializer(serializers.ModelSerializer):
    country = serializers.SlugRelatedField(
        slug_field='slug', queryset=Country.objects.all(), required=True
    )
    member_organisation = serializers.CharField(
        source="member_organisation.slug",
        read_only=True
    )
    name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = CompanyOrganisation
        fields = (
            'uuid', 'name', 'country', 'company', 'street1', 'street2', 'city', 'state', 'zip',
            'phone', 'gln', 'vat', 'credit_points_balance', 'active', 'prefix_override',
            'gln_capability', 'member_organisation',
        )

    def validate(self, attrs):
        if 'company' in attrs:
            attrs['name'] = attrs['company']
        return attrs

    def create(self, validated_data):
        request = self.context['request']
        member_organisation = request.user.profile.member_organisation
        if member_organisation is None:
            raise serializers.ValidationError(
                'Your profile must have member_organisation'
            )
        company = CompanyOrganisation.objects.create(
            member_organisation=member_organisation, **validated_data
        )
        return company


class CompanyUploadSerializer(BaseUploadSerializer):
    class Meta:
        model = MemberOrganisation
        upload_to_serializer = CompanySerializer
        upload_to_required_fields = ('uuid', 'country', 'company', )

    def validate_upload_fields_data(self, fields_data):
        return {
            field_name: field_value
            for field_name, field_value in fields_data.items()
            if field_value is not None
        }
