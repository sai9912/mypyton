from . import TestCase
import json
from products.views.subproducts import _get_request_quantity
from products.models.product import Product
from products.models.sub_product import SubProduct


class PageSubproductsFulledit(TestCase):
    url = '/products/4/fulledit_legacy/'
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

    def loadSubproduct(self):
        url = self.reverse('products:subproduct_add_case_details')
        self.loadSession()
        self.loadProducts()
        response = self.client.get(url)
        assert response.status_code == 200
        self.assertContains(response, 'New item (Step 2 of 2: Details)')
        response = self.client.post(url, self.valid_data)
        assert response.status_code == 302
        assert response.url == '/products/4/view_summary/'

    def loadSubproductsToProduct(self):
        products = Product.objects.all()
        product1 = products[0]
        product2 = products[1]
        product3 = products[2]
        subproducts = SubProduct.objects.all()
        assert len(subproducts) == 0
        subproduct1 = SubProduct(product=product1,
                                 sub_product=product2,
                                 quantity=10)
        subproduct1.save()
        subproduct2 = SubProduct(product=product1,
                                 sub_product=product3,
                                 quantity=20)
        subproduct2.save()
        subproducts = SubProduct.objects.all()
        assert len(subproducts) == 2

    def setUp(self):
        self.user = self.setUp_createAccount()

    def test_page_exist(self):
        self.loadSubproduct()
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'Edit product')

    def test_subproducts_on_page(self):
        self.loadSubproduct()
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'Subproducts')

    def test_gtin_on_page(self):
        self.loadSubproduct()
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, '05390001100010')

    def test_subproducts_ajax(self):
        self.loadSubproduct()
        response = self.client.get('/products/ajax/4/subproducts_list')
        data = json.loads(response.content)['data']
        assert data[0]['gtin'] == '05390000100004'
        assert data[0]['package_level'] == 'CASE'
        assert data[0]['description'] == 'Product 1'
        assert data[1]['gtin'] == '05390001100003'
        assert data[1]['package_level'] == 'PACK_OR_INNER_PACK'
        assert data[1]['description'] == 'Product 2'

    def test_get_request_quantity(self):
        post = {
            'action': 'remove',
            'data[2][DT_RowId]': '1',
            'data[2][gtin]': '05390001100003',
            'data[2][package_level]': 'PACK_OR_INNER_PACK',
            'data[2][description]': 'Product 2',
            'data[2][quantity]': '10'
        }
        sub_product_id, quantity = _get_request_quantity(post)
        assert sub_product_id == 2
        assert quantity == 10

    def test_ajax_av_subproducts_list(self):
        self.loadSubproduct()
        response = self.client.get('/products/ajax/4/av_subproducts_list')
        assert response.status_code == 200
        data = json.loads(response.content)['data']
        assert len(data) == 3
        assert data[0]['gtin'] == '05390001100003'
        assert data[1]['gtin'] == '05390001200000'
        assert data[2]['gtin'] == '05390001100010'

    def test_ajax_av_subproducts_list_filter(self):
        self.loadSubproduct()
        response = self.client.get('/products/ajax/2/av_subproducts_list')
        assert response.status_code == 200
        data = json.loads(response.content)['data']
        assert len(data) == 3, (data, len(data))
        assert data[0]['gtin'] == '05390001100003', data[0]['gtin']

    def test_ajax_av_subproduct_add(self):
        self.loadSession()
        self.loadProducts()
        self.loadSubproductsToProduct()
        subproducts = SubProduct.objects.order_by('id').all()
        assert len(subproducts) == 2
        subproducts1 = subproducts[0]
        assert subproducts1.quantity == 10
        subproducts2 = subproducts[1]
        assert subproducts2.quantity == 20
        post = {
            'action': 'edit',
            'data[2][DT_RowId]': '1',
            'data[2][gtin]': '05390001100034',
            'data[2][package_level]': 'PACK_OR_INNER_PACK',
            'data[2][description]': 'Product 2',
            'data[2][quantity]': '10'
        }
        response = self.client.post(self.reverse('products:ajax_subproduct_add', product_id=1), post)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['status'] == 'Ok'
        subproducts = SubProduct.objects.order_by('id').all()
        assert len(subproducts) == 2
        subproducts1 = subproducts[0]
        assert subproducts1.quantity == 20
        subproducts2 = subproducts[1]
        assert subproducts2.quantity == 20

    def test_ajax_av_subproduct_add_wrong_command(self):
        self.loadSession()
        self.loadProducts()
        self.loadSubproductsToProduct()
        post = {
            'action': 'remove',
            'data[2][DT_RowId]': '1',
            'data[2][gtin]': '05390001100034',
            'data[2][package_level]': 'PACK_OR_INNER_PACK',
            'data[2][description]': 'Product 2',
            'data[2][quantity]': '10'
        }
        response = self.client.post(self.reverse('products:ajax_subproduct_add', product_id=1), post)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['status'] == 'Error'
        assert data['message'] == 'Unknown command'

    def test_ajax_subproduct_modify(self):
        self.loadSession()
        self.loadProducts()
        self.loadSubproductsToProduct()
        subproducts = SubProduct.objects.order_by('id').all()
        assert len(subproducts) == 2
        subproducts1 = subproducts[0]
        assert subproducts1.quantity == 10
        subproducts2 = subproducts[1]
        assert subproducts2.quantity == 20
        post = {
            'action': 'edit',
            'data[2][DT_RowId]': '1',
            'data[2][gtin]': '05390001100034',
            'data[2][package_level]': 'PACK_OR_INNER_PACK',
            'data[2][description]': 'Product 2',
            'data[2][quantity]': '30'
        }
        response = self.client.post(self.reverse('products:ajax_subproduct_edit', product_id=1), post)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['status'] == 'Ok'
        subproducts = SubProduct.objects.order_by('id').all()
        assert len(subproducts) == 2
        subproducts1 = subproducts[0]
        assert subproducts1.quantity == 30
        subproducts2 = subproducts[1]
        assert subproducts2.quantity == 20

    def test_ajax_subproduct_modify_wrong_command(self):
        self.loadSession()
        self.loadProducts()
        self.loadSubproductsToProduct()
        post = {
            'action': 'wrong',
            'data[2][DT_RowId]': '1',
            'data[2][gtin]': '05390001100034',
            'data[2][package_level]': 'PACK_OR_INNER_PACK',
            'data[2][description]': 'Product 2',
            'data[2][quantity]': '10'
        }
        response = self.client.post(self.reverse('products:ajax_subproduct_edit', product_id=1), post)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['status'] == 'Error'
        assert data['message'] == 'Unknown command'

    def test_ajax_subproduct_delete(self):
        self.loadSubproduct()
        post = {
            'action': 'remove',
            'data[2][DT_RowId]': '1',
            'data[2][gtin]': '05390001100003',
            'data[2][package_level]': 'PACK_OR_INNER_PACK',
            'data[2][description]': 'Product 2',
            'data[2][quantity]': '10'
        }
        response = self.client.post('/products/ajax/4/subproduct_edit', post)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['status'] == 'Ok'
        response = self.client.get('/products/ajax/4/subproducts_list')
        assert response.status_code == 200
        data = json.loads(response.content)['data']
        assert len(data) == 1
        assert data[0]['gtin'] == '05390000100004'
        assert data[0]['package_level'] == 'CASE'
        assert data[0]['description'] == 'Product 1'

    def test_ajax_subproduct_delete_wrong(self):
        self.loadSubproduct()
        post = {
            'action': 'remove',
            'data[8][DT_RowId]': '1',
            'data[8][gtin]': '05390001100034',
            'data[8][package_level]': 'PACK_OR_INNER_PACK',
            'data[8][description]': 'Product 2',
            'data[8][quantity]': '10'
        }
        response = self.client.post('/products/ajax/4/subproduct_edit', post)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['status'] == 'Error'
        assert data['message'] == 'Subproduct not found'
