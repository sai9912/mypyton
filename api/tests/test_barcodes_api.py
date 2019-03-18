import json

from django.contrib.auth.models import User
from mixer.backend.django import mixer
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient
from unittest import skip

from BCM.models import Country
from company_organisations.models import CompanyOrganisation
from member_organisations.models import MemberOrganisation
from prefixes.models import Prefix
from products.models.product import Product
from services import prefix_service


class BarcodeGenericAPITestCase:
    """
    Abstract Class to test Barcode API
    This class should NOT inherent from any TestCase class
    """

    reverse_url_name = NotImplementedError
    reverse_url_kwarg = None

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    @classmethod
    def setUpTestData(cls):
        cls.country = Country(slug='BE', name='Belgium')
        cls.country.save()
        cls.member_organisation = MemberOrganisation(
            name='GS1', slug='gs1', is_active=1, country=cls.country
        )
        cls.member_organisation.save()
        cls.company_organisation = CompanyOrganisation.objects.create(**{
            'uuid': '53900011',
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

    @classmethod
    def get_token_from_data(cls, **kwargs):
        client = APIClient()
        response = client.post(reverse('api:login'), data=kwargs)
        return response.data['token']

    @classmethod
    def create_sample_product(cls, **kwargs):
        """
        Create Product with generic data or given data
        :param data: dict
        :return: products.models.Product
        """
        generic_data = {
            "gtin": '0' + cls.prefix.starting_from,
            "company_organisation": cls.company_organisation,
            "gs1_company_prefix": cls.prefix.prefix,
            "category": "Category 1",
            "label_description_i18n": json.dumps({"en": "Label 1"}),
            "description_i18n": json.dumps({"en": "Description 1"}),
            "brand_i18n": json.dumps({"en": "Brand 1"}),
            "sub_brand": "Sub Brand 1",
            "functional_name_i18n": json.dumps({"en": "Functional name 1"}),
            "variant": "Variant 1",
            "is_bunit": False,
            "is_cunit": True,
            "is_dunit": False,
            "is_vunit": True,
            "is_iunit": False,
            "is_ounit": True,
            "package_level_id": 70,
        }
        generic_data.update(kwargs)
        cls.prefix.increment_starting_from()
        prefix_service.save(cls.prefix)
        product = Product.objects.create(**generic_data)
        return product


class BarcodePreviewAPITestCase(BarcodeGenericAPITestCase, APITestCase):
    fixtures = (
        '../../fixtures/products.package_level.json',
    )

    reverse_url_name = 'api:barcodes'
    reverse_url_kwarg = None
    method = ['get']

    def setUp(self):
        super(BarcodePreviewAPITestCase, self).setUp()
        self.product = self.create_sample_product()

    def test_barcode_preview_with_watermark(self):
        api_url = reverse(
            self.reverse_url_name,
            kwargs={
                'gtin': self.product.gtin,
                'type': 'preview',
            }
        )

        response = self.client.get(api_url)
        self.assertDictEqual(
            response.data,
            {
                'gtin': self.product.gtin,
                'barcode_type': 'EAN13',
                'barcode': f'/static/bcgen/1/EAN13/{self.product.gtin}_preview.jpg'
            },
            'Returned data have not exected values'
        )

    def test_barcode_preview(self):
        api_url = reverse(
            self.reverse_url_name,
            kwargs={
                'gtin': self.product.gtin,
                'type': 'generate',
            }
        )

        response = self.client.get(
            api_url,
            data={
                'size': '0.8',
                'bwr': '0.0000',
                'rqz': 'true',
                'marks': 'false',
                'debug': 'false',
            }
        )

        response_data = response.data
        barcode_url = response_data.pop('barcode')
        self.assertRegex(
            barcode_url,
            f'/static/bcgen/1/EAN13/{self.product.gtin}_\w+.jpg',
            'Wrong barcode url generated'
        )

        self.assertDictEqual(
            response_data,
            {
                'gtin': self.product.gtin,
                'barcode_type': 'EAN13',
            },
            'Returned data have not exected values'
        )

    @skip('some troubles with .ps generating on circle-ci')
    def test_barcode_download(self):
        api_url = reverse(
            self.reverse_url_name,
            kwargs={
                'gtin': self.product.gtin,
                'type': 'generate',
            }
        )

        response = self.client.get(
            api_url,
            data={
                'download_type': 'raster',
                'size': '0.8',
                'bwr': '0.0000',
                'resolution': '300 dpi',
                'file_type': 'png',
                'ps_type': 'win',
                'label_type': 'L7161',
                'rqz': 'true',
                'marks': 'false',
                'debug': 'false',
            }
        )

        response_data = response.data
        barcode_url = response_data.pop('barcode')
        self.assertRegex(
            barcode_url.replace('EAN13/', 'EAN13/0'),
            f'/static/bcgen/1/EAN13/{self.product.gtin}.png',
            'Wrong barcode url generated'
        )

        self.assertDictEqual(
            response_data,
            {
                'gtin': self.product.gtin,
                'barcode_type': 'EAN13',
            },
            'Returned data have not exected values'
        )
