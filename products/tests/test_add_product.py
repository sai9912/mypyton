from . import TestCase
from services import prefix_service
from products.models.package_level import PackageLevel


class PageAddProductTestCase(TestCase):
    url = '/products/add/'
    user = None

    def setUp(self):
        self.user = self.setUp_createAccount()
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        if prefix == self.user.profile.product_active_prefix:
            self.user.profile.product_active_prefix = None
            self.user.profile.save()

    def test_page_exist(self):
        response = self.client.get(self.url + '?prefix=53900011')
        assert response.status_code == 200
        self.assertContains(response, 'New Product')
        self.assertContains(response, 'Packaging Level')

    def test_no_prefix_provided(self):
        response = self.client.get(self.url)
        assert response.status_code == 302
        assert response.url == '/prefixes/'

    def test_prefix_by_post(self):
        response = self.client.post(self.url, { 'prefix' : '53900011' })
        assert response.status_code == 200
        self.assertContains(response, 'New Product')
        self.assertContains(response, 'Packaging Level')

    def test_with_active_prefix(self):
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        prefix_service.make_active(user=self.user, prefix=prefix.prefix)
        response = self.client.get(self.url)
        self.assertContains(response, 'New Product')
        self.assertContains(response, 'Packaging Level')

    def test_title_express(self):
        response = self.client.get(self.url + '?prefix=53900011')
        assert response.status_code == 200
        self.assertContains(response, 'New Product')
        response = self.client.get(self.url + '?prefix=53900011&express=1')
        assert response.status_code == 200
        self.assertContains(response, 'Express Allocation')
        response = self.client.post(self.url, { 'prefix': '53900011', 'express': 1 })
        self.assertContains(response, 'Express Allocation')

    def test_select_packaging_level(self):
        response = self.client.get(self.url + '?prefix=53900011')
        assert response.status_code == 200
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        prefix_service.make_active(user=self.user, prefix=prefix.prefix)
        package_level = PackageLevel(id='70',
                                     level='Consumer Unit (Base Unit/Each) e.g. bottle of beer',
                                     unit_descriptor='BASE_UNIT_OR_EACH')
        package_level.save()
        response = self.client.post(self.url, { 'package_level': '70' })
        assert response.status_code == 302
        assert response.url == '/products/add_product_package_type/'
