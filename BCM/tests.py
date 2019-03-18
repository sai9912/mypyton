import doctest
import json

from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from test_plus import  TestCase as PlusTestCase

from BCM.factories import CountryFactory
from BCM.helpers.utils import resolve_boolean_value
from django.core.management import call_command
from django.test import TestCase

from company_organisations.factories import CompanyOrganisationFactory
from member_organisations.factories import (
    MemberOrganisationUserFactory,
    ProductTemplateFactory,
    MemberOrganisationFactory,
)
from member_organisations.models import ProductTemplate, ProductPackaging, ProductAttribute
from BCM.models import Country, LanguageByCountry, Language
from member_organisations.models import MemberOrganisation
from products.factories import ProductFactory, SubProductFactory
from products.models.package_level import PackageLevel
from products.models.package_type import PackageType
from products.models.product import Product
from unittest import skip

from products.models.sub_product import SubProduct
from users.factories import UserFactory, AuthTokenFactory, ProfileFactory
from .helpers import serialization_helpers


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(serialization_helpers))
    return tests


class TestImportDataManagementCommand(TestCase):
    def setUp(self):
        country = Country(slug='BE', name='Belgium')
        country.save()
        member_organisation = MemberOrganisation(
                name='GS1IE',
                slug='gs1ie',
                is_active=1,
                country=country
        )
        member_organisation.save()

    @skip('is_active is no longer kept on prefix level')
    def test_import_data_command(self):
        self.assertEquals(Product.objects.count(), 0)
        call_command('import_data', zip_file_path='deployment/test_files/sample_data_test.zip')
        self.assertEquals(Product.objects.count(), 2)


class TestLoadPackagingLevelTranslationsCommand(TestCase):
    def setUp(self):
        country = Country(slug='BE', name='Belgium')
        country.save()
        member_organisation = MemberOrganisation(
                name='GS1SE',
                slug='gs1se',
                is_active=1,
                country=country,
                pk=7
        )
        member_organisation.save()
        PackageLevel.objects.create(id=70, unit_descriptor='test')

    def test_load_pack_level_data_command(self):
        self.assertEquals(ProductTemplate.objects.count(), 0)
        call_command('load_pack_level_data', excel_file='deployment/test_files/UI_presets_v1_test_copy.xlsx')
        self.assertEquals(ProductTemplate.objects.count(), 1)
        pt = ProductTemplate.objects.get(pk=1)
        self.assertEquals(pt.name, 'gs1sv-base')
        self.assertEquals(pt.image_url, 'test.com')
        self.assertEquals(pt.ui_label, 'Test label')
        self.assertEquals(pt.ui_label_en, 'Test label')
        self.assertEquals(pt.ui_label_sv, 'Basnivå')

    # def test_load_pack_type_data(self):
    #     self.assertEquals(ProductPackaging.objects.count(), 0)
    #     call_command('load_pack_type_data', excel_file='deployment/test_files/UI_presets_v1_test_copy.xlsx')
    #     # data has 4 row with 2 sv and 2 en
    #     self.assertEquals(ProductPackaging.objects.count(), 2)
    #     name1 = "{mo_slug}-{code}-{package_level_id}".format(
    #             code='AA'.lower(),
    #             mo_slug='gs1se',
    #             package_level_id=70)
    #     name2 = "{mo_slug}-{code}-{package_level_id}".format(
    #             code='AE'.lower(),
    #             mo_slug='gs1se',
    #             package_level_id=70)
    #
    #     # checking value of first product type
    #     pp1 = ProductPackaging.objects.get(name=name1)
    #     self.assertEquals(pp1.ui_label_en, 'Intermediate bulk container, rigid plastic')
    #     self.assertEquals(pp1.ui_label_sv, 'Intermediate bulkbehållare, styv plast')
    #
    #     # checking value of second product type
    #     pp2 = ProductPackaging.objects.get(name=name2)
    #     self.assertEquals(pp2.ui_label_en, 'Aerosol')
    #     self.assertEquals(pp2.ui_label_sv, 'Aerosol')


class TestDumpLoadTemplateDateCommand(TestCase):
    def setUp(self):
        country = Country(slug='BE', name='Belgium', pk=7)
        country.save()
        member_organisation = MemberOrganisation(
                name='GS1SE',
                slug='gs1se',
                is_active=1,
                country=country,
                pk=7
        )
        member_organisation.save()
        sv = Language.objects.create(slug='sv', name='Swedish')
        en = Language.objects.create(slug='en', name='English')

        LanguageByCountry.objects.create(country=country, language=en, default=True)
        LanguageByCountry.objects.create(country=country, language=sv, default=False)
        PackageLevel.objects.create(id=70, unit_descriptor='test')

    def test_dump_templates_command(self):
        # add some attribute and tempalte data
        ProductAttribute.objects.create(
            **{
                "id": 1,
                "path": "products.models.product.Product.is_dunit",
                "definition_i18n": json.dumps({"en": "Indicator identifying the item as a dispatch (shipping) unit, per the information provider."}),
                "ui_mandatory": True,
                "ui_enabled": True,
                "ui_read_only": False,
                "ui_default_callable": "",
                "ui_field_validation_callable": "",
                "ui_form_validation_callable": "",
                "ui_label_i18n": json.dumps({"en": "The item is a Dispatch Unit"}),
                # "ui_label": "The item is a Dispatch Unit",
                # "ui_label_en": "The item is a Dispatch Unit",
                "csv_mandatory": True,
                "csv_default_callable": "",
                "csv_field_validation_callable": "",
                "csv_form_validation_callable": "",
                "codelist_validation": ""
            }
        )

        ProductAttribute.objects.create(**{
            "id": 2,
            "path": "products.models.product.Product.is_iunit",
            "definition_i18n": json.dumps({"en": "Indicator identifying the item as an invoicing unit, per the information provider."}),
            "ui_mandatory": True,
            "ui_enabled": True,
            "ui_read_only": False,
            "ui_default_callable": "",
            "ui_field_validation_callable": "",
            "ui_form_validation_callable": "",
            "ui_label_i18n": json.dumps({"en": "The item is an Invoice Unit"}),
            # "ui_label": "The item is an Invoice Unit",
            # "ui_label_en": "The item is an Invoice Unit",
            "csv_mandatory": True,
            "csv_default_callable": "",
            "csv_field_validation_callable": "",
            "csv_form_validation_callable": "",
            "codelist_validation": ""
        })
        pt = ProductTemplate.objects.create(
                **{
                    "id": 1,
                    "name": "gs1sv-base",
                    "order": 0,
                    "package_level_id": 70,
                    "member_organisation_id": 7,
                    "image_url": "/undefined.png",
                    "ui_label_i18n": json.dumps({"en": "Basniv\u00e5"}),
                    # "ui_label": "Basniv\u00e5",
                    # "ui_label_en": "Basniv\u00e5",
                }
        )
        pt.attributes.add(1)
        pt.attributes.add(2)
        call_command('dump_templates', mo_slug='gs1se', path='/tmp/UI_presets_v1_test_copy.xlsx')

    # @skip('definition_i18n fails')
    def test_load_v3_templates_command(self):
        self.assertEquals(ProductAttribute.objects.count(), 0)
        # self.assertEquals(ProductTemplate.objects.count(), 0)
        call_command(
            'load_templates_v3_i18n',
            xlsx_path_mask='deployment/test_files/template_test_data_v3.xlsx'
        )
        # count test
        self.assertEquals(ProductTemplate.objects.count(), 3)
        self.assertEquals(ProductTemplate.objects.get(name='gs1se-base').attributes.all().count(), 17)
        self.assertEquals(ProductTemplate.objects.get(name='gs1se-inner-case').attributes.all().count(), 23)
        self.assertEquals(ProductTemplate.objects.get(name='gs1se-inner-pallet').attributes.all().count(), 21)
        self.assertEquals(ProductPackaging.objects.count(), 41)


    def test_remove_templates_command(self):
        ProductAttribute.objects.create(
                **{
                    "id": 1,
                    "path": "products.models.product.Product.is_dunit",
                    "definition_i18n": "{'en': 'Indicator identifying the item as a dispatch (shipping) unit, per the information provider.'}",
                    "ui_mandatory": True,
                    "ui_enabled": True,
                    "ui_read_only": False,
                    "ui_default_callable": "",
                    "ui_field_validation_callable": "",
                    "ui_form_validation_callable": "",
                    "ui_label_i18n": json.dumps({"en": "The item is a Dispatch Unit"}),
                    "csv_mandatory": True,
                    "csv_default_callable": "",
                    "csv_field_validation_callable": "",
                    "csv_form_validation_callable": "",
                    "codelist_validation": ""}
        )

        ProductAttribute.objects.create(**{
            "id": 2,
            "path": "products.models.product.Product.is_iunit",
            "definition_i18n": "{'en': 'Indicator identifying the item as an invoicing unit, per the information provider.'}",
            "ui_mandatory": True,
            "ui_enabled": True,
            "ui_read_only": False,
            "ui_default_callable": "",
            "ui_field_validation_callable": "",
            "ui_form_validation_callable": "",
            "ui_label_i18n": json.dumps({"en": "The item is an Invoice Unit"}),
            "csv_mandatory": True,
            "csv_default_callable": "",
            "csv_field_validation_callable": "",
            "csv_form_validation_callable": "",
            "codelist_validation": ""
        })
        pt = ProductTemplate.objects.create(
                **{
                    "id": 1,
                    "name": "gs1sv-base",
                    "order": 0,
                    "package_level_id": 70,
                    "member_organisation_id": 7,
                    "image_url": "/undefined.png",
                    "ui_label_i18n": json.dumps({"en": "Basniv\u00e5"}),
                }
        )
        pt.attributes.add(1)
        pt.attributes.add(2)
        self.assertEquals(ProductTemplate.objects.count(), 1)
        self.assertEquals(ProductAttribute.objects.count(), 2)
        call_command('remove_templates', mo_slug='gs1se')

        self.assertEquals(ProductTemplate.objects.count(), 0)
        self.assertEquals(ProductAttribute.objects.count(), 0)

    def test_load_templates_gs1ie_command(self):
        country = Country(slug='IE', name='Ireland')
        country.save()
        member_organisation = MemberOrganisation(
                name='GS1IE',
                slug='gs1ie',
                is_active=1,
                country=country
        )
        member_organisation.save()
        PackageLevel.objects.create(id=60, unit_descriptor='gs1ie-inner-pack')
        PackageLevel.objects.create(id=50, unit_descriptor='gs1ie-inner-case')
        PackageLevel.objects.create(id=40, unit_descriptor='gs1ie-display_unit')
        PackageLevel.objects.create(id=30, unit_descriptor='gs1ie-inner-pallet')
        PackageType.objects.create(code='AA', type_i18n=json.dumps({'en': 'Type AA'}))
        PackageType.objects.create(code='AE', type_i18n=json.dumps({'en': 'Type AE'}))
        PackageType.objects.create(code='AM', type_i18n=json.dumps({'en': 'Type AM'}))

        self.assertEquals(ProductAttribute.objects.count(), 0)
        self.assertEquals(ProductTemplate.objects.count(), 0)
        call_command('load_templates_i18n', xlsx_path_mask='deployment/test_files/UI_presets_v2_templates_gs1ie_test.xlsx')
        # count test
        self.assertEquals(ProductTemplate.objects.count(), 5)
        self.assertEquals(ProductTemplate.objects.get(name='gs1ie-inner-pack').attributes.all().count(), 41)
        self.assertEquals(ProductTemplate.objects.get(name='gs1ie-inner-case').attributes.all().count(), 41)
        self.assertEquals(ProductTemplate.objects.get(name='gs1ie-display-unit').attributes.all().count(), 41)
        self.assertEquals(ProductTemplate.objects.get(name='gs1ie-inner-pallet').attributes.all().count(), 41)
        self.assertEquals(ProductPackaging.objects.count(), 3)


class TestHelperMethods(TestCase):
    def test_resolve_boolean_value(self):
        self.assertTrue(resolve_boolean_value('trUe'))
        self.assertTrue(resolve_boolean_value('trUE'))
        self.assertTrue(resolve_boolean_value('1'))
        self.assertTrue(resolve_boolean_value(1))
        self.assertTrue(resolve_boolean_value('TRUE'))
        self.assertTrue(resolve_boolean_value('true'))
        self.assertFalse(resolve_boolean_value('0'))
        self.assertFalse(resolve_boolean_value('3'))
        self.assertFalse(resolve_boolean_value(0))
        self.assertFalse(resolve_boolean_value('False'))
        self.assertFalse(resolve_boolean_value(''))
        self.assertFalse(resolve_boolean_value(None))
        self.assertFalse(resolve_boolean_value('narayan'))


class ViewTesCase(PlusTestCase):

    def setUp(self):
        self.user = UserFactory()
        self.country = CountryFactory()
        self.company_organisation = CompanyOrganisationFactory()

        go_group, _created = Group.objects.get_or_create(name='GO Admins')
        self.go_group = go_group
        mo_group, _created = Group.objects.get_or_create(name='MO Admins')
        self.mo_group = mo_group


    def test_index_redirect(self):
        url = '/accounts/login/'
        uuid = '123123'
        customer_role = f'{uuid}-admin'
        self.user.profile.customer_role = customer_role
        self.user.profile.save()
        self.company_organisation.uuid = uuid
        self.company_organisation.save()
        self.client.force_login(self.user)
        response = self.client.get(url)
        assert response.status_code == 200, response.status_code
        response_countries_id = response.context[0]['companies'].values_list(
            'id', flat=True
        )
        assert self.company_organisation.id in response_countries_id

        self.user.profile.customer_role = ''
        self.user.profile.save()

        response = self.client.get(url)
        assert response.status_code == 200, response.status_code
        companies = response.context[0].get('companies')
        assert companies is None

    def test_index(self):
        url = self.reverse('BCM:index')

        response = self.client.get(url)
        assert response.status_code == 200, response.status_code
        assert b'Activate is a service offered by' in response.content

        self.client.force_login(self.user)
        response = self.client.get(url)
        assert response.status_code == 302, response.status_code
        assert response.url == self.reverse('profile')

        self.user.groups.add(self.go_group)
        self.client.force_login(self.user)
        response = self.client.get(url)
        assert response.status_code == 302, response.status_code
        assert response.url == self.reverse('admin:go_admin')

        self.user.groups.all().delete()
        self.user.groups.add(self.mo_group)
        self.client.force_login(self.user)
        response = self.client.get(url)
        assert response.status_code == 302, response.status_code
        assert response.url == self.reverse('admin:mo_admin')

    def test_after_login(self):
        url = self.reverse('BCM:after_login')
        self.client.force_login(self.user)
        response = self.client.get(url)
        assert response.status_code == 302, response.status_code
        assert response.url == self.reverse('profile')

    def test_staff_member_register_view(self):
        url = self.reverse('BCM:signup')

        response = self.client.get(url)
        assert response.status_code == 200, response.status_code
        assert b'<title>GS1 Activate</title>' in response.content

        self.user.groups.add(self.go_group)
        self.client.force_login(self.user)
        response = self.client.get(url)
        assert response.status_code == 302, response.status_code
        assert response.url == self.reverse('admin:go_admin')

        self.user.groups.all().delete()
        self.user.groups.add(self.mo_group)
        self.client.force_login(self.user)
        response = self.client.get(url)
        assert response.status_code == 302, response.status_code
        assert response.url == self.reverse('admin:mo_admin')

    def test_staff_member_login_view(self):
        url = self.reverse('BCM:login')
        response = self.client.get(url)
        assert response.status_code == 200, response.status_code
        assert b'<title>GS1 Activate</title>' in response.content

        password = 'random123123'

        self.user.set_password(password)
        self.user.save()

        data = {
            'username': self.user.username,
            'password': password
        }
        response = self.client.post(url, data=data)
        assert response.status_code == 302, response.status_code
        assert response.url == self.reverse('profile'), response.url

        self.client.force_login(self.user)
        response = self.client.get(url)
        assert response.status_code == 302, response.status_code
        assert response.url == self.reverse('profile')

        self.user.groups.add(self.go_group)
        self.client.force_login(self.user)
        response = self.client.get(url)
        assert response.status_code == 302, response.status_code
        assert response.url == self.reverse('admin_profile_js')

        self.user.groups.all().delete()
        self.user.groups.add(self.mo_group)
        MemberOrganisationUserFactory(is_admin=True, user=self.user)
        self.client.force_login(self.user)
        response = self.client.get(url)
        assert response.status_code == 302, response.status_code
        assert response.url == self.reverse('admin_profile_js')

        self.user.is_staff = True
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.get(url)
        assert response.status_code == 302, response.status_code
        assert response.url == self.reverse('admin:index')

    def test_ss0_redirect_view(self):
        url = self.reverse('BCM:sso_redirect')

        response = self.client.get(url)
        assert response.status_code == 302, response.status_code
        assert response.url == self.reverse('BCM:index')

        self.client.force_login(self.user)
        response = self.client.get(url)
        assert response.status_code == 302, response.status_code
        assert response.url == self.reverse('BCM:index'),  response.url

        self.user.groups.add(self.go_group)
        self.client.force_login(self.user)
        response = self.client.get(url)
        assert response.status_code == 302, response.status_code
        assert response.url == self.reverse('admin:go_admin')

        self.user.groups.all().delete()
        self.user.groups.add(self.mo_group)
        self.client.force_login(self.user)
        response = self.client.get(url)
        assert response.status_code == 302, response.status_code
        assert response.url == self.reverse('admin:mo_admin')


class SubproductListAPIViewListTestCase(PlusTestCase):

    def setUp(self):
        self.gtin = '01234567890005'
        self.url = self.reverse('api:product-subproducts-list', gtin=self.gtin)

        self.product = ProductFactory(gtin=self.gtin)
        self.sub_product = ProductFactory()
        self.query = {
            # 'base': '',
            # 'pack': '',
            # 'case': '',
            # 'pallet': '',
            # 'display_shipper': '',
            # 'brand': True,
            # 'gtin': True,
            # 'description': True,
            # 'sku': True,
            # 'mark': True,
            # 'target_market': True,
        }
        self.data = {'gtin': self.gtin}
        self.member_organisation = MemberOrganisationFactory()
        self.profile = ProfileFactory()
        self.user = UserFactory(profile=self.profile)
        # string token
        self.token = AuthTokenFactory(user=self.user)
        self.api_client = APIClient()
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')

    def create_sub_products(self):
        SubProductFactory(
            product=self.product,
            sub_product=self.sub_product,
        )

    def test_invalid_gtin(self):
        invalid_gtin = 'invalidgtin'
        url = self.reverse('api:product-subproducts-list', gtin=invalid_gtin)
        response = self.api_client.get(url)
        assert response.status_code == 400, response.status_code
        assert response.data == {'message': 'Unknown GTIN'}, response.data

    def test_valid_gtin(self):
        """No Subproducts"""
        response = self.api_client.get(self.url)
        assert response.status_code == 200, response.status_code
        assert response.data == [], response.data

    def test_with_subprodurcts(self):
        self.create_sub_products()
        response = self.api_client.get(self.url)
        assert response.status_code == 200, response.status_code
        assert len(response.data) == 1, len(response.data)

    def test_with_product_template(self):
        self.create_sub_products()
        ProductTemplateFactory(
            member_organisation=self.user.profile.member_organisation
        )
        response = self.api_client.get(self.url)
        assert response.status_code == 200, response.status_code
        assert len(response.data) == 1, response.data


class SubproductListAPIViewCreateTestCase(PlusTestCase):

    def setUp(self):
        self.gtin = '01234567890005'
        self.url = self.reverse('api:product-subproducts-list', gtin=self.gtin)
        self.product = ProductFactory(gtin=self.gtin)
        self.member_organisation = MemberOrganisationFactory()
        self.profile = ProfileFactory()
        self.user = UserFactory(profile=self.profile)
        # string token
        self.token = AuthTokenFactory(user=self.user)
        self.api_client = APIClient()
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')

    def test_invalid_gtin(self):
        invalid_gtin = 'invalidgtin'
        url = self.reverse('api:product-subproducts-list', gtin=invalid_gtin)
        response = self.api_client.post(url)
        assert response.status_code == 400, response.status_code
        assert response.data == {'message': 'Unknown product GTIN'}, response.data

    def test_invalid_subproduct_gtin(self):
        response = self.api_client.post(
            self.url,
            data={'sub_product': 'invalid_gtin'}
        )
        assert response.status_code == 400, response.status_code
        assert response.data == {'message': 'Unknown product GTIN'}, response.data

    def test_without_quantity(self):
        sub_product_gtin = '012345678915'
        ProductFactory(gtin=sub_product_gtin)

        response = self.api_client.post(
            self.url,
            data={'subproduct': sub_product_gtin}
        )
        assert response.status_code == 400, response.status_code
        assert response.data == {'quantity': 'This field required'}, response.data

    def test_valid_data(self):
        sub_product_gtin = '012345678915'
        ProductFactory(gtin=sub_product_gtin)

        response = self.api_client.post(
            self.url,
            data={'subproduct': sub_product_gtin, 'quantity': 5}
        )
        assert response.status_code == 200, response.status_code

        expected_data = {
            'product': '01234567890005',
            'sub_product': '012345678915',
            'quantity': '5'
        }
        assert response.data == expected_data, response.data


class SubproductCreateListAPIViewTestCase(PlusTestCase):

    def setUp(self):
        self.url = self.reverse('api:product-create-subproducts')
        self.member_organisation = MemberOrganisationFactory()
        self.profile = ProfileFactory()
        self.user = UserFactory(profile=self.profile)
        # string token
        self.token = AuthTokenFactory(user=self.user)
        self.api_client = APIClient()
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')

    def test(self):
        pass


class SubproductRetrieveAPIViewTestCase(PlusTestCase):

    def setUp(self):

        self.member_organisation = MemberOrganisationFactory()
        self.profile = ProfileFactory()
        self.user = UserFactory(profile=self.profile)
        # string token
        self.token = AuthTokenFactory(user=self.user)
        self.api_client = APIClient()
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
        self.gtin = '01234567890005'

        self.product = ProductFactory(gtin=self.gtin)
        self.sub_product = ProductFactory()
        self.url = self.reverse(
            'api:product-subproducts-details',
            product=self.product.gtin,
            sub_product=self.sub_product.gtin,
        )
        self.sub_product_instance = SubProductFactory(
            product=self.product,
            sub_product=self.sub_product,
        )
    def test_method_get(self):
        response = self.api_client.get(self.url)
        assert response.status_code == 200, response.status_code

    def test_method_get_invalid_subproduct(self):
        url = self.reverse(
            'api:product-subproducts-details',
            product=self.product.gtin,
            sub_product='invalid_gtin',
        )
        response = self.api_client.get(url)
        assert response.status_code == 400, response.status_code
        assert response.data == {'message': 'Invalid subproduct gtin'}, response.data

    def test_method_get_invalid_product(self):
        url = self.reverse(
            'api:product-subproducts-details',
            sub_product=self.sub_product.gtin,
            product='invalid_gtin',
        )
        response = self.api_client.get(url)
        assert response.status_code == 400, response.status_code
        assert response.data == {'message': 'Invalid product gtin'}, response.data


    def test_method_patch_without_quantity(self):
        response = self.api_client.patch(self.url)
        assert response.status_code == 400, response.status_code
        assert response.data == {'quantity': 'This field required'}, response.data

    def test_method_patch_invalid_product(self):
        url = self.reverse(
            'api:product-subproducts-details',
            sub_product=self.sub_product.gtin,
            product='invalid_gtin',
        )
        response = self.api_client.patch(url, data={'quantity': 1})
        assert response.status_code == 400, response.status_code
        assert response.data == {'message': 'Invalid product gtin'}, response.data

    def test_method_patch_with_quantity(self):
        response = self.api_client.patch(self.url, data={'quantity': 1})
        assert response.status_code == 200, response.status_code
        expected_data = {
            'product': self.product.gtin,
            'sub_product': self.sub_product.gtin,
            'quantity': '1'
        }

        assert response.data == expected_data, response.data

    def test_method_delete_invalid_product(self):
        url = self.reverse(
            'api:product-subproducts-details',
            sub_product=self.sub_product.gtin,
            product='invalid_gtin',
        )
        response = self.api_client.delete(url)
        assert response.status_code == 400, response.status_code
        assert response.data == {'message': 'Invalid product gtin'}, response.data

    def test_method(self):
        response = self.api_client.delete(self.url)
        assert response.status_code == 200, response.status_code
        assert response.data == {'status': 'ok'}, response.data
        assert SubProduct.objects.count() == 0, SubProduct.objects.count()
