from . import TestCase
from django.contrib.auth.models import User

from services import prefix_service
from BCM.models import Country
from member_organisations.models import MemberOrganisation
from products.models.country_of_origin import CountryOfOrigin
from products.models.target_market import TargetMarket
from products.models.language import Language
from products.models.package_type import PackageType
from products.models.package_level import PackageLevel
from products.models.product import Product


class PrefixesTestCase(TestCase):
    url = '/prefixes/'
    user = None

    post_data = {       'uuid': '53900011',
                       'email': '53900011@test.com',
              'company_prefix': '53900011,53900012',
                'company_name': 'GS1 Ireland',
                     'credits': '39:20,43:100,44:100',
                     'txn_ref': 'Test_1,Test_3,Test_2',
         'member_organisation': 'gs1' }

    def setUp(self):
        country = Country(slug='BE', name='Belgium')
        country.save()
        member_organisation = MemberOrganisation(name='GS1',
                                                 slug='gs1',
                                                 is_active=1,
                                                 gs1_enable_advanced_dashboard=1,
                                                 country=country)
        member_organisation.save()
        response = self.client.post('/API/v0/AccountCreateOrUpdate/', self.post_data)
        self.client.get(response.url)
        self.user = User.objects.get(email='53900011@test.com')
        assert not self.user is None
        self.user.profile.agreed = True
        self.user.profile.save()

    def test_page_exist(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'Prefix management')

    def test_range_field(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, '<b>53900011</b><span style="color:#F26334">0000</span>3')
        self.assertContains(response, '<b>53900011</b><span style="color:#F26334">9999</span>1')
        self.assertContains(response, '<b>53900012</b><span style="color:#F26334">0000</span>0')
        self.assertContains(response, '<b>53900012</b><span style="color:#F26334">9999</span>8')

    def test_next_number_field(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertNotContains(response, '<b>53900011</b><span style="color:#F26334">0002</span>7')
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        prefix.starting_from = '5390001100027'
        prefix.save()
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        assert prefix.starting_from == '5390001100027'
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, '53900011</b><span style="color:#F26334">0002</span>7')

    def test_no_suspended_prefixes(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertNotContains(response, 'Suspended prefixes')

    def _test_suspended_prefixes_exist(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        prefix.is_suspended = 1
        prefix.save()
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        assert prefix.is_suspended == 1
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'Suspended prefixes')
        self.assertContains(response, '<td>53900011</td>')

    def test_make_active(self):
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        assert prefix == self.user.profile.product_active_prefix
        prefix1 = prefix.prefix
        prefix = prefix_service.find_item(user=self.user, prefix='53900012')
        assert prefix.prefix == '53900012'
        assert prefix != self.user.profile.product_active_prefix
        prefix2 = prefix.prefix
        prefix_service.make_active(user=self.user, prefix=prefix1)
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        assert prefix == self.user.profile.product_active_prefix
        prefix = prefix_service.find_item(user=self.user, prefix='53900012')
        assert prefix.prefix == '53900012'
        assert prefix != self.user.profile.product_active_prefix
        prefix_service.make_active(user=self.user, prefix=prefix2)
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        assert prefix != self.user.profile.product_active_prefix
        prefix = prefix_service.find_item(user=self.user, prefix='53900012')
        assert prefix.prefix == '53900012'
        assert prefix == self.user.profile.product_active_prefix

    def test_models_make_starting_from(self):
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        prefix.make_starting_from()
        assert prefix.starting_from == '5390001100003'

    def test_models_get_active(self):
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        assert prefix == self.user.profile.product_active_prefix

    def test_ajax(self):
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        assert prefix.description == ''
        prefix_id = prefix.id
        response = self.client.post('/prefixes/ajax/', {'pk': prefix_id, 'value': 'New description'})
        assert response.status_code == 200
        assert response.content == b'{"success": true}'
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        assert prefix.description == 'New description'

    def test_product_count(self):
        country_of_origin = CountryOfOrigin.service.create(code='250', name='FRANCE')
        target_market = TargetMarket.service.create(code='056', market='BELGIUM')
        language = Language.service.create(slug='de', name='German')
        package_type = PackageType.service.create(
            type_i18n='{"en": "Bag"}', code='BG', ui_enabled=1
        )

        package_level_case = PackageLevel.service.create(id=50, level='Outer Case e.g. case of beer (bottles or packs)', unit_descriptor='CASE')

        self.product1 = Product.service.create( gtin = '05390001100003',
                         gln_of_information_provider = '5390001100003',
                                             company = 'Company 1',
                                            category = '11111111',
                                   label_description = 'Label Description 1',
                                         description = 'Product 1',
                                                 sku = 'SKU 1',
                                               brand = 'Brand 1',
                                     functional_name = 'Functional Name 1',
                                   country_of_origin = country_of_origin,
                                       target_market = target_market,
                                            language = language,
                                        package_type = package_type,
                                       package_level = package_level_case,
                                               owner = self.user,
                                  gs1_company_prefix = '53900011')

        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, '1 Product')
