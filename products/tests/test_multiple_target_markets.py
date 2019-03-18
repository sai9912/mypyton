from . import TestCase
from ..models.product import Product
from ..models.target_market import TargetMarket
from ..models.package_level import PackageLevel
from services import gtin_target_market_service, prefix_service


class MultipleTargetMarkets(TestCase):
    user = None
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

    def test_other_target_markets(self):
        product = Product.objects.get(id=2)
        target_market = TargetMarket.objects.get(market='FRANCE')
        gtin_target_market_service.create(product, target_market)
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'Other Target Markets:')
        self.assertContains(response, 'FRANCE</a>')

    def test_created_tm1_changed_tm2(self):
        products_count_old = len(Product.objects.all())
        target_market_new = TargetMarket.objects.get(market='ITALY')
        product = Product.objects.get(id=2)
        assert target_market_new.code != product.target_market.code
        post = {'gtin': product.gtin,
                'gs1_company_prefix': product.gs1_company_prefix,
                'gln_of_information_provider': product.gln_of_information_provider,
                'company': product.company,
                'category': product.category,
                'label_description': product.label_description,
                'description': product.description,
                'sku': product.sku,
                'brand': product.brand,
                'functional_name': product.functional_name,
                'country_of_origin': product.country_of_origin.code,
                'target_market': target_market_new.code,        # change Target Market
                'language': product.language.slug,
                'package_type': product.package_type,
                'package_level': product.package_level,
                'is_cunit': 'on',
                'bar_placement': 'bar_placement'
        }
        response = self.client.post(self.url, post)
        assert response.status_code == 200
        products_count_new = len(Product.objects.all())
        assert products_count_old == products_count_new         # product the same, no new product

    def test_tm_stays_gtin_allocated(self):
        products_count_old = len(Product.objects.all())
        product = Product.objects.get(id=2)
        product.package_level_id = PackageLevel.BASE
        product.save()
        prefix = prefix_service.find_item(user=self.user, prefix=product.gs1_company_prefix)
        for i in range(0, 3):
            prefix.increment_starting_from()
        prefix_service.save(prefix)
        url = self.reverse(
            'products:duplicate_product',
            product_id=product.id,
            target_market=product.target_market.code
        )
        response = self.client.get(url)
        assert response.status_code == 302
        assert response.url == '/products/4/fulledit/'
        assert response.url != self.reverse('products:fulledit', product_id=product.id)
        products_count_new = len(Product.objects.all())
        assert products_count_new == products_count_old + 1       # new product created

    def test_tm_changed_gtin_same(self):
        products_count_old = len(Product.objects.all())
        target_market_new = TargetMarket.objects.get(market='ITALY')
        product = Product.objects.get(id=2)
        assert target_market_new.code != product.target_market.code
        url = self.reverse('products:duplicate_product', product_id=product.id, target_market=target_market_new.code)
        response = self.client.get(url)
        assert response.status_code == 302
        assert response.url == self.reverse('products:fulledit', product_id=product.id)
        products_count_new = len(Product.objects.all())
        assert products_count_old == products_count_new         # product the same, no new product
        assert True
