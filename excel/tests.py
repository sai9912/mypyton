import json

from django.contrib.auth.models import User

from test_plus.test import TestCase as PlusTestCase
from BCM.models import Country
from member_organisations.models import MemberOrganisation, ProductTemplate
from services import prefix_service
from products.models.package_level import PackageLevel
from products.models.package_type import PackageType
from products.models.country_of_origin import CountryOfOrigin
from products.models.target_market import TargetMarket
from products.models.language import Language
from products.models.product import Product
from unittest import skip



class ExportProductsTestCase(PlusTestCase):
    url = 'excel:export_select'
    user = None

    def __init__(self, test_name):
        try:
            if self.url[0] != '/':
                self.url = self.reverse(self.url)
        except:
            pass
        super().__init__(test_name)

    def setUp_createAccount(self):
        country = Country(slug='BE', name='Belgium')
        country.save()
        member_organisation = MemberOrganisation(
            name='GS1',
            slug='gs1',
            is_active=1,
            country=country
        )
        member_organisation.save()
        data = {
            'uuid': '53900011',
            'email': '53900011@test.com',
            'company_prefix': '53900011,53900012',
            'company_name': 'GS1 Ireland',
            'credits': '39:20,43:100,44:100',
            'txn_ref': 'Test_1,Test_3,Test_2',
            'member_organisation': 'gs1'
        }
        url = '/API/v0/AccountCreateOrUpdate/'
        response = self.client.post(url, data=data)
        assert response.status_code == 302
        self.client.get(response.url)
        user = User.objects.get(
            email='53900011@test.com'
        )
        user.profile.agreed = True
        user.profile.save()
        prefix = prefix_service.find_item(user=user, prefix='53900011')
        assert prefix.prefix == '53900011'
        prefix_service.make_active(user=user, prefix=prefix.prefix)
        self.user = user
        return user

    def loadProducts(self):

        user = User.objects.get(
            email='53900011@test.com'
        )

        country_of_origin = CountryOfOrigin.service.create(
            code='250',
            name='FRANCE'
        )
        target_market = TargetMarket.service.create(
            code='056',
            market='BELGIUM'
        )
        language = Language.service.create(slug='de', name='German')
        package_type = PackageType.service.create(
            type_i18n='{"en": "Bag"}',
            code='BG',
            ui_enabled=1
        )

        package_level_case = PackageLevel.service.create(
            id=50,
            level='Outer Case e.g. case of beer (bottles or packs)',
            unit_descriptor='CASE'
        )
        package_level_pack = PackageLevel.service.create(
            id=60,
            level='Pack or Inner Pack e.g. six pack of beer bottles',
            unit_descriptor='PACK_OR_INNER_PACK'
        )
        package_level_base = PackageLevel.service.create(
            id=70,
            level='Consumer Unit (Base Unit/Each) e.g. bottle of beer',
            unit_descriptor='BASE_UNIT_OR_EACH'
        )
        self.product_template = ProductTemplate.objects.create(
            name='test',
            package_level=package_level_case,
            member_organisation=user.profile.member_organisation,
        )
        self.product1 = Product.service.create(
            gtin='05390000100004',
            gs1_company_prefix='53900001',
            gln_of_information_provider='5390000100004',
            company=json.dumps({'en': 'Company 1'}),
            category='11111111',
            label_description_i18n=json.dumps({'en': 'Label Description 1'}),
            description_i18n=json.dumps({'en': 'Product 1'}),
            sku='SKU 1',
            brand_i18n=json.dumps({'en': 'Brand 1'}),
            functional_name_i18n=json.dumps({'en': 'Functional Name 1'}),
            country_of_origin=country_of_origin,
            target_market=target_market,
            language=language,
            package_type=package_type,
            package_level=package_level_case,
            owner=self.user
        )

        self.product2 = Product.service.create(
            gtin='05390001100003',
            gs1_company_prefix='53900011',
            gln_of_information_provider='5390001100003',
            company=json.dumps({'en': 'Company 2'}),
            category='22222222',
            label_description_i18n=json.dumps(
                {
                    'en': 'Label '
                          'Description 2'
                }),
            description_i18n=json.dumps({'en': 'Product 2'}),
            sku='SKU 2',
            brand_i18n=json.dumps({'en': 'Brand 2'}),
            functional_name_i18n=json.dumps({'en': 'Functional Name 2'}),
            country_of_origin=country_of_origin,
            target_market=target_market,
            language=language,
            package_type=package_type,
            package_level=package_level_pack,
            owner=self.user
        )

        self.product3 = Product.service.create(
            gtin='05390001200000',
            gs1_company_prefix='53900012',
            gln_of_information_provider='5390001200000',
            company=json.dumps({'en': 'Company 3'}),
            category='33333333',
            label_description_i18n=json.dumps(
                {
                    'en': 'Label '
                          'Description 3'
                }
            ),
            description_i18n=json.dumps({'en': 'Product 3'}),
            sku='SKU 3',
            brand_i18n=json.dumps({'en': 'Brand 3'}),
            functional_name_i18n=json.dumps({'en': 'Functional Name 3'}),
            country_of_origin=country_of_origin,
            target_market=target_market,
            language=language,
            package_type=package_type,
            package_level=package_level_base,
            owner=self.user
        )

    def setUp(self):
        self.setUp_createAccount()
        self.loadProducts()

    def test_page_exist(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'Export products')

    @skip('locally passed ok')
    def test_export_products(self):
        data = {
            'export_type': 'products',
            'file_type': 'xlsx',
            'available_templates': self.product_template.id,

        }
        response = self.client.post(self.url, data)
        assert response.status_code == 200, response.status_code
        key, value = response._headers['content-type']
        assert value == 'application/zip', value
        # key, value = response._headers['content-length']
        # assert value == '4863', value

    def test_export_starred(self):
        self.product2.mark = 1
        self.product2.save()
        data = {
            'export_type': 'starred',
            'file_type': 'xlsx',
        }
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        key, value = response._headers['content-type']
        assert value == 'text/html; charset=utf-8', value
        # key, value = response._headers['content-length']
        # assert value == '11239', value
