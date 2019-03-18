import random

from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group, User
from django.db import models
from django.test import RequestFactory
from django.urls import reverse
from django.utils.translation import ugettext as _
from mixer.main import Mixer
from test_plus import TestCase as TestCasePlus

from BCM.models import Country
from company_organisations.models import (
    CompanyOrganisationOwner
)
from member_organisations.admin import MemberOrganisationOwnerAdmin
from member_organisations.models import (
    MemberOrganisation, MemberOrganisationUser
)


class GOAdminTestCase(TestCasePlus):
    fixtures = ['bcm.json', 'groups.json']
    url_prefix = 'go_admin'
    group_name = 'GO Admins'
    model_instances = None
    users_credentials = None

    login_url = reverse('BCM:login')
    signup_url = reverse('BCM:signup')
    go_admin_index_url = reverse('admin:go_admin')
    mo_admin_index_url = reverse('admin:mo_admin')
    vue_mo_admin_index_url = reverse('admin_profile_js')

    def setUp(self):

        self.users_credentials = {
            'superuser': {
                'username': 'superuser@gmail.com',
                'password': 'TestPassword1',
            },
            'goadmin': {
                'username': 'goadmin@gmail.com',
                'password': 'TestPassword2',
            },
            'moadmin': {
                'username': 'moadmin@gmail.com',
                'password': 'TestPassword3',
            }
        }

        self.mo_admin_instance = MemberOrganisationOwnerAdmin(
            CompanyOrganisationOwner, AdminSite()
        )
        self.group = Group.objects.get(name=self.group_name)
        self.request_factory = RequestFactory()
        self.mixer = Mixer(locale='en')
        self.model_instances = self.create_required_instances()

    def create_required_instances(self):
        superuser = self.create_django_user(self.users_credentials['superuser'])
        country1 = Country.objects.all().first()
        mo1, is_created = MemberOrganisation.objects.get_or_create(
            country=country1, name='GS1 Test'
        )

        return {
            variable_name: instance
            for variable_name, instance in locals().items()
            if isinstance(instance, models.Model)
        }

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

    def create_django_user(self, user_credentials=None, add_to_group=True):

        if user_credentials:
            user = User(**user_credentials)
            user.set_password(user_credentials['password'])
            user.save()
        else:
            user = self.mixer.blend(User)

        if add_to_group:
            user.groups.add(self.group)

        return user

    @classmethod
    def randomize_string(cls, input_string):
        return ''.join(
            random.choice((str.upper, str.lower))(x)
            for x in input_string
        )

    def test_go_admin_registration(self):
        """
        GO admin user signup/login/check basic permissions
        """

        credentials = self.users_credentials['goadmin']
        post_data = {
            'username': credentials['username'],
            'password1': credentials['password'],
            'password2': credentials['password'],
            'registration_type': 'go_admin',
        }

        # create a GO Admin user with given credentials
        # expected result: not activated GO Admin user
        response = self.client.post(self.signup_url, data=post_data)

        self.assertEqual(
            response.status_code,
            302,
            _('User must be redirected to main GO admin page with '
              '"user is not activated" notification')
        )

        self.assertEqual(
            response.url, self.go_admin_index_url,
            _('User must be redirected to main GO admin page with '
              '"user is not activated" notification')
        )

        goadmin_user = User.objects.filter(
            username=post_data['username'], is_active=False
        ).first()

        self.assertTrue(
            goadmin_user, _('GO admin user must be created with .is_active=False')
        )
        goadmin_user.is_active = True
        goadmin_user.save()

        response = self.client.post(self.login_url, data=self.users_credentials['goadmin'])
        self.assertEqual(
            response.url, self.vue_mo_admin_index_url,
            _(f'Login failed for {self.users_credentials["goadmin"]}')
        )

        response = self.client.get(self.go_admin_index_url)

        required_apps = [
            'Audit', 'Authentication and Authorization', 'Bcm', 'Companies',
            'GS1 Member Organisations', 'Prefixes', 'Products'
        ]
        available_apps = [str(item['name']) for item in response.context_data['available_apps']]

        self.assertEqual(
            set(required_apps), set(available_apps),
            _(f'User must have an access to the following apps: {required_apps}')
        )

    def test_mo_admin_registration(self):
        """
        MO admin user signup/login/check basic permissions
        """

        credentials = self.users_credentials['moadmin']
        post_data = {
            'username': credentials['username'],
            'password1': credentials['password'],
            'password2': credentials['password'],
            'registration_type': self.model_instances['mo1'].pk,
        }

        # create a MO Admin user with given credentials
        # expected result: not activated MO Admin user
        response = self.client.post(self.signup_url, data=post_data)

        self.assertEqual(
            response.status_code,
            302,
            _('User must be redirected to main MO admin page with '
              '"user is not activated" notification')
        )

        self.assertEqual(
            response.url, self.mo_admin_index_url,
            _('User must be redirected to main MO admin page with '
              '"user is not activated" notification')
        )

        moadmin_user = User.objects.filter(
            username=post_data['username'], is_active=False
        ).first()

        self.assertTrue(
            moadmin_user, _('MO admin user must be created with .is_active=False')
        )
        moadmin_user.is_active = True
        moadmin_user.save()

        response = self.client.post(self.login_url, data=self.users_credentials['moadmin'])
        self.assertEqual(
            response.url, self.vue_mo_admin_index_url,
            _(f'Login failed for {self.users_credentials["moadmin"]}')
        )

        response = self.client.get(self.mo_admin_index_url)
        required_apps = [
            'Audit', 'Companies', 'Prefixes', 'Products', 'Authentication and Authorization',
            'GS1 Member Organisations',
        ]
        available_apps = [str(item['name']) for item in response.context_data['available_apps']]

        self.assertEqual(
            set(required_apps), set(available_apps),
            _(f'User must have an access to the following apps: {required_apps}')
        )

    def test_not_activated_mo_admin_users(self):
        """
        1. creates a GO Admin manually
        2. registers MO Admin
        3. login with GO Admin credentials
        4. activate MO admin with post request
        5. check login for MO Admin
        """

        # create already activated go admin
        goadmin = self.create_django_user(self.users_credentials['goadmin'])
        mo = MemberOrganisation.objects.all().first()

        MemberOrganisationUser.objects.create(
            user=goadmin, organization=mo, is_admin=True
        )

        credentials = self.users_credentials['moadmin']
        post_data = {
            'username': credentials['username'],
            'password1': credentials['password'],
            'password2': credentials['password'],
            'registration_type': self.model_instances['mo1'].pk,
        }

        # create a MO Admin user with given credentials
        # expected result: not activated MO Admin user
        response = self.client.post(self.signup_url, data=post_data)
        self.assertEqual(
            response.url, self.mo_admin_index_url, _(f'Signup failed for {credentials}')
        )

        moadmin = User.objects.get(username=credentials['username'])

        # login as go admin
        login_result = self.client.login(**self.users_credentials['goadmin'])
        self.assertTrue(
            login_result,
            _('Login failed for GO Admin with credentials: {self.users_credentials["goadmin"]}')
        )

        # activate MO admin with post request
        goadmin_user_change_url = reverse(
            'admin:go_admin_auth_user_change', args=(moadmin.pk,)
        )

        self.assertFalse(moadmin.is_active, _('MO Admin must not be activated here'))

        post_data = {'is_active': 'checked'}
        response = self.client.post(goadmin_user_change_url, data=post_data)
        moadmin.refresh_from_db()
        self.assertTrue(moadmin.is_active, _('MO Admin must be activated here'))

    def test_case_insensitive_login(self):
        """
        """

        # create already activated go admin
        goadmin = self.create_django_user(self.users_credentials['goadmin'], add_to_group=True)

        credentials = self.users_credentials['goadmin']
        post_data = {
            'username': self.randomize_string(credentials['username']),  # randomize login case
            'password': credentials['password'],
        }

        # login with case-randomized username
        response = self.client.post(self.login_url, data=post_data)

        self.assertEqual(
            response.status_code,
            302,
            _('User must be redirected to main GO admin page')
        )

        self.assertEqual(
            response.url, self.vue_mo_admin_index_url,
            _(f'Login failed for {credentials}, must be allowed with a randomized case username')
        )
