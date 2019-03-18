from . import TestCase
from services import prefix_service, product_service, sub_product_service


class SubproductsAddCaseDetailsTestCase(TestCase):
    url = 'products:subproduct_add_case_details'
    user = None

    valid_data = {             'gtin': '05390001100010',
                      'bar_placement': '/static/products/site/wizard/proddesc/innerpack_PIDS.gif',
                      'package_level': '60',
                       'package_type': '1',
                              'gtin0': '0',
                            'company': 'GS1 France',
                  'label_description': 'Valid Label Description',
                              'brand': 'Valid Brand',
                          'sub_brand': 'Valid Sub brand',
                    'functional_name': 'Valid Product Type/Functional Name',
                            'variant': 'Valid Variant',
                        'description': 'Valid Product/Trade Item Description',
                           'category': '12345678',
                                'sku': 'Company/Internal Product Code or SKU',
                           'is_cunit': 'on',
                  'country_of_origin': '250',
                      'target_market': '056',
                           'language': 'de',
        'gln_of_information_provider': '5390001100010',
                              'pid_1': '10',
                              'pid_2': '20'
    }

    def loadSession(self):
        session = self.client.session
        session['new_product'] = {'gtin': '5390001100003',
                                  'package_level': '60',
                                  'package_type': '1',
                                  'bar_placement': '/static/products/site/wizard/proddesc/CS.png',
                                  'sub_products': [1, 2]}
        session.save()

    def setUp(self):
        self.user = self.setUp_createAccount()

    def test_page_exist(self):
        self.loadSession()
        self.loadProducts()
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'New item (Step 2 of 2: Details)')

    def _test_no_session(self):
        self.loadProducts()
        response = self.client.get(self.url)
        assert response.status_code == 404

    def test_no_products(self):
        self.loadSession()
        response = self.client.get(self.url)
        assert response.status_code == 302
        assert response.url == self.reverse('products:subproduct_add_case')
        session = self.client.session
        flash_messages = session['flash_messages']
        assert flash_messages[0][0] == 'Choose products for this container'
        assert flash_messages[0][1] == 'danger'

    def test_flashed_message(self):
        self.loadSession()
        response = self.client.get(self.url)
        assert response.status_code == 302
        assert response.url == self.reverse('products:subproduct_add_case')
        session = self.client.session
        flash_messages = session['flash_messages']
        assert flash_messages[0][0] == 'Choose products for this container'
        assert flash_messages[0][1] == 'danger'
        self.loadProducts()
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'New item (Step 2 of 2: Details)')
        self.assertContains(response, 'Choose products for this container')

    def test_post(self):
        self.loadSession()
        self.loadProducts()
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'New item (Step 2 of 2: Details)')
        response = self.client.post(self.url, self.valid_data)
        assert response.status_code == 302
        assert response.url == '/products/4/view_summary/'

    def test_get_associated(self):
        self.loadSession()
        self.loadProducts()
        response = self.client.post(self.url, self.valid_data)
        assert response.status_code == 302
        assert response.url == '/products/4/view_summary/'
        product = product_service.get(gtin='05390001100010')
        associated = sub_product_service.get_associated(product)
        assert associated[0].sub_product.gtin == '05390000100004'
        assert associated[1].sub_product.gtin == '05390001100003'

    def test_increase_active_prefix(self):
        prefix = prefix_service.find_item(user=self.user, starting_from='5390001100003')
        self.loadSession()
        self.loadProducts()
        response = self.client.post(self.url, self.valid_data)
        assert response.status_code == 302
        assert response.url == '/products/4/view_summary/'
        prefix = prefix_service.find_item(user=self.user, prefix=prefix.prefix)
        assert prefix.starting_from == '5390001100027'

    def test_barcode_placement(self):
        self.loadSession()
        self.loadProducts()
        response = self.client.post(self.url, self.valid_data)
        assert response.status_code == 302
        assert response.url == '/products/4/view_summary/'
        product = product_service.get(gtin='05390001100010')
        assert product.bar_placement == '/static/products/site/wizard/proddesc/innerpack_PIDS.gif'

    def test_preselect_country(self):
        self.loadSession()
        self.loadProducts()
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, '<option value="056" selected>BELGIUM</option>')

    def test_preselect_language(self):
        self.user.profile.language = 'de'
        self.user.profile.save()
        self.loadSession()
        self.loadProducts()
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, '<option value="de" selected>German</option>')
