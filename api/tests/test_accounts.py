from django.contrib.auth.models import User, Group
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from api.factories import ApiKeyFactory
from member_organisations.models import MemberOrganisation
from company_organisations.models import CompanyOrganisation
from prefixes.models import Prefix
from BCM.models import Country
from test_plus import TestCase as PlusTestCase


import doctest

from users.factories import UserFactory, AuthTokenFactory
from .. import serializers, utils



def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(serializers))
    tests.addTests(doctest.DocTestSuite(utils))
    return tests


class AccountSerializerTest(APITestCase):

    def setUp(self):
        country = Country.objects.create(slug='IE', name='Ireland')
        self.member_organisation = MemberOrganisation.objects.create(name='GS1IE', slug='gs1ie', is_active=1, country=country)
        self.user = User.objects.create_user(username='test_user', password='password')
        mo_admin_group = Group.objects.create(name='MO Admins')
        self.user.groups.add(mo_admin_group)
        self.member_organisation.add_user(self.user)
        self.user.profile.member_organisation_id = 1
        self.user.profile.save()

        self.client = APIClient()
        response = self.client.post(reverse('api:login'), data={
                                    'username': 'test_user', 'password': 'password'})
        self.token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_login_view_get(self):
        url = reverse('api:login')
        count_tokens = self.user.auth_token_set.all().count()
        self.client.get(url)
        self.assertEquals(
            self.user.auth_token_set.all().count(),
            count_tokens + 1
        )

    def test_set_agreement(self):
        url = reverse("api:user_profile", args=["test_user"])
        response = self.client.get(url)
        response_data = response.json()
        self.assertFalse(response_data["agreed"])
        json_data = {
            "agreed": True,
            "agreed_version": "None",
            "agreed_date": "2018-01-01T00:00"
        }
        response = self.client.patch(url, data=json_data, format="json")
        response = self.client.get(url, format="json")
        new_data = response.json()
        self.assertTrue(new_data["agreed"])

    def test_terms(self):
        url = reverse("api:terms")
        json_data = self.client.get(url).json()
        keys = json_data.keys()
        self.assertIn("terms", keys)
        self.assertIn("terms_cloud", keys)
        self.assertIn("date_terms", keys)
        self.assertIn("date_terms_cloud", keys)
        self.assertNotIn("apprais", keys)

    def test_register_with_prefix(self):
        url = '/api/v1/register/'
        prefix = '53900011'
        data = {
            'uuid': f'{prefix}',
            'email': f'{prefix}@test.com',
            'company_prefix': f'{prefix}',
            'company_name': f'Company w. gcp {prefix}',
            'member_organisation': 'gs1ie'
        }
        response = self.client.post(url, data)
        assert response.status_code == 201
        assert str(response.content[:17]) == str(b'"/users/api/auth/')

    def test_register_without_prefix(self):
        url = '/api/v1/register/'
        prefix = '53900011'
        data = {
            'uuid': f'{prefix}',
            'email': f'{prefix}@test.com',
            'company_name': f'Company w. gcp {prefix}',
            'member_organisation': 'gs1ie'
        }
        response = self.client.post(url, data)
        assert response.status_code == 201
        assert str(response.content[:17]) == str(b'"/users/api/auth/')


class AccountsTestCase(PlusTestCase):
    def setUp(self):
        self.user = UserFactory()
        # string token
        self.token = AuthTokenFactory(user=self.user)
        self.api_client = APIClient()
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')

    def test_login_view_get_forbidden(self):
        url = self.reverse('api:login')
        response = self.client.get(url)
        self.assertEquals(
            response.status_code,
            403
        )
    def test_logout(self):
        url = self.reverse('api:logout')
        response = self.api_client.post(url)
        assert response.status_code == 204, response.status_code

    def test_logout_all(self):
        url = self.reverse('api:logout-all')
        self.token = AuthTokenFactory(user=self.user)
        assert self.user.auth_token_set.count() == 2, self.user.auth_token_set.count()
        response = self.api_client.post(url)
        assert response.status_code == 204, response.status_code
        assert self.user.auth_token_set.count() == 0, self.user.auth_token_set.count()

    def test_protected_data(self):
        url = self.reverse('api:protected-data')
        response = self.api_client.get(url)
        assert response.status_code == 200
        assert response.content == b'{"data":"THIS IS THE PROTECTED STRING FROM SERVER"}'


class LoginAPITestCase(APITestCase):
    def setUp(self):
        country = Country(slug='BE', name='Belgium')
        country.save()
        self.member_organisation = MemberOrganisation(name='GS1',
                                                     slug='gs1',
                                                     is_active=1,
                                                     country=country,
                                                     gs1_prefix_regex='^539|^501|^509|^0\\d\\d')
        self.member_organisation.save()
        self.company_orgnisation = CompanyOrganisation.objects.create(**{
            'uuid': '53900011',
            'company': 'GS1 Ireland',
            'name': 'GS1 Ireland',
            'member_organisation': self.member_organisation,
            'country': country,
        })
        self.user = User.objects.create_user(username='test', password='password')
        mo_admin_group = Group.objects.create(name='MO Admins')
        self.user.groups.add(mo_admin_group)
        self.member_organisation.add_user(self.user)
        self.company_orgnisation.add_user(self.user)
        self.user.profile.company_organisation = self.company_orgnisation
        self.user.profile.member_organisation = self.member_organisation
        self.user.profile.save()

    def test_product_active_prefix(self):
        generic_data = {
            'prefix': '723372372',
            'is_suspended': False,
            'is_special': '',
            'starting_from': '7233723720006',
            'company_organisation': self.company_orgnisation,
            'member_organisation': self.member_organisation,
            'description': 'Some description prefix'
        }
        Prefix.objects.create(**generic_data)

        login_data = {'username': 'test', 'password': 'password'}
        client = APIClient()
        response = client.post(reverse('api:login'), data=login_data)
        token = response.data['token']

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        response = self.client.get(reverse('api:packaging-list'))
        assert response.status_code == 200
        assert response.wsgi_request.user.profile.product_active_prefix.prefix == '723372372'


class ApiKeyTestCase(PlusTestCase):

    def setUp(self):
        self.api_key = ApiKeyFactory(key=None)

    def test_generate_key(self):
        self.api_key.key = None
        self.api_key.save()
        assert self.api_key.key, self.api_key.key
