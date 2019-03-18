from test_plus import TestCase

from products.factories import (
    LanguageFactory, CountryOfOriginFactory,
    TargetMarketFactory,
    DimensionUOMFactory,
    WeightUOMFactory,
    NetContentUOMFactory,
)


class ListAPIViewTestCaseMixin:
    factory = None
    count = 2
    url_patern = ''

    def setUp(self):
        self.url = self.reverse(f'api:{self.url_patern}')


    def create_instances(self, count):

        for i in range(count):
            self.factory()

    def test_method_list(self):
        count = 2
        self.create_instances(count)
        response = self.client.get(self.url)
        assert response.status_code == 200, response.status_code
        assert len(response.data) == count,len(response.data)

class LanguageListAPIViewTestCase(ListAPIViewTestCaseMixin, TestCase):

    factory = LanguageFactory
    url_patern = 'languages-list'


class COOListAPIViewTestCase(ListAPIViewTestCaseMixin, TestCase):
    factory = CountryOfOriginFactory
    url_patern = 'countries-list'


class TMListAPIViewTestCase(ListAPIViewTestCaseMixin, TestCase):
    factory = TargetMarketFactory
    url_patern = 'target-market-list'


class ProductDimensionUOMViewTestCasee(ListAPIViewTestCaseMixin, TestCase):
    factory = DimensionUOMFactory
    url_patern = 'dimensions-uom'


class ProductWeightsUOMViewTestCase(ListAPIViewTestCaseMixin, TestCase):
    factory = WeightUOMFactory
    url_patern = 'weights-uom'


class ProductNetContentUOMViewTestCase(ListAPIViewTestCaseMixin, TestCase):
    factory = NetContentUOMFactory
    url_patern = 'net-content-uom'
