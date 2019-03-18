from test_plus.test import TestCase as PlusTestCase
from django.contrib.auth.models import User
from BCM.models import Country
from member_organisations.models import MemberOrganisation
from services import prefix_service, users_service


class TestCase(PlusTestCase):
    def __init__(self, test_name):
        try:
            if self.url[0] != '/':
                self.url = self.reverse(self.url)
        except:
            pass
        return super().__init__(test_name)

    def setUp_createAccount(self):
        country, is_created = Country.objects.get_or_create(slug='BE', name='Belgium')
        member_organisation, is_created = MemberOrganisation.objects.get_or_create(
            slug='gs1',
            defaults=dict(name='GS1', gs1_enable_advanced_dashboard=1, is_active=1, country=country)
        )
        response = self.client.post('/API/v0/AccountCreateOrUpdate/', {'uuid': '53900011',
                                                                       'email': '53900011@test.com',
                                                                       'company_prefix': '53900011,53900012',
                                                                       'company_name': 'GS1 Ireland',
                                                                       'credits': '39:20,43:100,44:100',
                                                                       'txn_ref': 'Test_1,Test_3,Test_2',
                                                                       'member_organisation': 'gs1'})
        assert response.status_code == 302
        self.client.get(response.url)
        user = User.objects.get(email='53900011@test.com')
        assert not user is None
        user.profile.agreed = True
        user.profile.save()
        prefix = prefix_service.find_item(user=user, prefix='53900011')
        assert prefix.prefix == '53900011'
        prefix_service.make_active(user=user, prefix=prefix.prefix)
        return user


class TestGLN(TestCase):
    user = None

    def setUp(self):
        self.user = self.setUp_createAccount()

    def test_active_prefix_widget(self):
        url = self.reverse('prefixes:prefixes_list')
        response = self.client.get(url)
        assert response.status_code == 200

    def _test_no_gln(self):
        company_organisation = users_service.get_company_organisation(self.user)
        company_organisation.gln_capability = False
        company_organisation.save()
        url = self.reverse('prefixes:prefixes_list')
        response = self.client.get(url)
        assert response.status_code == 200
        self.assertNotContains(response, 'Locations:')

    def test_gln_exist(self):
        company_organisation = users_service.get_company_organisation(self.user)
        company_organisation.gln_capability = True
        company_organisation.save()
        url = self.reverse('prefixes:prefixes_list')
        response = self.client.get(url)
        assert response.status_code == 200


