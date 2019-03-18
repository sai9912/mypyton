from unittest.mock import patch

from rest_framework import serializers

from company_organisations.factories import CompanyOrganisationFactory
from company_organisations.models import (
    CompanyOrganisation,
    CompanyOrganisationUser,
)
from django.core.management import call_command
from test_plus.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User

from member_organisations.factories import MemberOrganisationFactory
from services import prefix_service
from BCM.models import Country
from member_organisations.models import (
    MemberOrganisation,
    MemberOrganisationUser,
)
from users.models import UsersService, Profile
from .factories import UserFactory


class UsersTestCase(TestCase):
    url = '/profile/'
    user = None

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
        country = Country(slug='BE', name='Belgium')
        country.save()
        member_organisation = MemberOrganisation(name='GS1',
                                                 slug='gs1',
                                                 is_active=1,
                                                 country=country)
        member_organisation.save()
        response = self.client.post('/API/v0/AccountCreateOrUpdate/',
                                    self.post_data)
        self.client.get(response.url)
        self.user = User.objects.get(email='53900011@test.com')
        assert self.user is not None
        self.user.profile.agreed = True
        self.user.profile.save()

    def test_page_exist(self):
        response = self.client.get(self.url, follow=True)
        assert response.status_code == 200
        self.assertContains(response, 'Dashboard')

    # @skip('profile page changed')
    def test_range_field(self):
        response = self.client.get(self.url, follow=True)
        assert response.status_code == 200
        # self.assertContains(response, '<b>53900011</b><span
        # style="color:#F26334">0000</span>3')
        # self.assertContains(response, '<b>53900011</b><span
        # style="color:#F26334">9999</span>1')
        # self.assertContains(response, '<b>53900012</b><span
        # style="color:#F26334">0000</span>0')
        # self.assertContains(response, '<b>53900012</b><span
        # style="color:#F26334">9999</span>8')

    # @skip('profile page changed')
    def test_next_number_field(self):
        response = self.client.get(self.url, follow=True)
        assert response.status_code == 200
        # self.assertNotContains(response, '<b>53900011</b><span
        # style="color:#F26334">0002</span>7')
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        prefix.starting_from = '5390001100027'
        prefix.save()
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        assert prefix.starting_from == '5390001100027'
        response = self.client.get(self.url, follow=True)
        assert response.status_code == 200
        # self.assertContains(response, '<b>53900011</b><span
        # style="color:#F26334">0002</span>7')

    def test_terms_agreed(self):
        response = self.client.post(self.url,
                                    {'submit': 'Submit', 'agree': 'on'},
                                    follow=True)
        assert response.status_code == 200
        response = self.client.get(self.url, follow=True)
        assert response.status_code == 200
        self.assertNotContains(response, 'I agree to the Terms and Conditions')

    def test_decorator_user_agreement_required(self):
        self.user.profile.member_organisation.gs1_terms_enable = True
        self.user.profile.member_organisation.save()
        self.user.profile.agreed = False
        self.user.profile.save()
        response = self.client.get(self.url)
        assert response.status_code == 302
        url = response.url
        assert url == '/users/user_agreement_required?next=/profile/'
        response = self.client.get(url)
        assert response.status_code == 200
        self.assertContains(response, 'Agreement required')
        self.assertContains(response, 'I agree to the Terms and Conditions')

    def test_decorator_user_agreement_required_agreed(self):
        self.user.profile.agreed = False
        self.user.profile.member_organisation.gs1_terms_version = (
            settings.TERMS_VERSION
        )
        self.user.profile.member_organisation.save()
        self.user.profile.save()
        url = '/users/user_agreement_required?next=/profile/'
        data = {
            'agree': 'on',
            'terms_version': settings.TERMS_VERSION,
            'url_next': '/profile/'
        }
        response = self.client.post(url, data)
        assert response.status_code == 302, response.status_code
        assert response.url == '/profile/'

    def test_decorator_user_agreement_required_not_agreed(self):
        self.user.profile.agreed = False
        self.user.profile.save()
        url = '/users/user_agreement_required?next=/profile/'
        response = self.client.post(url, {
            'terms_version': settings.TERMS_VERSION,
            'url_next': '/profile/'
        })
        assert response.status_code == 200
        self.assertContains(response, 'Agreement required')
        self.assertContains(response, 'I agree to the Terms and Conditions')

    def test_decorator_user_agreement_required_wrong_version(self):
        self.user.profile.agreed = False
        self.user.profile.save()
        url = '/users/user_agreement_required?next=/profile/'
        response = self.client.post(url, {
            'agree': 'on',
            'terms_version': '1900/01/01',
            'url_next': '/profile/'
        })
        assert response.status_code == 200
        self.assertContains(response, 'Agreement required')
        self.assertContains(response, 'I agree to the Terms and Conditions')

    def test_user_agreement_required_leftside_menu(self):
        self.user.profile.agreed = False
        self.user.profile.save()
        url = '/users/user_agreement_required?next=/profile/'
        response = self.client.get(url)
        assert response.status_code == 200
        self.assertContains(response, 'Agreement required')
        self.assertNotContains(response, 'My Account')
        self.assertNotContains(response, 'Product Manager')

    def test_check_logout(self):
        response = self.client.get(self.url, follow=True)
        assert response.status_code == 200
        self.assertContains(response, 'Log out')

    def test_company_and_user(self):
        response = self.client.get(self.url, follow=True)
        assert response.status_code == 200
        self.assertContains(response, 'Company name:')
        self.assertContains(response, 'User:')


class ManagementCommandTest(TestCase):
    def setUp(self):
        c, created = Country.objects.get_or_create(name='Test Country',
                                                   slug='TC')
        c2, created = Country.objects.get_or_create(name='Test Country2',
                                                    slug='T2')
        mo = MemberOrganisation.objects.create(country=c, name='mo1',
                                               is_active=True, slug='mo1')
        mo2 = MemberOrganisation.objects.create(country=c2, name='gs1go',
                                                is_active=True, slug='gs1go')

    def test_001_load_mo_user_command(self):
        def mocked_json_load(*args, **kwargs):
            return {
                "organisations": {
                    "mo1": [{
                        "name": "Jan Konecny",
                        "user_role": "mo1-admin",
                        "email": "konecny@gs1cz.org",
                        "password": "dummy",
                        "country_prefix": "859"
                    }],
                    "gs1go": [{
                        "name": "Narayan Kandel",
                        "user_role": "gs1go-admin",
                        "email": "npkand@gmail.com",
                        "password": "dummy"
                    }]
                }
            }

        # initially there should be zero user
        self.assertEquals(User.objects.count(), 0)

        with patch("json.load", side_effect=mocked_json_load):
            call_command('load_mo_user')
            # now we expect 2 user at db and it should be 'konecny@gs1cz.org'
            # and 'npkand@gmail.com'
            self.assertEquals(User.objects.count(), 2)
            self.assertTrue(
                User.objects.filter(email='konecny@gs1cz.org').exists())

            user = User.objects.get(email='konecny@gs1cz.org')
            # now verify the group for the user
            self.assertTrue(user.groups.filter(name='MO Admins').exists())
            self.assertFalse(user.groups.filter(name='GO Admins').exists())

            user2 = User.objects.get(email='npkand@gmail.com')
            # now verify group for go user
            self.assertTrue(user2.groups.filter(name='MO Admins').exists())
            self.assertTrue(user2.groups.filter(name='GO Admins').exists())

    def test_002_load_company_user_command(self):
        def mocked_json_load(*args, **kwargs):
            return {
                "companies": [
                    {
                        "prefixes": ["8594379"], "name": "Zentiva k. s.",
                        "email": "test@gs1cz-01.com", "uuid": "gs1cz-01",
                        "role": "mo1"
                    }]
            }

        # initially there should be zero CompanyOrganization
        self.assertEquals(CompanyOrganisation.objects.count(), 0)

        with patch("json.load", side_effect=mocked_json_load):
            call_command('load_company_user')
            # now we expect one company organization
            self.assertEquals(CompanyOrganisation.objects.count(), 1)
            # and it should be 'gs1cz-01'
            self.assertTrue(
                CompanyOrganisation.objects.filter(uuid='gs1cz-01').exists())
            co = CompanyOrganisation.objects.get(uuid='gs1cz-01')
            # verify company name and user's email
            self.assertEquals(co.name, "Zentiva k. s.")
            self.assertEquals(co.users.first().email, 'test@gs1cz-01.com')


class TermsAgreeTestCase(TestCase):
    url = '/profile/'
    user = None

    post_data = {
        'uuid': 'gs1se-company',
        'email': '735009647@test.com',
        'company_prefix': '735009647',
        'company_name': 'GS1 Sweden',
        'member_organisation': 'gs1se'
    }

    def setUp(self):
        country = Country(slug='SE', name='Sweden')
        country.save()
        member_organisation = MemberOrganisation(name='GS1se',
                                                 slug='gs1se',
                                                 is_active=1,
                                                 country=country)
        member_organisation.save()
        response = self.client.post('/API/v0/AccountCreateOrUpdate/',
                                    self.post_data)
        self.client.get(response.url)
        self.user = User.objects.get(email='735009647@test.com')
        assert self.user is not None
        self.user.profile.agreed = True
        self.user.profile.save()

    def test_page_exist(self):
        response = self.client.get(self.url, follow=True)
        assert response.status_code == 200
        self.assertContains(response, 'Dashboard')

    def test_footer_terms(self):
        response = self.client.get(self.url, follow=True)
        assert response.status_code == 200
        self.assertContains(response, '/static/legal/terms_gs1se.txt')

    def test_terms_agre(self):
        response = self.client.get(self.url, follow=True)
        assert response.status_code == 200
        self.assertNotContains(response, 'name="agree"')

    def test_terms_agreed(self):
        response = self.client.post(self.url,
                                    {'submit': 'Submit', 'agree': 'on'},
                                    follow=True)
        assert response.status_code == 200
        response = self.client.get(self.url, follow=True)
        assert response.status_code == 200
        self.assertNotContains(response, 'name="agree"')

    def test_terms_none_type(self):
        self.user.profile.member_organisation = None
        self.user.profile.save()
        response = self.client.get(self.url, follow=True)
        assert response.status_code == 200
        self.assertNotContains(response, 'name="agree"')

    def test_terms_page_exist(self):
        response = self.client.get('/terms/', follow=True)
        assert response.status_code == 200

    def test_organization_user_detail_reverse(self):
        url = self.reverse('organization_user_detail', organization_pk=1,
                           user_pk=2)
        assert url == '/users/organization_user_detail/1/2/'

    def test_organization_user_detail_exist(self):
        url = self.reverse('organization_user_detail', organization_pk=1,
                           user_pk=2)
        response = self.client.get(url)
        assert response.status_code == 302
        assert response.url == '/admin/auth/user/2/change/'


class UserServiceTestCase(TestCase):

    def setUp(self):
        self.auth_user = UserFactory()
        self.member_organisation = MemberOrganisationFactory()
        self.company_organisation = CompanyOrganisationFactory()
        self.uid = '123qwe123'
        self.details = {
            'member_organisation': self.member_organisation,
            'company_organisation': self.company_organisation,
            'uid': self.uid
        }

    def test_update_details(self):
        UsersService().update_details(self.auth_user, self.details)
        profile = Profile.objects.select_related(
            'member_organisation'
        ).get(id=self.auth_user.profile.id)
        assert (profile.member_organisation.country_id ==
                self.member_organisation.country_id)
        assert profile.company_organisation_id == self.company_organisation.id
        assert profile.uid == self.uid

    def test_update_details_check_multiple_member_organisations(self):

        for _ in range(2):
            member_organisation = MemberOrganisationFactory()
            MemberOrganisationUser.objects.create(
                user=self.auth_user,
                organization=member_organisation,
                is_admin=True
            )
        error = None
        try:
            UsersService().update_details(self.auth_user, self.details)
        except serializers.ValidationError as e:
            error = str(e)
        error_for_check = serializers.ValidationError(
            'Multiple member organizations for the same user are not allowed'
        )
        assert error == str(error_for_check), error

    def test_update_details_check_multiple_company_organisations(self):

        for _ in range(2):
            company_organisation = CompanyOrganisationFactory()
            CompanyOrganisationUser.objects.create(
                user=self.auth_user,
                organization=company_organisation,
                is_admin=True
            )

        self.details.pop('member_organisation')
        error = None
        try:
            UsersService().update_details(self.auth_user, self.details)
        except serializers.ValidationError as e:
            error = str(e)
        error_for_check = serializers.ValidationError(
            'Multiple companies for the same user are not allowed'
        )
        assert error == str(error_for_check), error

    def test_create(self):
        email = 'test@test123.ru'
        UsersService().create(email=email, defaults=self.details)
        user = User.objects.filter(email=email).first()
        assert user
        assert user.profile.member_organisation == self.member_organisation
        assert user.profile.company_organisation == self.company_organisation
        assert user.profile.uid == self.uid

    def test_get(self):
        profile = UsersService().get(self.auth_user, 'profile')
        assert self.auth_user.profile == profile
        member_organisation = UsersService().get(
            self.auth_user,
            'member_organisation'
        )
        assert self.auth_user.profile.member_organisation == member_organisation
        nothing = UsersService().get(
            self.auth_user,
            'field_does_not_exist'
        )
        assert nothing is None
