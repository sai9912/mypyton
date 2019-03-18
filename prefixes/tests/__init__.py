from test_plus.test import TestCase as PlusTestCase
from django.contrib.auth.models import User

from services import prefix_service
from BCM.models import Country
from member_organisations.models import MemberOrganisation


class TestCase(PlusTestCase):
    def setUp_createAccount(self):
        country = Country(slug='BE', name='Belgium')
        country.save()
        member_organisation = MemberOrganisation(name='GS1',
                                                 slug='gs1',
                                                 is_active=1,
                                                 gs1_enable_advanced_dashboard=1,
                                                 country=country)
        member_organisation.save()
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
