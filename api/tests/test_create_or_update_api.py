from BCM.models import Country
from member_organisations.models import MemberOrganisation, MemberOrganisationUser
from services import users_service, logs_service
from django.contrib.auth.models import User as AuthUser, Group
from prefixes.models import Prefix
from rest_framework.reverse import reverse
from company_organisations.models import CompanyOrganisation
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from products.models.country_of_origin import CountryOfOrigin
from products.models.target_market import TargetMarket
from products.models.language import Language


class Gs1IeTestCase(APITestCase):
    url = '/api/v1/register/'

    post_data = {
        'uuid': '53900011',
        'email': '53900011@test.com',
        'company_prefix': '53900011,53900012',
        'company_name': 'GS1 Ireland',
        'credits': '39:20,43:100,44:100',
        'txn_ref': 'Test_1,Test_3,Test_2',
        'member_organisation': 'gs1'
    }

    def setUp(self):
        country, is_created = Country.objects.get_or_create(slug='BE', name='Belgium')
        member_organisation = MemberOrganisation(name='GS1', slug='gs1', is_active=1, country=country)
        member_organisation.save()

    def test_page_exist_but_not_allowed_method(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.data, {"detail": "Method \"GET\" not allowed."})

    def test_required_fields(self):
        response = self.client.post(self.url)
        self.assertEqual(
            response.data,
            {
                "uuid": [
                    "This field is required."
                ],
                "email": [
                    "This field is required."
                ],
                "member_organisation": [
                    "This field is required."
                ]
            }
        )

    def test_success_fully_post(self):
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, 201)

    def test_users_data(self):
        self.client.post(self.url, self.post_data)
        auth_user = AuthUser.objects.filter(email='53900011@test.com').first()
        self.assertTrue(auth_user is not None)
        company_organisation = users_service.get_company_organisation(auth_user)
        self.assertEqual(company_organisation.uuid, '53900011')
        self.assertEqual(company_organisation.company, 'GS1 Ireland')

    def test_prefixes_data(self):
        self.client.post(self.url, self.post_data)
        prefixes = Prefix.objects.all()
        self.assertEqual(len(prefixes), 2)
        self.assertEqual(prefixes[0].prefix, '53900011')
        self.assertEqual(prefixes[1].prefix, '53900012')

    def test_audit_data(self):
        self.client.post(self.url, self.post_data)
        audit = logs_service.all()
        self.assertEqual(len(audit), 1)
        self.assertEqual(audit[0].logger, 'audit')
        self.assertEqual(audit[0].level, 'INFO')
        self.assertEqual(audit[0].msg, 'logging in: 53900011@test.com::GS1 Ireland')
        self.assertEqual(audit[0].username, '53900011@test.com')

    def test_user_login(self):
        post_data = {
            'uuid': '53900011',
            'email': '53900011@test.com',
            'company_prefix': '53900011,53900012',
            'company_name': 'GS1 Ireland',
            'credits': '39:20,43:100,44:100',
            'txn_ref': 'Test_1,Test_3,Test_2',
            'member_organisation': 'gs1'
        }
        member_organisation = MemberOrganisation.objects.get(slug='gs1')
        member_organisation.login_api_auth_only = False
        member_organisation.save()
        response = self.client.post(self.url, post_data)
        self.assertEqual(response.status_code, 201)
        member_organisation = MemberOrganisation.objects.get(slug='gs1')
        member_organisation.login_api_auth_only = True
        member_organisation.save()
        response = self.client.post(self.url, post_data)
        self.assertEqual(response.status_code, 200)


class UserTestCase(APITestCase):
    def setUp(self):
        country = Country(slug='BE', name='Belgium')
        country.save()
        self.member_organisation = MemberOrganisation(
            name='GS1', slug='gs1', is_active=1, country=country
        )
        self.member_organisation.save()
        self.company_orgnisation = CompanyOrganisation.objects.create(**{
            'uuid': '53900011',
            'company': 'GS1 Ireland',
            'name': 'GS1 Ireland',
            'member_organisation': self.member_organisation,
            'country': country,
        })
        self.user = User.objects.create_user(username='test', password='password')
        self.mo_user = MemberOrganisationUser.objects.create(
            user=self.user,
            organization=self.member_organisation,
            is_admin=True,
        )
        self.company_orgnisation.add_user(self.user)
        self.profile = self.user.profile
        self.profile.member_organisation_id = 1
        self.profile.save()
        response = self.client.post(
            reverse('api:login'),
            data={'username': 'test', 'password': 'password'}
        )
        self.token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_create_user(self):
        url = reverse('api:user-create', args=('53900011',))
        data = {'uid': 'abba-123',
                'email': 'test@test.com',
                'first_name': 'test_first_name',
                'last_name': 'test_last_name'}
        response = self.client.post(url, data)
        assert response.status_code == 201, response.data
        assert response.data['email'] == data['email']
        assert response.data['first_name'] == data['first_name']
        assert response.data['last_name'] == data['last_name']

    def test_create_user_without_uid(self):
        url = reverse('api:user-create', args=('53900011',))
        data = {'email': 'test@test.com',
                'first_name': 'test_first_name',
                'last_name': 'test_last_name'}
        response = self.client.post(url, data)
        assert response.status_code == 400
        assert response.data['uid'][0] == 'This field is required.'

    def test_create_user_with_existing_uid(self):
        url = reverse('api:user-create', args=('53900011',))
        # Create user
        data = {'uid': 'abba-123',
                'email': 'test@test.com',
                'first_name': 'test_first_name',
                'last_name': 'test_last_name'}
        response = self.client.post(url, data)
        assert response.status_code == 201
        # Create User with existing UID
        data = {'uid': 'abba-123',
                'email': 'duplicate@test.com',
                'first_name': 'duplicate_first_name',
                'last_name': 'duplicate_last_name'}
        response = self.client.post(url, data)
        assert response.status_code == 400
        assert response.data['uid'][0] == 'User with this uid already exists', response.data['uid'][0]

    def test_update_user_with_same_uid_and_email(self):
        url = reverse('api:user-create', args=('53900011',))
        # Create user
        data = {'uid': 'abba-123',
                'email': 'test@test.com',
                'first_name': 'test_first_name',
                'last_name': 'test_last_name'}
        response = self.client.post(url, data)
        assert response.status_code == 201
        group, created = Group.objects.get_or_create(name='GO Admins')
        self.user.groups.add(group)
        data = {'uid': 'abba-123',
                'email': 'test@test.com',
                'first_name': 'duplicate_first_name',
                'last_name': 'duplicate_last_name'}
        url = reverse('api:user-detail', kwargs={'profile__uid': 'abba-123'})
        response = self.client.put(url, data)
        assert response.status_code == 200, response.data

    def test_create_product_defaults(self):
        CountryOfOrigin.service.create(code='21', name='BELGIUM')
        TargetMarket.service.create(code='21', market='BELGIUM')
        Language.service.create(slug='en', name='English')
        url = reverse('api:defaults-list')
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.data['country_of_origin'] == None
        assert response.data['target_market'] == None
        assert response.data['language'] == 1
