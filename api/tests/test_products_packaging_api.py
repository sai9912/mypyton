from unittest import skip

from django.contrib.auth.models import User
from mixer.backend.django import mixer
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from BCM.models import Country
from company_organisations.models import CompanyOrganisation
from member_organisations.models import MemberOrganisation, ProductPackaging


class ProductPackagingGenericAPITestCase:
    """
    Abstract Class to test Product API
    This class should NOT inherent from any TestCase class
    """
    reverse_url_name = NotImplementedError
    reverse_url_kwarg = None

    @classmethod
    def setUpTestData(cls):
        country = Country(slug='BE', name='Belgium')
        country.save()
        cls.member_organisation = MemberOrganisation(name='GS1', slug='gs1', is_active=1, country=country)
        cls.member_organisation.save()
        cls.company_organisation = CompanyOrganisation.objects.create(**{
            'uuid': '53900011',
            'company': 'GS1 Ireland',
            'name': 'GS1 Ireland',
            'member_organisation': cls.member_organisation,
            'country': country,
        })
        cls.user = User.objects.create_user(username='test', password='password')
        cls.company_organisation.add_user(cls.user)
        cls.token = cls.get_token_from_data({'username': 'test', 'password': 'password'})
        cls.reverse_url = reverse(
            cls.reverse_url_name, kwargs=cls.reverse_url_kwarg
        )

    @classmethod
    def get_token_from_data(cls, data=None):
        client = APIClient()
        response = client.post(reverse('api:login'), data=data)
        return response.data['token']

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    @classmethod
    def create_sample_product_packaging(cls, **kwargs):
        """
        Create ProductPackaging with generic data or given data
        :param data: dict
        :return: member_organisation.models.ProductPackaging
        """
        return mixer.blend(ProductPackaging, **kwargs)

    def response_test_data(self, response_data, data_dict):
        """
        Compare all product packaging fields in the response with given data.
        :param response_data: dict (From response)
        :param data_dict: dict (Expected data)
        :return: None
        """
        self.assertEqual(response_data["name"], data_dict["name"])
        self.assertEqual(response_data["order"], data_dict["order"])
        self.assertEqual(response_data["package_level"], data_dict["package_level"])
        self.assertEqual(response_data["member_organisation"], data_dict["member_organisation"])
        self.assertEqual(response_data["package_type"], data_dict["package_type"])
        self.assertEqual(response_data["image_url"], data_dict["image_url"])
        self.assertEqual(response_data["ui_label_i18n"], data_dict["ui_label_i18n"])
        self.assertEqual(response_data["ui_description_i18n"], data_dict["ui_description_i18n"])

    def from_models_object_to_dict(self, obj):
        """
        Take data from given object with the fields defined bellow
        :param obj: Object
        :return: dict
        """
        return {
            "name": obj.name,
            "order": obj.order,
            "package_level": obj.package_level.pk,
            "member_organisation": obj.member_organisation.pk,
            "package_type": obj.package_type.pk,
            "image_url": obj.image_url,
            "ui_label": obj.ui_label,
            "ui_description": obj.ui_description,
        }

    @skip('"please remove authentication" from github #122')
    def test_try_access_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'myfaketoken')
        for method in self.method:
            client_method = getattr(self.client, method)
            response = client_method(self.reverse_url)

            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.data, {"detail": "Invalid token."})

    @skip('"please remove authentication" from github #122')
    def test_try_access_without_token(self):
        self.client.credentials()
        for method in self.method:
            client_method = getattr(self.client, method)
            response = client_method(self.reverse_url)

            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.data, {"detail": "Authentication credentials were not provided."})


class ProductPackagingListAPITestCase(ProductPackagingGenericAPITestCase, APITestCase):
    reverse_url_name = 'api:packaging-list'
    method = ['get']

    def setUp(self):
        super(ProductPackagingListAPITestCase, self).setUp()
        self.product_packaging = self.create_sample_product_packaging(
            member_organisation=self.member_organisation
        )

    def test_empty_product_packaging(self):
        self.product_packaging.delete()
        response = self.client.get(self.reverse_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    # def test_list_product_packaging(self):
    #     response = self.client.get(self.reverse_url)
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.response_test_data(response.data[0], {
    #         "name": self.product_packaging.name,
    #         "order": self.product_packaging.order,
    #         "package_level": self.product_packaging.package_level.pk,
    #         "member_organisation": self.product_packaging.member_organisation.slug,
    #         "package_type": self.product_packaging.package_type.pk,
    #         "image_url": self.product_packaging.image_url,
    #         "ui_label_i18n": self.product_packaging.ui_label_i18n,
    #         "ui_description_i18n": self.product_packaging.ui_description_i18n,
    #     })
