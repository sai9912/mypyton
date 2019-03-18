from . import TestCase
from django.contrib.auth.models import User

from BCM.models import Country
from member_organisations.models import MemberOrganisation
from ..models import Prefix
from users.helpers import get_api_auth


class ServiceManagerTestCase(TestCase):
    def setUp_create_user1(self):
        response = self.client.post('/API/v0/AccountCreateOrUpdate/', { 'uuid': '0001',
                                                                       'email': 'tester01@test.com',
                                                              'company_prefix': '53900001',
                                                                'company_name': 'company 01',
                                                         'member_organisation': 'gs1-belgium' })
        self.client.get(response.url)
        user = User.objects.get(email='tester01@test.com')
        assert not user is None
        user.profile.agreed = True
        user.profile.save()
        return user

    def setUp_create_user2(self):
        response = self.client.post('/API/v0/AccountCreateOrUpdate/', { 'uuid': '0002',
                                                                       'email': 'tester02@test.com',
                                                              'company_prefix': '53900002',
                                                                'company_name': 'company 02',
                                                         'member_organisation': 'gs1-belgium' })
        self.client.get(response.url)
        user = User.objects.get(email='tester02@test.com')
        assert not user is None
        user.profile.agreed = True
        user.profile.save()
        return user

    def setUp_create_user3(self):
        response = self.client.post('/API/v0/AccountCreateOrUpdate/', { 'uuid': '0002',
                                                                       'email': 'tester03@test.com',
                                                              'company_prefix': '53900003',
                                                                'company_name': 'company 02',
                                                         'member_organisation': 'gs1-belgium' })
        self.client.get(response.url)
        user = User.objects.get(email='tester03@test.com')
        assert not user is None
        user.profile.agreed = True
        user.profile.save()
        return user

    def setUp(self):
        country = Country(slug='BE', name='Belgium')
        country.save()
        member_organisation = MemberOrganisation(name='GS1 Belgium',
                                                 slug='gs1-belgium',
                                                 is_active=1,
                                                 gs1_enable_advanced_dashboard=True,
                                                 country=country)
        member_organisation.save()

        self.user1 = self.setUp_create_user1()
        self.user2 = self.setUp_create_user2()

    def test_check_instance(self):
        with self.assertRaises(ValueError) as error:
            Prefix.service.check_instance(None)
        assert error.exception.__str__() == 'None is not of type Prefix'
        prefix = Prefix()
        Prefix.service.check_instance(prefix)

    def test_prefix_list_user1(self):
        url_auth_user1 = get_api_auth(self.user1.email)
        response = self.get(url_auth_user1)
        assert response.status_code == 302
        assert response.url == self.reverse('profile')
        response = self.get(self.reverse('prefixes:prefixes_list'))
        assert response.status_code == 200
        self.assertContains(response, '53900001')
        self.assertNotContains(response, '53900002')

    def test_prefix_list_user2_other_company(self):
        url_auth_user2 = get_api_auth(self.user2.email)
        response = self.get(url_auth_user2)
        assert response.status_code == 302
        assert response.url == self.reverse('profile')
        response = self.get(self.reverse('prefixes:prefixes_list'))
        assert response.status_code == 200
        self.assertNotContains(response, '53900001')
        self.assertContains(response, '53900002')

    def test_prefix_list_user3_same_company(self):
        user3 = self.setUp_create_user3()
        url_auth_user3 = get_api_auth(user3.email)
        response = self.get(url_auth_user3)
        assert response.status_code == 302
        assert response.url == self.reverse('profile')
        response = self.get(response.url)
        assert response.status_code == 200
        self.assertContains(response, '53900002')
        self.assertContains(response, '53900003')
