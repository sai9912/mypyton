import json

from . import TestCase
from services import prefix_service
from products.models.package_level import PackageLevel
from products.models.package_type import PackageType
from products.models.dimension_uom import DimensionUOM
from products.models.weight_uom import WeightUOM
from products.models.country_of_origin import CountryOfOrigin
from products.models.target_market import TargetMarket
from products.models.language import Language
from products.models.product import Product


class PageProductAddDetailsTestCase(TestCase):
    url = '/products/add/details/'
    user = None

    valid_data = {               'gtin': '05390001100003',
                              'company': 'GS1 France',
                    'label_description': 'Valid Label Description',
                                 'mark': '',
                                'brand': 'Valid Brand',
                            'sub_brand': 'Valid Sub brand',
                      'functional_name': 'Valid Product Type/Functional Name',
                              'variant': 'Valid Variant',
                          'description': 'Valid Product/Trade Item Description',
                             'category': '12345678',
                                  'sku': 'Company/Internal Product Code or SKU',
                             'is_cunit': 'on',
                             'is_dunit': 'on',
                             'is_vunit': 'on',
                             'is_iunit': 'on',
                             'is_ounit': 'on',
                    'country_of_origin': '250',
                        'target_market': '056',
                             'language': 'de',
          'gln_of_information_provider': '5390001100003',
                         'gross_weight': '100',
                     'gross_weight_uom': 'ONZ',
                           'net_weight': '200',
                       'net_weight_uom': 'ONZ',
                                'depth': '300',
                            'depth_uom': 'CMT',
                                'width': '400',
                            'width_uom': 'CMT',
                               'height': '500',
                           'height_uom': 'CMT',
                               'upload': '',
                          'website_url': '',
                        'bar_placement': '/static/products/site/wizard/proddesc/BG.png',
                        'package_level': '70',
                         'package_type': '14'
        }

    def setUp_addProduct(self):
        package_level = PackageLevel(id='70',
                                     level='Consumer Unit (Base Unit/Each) e.g. bottle of beer',
                                     unit_descriptor='BASE_UNIT_OR_EACH')
        package_level.save()
        response = self.client.post('/products/add/', { 'package_level': '70' })
        assert response.status_code == 302
        assert response.url == '/products/add_product_package_type/'

    def setUp_addProductPackageType(self):
        member_organisation = self.user.member_organisations_memberorganisation.first()
        package_type = PackageType(
            id=14,
            type_i18n='{"en": "Tray"}',
            code='PU',
            member_organisation=member_organisation,
            ui_enabled=1,
        )
        package_type.save()
        response = self.client.post(
            '/products/add_product_package_type/',
            {
                'package_type': '14',
                'bar_placement': '/static/products/site/wizard/proddesc/BG.png'
            }
        )
        assert response.status_code == 302
        assert response.url == '/products/add/details/'

    def setUp(self):
        self.user = self.setUp_createAccount()
        self.setUp_addProduct()
        self.setUp_addProductPackageType()

        dimension_uom = DimensionUOM(uom_i18n='{"en": "Centimetres"}', abbr='cm', code='CMT')
        dimension_uom.save()
        weight_uom = WeightUOM(uom_i18n='{"en": "Ounces"}', abbr='oz', code='ONZ')
        weight_uom.save()
        country_of_origin = CountryOfOrigin(code='250', name='FRANCE')
        country_of_origin.save()
        #target_market = TargetMarket(code='056', market='BELGIUM')
        #target_market.save()
        language = Language(slug='de', name='German')
        language.save()

    def test_page_exist(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'New Base Unit / Each')

    def test_valid_data(self):
        response = self.client.post(self.url, self.valid_data)
        assert response.status_code == 302
        assert response.url == '/products/1/view_summary/'

    def test_field_label_description(self):
        data = self.valid_data.copy()
        data['label_description'] = ''
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Label description field is required.')
        self.assertContains(response, 'This field is required.')

    def test_field_brand(self):
        data = self.valid_data.copy()
        data['brand'] = ''
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Brand field is required.')
        self.assertContains(response, 'This field is required.')

    def test_field_functional_name(self):
        data = self.valid_data.copy()
        data['functional_name'] = ''
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Product Type/Functional Name field is required.')
        self.assertContains(response, 'This field is required.')

    def test_field_description(self):
        data = self.valid_data.copy()
        data['description'] = ''
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Product/Trade Item Description field is required.')
        self.assertContains(response, 'This field is required.')

    def test_field_category(self):
        data = self.valid_data.copy()
        data['category'] = ''
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Global Product Classification field is required.')
        self.assertContains(response, 'This field is required.')

    def test_field_options(self):
        data = self.valid_data.copy()
        data['is_cunit'] = ''
        data['is_dunit'] = ''
        data['is_vunit'] = ''
        data['is_iunit'] = ''
        data['is_ounit'] = ''
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Options: At least one option must be selected.')

    def test_field_country_of_origin(self):
        data = self.valid_data.copy()
        data['country_of_origin'] = 'AAA'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Select a valid choice. AAA is not one of the available choices.')

    def test_field_target_market(self):
        data = self.valid_data.copy()
        data['target_market'] = 'AAA'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Select a valid choice. AAA is not one of the available choices.')

    def test_field_language(self):
        data = self.valid_data.copy()
        data['language'] = 'AAA'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Select a valid choice. AAA is not one of the available choices.')

    def test_field_gross_weight_uom(self):
        data = self.valid_data.copy()
        data['gross_weight_uom'] = 'AAA'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Select a valid choice. AAA is not one of the available choices.')

    def test_field_net_weight_uom(self):
        data = self.valid_data.copy()
        data['net_weight_uom'] = 'AAA'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Select a valid choice. AAA is not one of the available choices.')

    def test_field_depth_uom(self):
        data = self.valid_data.copy()
        data['depth_uom'] = 'AAA'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Select a valid choice. AAA is not one of the available choices.')

    def test_field_width_uom(self):
        data = self.valid_data.copy()
        data['width_uom'] = 'AAA'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Select a valid choice. AAA is not one of the available choices.')

    def test_field_height_uom(self):
        data = self.valid_data.copy()
        data['height_uom'] = 'AAA'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Select a valid choice. AAA is not one of the available choices.')

    def test_gross_weight_range(self):
        data = self.valid_data.copy()
        data['gross_weight'] = '-10'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Gross weight must be a positive number greater than zero and less than 1000000.00')
        data['gross_weight'] = '10000000'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Gross weight must be a positive number greater than zero and less than 1000000.00')
        data['gross_weight'] = 'AAA'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Gross weight must be a positive number greater than zero and less than 1000000.00')
        data['gross_weight'] = '100'
        response = self.client.post(self.url, data)
        assert response.status_code == 302
        assert response.url == '/products/1/view_summary/'

    def test_net_weight_range(self):
        data = self.valid_data.copy()
        data['net_weight'] = '-10'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Net weight must be a positive number greater than zero and less than 1000000.00')
        data['net_weight'] = '10000000'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Net weight must be a positive number greater than zero and less than 1000000.00')
        data['net_weight'] = 'AAA'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Net weight must be a positive number greater than zero and less than 1000000.00')
        data['net_weight'] = '100'
        response = self.client.post(self.url, data)
        assert response.status_code == 302
        assert response.url == '/products/1/view_summary/'

    def test_depth_range(self):
        data = self.valid_data.copy()
        data['depth'] = '-10'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Depth must be a positive number greater than zero and less than 1000000.00')
        data['depth'] = '10000000'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Depth must be a positive number greater than zero and less than 1000000.00')
        data['depth'] = 'AAA'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Depth must be a positive number greater than zero and less than 1000000.00')
        data['depth'] = '100'
        response = self.client.post(self.url, data)
        assert response.status_code == 302
        assert response.url == '/products/1/view_summary/'

    def test_width_range(self):
        data = self.valid_data.copy()
        data['width'] = '-10'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Width must be a positive number greater than zero and less than 1000000.00')
        data['width'] = '10000000'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Width must be a positive number greater than zero and less than 1000000.00')
        data['width'] = 'AAA'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Width must be a positive number greater than zero and less than 1000000.00')
        data['width'] = '100'
        response = self.client.post(self.url, data)
        assert response.status_code == 302
        assert response.url == '/products/1/view_summary/'

    def test_height_range(self):
        data = self.valid_data.copy()
        data['height'] = '-10'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Height must be a positive number greater than zero and less than 1000000.00')
        data['height'] = '10000000'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Height must be a positive number greater than zero and less than 1000000.00')
        data['height'] = 'AAA'
        response = self.client.post(self.url, data)
        assert response.status_code == 200
        self.assertContains(response, 'Height must be a positive number greater than zero and less than 1000000.00')
        data['height'] = '100'
        response = self.client.post(self.url, data)
        assert response.status_code == 302
        assert response.url == '/products/1/view_summary/'

    def test_dbfield_company_organisation(self):
        response = self.client.post(self.url, self.valid_data)
        assert response.status_code == 302
        assert response.url == '/products/1/view_summary/'
        product = Product.objects.get(gtin='05390001100003')
        assert product.company_organisation.id == 1

    def test_dbfield_member_organisation(self):
        response = self.client.post(self.url, self.valid_data)
        assert response.status_code == 302
        assert response.url == '/products/1/view_summary/'
        product = Product.objects.get(gtin='05390001100003')
        assert product.member_organisation.pk == 1

    def test_prefix_increase(self):
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        starting_from = prefix.starting_from
        response = self.client.post(self.url, self.valid_data)
        assert response.status_code == 302
        assert response.url == '/products/1/view_summary/'
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        assert starting_from != prefix.starting_from

    def test_prefix_rollover_9999(self):
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        prefix.starting_from = '5390001199991'
        prefix.increment_starting_from()
        assert prefix.starting_from == '5390001100003'

    def test_prefix_rollover_product(self):
        response = self.client.post(self.url, self.valid_data)
        assert response.status_code == 302
        assert response.url == '/products/1/view_summary/'
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        prefix.starting_from = '5390001199991'
        prefix.increment_starting_from()
        assert prefix.starting_from == '5390001100010'

    def test_preselect_country(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, '<option value="056" selected>BELGIUM</option>')

    def test_preselect_language(self):
        self.user.profile.language = 'de'
        self.user.profile.save()
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, '<option value="de" selected>German</option>')
