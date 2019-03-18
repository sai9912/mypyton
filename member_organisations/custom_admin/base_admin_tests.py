import json

from django.db.models import DateTimeField
from django.utils.dateparse import parse_datetime
from mixer.backend.django import Mixer
from django.contrib.auth.models import Group, User
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory
from django.urls import reverse
from django.core import serializers
from django.db import models

from audit.models import Log
from member_organisations.admin import MemberOrganisationOwnerAdmin
from member_organisations.models import (
    MemberOrganisation, MemberOrganisationUser, MemberOrganisationOwner
)
from company_organisations.models import (
    CompanyOrganisation, CompanyOrganisationOwner, CompanyOrganisationUser
)
from BCM.models import Country, Language, LanguageByCountry
from prefixes.models import Prefix


class BaseAdminTestCase:
    fixtures = ['bcm.json', 'groups.json']
    """
    We have to inherit from "object" here cause TestCase is something like singleton
    and if TestCase will be specified here, base class will be tested too with errors
    """

    url_prefix = None  # 'mo_admin' / 'go_admin'
    group_name = None  # 'MO Admins' / 'GO Admins'
    mo_admin_instance = None
    main_user_credentials = None
    group = None
    request_factory = None
    mixer = None

    def setUp(self):
        self.mo_admin_instance = MemberOrganisationOwnerAdmin(
            CompanyOrganisationOwner, AdminSite()
        )
        self.main_user_credentials = {
            'username': 'moadmin',
            'password': '1234',
        }
        self.group = Group.objects.get(name=self.group_name)
        self.request_factory = RequestFactory()
        self.mixer = Mixer(locale='en')

    def create_required_instances(self):
        user11 = self.create_django_user(self.main_user_credentials)
        user12 = self.create_django_user()
        user21 = self.create_django_user()

        mo1 = self.mixer.blend(
            MemberOrganisation,
            name='GS1 France',
            country=Country.objects.get(name='France')
        )
        mo2 = self.mixer.blend(
            MemberOrganisation,
            name='GS1 Belgium',
            country=Country.objects.get(name='Belgium')
        )

        mo1_user1 = self.mixer.blend(
            MemberOrganisationUser, organization=mo1, user=user11, is_admin=True
        )
        mo1_user2 = self.mixer.blend(
            MemberOrganisationUser, organization=mo1, user=user12, is_admin=True
        )
        mo2_user1 = self.mixer.blend(MemberOrganisationUser, organization=mo2, user=user21)

        mo_owner1 = self.mixer.blend(
            MemberOrganisationOwner, organization_user=mo1_user1, organization=mo1
        )
        mo_owner2 = self.mixer.blend(
            MemberOrganisationOwner, organization_user=mo2_user1, organization=mo2
        )

        co_fields = self.get_force_random_fields_for_mixer(
            CompanyOrganisation,
            company='CO1 Test',
            member_organisation=mo1,
            country=mo1.country,
            active=True,
            excluded_fields=['created']
        )
        co1 = self.mixer.blend(CompanyOrganisation, **co_fields)

        co_fields = self.get_force_random_fields_for_mixer(
            CompanyOrganisation,
            company='CO2 Test',
            member_organisation=mo2,
            country=mo2.country,
            active=True,
            excluded_fields=['created']
        )
        co2 = self.mixer.blend(CompanyOrganisation, **co_fields)

        co1_user1 = self.mixer.blend(
            CompanyOrganisationUser,
            user=user11, organization=co1, is_admin=True,
        )

        co2_user1 = self.mixer.blend(
            CompanyOrganisationUser,
            user=user21, organization=co2, is_admin=True,
        )

        co1_owner = self.mixer.blend(
            CompanyOrganisationOwner, organization_user=co1_user1, organization=co1
        )

        co2_owner = self.mixer.blend(
            CompanyOrganisationOwner, organization_user=co2_user1, organization=co2
        )

        co1_prefix1 = self.mixer.blend(Prefix, company_organisation=co1, member_organisation=mo1)
        co2_prefix1 = self.mixer.blend(Prefix, company_organisation=co2, member_organisation=mo2)

        co1_log1 = self.mixer.blend(Log)
        co2_log1 = self.mixer.blend(Log)

        return {
            variable_name: instance
            for variable_name, instance in locals().items()
            if isinstance(instance, models.Model)
        }

    def create_django_user(self, user_credentials=None, add_to_group=True):

        if user_credentials:
            user = User(**user_credentials)
            user.set_password(self.main_user_credentials['password'])
            user.save()
        else:
            user = self.mixer.blend(User)

        if add_to_group:
            user.groups.add(self.group)
        return user

    def get_force_random_fields_for_mixer(self, model_class, excluded_fields=None, **kwargs):
        """
        Mixer sets default values from model,
        but it raises errors when blank=False and default='' at the same time,
        so we have to force fields to be set by random values

        :param model_class:
        :param excluded_fields: ('id', )  # prevent to randomize some fields
        :param kwargs: field_name=instance or value  # predefined field values
        :return: dict of field_names: random/predefined values
        """

        excluded_fields = {'id'} | set(excluded_fields or [])

        co_fields = {
            field.name: self.mixer.RANDOM
            for field in model_class._meta.fields if field.name not in excluded_fields
        }

        for field_name, field_value in kwargs.items():
            co_fields[field_name] = field_value

        return co_fields

    @classmethod
    def model_instance_to_post_data(cls, instance):
        data = serializers.serialize('json', [instance, ])
        post_data = json.loads(data)
        post_data = post_data[0]['fields']

        for field in instance._meta.fields:
            # splitting date and time for admin forms
            if isinstance(field, DateTimeField):
                field_datetime = parse_datetime(post_data[field.name])
                post_data[f'{field.name}_0'] = str(field_datetime.date())
                post_data[f'{field.name}_1'] = str(field_datetime.time())
                del post_data[field.name]
            if not field.serialize and isinstance(field, models.ForeignKey):
                post_data[field.name] = getattr(instance, field.name).pk

        return post_data

    def get_urls_by_types(self, url_types, excluded_apps=None):
        """
        Filters url list by types like: "changelist", "add", "change", "delete"
        """

        excluded_apps = excluded_apps if excluded_apps else []
        url_names = list()

        for url in self.mo_admin_instance.get_urls():
            if not url.name:
                continue
            if not url.name.startswith(self.url_prefix):
                continue

            denied_app_urls = [
                app_name for app_name in excluded_apps
                if url.name.startswith(f'{self.url_prefix}_{app_name}')
            ]
            if denied_app_urls:
                continue

            if any(url_type in url.name for url_type in url_types):
                url_names.append(reverse(f'admin:{url.name}'))

        return url_names

    def get_url_for_model(self, model_class, action, pk=None):
        app_label = model_class._meta.app_label
        model_name = model_class._meta.model_name

        return (
            reverse(
                f'admin:{self.url_prefix}_{app_label}_{model_name}_{action}',
                args=(pk,) if pk else None))

    def test_changelist_add_urls_non_authorized_user(self):
        """
        Non authorized users must receive 302 http response to login page
        """

        url_names = self.get_urls_by_types(['changelist', 'add'], excluded_apps=['auth'])

        for url_name in url_names:
            response = self.client.get(url_name)
            self.assertEqual(
                response.status_code, 302,
                f'URL "{url_name}" should be denied for non authorized users'
            )

    def test_changelist_add_urls_authorized_user(self):
        """
        Authorized and authenticated users must receive 200 http response
        """

        login_result = self.client.login(**self.main_user_credentials)
        self.assertTrue(login_result, 'Can\'t login to with test user credentials')

        url_names = self.get_urls_by_types(
            ['changelist', 'add'],
            excluded_apps=['auth','member_organisations',]
        )
        for url_name in url_names:
            response = self.client.get(url_name)
            self.assertEqual(
                response.status_code, 200,
                f'URL "{url_name}" should be allowed for authorized/authenticated users'
            )

    def perform_adding_tests(self, models_config):
        for model_class, model_conf in models_config.items():
            if not model_conf:
                continue

            predefined_fields = model_conf.get('predefined_fields', {})

            model_fields = self.get_force_random_fields_for_mixer(
                model_class, excluded_fields=['created'], **predefined_fields
            )
            model_instance = self.mixer.blend(model_class, **model_fields)
            model_instance.delete()  # it seems mixer doesn't care about his commit=False
            post_data = self.model_instance_to_post_data(model_instance)

            self.assertFalse(
                model_class.objects.filter(**predefined_fields).exists(),
                f'the {model_class} instance with predefined data: '
                f'"{predefined_fields}" mustn\'t be in the test database before submitting'
            )

            # instance creating is here
            model_add_url = self.get_url_for_model(model_class, 'add')
            response = self.client.post(model_add_url, data=post_data)

            self.assertEqual(
                response.status_code, 302,
                f'Should be a redirect after an instance submitting, model: "{model_class}"'
            )

            self.assertEqual(
                response.url,
                self.get_url_for_model(model_class, 'changelist'),
                f'Wrong redirect url after an instace adding, model: "{model_class}"'
            )

            self.assertTrue(
                model_class.objects.filter(**predefined_fields).exists(),
                f'CompanyOrganisation "{model_instance}" must be '
                f'in the test database after submitting'
            )

    def perform_deleting_tests(self, models_config):
        for model_class, model_conf in models_config.items():
            if 'model_instance' not in model_conf:
                continue

            model_instance = model_conf['model_instance']
            post_data = {'post': 'yes'}

            co_url = self.get_url_for_model(model_class, 'delete', model_instance.pk)

            # instance creating is here
            response = self.client.post(co_url, data=post_data)

            self.assertEqual(
                response.status_code, 302,
                f'Should be a redirect after an instance submitting, model: "{model_class}"'
            )

            self.assertEqual(
                response.url,
                self.get_url_for_model(model_class, 'changelist'),
                f'Wrong redirect url after an instace removing for {model_class}'
            )

            self.assertFalse(
                model_class.objects.filter(pk=model_instance.pk).exists(),
                f'"{model_instance}" must be removed here already'
            )
