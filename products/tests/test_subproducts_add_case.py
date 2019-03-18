from . import TestCase
from services import prefix_service
from products.models.package_level import PackageLevel
from ..helpers import subproduct_helper


class SubproductsAddCaseTestCase(TestCase):
    url = 'products:subproduct_add_case'
    user = None

    def _add_package_type(self):
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        prefix_service.make_active(user=self.user, prefix=prefix.prefix)
        package_level = PackageLevel(id='60',
                                     level='Consumer Unit (Base Unit/Each) e.g. bottle of beer',
                                     unit_descriptor='BASE_UNIT_OR_EACH')
        package_level.save()
        response = self.client.post('/products/add/', { 'package_level': '60' })
        assert response.status_code == 302
        assert response.url == '/products/add_product_package_type/'

    def setUp(self):
        self.user = self.setUp_createAccount()

    def test_is_exist(self):
        self._add_package_type()
        response = self.get(self.url)
        assert response.status_code == 200

    def test_ajax_select(self):
        self.loadProducts()
        response = self.get('/products/ajax/1/subproduct_select')
        assert response.status_code == 200
        assert response.content == b'{"success": true}'

    def test_ajax_unselect(self):
        self.loadProducts()
        response = self.get('/products/ajax/1/subproduct_select')
        assert response.status_code == 200
        assert response.content == b'{"success": true}'
        response = self.get('/products/ajax/1/subproduct_unselect')
        assert response.status_code == 200
        assert response.content == b'{"success": true}'

    def test_ajax_selected(self):
        self.loadProducts()
        response = self.get('/products/ajax/1/subproduct_select')
        assert response.status_code == 200
        assert response.content == b'{"success": true}'
        response = self.get('/products/ajax/2/subproduct_select')
        assert response.status_code == 200
        assert response.content == b'{"success": true}'
        response = self.get('/products/ajax/subproduct_selected')
        assert response.status_code == 200
        assert response.content == b'{"sub_products": ["05390000100004", "05390001100003"]}'

    def test_show_prefix(self):
        self._add_package_type()
        response = self.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, '53900011')

    def test_subproducts_reset(self):
        session = {}
        assert subproduct_helper.subproducts_reset(session) is None
        assert session == {}
        session = { 'new_product' : {} }
        assert subproduct_helper.subproducts_reset(session) is None
        assert session['new_product']['sub_products'] == []
        session = { 'new_product' : { 'sub_products' : ['sub_product1', 'sub_product2'] } }
        assert subproduct_helper.subproducts_reset(session) is None
        assert session['new_product']['sub_products'] == []
