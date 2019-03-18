import json

from django.contrib.auth.models import User, Group
from mixer.backend.django import mixer
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient
from unittest import skip
from test_plus import TestCase as PlusTestCase
from BCM.models import Country
from api.serializers.product_serializers import \
    (
    ProductCountryOfOriginSerializer, ProductLanguageSerializer,
    ProductTargetMarketSerializer,
    ProductDimensionUOMSerializer,
    ProductNetContentUOMSerializer,
    ProductWeightUOMSerializer,
)
from barcodes.utilities import isValid
from company_organisations.factories import CompanyOrganisationFactory
from company_organisations.models import CompanyOrganisation
from member_organisations.factories import (
    ProductTemplateFactory,
    ProductAttributeFactory,
    MemberOrganisationFactory,
    MemberOrganisationUserFactory,
)
from member_organisations.models import MemberOrganisation
from prefixes.factories import PrefixFactory
from prefixes.models import Prefix
from products.factories import (
    ProductFactory, ProductImageFactory,
    CountryOfOriginFactory,
    LanguageFactory,
    TargetMarketFactory,
    DimensionUOMFactory,
    NetContentUOMFactory,
    WeightUOMFactory,
)
from products.models.product import Product, ProductImage
from products.models.country_of_origin import CountryOfOrigin
from products.models.target_market import TargetMarket
from products.models.language import Language
from services import prefix_service
from users.factories import UserFactory, AuthTokenFactory


class ProductGenericAPITestCase:
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
            "description_i18n": json.dumps({"en": "Descript 1"}),
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
        }
        generic_data.update(kwargs)
        cls.prefix.increment_starting_from()
        prefix_service.save(cls.prefix)
        product = Product.objects.create(**generic_data)
        return product

    def response_test_data(self, response_data, data_dict):
        """
        Compare all product fields in the response with given data.
        :param response_data: dict (From response)
        :param data_dict: dict (Expected data)
        :return: None
        """
        self.assertEqual(response_data["gtin"]["value"], data_dict["gtin"])
        self.assertEqual(response_data["category"]["value"], data_dict["category"])
        self.assertEqual(response_data["label_description_i18n"]["value"]["en"], data_dict["label_description"])
        self.assertEqual(response_data["description_i18n"]["value"]["en"], data_dict["description"])
        self.assertEqual(response_data["brand_i18n"]["value"]["en"], data_dict["brand"])
        self.assertEqual(response_data["sub_brand"]["value"], data_dict["sub_brand"])
        self.assertEqual(response_data["functional_name_i18n"]["value"]["en"], data_dict["functional_name"])
        self.assertEqual(response_data["variant"]["value"], data_dict["variant"])
        self.assertEqual(response_data["is_bunit"]["value"], data_dict["is_bunit"])
        self.assertEqual(response_data["is_cunit"]["value"], data_dict["is_cunit"])
        self.assertEqual(response_data["is_dunit"]["value"], data_dict["is_dunit"])
        self.assertEqual(response_data["is_vunit"]["value"], data_dict["is_vunit"])
        self.assertEqual(response_data["is_iunit"]["value"], data_dict["is_iunit"])
        self.assertEqual(response_data["is_ounit"]["value"], data_dict["is_ounit"])

    def from_models_object_to_dict(self, obj):
        """
        Take data from given object with the fields defined bellow
        :param obj: Object
        :return: dict
        """
        return {
            "gtin": obj.gtin,
            "category": obj.category,
            "label_description": obj.label_description,
            "description": obj.description,
            "brand": obj.brand,
            "sub_brand": obj.sub_brand,
            "functional_name": obj.functional_name,
            "variant": obj.variant,
            "is_bunit": obj.is_bunit,
            "is_cunit": obj.is_cunit,
            "is_dunit": obj.is_dunit,
            "is_vunit": obj.is_vunit,
            "is_iunit": obj.is_iunit,
            "is_ounit": obj.is_ounit,
        }

    def test_try_access_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'myfaketoken')
        for method in self.method:
            client_method = getattr(self.client, method)
            response = client_method(self.reverse_url)

            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.data, {"detail": "Invalid token."})

    def test_try_access_without_token(self):
        self.client.credentials()
        for method in self.method:
            client_method = getattr(self.client, method)
            response = client_method(self.reverse_url)

            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.data, {"detail": "Authentication credentials were not provided."})


class ProductListAPITestCase(ProductGenericAPITestCase, APITestCase):
    reverse_url_name = 'api:product-list'
    method = ['get']

    def setUp(self):
        super(ProductListAPITestCase, self).setUp()
        self.product = self.create_sample_product()

    def test_empty_product_from_correct_company_uuid(self):
        self.product.delete()
        response = self.client.get(self.reverse_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['products'], [])

    def test_list_product(self):
        response = self.client.get(self.reverse_url)

        self.assertEqual(response.status_code, 200)
        self.response_test_data(response.data['products'][0], {
            "gtin": "01234567890012",
            "category": "Category 1",
            "label_description": "Label 1",
            "description": "Descript 1",
            "brand": "Brand 1",
            "sub_brand": "Sub Brand 1",
            "functional_name": "Functional name 1",
            "variant": "Variant 1",
            "is_bunit": False,
            "is_cunit": True,
            "is_dunit": False,
            "is_vunit": True,
            "is_iunit": False,
            "is_ounit": True,
        })


class ProductCreateAPITestCase(ProductGenericAPITestCase, APITestCase):
    reverse_url_name = 'api:product-list'
    method = ['post']

    def test_create_product_correctly(self):
        self.assertFalse(Product.objects.filter(gs1_company_prefix=self.prefix.prefix).exists())
        response = self.client.post(self.reverse_url, data={
            "gs1_company_prefix": self.prefix.prefix,
            "category": "Category 1",
            "label_description_i18n": json.dumps({"en": "Label 1"}),
            "description_i18n": json.dumps({"en": "Descript 1"}),
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
        }, format='json')

        product = Product.objects.get(gtin="01234567890005")
        expected_data = {
            "gtin": "01234567890005",
            "category": "Category 1",
            "label_description": "Label 1",
            "description": "Descript 1",
            "brand": "Brand 1",
            "sub_brand": "Sub Brand 1",
            "functional_name": "Functional name 1",
            "variant": "Variant 1",
            "is_bunit": False,
            "is_cunit": True,
            "is_dunit": False,
            "is_vunit": True,
            "is_iunit": False,
            "is_ounit": True,
        }

        self.assertEqual(response.status_code, 201)
        self.assertTrue(isValid(response.data['gtin']['value']))  # Check if GTIN is valid (mod10)
        self.assertTrue(len(response.data['gtin']['value']) == 14)  # Check if GTIN starts with prefix
        self.assertTrue(response.data['gtin']['value'][1:].startswith(self.prefix.prefix))  # Check if GTIN starts with prefix
        self.response_test_data(response.data, expected_data)
        self.response_test_data(response.data, self.from_models_object_to_dict(product))

    # @skip('Supress message')
    def test_create_product_without_allocation_capacity(self):
        for i in range(10):
            self.create_sample_product()

        response = self.client.post(self.reverse_url, data={
            "gs1_company_prefix": self.prefix.prefix,
            "category": "Category 1",
            "label_description": "Label 1",
            "description": "Descript 1",
            "brand": "Brand 1",
            "sub_brand": "Sub Brand 1",
            "functional_name": "Functional name 1",
            "variant": "Variant 1",
            "is_bunit": False,
            "is_cunit": True,
            "is_dunit": False,
            "is_vunit": True,
            "is_iunit": False,
            "is_ounit": True,
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            "non_field_errors": [
                "not allowed to create products for this prefix."
            ]
        })

    def test_create_product_without_gtin(self):
        post_data = {
            "category": "Category 1",
            "label_description": "Label 1",
            "description": "Descript 1",
            "brand": "Brand 1",
            "sub_brand": "Sub Brand 1",
            "functional_name": "Functional name 1",
            "variant": "Variant 1",
            "is_bunit": False,
            "is_cunit": True,
            "is_dunit": False,
            "is_vunit": True,
            "is_iunit": False,
            "is_ounit": True,
        }

        response = self.client.post(self.reverse_url, data=post_data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'gs1_company_prefix': ['This field is required.']
        })

    def test_create_product_does_not_exist(self):
        post_data = {
            "gs1_company_prefix": "",
            "category": "Category 1",
            "label_description": "Label 1",
            "description": "Descript 1",
            "brand": "Brand 1",
            "sub_brand": "Sub Brand 1",
            "functional_name": "Functional name 1",
            "variant": "Variant 1",
            "is_bunit": False,
            "is_cunit": True,
            "is_dunit": False,
            "is_vunit": True,
            "is_iunit": False,
            "is_ounit": True,
        }

        response = self.client.post(self.reverse_url, data=post_data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'gs1_company_prefix': ['given prefix does not exist.']
        })

    def test_try_to_set_company_organisation_been_company_organisation(self):
        post_data = {
            "company_organisation": self.company_organisation.pk,
            "gs1_company_prefix": self.prefix.prefix,
            "category": "Category 1",
            "label_description": "Label 1",
            "description": "Descript 1",
            "brand": "Brand 1",
            "sub_brand": "Sub Brand 1",
            "functional_name": "Functional name 1",
            "variant": "Variant 1",
            "is_bunit": False,
            "is_cunit": True,
            "is_dunit": False,
            "is_vunit": True,
            "is_iunit": False,
            "is_ounit": True,
        }

        response = self.client.post(self.reverse_url, data=post_data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'company_organisation': ['this field is read-only for Company organisation.']
        })

    def test_try_to_set_owner_been_company_organisation(self):
        post_data = {
            "gs1_company_prefix": self.prefix.prefix,
            "owner": self.user.pk,
            "category": "Category 1",
            "label_description": "Label 1",
            "description": "Descript 1",
            "brand": "Brand 1",
            "sub_brand": "Sub Brand 1",
            "functional_name": "Functional name 1",
            "variant": "Variant 1",
            "is_bunit": False,
            "is_cunit": True,
            "is_dunit": False,
            "is_vunit": True,
            "is_iunit": False,
            "is_ounit": True,
        }

        response = self.client.post(self.reverse_url, data=post_data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'owner': ['this field is read-only for Company organisation.']
        })


class ProductRetrieveAPITestCase(ProductGenericAPITestCase, APITestCase):
    reverse_url_name = 'api:product-detail'
    reverse_url_kwarg = {'gtin': '01234567890005'}
    method = ['get']

    @classmethod
    def setUpTestData(cls):
        super(ProductRetrieveAPITestCase, cls).setUpTestData()
        cls.product = cls.create_sample_product()

    def test_retrieve_product_correctly(self):
        response = self.client.get(self.reverse_url)

        self.assertEqual(response.status_code, 200)
        self.response_test_data(response.data, {
            "gtin": "01234567890005",
            "category": "Category 1",
            "label_description": "Label 1",
            "description": "Descript 1",
            "brand": "Brand 1",
            "sub_brand": "Sub Brand 1",
            "functional_name": "Functional name 1",
            "variant": "Variant 1",
            "is_bunit": False,
            "is_cunit": True,
            "is_dunit": False,
            "is_vunit": True,
            "is_iunit": False,
            "is_ounit": True,
        })

    def test_404_when_gtin_does_not_exist(self):
        response = self.client.get(reverse(
            'api:product-detail', kwargs={'gtin': '0000000'}
        ))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {
            "detail": "Not found."
        })


class ProductsUpdateAPITestCase(ProductGenericAPITestCase, APITestCase):
    reverse_url_name = 'api:product-detail'
    reverse_url_kwarg = {'gtin': '01234567890005'}
    method = ['patch', 'put']

    @classmethod
    def setUpTestData(cls):
        super(ProductsUpdateAPITestCase, cls).setUpTestData()
        cls.product = cls.create_sample_product()

    def test_update_partial_product_correctly(self):
        response = self.client.patch(self.reverse_url, data={"is_bunit": True}, format='json')

        expected_data = {
            "gtin": "01234567890005",
            "category": "Category 1",
            "label_description": "Label 1",
            "description": "Descript 1",
            "brand": "Brand 1",
            "sub_brand": "Sub Brand 1",
            "functional_name": "Functional name 1",
            "variant": "Variant 1",
            "is_bunit": True,
            "is_cunit": True,
            "is_dunit": False,
            "is_vunit": True,
            "is_iunit": False,
            "is_ounit": True,
        }

        self.product = Product.objects.get(pk=self.product.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.product.is_bunit, True)
        self.response_test_data(response.data, expected_data)
        self.response_test_data(response.data, self.from_models_object_to_dict(self.product))

    def test_different_users_update_from_same_co(self):
        user = User.objects.create_user(username='test2', password='password')
        self.company_organisation.add_user(user)
        token = self.get_token_from_data(**{'username': 'test2', 'password': 'password'})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        response = self.client.patch(self.reverse_url, data={"is_bunit": True}, format='json')

        expected_data = {
            "gtin": "01234567890005",
            "category": "Category 1",
            "label_description": "Label 1",
            "description": "Descript 1",
            "brand": "Brand 1",
            "sub_brand": "Sub Brand 1",
            "functional_name": "Functional name 1",
            "variant": "Variant 1",
            "is_bunit": True,
            "is_cunit": True,
            "is_dunit": False,
            "is_vunit": True,
            "is_iunit": False,
            "is_ounit": True,
        }

        self.product = Product.objects.get(pk=self.product.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.product.is_bunit, True)
        self.response_test_data(response.data, expected_data)
        self.response_test_data(response.data, self.from_models_object_to_dict(self.product))

    def test_different_users_update_from_different_co(self):
        company_organisation = CompanyOrganisation.objects.create(**{
            'uuid': '53900012',
            'company': 'GS2 New',
            'name': 'GS2 New',
            'member_organisation': self.member_organisation,
            'country': self.country,
        })
        user = User.objects.create_user(username='test2', password='password')
        company_organisation.add_user(user)
        token = self.get_token_from_data(**{'username': 'test2', 'password': 'password'})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        response = self.client.patch(self.reverse_url, data={"is_bunit": True}, format='json')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {'detail': 'Not found.'})

    def test_gs1_company_prefix_is_not_editable(self):
        response = self.client.patch(self.reverse_url, data={"gs1_company_prefix": "3223232"}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'gs1_company_prefix': ['this field is not editable.']
        })

    def test_404_when_gtin_does_not_exist_partial(self):
        response_partial = self.client.patch(reverse(
            'api:product-detail', kwargs={'gtin': '0000000'}
        ))

        self.assertEqual(response_partial.status_code, 404)
        self.assertEqual(response_partial.data, {
            "detail": "Not found."
        })

    def test_404_when_gtin_does_not_exist_fully(self):
        response_fully = self.client.put(reverse(
            'api:product-detail', kwargs={'gtin': '0000000'}
        ))

        self.assertEqual(response_fully.status_code, 404)
        self.assertEqual(response_fully.data, {
            "detail": "Not found."
        })


class ProductsUpdateAPIPlusTestCase(PlusTestCase):
    def setUp(self):
        self.user = UserFactory(is_staff=True)
        self.mo_group = Group.objects.create(name='MO Admins')
        self.user.groups.add(self.mo_group)
        mo_user = MemberOrganisationUserFactory(user=self.user)
        self.user.profile.member_organisation = mo_user.organization
        self.user.profile.save()
        self.token = AuthTokenFactory(user=self.user)
        self.headers = dict(
            HTTP_AUTHORIZATION=f'Token {self.token}',

        )
        self.client = APIClient()
        self.client.credentials(**self.headers)
        gtin = '01234567890005'
        self.language = LanguageFactory(slug='en')

        data = {
            'gtin': gtin,
            'member_organisation': self.user.profile.member_organisation,
            'label_description_i18n': json.dumps({'en': 'label_description'}),
            'description_i18n': json.dumps({'en': 'description'}),
            'brand_i18n': json.dumps({'en': 'brand'}),
            'functional_name_i18n': json.dumps({'en': 'functional_name'}),
            'gs1_cloud_state': 'ACTIVE',
            'language': self.language
        }
        self.product = ProductFactory(**data)

        reverse_url_name = 'api:product-detail'
        self.url = self.reverse(reverse_url_name, gtin=gtin)

    def test_apply_product_template_without_any_action(self):
        product_template_name = 'product_template_name'

        field_name = 'is_dunit'
        path = f'random text.{field_name}'

        product_template = ProductTemplateFactory(name=product_template_name)
        product_attribute = ProductAttributeFactory(
            path=path,
            ui_mandatory=False
        )
        product_template.attributes.add(product_attribute)

        self.do_request_and_check_response(
            product_template,
            field_name,
            product_attribute,
            data={'is_dunit': False}
        )

    def test_apply_product_template_with_raise_error(self):
        product_template_name = 'product_template_name'

        field_name = 'is_dunit'
        path = f'random text.{field_name}'

        product_template = ProductTemplateFactory(name=product_template_name)

        product_attribute = ProductAttributeFactory(
            path=path,
            ui_mandatory=False,
            ui_form_validation_callable='rest_framework.validators.'
                                        'UniqueForDateValidator'
        )

        product_template.attributes.add(product_attribute)

        kwargs = dict(
            data={},
            QUERY_STRING=f'template_name={product_template.name}'
        )
        response = self.client.patch(
            self.url,
            **kwargs
        )
        assert response.status_code == 400
        assert response.data == ['Callable error'], response.data

        product_attribute.ui_form_validation_callable = (
            'rest_framework.validators'
        )
        product_attribute.save()
        kwargs = dict(
            data={},
            QUERY_STRING=f'template_name={product_template.name}'
        )
        response = self.client.patch(
            self.url,
            **kwargs
        )
        assert response.status_code == 400
        assert response.data == ['Callable error'], response.data

    def test_apply_product_template(self):
        product_template_name = 'product_template_name'

        field_name = 'random_name'
        path = f'random text.{field_name}'

        product_template = ProductTemplateFactory(name=product_template_name)
        product_attribute = ProductAttributeFactory(
            path=path,
            ui_mandatory=False,
            ui_read_only=True,
        )
        product_template.attributes.add(product_attribute)
        data = {'is_dunit': False}
        self.do_request_and_check_response(
            product_template,
            field_name,
            product_attribute,
            data
        )
        field_name = 'website_url'
        path = f'random text.{field_name}'
        product_attribute.path = path
        product_attribute.ui_mandatory = True
        product_attribute.ui_read_only = False
        product_attribute.ui_default_callable = ('api.validators.'
                                                 'DescriptionValidator')
        product_attribute.ui_field_validation_callable = (
            'api.validators.DescriptionValidator'
        )
        product_attribute.ui_form_validation_callable = ('api.validators.'
                                                         'DescriptionValidator')
        product_attribute.ui_label = False
        product_attribute.save()
        company_organisation = CompanyOrganisationFactory()

        data = {
            'is_dunit': False,
            'gtin': '01234567890003',
            'company_organisation': company_organisation.id,
        }

        self.do_request_and_check_response(
            product_template,
            field_name,
            product_attribute,
            data
        )

    def test_image(self):
        image = self.get_image_file()
        product_image = ProductImageFactory(
            product=self.product,
            language=self.product.language
        )

        data = {'image_upload': image}

        self.do_request_and_check_response(
            None,
            None,
            None,
            data
        )
        product = Product.objects.get(id=self.product.id)
        # check deleting old product_image
        assert not ProductImage.objects.filter(id=product_image.id).exists()
        product_image = ProductImage.objects.first()
        url = getattr(product, f'image_{product.language.slug}')
        assert url == product_image.image.url, url

    def test_image_image_i18n(self):
        product_template_name = 'product_template_name'

        field_name = 'image_i18n'
        path = f'random text.{field_name}'
        product_template = ProductTemplateFactory(name=product_template_name)
        product_attribute = ProductAttributeFactory(
            path=path,
            ui_mandatory=False,
            ui_read_only=True,
        )
        product_template.attributes.add(product_attribute)

        image = self.get_image_file()
        ProductImageFactory(
            product=self.product,
            language=self.product.language
        )
        data = {
            'image_i18n': json.dumps({'en': 'image'}),
            'image_upload': image
        }
        self.do_request_and_check_response(
            product_template,
            field_name,
            product_attribute,
            data
        )

    def test_validate(self):
        product_template_name = 'product_template_name'

        field_name = 'is_dunit'
        path = f'random text.{field_name}'

        product_template = ProductTemplateFactory(name=product_template_name)
        product_attribute = ProductAttributeFactory(
            path=path,
            ui_mandatory=False,
            ui_read_only=True,
        )
        product_template.attributes.add(product_attribute)
        data = {'is_dunit': False}
        self.do_request_and_check_response(
            product_template,
            field_name,
            product_attribute,
            data
        )

    @staticmethod
    def get_image_file():

        from django.core.files.uploadedfile import SimpleUploadedFile

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            'small.gif',
            small_gif,
            content_type='image/gif'
        )
        return uploaded

    def do_request_and_check_response(self, product_template,
                                      field_name, product_attribute, data):
        kwargs = dict(
            data=data,
        )
        if product_template:
            kwargs.update(
                dict(QUERY_STRING=f'template_name={product_template.name}')
            )
        response = self.client.patch(
            self.url,
            **kwargs
        )
        if response.data.get(field_name):
            field = response.data[field_name]
            assert field['ui_mandatory'] == product_attribute.ui_mandatory
            assert field['ui_enabled'] == product_attribute.ui_enabled
            assert field['ui_label_i18n'] == product_attribute.ui_label_i18n
            assert field['definition'] == product_attribute.definition

        self.check_response_data(response.data)
        return response.data

    def check_response_data(self, response_data):
        data = self.get_data_from_db()
        for field in self.fields_for_check:
            response_field = response_data.get(field)
            if response_field:
                response_field = response_field['value']
            else:
                response_field = response_data[f'{field}_i18n']['value']
                response_field = response_field.get('en') or '???'

            assert response_field == data[field], (
                field, response_field, data[field]
            )

    def get_data_from_db(self):
        product = Product.objects.get(id=self.product.id)
        data = {
            field: getattr(product, field)
            for field in self.fields_for_check
        }
        return data

    @property
    def fields_for_check(self):
        return [
            "gtin",
            "category",
            "label_description",
            "description",
            "brand",
            "sub_brand",
            "functional_name",
            "variant",
            "is_bunit",
            "is_cunit",
            "is_dunit",
            "is_vunit",
            "is_iunit",
            "is_ounit",
        ]


class RepresentativeSerializerTestCase(PlusTestCase):

    @staticmethod
    def test_to_representation():
        data = (
            (ProductLanguageSerializer, LanguageFactory, 'name'),
            (ProductCountryOfOriginSerializer, CountryOfOriginFactory, 'name'),
            (ProductTargetMarketSerializer, TargetMarketFactory, 'market'),
            (ProductDimensionUOMSerializer, DimensionUOMFactory, 'uom'),
            (ProductNetContentUOMSerializer, NetContentUOMFactory, 'uom'),
            (ProductWeightUOMSerializer, WeightUOMFactory, 'uom'),
        )

        for serializer_class, factory, field in data:
            instance = factory()
            validated_data = serializer_class(instance).data
            assert validated_data[field] == getattr(instance, field)


class ProductsDeleteAPITestCase(ProductGenericAPITestCase, APITestCase):
    reverse_url_name = 'api:product-detail'
    reverse_url_kwarg = {'gtin': '01234567890005'}
    method = ['delete']

    @classmethod
    def setUpTestData(cls):
        super(ProductsDeleteAPITestCase, cls).setUpTestData()
        cls.product = cls.create_sample_product()

    def test_delete_product_correctly(self):
        response = self.client.delete(self.reverse_url)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, None)
        self.assertFalse(Product.objects.filter(pk=self.prefix.pk).exists())

    def test_404_when_gtin_does_not_exist(self):
        response = self.client.delete(reverse(
            'api:product-detail', kwargs={'gtin': '0000000'}
        ))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {
            "detail": "Not found."
        })


class SubproductsAPITestCase(ProductGenericAPITestCase, APITestCase):
    reverse_url_name = 'api:product-create-subproducts'
    method = []

    @classmethod
    def setUpTestData(cls):
        super(SubproductsAPITestCase, cls).setUpTestData()
        cls.product = cls.create_sample_product()

    def test_subproducts(self):
        products = Product.objects.all()
        session = self.client.session
        session['new_product'] = {}
        session['new_product']['sub_products'] = ['01234567890005']
        session.save()
        response = self.client.get(self.reverse_url)
        assert response.status_code == 200
        # assert response.content_type == 'application/json'
        json = response.json()
        assert len(json) == 1
        assert json[0]['gtin']['value'] == '01234567890005'


class ProductDefaultAPITestCase(ProductGenericAPITestCase, APITestCase):
    reverse_url_name = 'api:defaults-list'
    method = []

    @classmethod
    def setUpTestData(cls):
        super(ProductDefaultAPITestCase, cls).setUpTestData()
        cls.product = cls.create_sample_product()
        CountryOfOrigin.objects.create(code='21', name='BELGIUM')
        CountryOfOrigin.objects.create(code='103', name='IRELAND')
        TargetMarket.objects.create(code='21', market='BELGIUM')
        TargetMarket.objects.create(code='103', market='IRELAND')
        Language.objects.create(slug='en', name='English')
        country_ie = Country(slug='IE', name='Ireland')
        country_ie.save()
        cls.company_organisation.country = country_ie
        cls.company_organisation.save()

    def test_company_organisation_country(self):
        self.user.profile.company_organisation = self.company_organisation
        self.user.profile.member_organisation = self.member_organisation
        self.user.profile.save()
        response = self.client.get(self.reverse_url)
        assert response.status_code == 200
        data = response.json()
        assert data['country_of_origin'] == 2
        assert data['target_market'] == 2
        assert data['language'] == 1

    def test_member_organisation_country(self):
        self.user.profile.company_organisation = None
        self.user.profile.member_organisation = self.member_organisation
        self.user.profile.save()
        response = self.client.get(self.reverse_url)
        assert response.status_code == 200
        data = response.json()
        assert data['country_of_origin'] == None
        assert data['target_market'] == None
        assert data['language'] == 1


class ProductCloneAPIViewTestCase(APITestCase):

    def setUp(self):
        self.url = '/api/v1/products/clone/'

    def test_method_post_invalid(self):
        data = {
            'subproduct_gtin': '12345678912345',
            'newproduct_gtin': '12345678912345',
            'package_level': 12
        }
        response = self.client.post(self.url, data=data)
        self.assertEquals(
            response.status_code,
            400
        )
        self.assertEquals(
            json.loads(response.content),
            {'message': 'Invalid gtin'}
        )

    def test_method_post_valid(self):
        Product.objects.create(
            gtin='12345678912123'
        )

        data = {
            'subproduct_gtin': '12345678912123',
            'newproduct_gtin': '12345678912345',
            'package_level': 12
        }
        response = self.client.post(self.url, data=data)
        self.assertEquals(
            response.status_code,
            200
        )
        self.assertEquals(
            list(json.loads(response.content).keys()),
            ['product_id']
        )

    def test_method_put(self):
        username = 'test@test.ru'
        user = User.objects.create(
            username=username,
            email='root@root.tuqwe'
        )

        data = {'gtin': '12345678912123',}

        Product.objects.create(**data)
        self.client.force_authenticate(user)
        response = self.client.put(self.url, data=data)

        self.assertEquals(
            response.status_code,
            200
        )
        self.assertEquals(
            list(json.loads(response.content).keys()),
            ['existed', 'templates']
        )

    def test_method_put_without_login(self):
        response = self.client.put(self.url)
        self.assertEquals(
            response.status_code,
            401
        )
