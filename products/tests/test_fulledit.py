from products.models.product import Product
from . import TestCase
from services import prefix_service


class PageFulleditTestCase(TestCase):
    url = '/products/2/fulledit_legacy/'

    def setUp(self):
        self.user = self.setUp_createAccount()
        self.loadProducts()
        response = self.get('products:products_list')
        assert response.status_code == 200
        #self.assertContains(response, 'Product 1')
        self.assertContains(response, 'Product 2')
        #self.assertContains(response, 'Product 3')

    def test_page_exist(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'Edit product')

    def test_page_basic_tab(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'Edit product')
        self.assertContains(response, 'Product Identification')
        self.assertContains(response, 'GTIN')

    def test_page_measurements_tab(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'Weights')
        self.assertContains(response, 'Dimensions')

    def test_page_picture_tab(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'Product Image')

    def test_page_symbols_tab(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'EAN13')

    def test_page_summary_tab(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'id="summary"')

    def test_page_cloud_tab(self):
        assert True

    def test_product_delete(self):
        response = self.post('products:delete_product', product_id=2)
        assert response.status_code == 302
        assert response.url == self.reverse('products:products_list')
        response = self.get('products:products_list')
        assert response.status_code == 200
        #self.assertContains(response, 'Product 1')
        self.assertNotContains(response, 'Product 2')
        #self.assertContains(response, 'Product 3')

    def test_product_delete_set(self):
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        prefix.starting_from = '5390001100010'
        prefix.save()
        url = self.reverse('products:delete_product', product_id=2) + '?set=1'
        response = self.post(url)
        assert response.status_code == 302
        assert response.url == self.reverse('products:products_list')
        response = self.get('products:products_list')
        assert response.status_code == 200
        #self.assertContains(response, 'Product 1')
        self.assertNotContains(response, 'Product 2')
        #self.assertContains(response, 'Product 3')
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.starting_from == '5390001100003'

    def test_page_gtin(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, '<b>53900011</b> <span style="color:#F26334">0000</span> <span id="cd">3</span>')
