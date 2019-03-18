from . import TestCase
from services import prefix_service
from products.models.country_of_origin import CountryOfOrigin
from products.models.target_market import TargetMarket
from products.models.language import Language
from products.models.package_type import PackageType
from products.models.package_level import PackageLevel
from products.models.product import Product


class SetStartingTestCase(TestCase):
    url = '/prefixes/prefixes_set_starting/1'
    user = None
    product = None

    def loadProducts(self):
        country_of_origin = CountryOfOrigin.service.create(code='250', name='FRANCE')
        target_market = TargetMarket.service.create(code='056', market='BELGIUM')
        language = Language.service.create(slug='de', name='German')
        package_type = PackageType.service.create(
            type_i18n='{"en": "Bag"}', code='BG', ui_enabled=1
        )

        package_level_base = PackageLevel.service.create(id=70, level='Consumer Unit (Base Unit/Each) e.g. bottle of beer', unit_descriptor='BASE_UNIT_OR_EACH')

        self.product = Product.service.create(gtin='05390001100102',
                                              gs1_company_prefix='53900011',
                                              gln_of_information_provider='5390001100102',
                                              company='Company',
                                              category='11111111',
                                              label_description='Label Description',
                                              description='Product',
                                              sku='SKU',
                                              brand='Brand',
                                              functional_name='Functional Name',
                                              country_of_origin=country_of_origin,
                                              target_market=target_market,
                                              language=language,
                                              package_type=package_type,
                                              package_level=package_level_base,
                                              owner=self.user)

    def setUp(self):
        self.user = self.setUp_createAccount()

    def test_page_exist(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'Set starting number for a range')

    def test_set_starting_number(self):
        response = self.client.post(self.url, {'starting_number': '0010'})
        assert response.status_code == 302
        assert response.url == self.reverse('prefixes:prefixes_list')
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.starting_from == '5390001100102'

    def test_set_starting_number(self):
        self.loadProducts()
        response = self.client.post(self.url, {'starting_number': '0010'})
        assert response.status_code == 200
        self.assertContains(response, 'This number is already assigned. Try another one.')
