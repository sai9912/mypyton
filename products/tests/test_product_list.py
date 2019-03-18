from . import TestCase


class PageProductsListTestCase(TestCase):
    url = 'products:products_list'
    user = None
    product1 = None
    product2 = None
    product3 = None

    def setUp(self):
        self.user = self.setUp_createAccount()

    def test_page_exist(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'Edit your product catalogue')
        self.assertContains(response, 'No products found')

    def test_page_load_products(self):
        self.loadProducts()
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'Product 2')

    def test_page_render_gtin(self):
        self.loadProducts()
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, '0<b>53900011</b>0000<b>3</b>')

    def test_search_case(self):
        self.loadProducts()
        response = self.client.post(self.url, {'case':'on'})
        assert response.status_code == 200
        self.assertNotContains(response, 'Product 2')
        self.assertNotContains(response, 'Product 3')

    def test_search_pack(self):
        self.loadProducts()
        response = self.client.post(self.url, {'pack':'on'})
        assert response.status_code == 200
        self.assertNotContains(response, 'Product 1')
        self.assertContains(response, 'Product 2')
        self.assertNotContains(response, 'Product 3')

    def test_search_base(self):
        self.loadProducts()
        response = self.client.post(self.url, {'base':'on'})
        assert response.status_code == 200
        self.assertNotContains(response, 'Product 1')
        self.assertNotContains(response, 'Product 2')

    def test_search_brand(self):
        self.loadProducts()
        response = self.client.post(self.url, {'case':'on', 'pack':'on', 'base':'on', 'brand':'Brand 1'})
        assert response.status_code == 200
        self.assertNotContains(response, 'Product 2')
        self.assertNotContains(response, 'Product 3')

    def test_search_description(self):
        self.loadProducts()
        response = self.client.post(self.url, {'case':'on', 'pack':'on', 'base':'on', 'description':'Product 2'})
        assert response.status_code == 200
        self.assertNotContains(response, 'Product 1')
        self.assertContains(response, 'Product 2')
        self.assertNotContains(response, 'Product 3')

    def test_search_sku(self):
        self.loadProducts()
        response = self.client.post(self.url, {'case':'on', 'pack':'on', 'base':'on', 'sku':'SKU 3'})
        assert response.status_code == 200
        self.assertNotContains(response, 'Product 1')
        self.assertNotContains(response, 'Product 2')

    def test_search_gtin(self):
        self.loadProducts()
        response = self.client.post(self.url, {'case':'on', 'pack':'on', 'base':'on', 'gtin':'10000'})
        assert response.status_code == 200
        self.assertContains(response, 'Product 2')
        self.assertNotContains(response, 'Product 3')

    def test_mark(self):
        self.loadProducts()
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'Product 2')
        response = self.client.post(self.url, {'case':'on', 'pack':'on', 'base':'on', 'mark':'on'})
        assert response.status_code == 200
        self.assertNotContains(response, 'Product 1')
        self.assertNotContains(response, 'Product 2')
        self.assertNotContains(response, 'Product 3')
        self.assertContains(response, 'No products found')
        response = self.client.post('/products/ajax/%i/mark/' % self.product1.id, {})
        assert response.status_code == 200
        response = self.client.post(self.url, {'case':'on', 'pack':'on', 'base':'on', 'mark':'on'})
        assert response.status_code == 200
        self.assertNotContains(response, 'Product 2')
        self.assertNotContains(response, 'Product 3')

    def test_unmark(self):
        self.loadProducts()
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'Product 2')
        response = self.client.post(self.url, {'case':'on', 'pack':'on', 'base':'on', 'mark':'on'})
        assert response.status_code == 200
        self.assertNotContains(response, 'Product 1')
        self.assertNotContains(response, 'Product 2')
        self.assertNotContains(response, 'Product 3')
        self.assertContains(response, 'No products found')
        response = self.client.post('/products/ajax/%i/mark/' % self.product1.id, {})
        assert response.status_code == 200
        response = self.client.post('/products/ajax/%i/mark/' % self.product2.id, {})
        assert response.status_code == 200
        response = self.client.post('/products/ajax/%i/mark/' % self.product3.id, {})
        assert response.status_code == 200
        response = self.client.post(self.url, {'case':'on', 'pack':'on', 'base':'on', 'mark':'on'})
        assert response.status_code == 200
        self.assertContains(response, 'Product 2')
        self.assertNotContains(response, 'No products found')
        response = self.client.post('/products/ajax/%i/unmark/' % self.product2.id, {})
        assert response.status_code == 200
        response = self.client.post(self.url, {'case':'on', 'pack':'on', 'base':'on', 'mark':'on'})
        assert response.status_code == 200
        self.assertNotContains(response, 'Product 2')

    def test_logo(self):
        self.loadProducts()
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, '/static/site/logo/gs1-logo.png')

    def test_change_logo(self):
        self.loadProducts()
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, '/static/site/logo/gs1-logo.png')
        self.user.profile.member_organisation.gs1_logo_path = '/static/site/logo/new_logo.png'
        self.user.profile.member_organisation.save()
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, '/static/site/logo/new_logo.png')
