import re

from django.db import IntegrityError
from django.utils.translation import gettext as _
from rest_framework import serializers, status as request_status
from rest_framework.exceptions import APIException, ValidationError

from company_organisations.models import CompanyOrganisation
from member_organisations.models import MemberOrganisation
from services import users_service


class AccountCreateOrUpdateSerializer(serializers.Serializer):
    uuid = serializers.CharField(label=_('Unique User Id'))
    email = serializers.EmailField(label=_('User Email'))
    password = serializers.CharField(label=_('User Password'), required=False)
    company_prefix = serializers.CharField(label=_('Company Prefix'), required=False)
    company_name = serializers.CharField(
        label=_('Company Name'), required=False)
    credits = serializers.CharField(label=_('Credit Points'), required=False)
    txn_ref = serializers.CharField(
        label=_('Unique Transaction Reference'), required=False)
    member_organisation = serializers.CharField(label=_('GS1 MO'))

    def validate_member_organisation(self, value):
        try:
            value = MemberOrganisation.objects.get(slug=value)
        except MemberOrganisation.DoesNotExist:
            raise serializers.ValidationError(
                _("defined member_organisation does not exist."))
        return value

    def validate_company_prefix(self, value):
        slug_member_organisation = self.initial_data.get('member_organisation')
        try:
            member_organisation = MemberOrganisation.objects.get(slug=slug_member_organisation)
        except MemberOrganisation.DoesNotExist:
            raise serializers.ValidationError(
                _("defined member_organisation does not exist for validate company_prefix."))
        errors = []
        form_prefixes = value.split(',')
        for prfx in form_prefixes:
            m = re.match(member_organisation.gs1_prefix_regex, prfx[:3])
            if not re.match(member_organisation.gs1_prefix_regex, prfx[:3]) or len(prfx) < 6:
                if prfx.find('20') == 0:  # we will not complain about variable weight
                    continue
                else:
                    errors.append(_('invalid prefix') + ' %s' % prfx)
        if errors:
            raise serializers.ValidationError(', '.join(errors))
        return value

    def save(self, **kwargs):
        self.instance = CompanyOrganisation.objects.filter(
            uuid=self.validated_data.get('uuid'),
            member_organisation=self.validated_data['member_organisation'],
        ).first()
        company_organisation = super(AccountCreateOrUpdateSerializer, self).save(**kwargs)

        details = {
            'username': self.validated_data.get('email'),
            'member_organisation': self.validated_data['member_organisation'],
            'company_organisation': company_organisation
        }
        auth_user, auth_user_created = users_service.get_or_create(
            email=self.validated_data['email'], defaults=details
        )

        if not auth_user_created:
            auth_user = users_service.update_details(auth_user, details)

        if self.validated_data.get('password', ''):
            auth_user.set_password(self.validated_data.get('password'))
        else:
            auth_user.set_unusable_password()

        auth_user.save()
        company_organisation = users_service.get_company_organisation(auth_user)

        return company_organisation, auth_user

    def create(self, validated_data):
        try:
            company_organisation = CompanyOrganisation.objects.create(
                company=validated_data.get('company_name', ''),
                name=validated_data.get('company_name', ''),
                uuid=validated_data.get('uuid'),
                member_organisation=validated_data['member_organisation'],
            )
        except IntegrityError as error:
            raise ValidationError('Wrong company data')
        return company_organisation

    def update(self, instance, validated_data):
        instance.company = validated_data.get('company_name', '')
        instance.name = validated_data.get('company_name', '')
        instance.uuid = validated_data.get('uuid')
        instance.member_organisation = validated_data.get(
            'member_organisation')
        instance.save()

        return instance
