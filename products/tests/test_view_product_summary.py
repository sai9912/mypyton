from unittest import skip

from . import TestCase


class PageViewProductSummary(TestCase):
    url = '/products/2/view_summary/'
    user = None

    def setUp(self):
        self.user = self.setUp_createAccount()
        self.loadProducts()

    def test_page_exist(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'Summary')
        self.assertContains(response, 'GS1 Company Prefix')

    @skip('temporary disabled, new pdf generator is coming')
    def test_pdf_summary(self):
        url='/products/2/print_summary/'
        response = self.client.get(url)
        assert response.status_code == 200
        assert response._headers['content-type'][1] == 'application/pdf'
