from django.contrib.auth.models import User, Group
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from BCM.models import Country
from company_organisations.models import CompanyOrganisation
from member_organisations.models import MemberOrganisation
from prefixes.models import Prefix
from unittest import skip


class PrefixGenericTestCase:
    """
    Abstract Class to test Prefix API
    This class should NOT inherent from any TestCase class
    """
    reverse_url_name = NotImplementedError
    reverse_url_kwarg = None

    @classmethod
    def setUpTestData(cls):
        country = Country(slug='BE', name='Belgium')
        country.save()
        cls.member_organisation = MemberOrganisation(name='GS1',
                                                     slug='gs1',
                                                     is_active=1,
                                                     country=country,
                                                     gs1_prefix_regex='^539|^501|^509|^0\\d\\d')
        cls.member_organisation.save()
        cls.company_orgnisation = CompanyOrganisation.objects.create(**{
            'uuid': '53900011',
            'company': 'GS1 Ireland',
            'name': 'GS1 Ireland',
            'member_organisation': cls.member_organisation,
            'country': country,
        })
        cls.user = User.objects.create_user(username='test', password='password')
        mo_admin_group = Group.objects.create(name='MO Admins')
        cls.user.groups.add(mo_admin_group)
        cls.member_organisation.add_user(cls.user)
        cls.company_orgnisation.add_user(cls.user)
        cls.user.profile.company_organisation = cls.company_orgnisation
        cls.user.profile.member_organisation = cls.member_organisation
        cls.user.profile.save()
        cls.token = cls.get_token_from_data({'username': 'test', 'password': 'password'})
        cls.reverse_url = reverse(cls.reverse_url_name, kwargs=cls.reverse_url_kwarg)

    @classmethod
    def get_token_from_data(cls, data={}):
        client = APIClient()
        response = client.post(reverse('api:login'), data=data)
        return response.data['token']

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    @classmethod
    def create_sample_prefix(cls, data={}):
        """
        Create Prefix with generic data or given data
        :param data: dict
        :return: prefixes.models.Prefix
        """
        generic_data = {
            "prefix": "723372372",
            # "is_active": True,
            "is_suspended": False,
            "is_special": "",
            "starting_from": "7233723720006",
            "company_organisation": cls.company_orgnisation,
            "member_organisation": cls.member_organisation,
            "description": "Some description prefix"
        }
        generic_data.update(data)
        prefix = Prefix.objects.create(**generic_data)
        cls.user.profile.product_active_prefix = prefix
        cls.user.profile.save()
        return prefix

    def response_test_data(self, response_data, data_dict):
        """
        Compare all prefix fields in the response with given data.
        :param response_data: dict (From response)
        :param data_dict: dict (Expected data)
        :return: None
        """
        self.assertEqual(response_data["prefix"], data_dict["prefix"])
        # self.assertEqual(response_data["is_active"], data_dict["is_active"])
        self.assertEqual(response_data["is_suspended"], data_dict["is_suspended"])
        self.assertEqual(response_data["is_special"], data_dict["is_special"])
        # self.assertEqual(response_data["starting_from"], data_dict["starting_from"])
        # self.assertEqual(response_data["starting_from_gln"], data_dict["starting_from_gln"])
        self.assertEqual(response_data["member_organisation"], data_dict["member_organisation"])
        self.assertEqual(response_data["description"], data_dict["description"])

    def from_models_object_to_dict(self, obj):
        """
        Take data from given object with the fields defined bellow
        :param obj: Object
        :return: dict
        """
        return {
            "prefix": obj.prefix,
            # "is_active": obj.is_active,
            "is_suspended": obj.is_suspended,
            "is_special": obj.is_special,
            "created": obj.created.isoformat().replace('+00:00', 'Z'),
            "updated": obj.updated.isoformat().replace('+00:00', 'Z'),
            "starting_from": obj.starting_from,
            "starting_from_gln": obj.starting_from_gln,
            "member_organisation": obj.member_organisation.slug,
            "description": obj.description,
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
            try:
                client_method = getattr(self.client, method)
                response = client_method(self.reverse_url)

                self.assertEqual(response.status_code, 401)
                self.assertEqual(response.data, {"detail": "Authentication credentials were not provided."})
            except Exception as e:
                assert str(e) == "'AnonymousUser' object has no attribute 'profile'"


class PrefixListAPITestCase(PrefixGenericTestCase, APITestCase):
    reverse_url_name = 'api:prefixes-list'
    method = ['get']

    def setUp(self):
        super(PrefixListAPITestCase, self).setUp()
        self.prefix = self.create_sample_prefix()

    def test_empty_prefix_from_correct_company_uuid(self):
        self.prefix.delete()
        response = self.client.get(self.reverse_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_list_prefix_from_correct_company_uuid(self):
        response = self.client.get(self.reverse_url)

        self.assertEqual(response.status_code, 200)
        self.response_test_data(response.data[0], {
            "prefix": "723372372",
            # "is_active": True,
            "is_suspended": False,
            "is_special": "",
            "created": self.prefix.created.isoformat().replace('+00:00', 'Z'),
            "updated": self.prefix.updated.isoformat().replace('+00:00', 'Z'),
            "starting_from": "5390001100003",
            "starting_from_gln": None,
            "member_organisation": self.member_organisation.slug,
            "description": "Some description prefix",
        })


class PrefixCreateAPITestCase(PrefixGenericTestCase, APITestCase):
    reverse_url_name = 'api:prefix-create'
    reverse_url_kwarg = {'uuid': '53900011'}
    method = ['post']

    def test_create_prefix_with_correctly_company_uuid(self):
        post_data = {
            "prefix": "539548454",
            # "is_active": True,
            "is_suspended": False,
            "is_special": "yes",
            "starting_from": "5390001100003",
            "starting_from_gln": None,
            "description": "Some description"
        }
        self.assertFalse(Prefix.objects.filter(prefix="539548454").exists())

        response = self.client.post(self.reverse_url, data=post_data, format='json')

        prefix = Prefix.objects.get(prefix="539548454")
        expected_data = {
            "prefix": "539548454",
            # "is_active": True,
            "is_suspended": False,
            "is_special": "yes",
            "created": prefix.created.isoformat().replace('+00:00', 'Z'),
            "updated": prefix.updated.isoformat().replace('+00:00', 'Z'),
            "starting_from": "5390001100003",
            "starting_from_gln": None,
            "member_organisation": self.member_organisation.slug,
            "description": "Some description"
        }

        self.assertEqual(response.status_code, 201)
        self.response_test_data(response.data, expected_data)
        self.response_test_data(self.from_models_object_to_dict(prefix), expected_data)

    def test_create_prefix_without_prefix(self):
        post_data = {
            # "is_active": True,
            "is_suspended": False,
            "is_special": "yes",
            "starting_from": "5390001100003",
            "starting_from_gln": None,
            "member_organisation": self.member_organisation.slug,
            "description": "Some description"
        }

        response = self.client.post(self.reverse_url, data=post_data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            "prefix": [
                "This field is required."
            ]
        })

    def test_create_prefix_with_existing_prefix(self):
        self.create_sample_prefix()
        post_data = {
            "prefix": "723372372",
            # "is_active": True,
            "is_suspended": False,
            "is_special": "yes",
            "starting_from": "5390001100003",
            "starting_from_gln": None,
            "member_organisation": self.member_organisation.slug,
            "description": "Some description"
        }

        response = self.client.post(self.reverse_url, data=post_data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            "prefix": [
                "prefix with this prefix already exists."
            ]
        })

    def test_try_create_prefix_with_more_then_12_prefix_characters(self):
        self.create_sample_prefix()
        post_data = {
            "prefix": "1234567890123",
            # "is_active": True,
            "is_suspended": False,
            "is_special": "yes",
            "starting_from": "5390001100003",
            "starting_from_gln": None,
            "member_organisation": self.member_organisation.slug,
            "description": "Some description"
        }

        response = self.client.post(self.reverse_url, data=post_data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            "prefix": [
                "Ensure this field has no more than 12 characters."
            ]
        })

    def test_try_create_prefix_with_less_then_5_prefix_characters(self):
        self.create_sample_prefix()
        post_data = {
            "prefix": "33",
            # "is_active": True,
            "is_suspended": False,
            "is_special": "yes",
            "starting_from": "5390001100003",
            "starting_from_gln": None,
            "member_organisation": self.member_organisation.slug,
            "description": "Some description"
        }

        response = self.client.post(self.reverse_url, data=post_data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            "prefix": [
                "Ensure this field has at least 5 characters."
            ]
        })

    def test_match_gs1_prefix_regex(self):
        response = self.client.post(self.reverse_url,
                                    {'prefix': '53900012'},
                                    format='json')
        assert response.status_code == 201
        assert response.data['prefix'] == '53900012'

    def test_not_match_gs1_prefix_regex(self):
        response = self.client.post(self.reverse_url,
                                    {'prefix': '53800012'},
                                    format='json')
        assert response.status_code == 400
        res = response.data['prefix']
        assert response.data['prefix'] == ['Prefix not valid']


class PrefixesRetrieveAPITestCase(PrefixGenericTestCase, APITestCase):
    reverse_url_name = 'api:prefixes-detail'
    reverse_url_kwarg = {'prefix': '723372372'}
    method = ['get']

    @classmethod
    def setUpTestData(cls):
        super(PrefixesRetrieveAPITestCase, cls).setUpTestData()
        cls.prefix = cls.create_sample_prefix()

    def test_retrieve_prefix_correctly(self):
        response = self.client.get(self.reverse_url)

        self.assertEqual(response.status_code, 200)
        self.response_test_data(response.data, {
            "prefix": "723372372",
            # "is_active": True,
            "is_suspended": False,
            "is_special": "",
            "created": self.prefix.created.isoformat().replace('+00:00', 'Z'),
            "updated": self.prefix.updated.isoformat().replace('+00:00', 'Z'),
            "starting_from": "5390001100003",
            "starting_from_gln": None,
            "member_organisation": self.member_organisation.slug,
            "description": "Some description prefix"
        })

    def test_404_when_prefix_does_not_exist(self):
        response = self.client.get(reverse(
            'api:prefixes-detail', kwargs={'prefix': '0000000'}
        ))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {
            "detail": "Not found."
        })


class PrefixesUpdateAPITestCase(PrefixGenericTestCase, APITestCase):
    reverse_url_kwarg = {'prefix': '723372372'}
    reverse_url_name = 'api:prefixes-detail'
    method = ['patch', 'put']

    @classmethod
    def setUpTestData(cls):
        super(PrefixesUpdateAPITestCase, cls).setUpTestData()
        cls.prefix = cls.create_sample_prefix({"is_special": "yes"})

    # @skip('is_active have been moved to the Profile model')
    # def test_update_partial_prefix_correctly(self):
    #     response = self.client.patch(self.reverse_url, data={"is_active": "False"}, format='json')
    #
    #     expected_data = {
    #         "prefix": "723372372",
    #         # "is_active": False,
    #         "is_suspended": False,
    #         "is_special": "yes",
    #         "created": self.prefix.created.isoformat().replace('+00:00', 'Z'),
    #         "updated": self.prefix.updated.isoformat().replace('+00:00', 'Z'),
    #         "starting_from": "5390001100003",
    #         "starting_from_gln": None,
    #         "member_organisation": self.member_organisation.slug,
    #         "description": "Some description prefix"
    #     }
    #
    #     self.prefix = Prefix.objects.get(pk=self.prefix.pk)
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertNotEqual(self.user.profile.product_active_prefix, self.prefix)
    #     self.response_test_data(response.data, expected_data)
    #     self.response_test_data(self.from_models_object_to_dict(self.prefix), expected_data)

    def test_update_fully_prefix_correctly(self):
        response = self.client.put(self.reverse_url, data={"prefix": "539111111"}, format='json')

        expected_data = {
            "prefix": "539111111",
            # "is_active": True,
            "is_suspended": False,
            "is_special": "yes",
            "created": self.prefix.created.isoformat().replace('+00:00', 'Z'),
            "updated": self.prefix.updated.isoformat().replace('+00:00', 'Z'),
            "starting_from": "5390001100003",
            "starting_from_gln": None,
            "member_organisation": self.member_organisation.slug,
            "description": "Some description prefix"
        }

        self.prefix = Prefix.objects.get(pk=self.prefix.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.prefix.prefix, "539111111")
        self.response_test_data(response.data, expected_data)
        self.response_test_data(self.from_models_object_to_dict(self.prefix), expected_data)

    def test_try_fully_update_without_prefix(self):
        response = self.client.put(self.reverse_url, data={"is_active": False}, format='json')

        expected_data = {
            "prefix": [
                "This field is required."
            ]
        }

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.user.profile.product_active_prefix, self.prefix)
        self.assertEqual(response.data, expected_data)

    def test_try_update_prefix_with_less_then_five_characters(self):
        response = self.client.put(self.reverse_url, data={"prefix": '22'}, format='json')

        expected_data = {
            "prefix": [
                "Ensure this field has at least 5 characters."
            ]
        }

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.user.profile.product_active_prefix, self.prefix)
        self.assertEqual(response.data, expected_data)

    def test_try_update_prefix_with_more_then_twelve_characters(self):
        response = self.client.put(self.reverse_url, data={"prefix": '1234567890123'}, format='json')

        expected_data = {
            "prefix": [
                "Ensure this field has no more than 12 characters."
            ]
        }

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.user.profile.product_active_prefix, self.prefix)
        self.assertEqual(response.data, expected_data)

    def test_404_when_prefix_does_not_exist_partial(self):
        response_partial = self.client.patch(reverse(
            'api:prefixes-detail', kwargs={'prefix': '0000000'}
        ))

        self.assertEqual(response_partial.status_code, 404)
        self.assertEqual(response_partial.data, {
            "detail": "Not found."
        })

    def test_404_when_prefix_does_not_exist_fully(self):
        response_fully = self.client.put(reverse(
            'api:prefixes-detail', kwargs={'prefix': '0000000'}
        ))

        self.assertEqual(response_fully.status_code, 404)
        self.assertEqual(response_fully.data, {
            "detail": "Not found."
        })


class PrefixesDeleteAPITestCase(PrefixGenericTestCase, APITestCase):
    reverse_url_kwarg = {'prefix': '723372372'}
    reverse_url_name = 'api:prefixes-detail'
    method = ['delete']

    @classmethod
    def setUpTestData(cls):
        super(PrefixesDeleteAPITestCase, cls).setUpTestData()
        cls.prefix = cls.create_sample_prefix()

    def test_delete_prefix_correctly(self):
        response = self.client.delete(self.reverse_url)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, None)
        self.assertFalse(Prefix.objects.filter(pk=self.prefix.pk).exists())

    def test_404_when_prefix_does_not_exist(self):
        response = self.client.delete(reverse(
            'api:prefixes-detail', kwargs={'prefix': '0000000'}
        ))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {
            "detail": "Not found."
        })
