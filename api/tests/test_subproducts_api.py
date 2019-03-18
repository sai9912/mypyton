import json

from django.contrib.auth.models import User
from mixer.backend.django import mixer
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from unittest import skip

from BCM.models import Country
from company_organisations.models import CompanyOrganisation
from member_organisations.models import MemberOrganisation
from prefixes.models import Prefix
from products.models.product import Product
from services import prefix_service


class SubproductGenericAPITestCase:
    """
    Abstract Class to test Product API
    This class should NOT inherent from any TestCase class
    """
    reverse_url_name = NotImplementedError
    reverse_url_kwarg = None

    @classmethod
    def setUpTestData(cls):
        cls.country = Country(slug='BE', name='Belgium')
        cls.country.save()
        cls.member_organisation = MemberOrganisation(name='GS1', slug='gs1', is_active=1, country=cls.country)
        cls.member_organisation.save()
        cls.company_organisation = CompanyOrganisation.objects.create(**{
            'uuid': '08919800',
            'company': 'GS1 Ireland',
            'name': 'GS1 Ireland',
            'member_organisation': cls.member_organisation,
            'country': cls.country,
        })
        cls.prefix = mixer.blend(Prefix, prefix='12345678900')
        cls.prefix.make_starting_from()
        cls.user = User.objects.create_user(username='test', password='password')
        cls.company_organisation.add_user(cls.user)
        cls.token = cls.get_token_from_data(**{'username': 'test', 'password': 'password'})
        cls.reverse_url = reverse(
            cls.reverse_url_name, kwargs=cls.reverse_url_kwarg
        )

    @classmethod
    def get_token_from_data(cls, **kwargs):
        client = APIClient()
        response = client.post(reverse('api:login'), data=kwargs)
        return response.data['token']

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def create_sample_product(self, **kwargs):
        """
        Create Product with generic data or given data
        :param data: dict
        :return: products.models.Product
        """
        generic_data = {
            'gtin': '20891980000005',
            'company_organisation': self.company_organisation,
            'gs1_company_prefix': self.prefix.prefix,
            'category': 'Category',
            'label_description_i18n': json.dumps({'en': 'Product Label'}),
            'description_i18n': json.dumps({'en': 'Product Description'}),
            'brand_i18n': json.dumps({'en': 'Brand'}),
            'sub_brand': 'Sub Brnad',
            'functional_name_i18n': json.dumps({'en': 'Product Functional name'}),
            'variant': 'Variant',
            'is_bunit': False,
            'is_cunit': True,
            'is_dunit': False,
            'is_vunit': True,
            'is_iunit': False,
            'is_ounit': True,
        }
        generic_data.update(kwargs)
        self.prefix.increment_starting_from()
        prefix_service.save(self.prefix)
        product = Product.objects.create(**generic_data)
        return product

    def create_sample_subproduct(self, **kwargs):
        """
        Create Subproduct with generic data or given data
        :param data: dict
        :return: products.models.Product
        """
        generic_data = {
            'gtin': '00891980000001',
            'company_organisation': self.company_organisation,
            'gs1_company_prefix': self.prefix.prefix,
            'category': 'Category',
            'label_description_i18n': json.dumps({'en': 'Subproduct Label'}),
            'description_i18n': json.dumps({'en': 'Subproduct Description'}),
            'brand_i18n': json.dumps({'en': 'Brand'}),
            'sub_brand': 'Sub Brand',
            'functional_name_i18n': json.dumps({'en': 'Subproduct Functional name'}),
            'variant': 'Variant 1',
            'is_bunit': False,
            'is_cunit': True,
            'is_dunit': False,
            'is_vunit': True,
            'is_iunit': False,
            'is_ounit': True,
        }
        generic_data.update(kwargs)
        self.prefix.increment_starting_from()
        prefix_service.save(self.prefix)
        product = Product.objects.create(**generic_data)
        return product

    def create_subproduct(self):
        url = reverse('api:product-subproducts-list', kwargs={'gtin': '20891980000005'})

        response = self.client.post(url, {'subproduct': '00891980000001',
                                          'quantity': 5})


class ProductListAPITestCase(SubproductGenericAPITestCase, APITestCase):
    reverse_url_name = 'api:product-subproducts-details'
    reverse_url_kwarg = {'product': '20891980000005', 'sub_product': '00891980000001'}
    product_gtin = '20891980000005'
    sub_product_gtin = '00891980000001'

    def setUp(self):
        self.create_sample_product()
        self.create_sample_subproduct()

    def test_subproduct_details(self):
        self.create_subproduct()
        response = self.client.get(self.reverse_url)
        assert response.status_code == 200
        assert response.data['gtin']['value'] == '00891980000001'

    def test_subproduct_add(self):
        response = self.client.post(self.reverse_url, {'quantity':10})
        assert response.status_code == 200
        assert response.data['product'] == self.product_gtin
        assert response.data['sub_product'] == self.sub_product_gtin
        assert response.data['quantity'] == 10

    def test_subproduct_add_same(self):
        response = self.client.post(self.reverse_url, {'quantity': 10})
        assert response.status_code == 200
        assert response.data['product'] == self.product_gtin
        assert response.data['sub_product'] == self.sub_product_gtin
        assert response.data['quantity'] == 10
        response = self.client.post(self.reverse_url, {'quantity': 20})
        assert response.status_code == 400
        assert response.data['message'] == 'Subproduct exist'
