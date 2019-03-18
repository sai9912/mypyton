from collections import OrderedDict

from django.test import TestCase
from member_organisations.custom_admin.base_admin_tests import BaseAdminTestCase

from company_organisations.models import (
    CompanyOrganisation, CompanyOrganisationOwner, CompanyOrganisationUser
)
from audit.models import Log
from prefixes.models import Prefix
from products.models.product import Product


class MOAdminTestCase(BaseAdminTestCase, TestCase):
    url_prefix = 'mo_admin'
    group_name = 'MO Admins'

    # todo: allowed/not allowed related model querysets/instances for admin-specific models

    def setUp(self):
        super().setUp()
        self.model_instances = self.create_required_instances()

    def test_access_for_mo_admin_co(self):
        """
        mo1_user1 should be able to view companies in his MOs
        """

        login_result = self.client.login(**self.main_user_credentials)
        self.assertTrue(login_result, 'Can\'t login with test user credentials')

        co_url = self.get_url_for_model(
            CompanyOrganisation, 'change', self.model_instances['co1'].pk
        )
        response = self.client.get(co_url)
        self.assertEqual(
            response.status_code, 200,
            f'URL "{co_url}" should be allowed for mo1 user'
        )

        co_url = self.get_url_for_model(
            CompanyOrganisation, 'change', self.model_instances['co2'].pk
        )
        response = self.client.get(co_url)
        self.assertEqual(
            response.status_code, 302,
            f'URL "{co_url}" should be denied for mo1 user'
        )

    def test_change_co_for_mo_admin(self):
        """
        mo1_user1 should be able to change companies with his MOs
        """

        login_result = self.client.login(**self.main_user_credentials)
        self.assertTrue(login_result, 'Can\'t login with test user credentials')

        test_co = self.model_instances['co1']
        post_data = self.model_instance_to_post_data(test_co)
        post_data['phone'] = '1111222233334444'  # field which will be changed

        co_url = self.get_url_for_model(CompanyOrganisation, 'change', test_co.pk)

        # instance creating is here
        response = self.client.post(co_url, data=post_data)

        self.assertEqual(
            response.status_code, 302, 'Should be a redirect after an instance submitting'
        )

        self.assertEqual(
            response.url,
            self.get_url_for_model(CompanyOrganisation, 'changelist'),
            f'Wrong redirect url after an instace updating'
        )

        self.assertTrue(
            CompanyOrganisation.objects.filter(
                company=test_co.company,
                phone=post_data['phone'],  # must be updated in the test database
                member_organisation=self.model_instances['mo1'],
                country=self.model_instances['mo1'].country
            ).exists(),
            f'CompanyOrganisation "{test_co}" must have updated phone number'
        )

    def test_add_all_models_for_mo_admin(self):
        """
        Test all models for adding instances
        :return:
        """

        login_result = self.client.login(**self.main_user_credentials)
        self.assertTrue(login_result, 'Can\'t login with test user credentials')

        # to avoid troubles with unique indexes and already exists instances
        self.model_instances['co1_owner'].delete()
        self.model_instances['co1_prefix1'].delete()

        models_config = {
            # new instances configuration dictionary
            CompanyOrganisation: {
                'predefined_fields': {
                    'company': 'New test company',
                    'member_organisation': self.model_instances['mo1'],
                    'country': self.model_instances['mo1'].country,
                    'active': True
                }
            },
            CompanyOrganisationOwner: {
                'predefined_fields': {
                    'organization': self.model_instances['co1'],
                    'organization_user': self.model_instances['co1_user1'],
                }
            },
            CompanyOrganisationUser: {
                'predefined_fields': {
                    'user': self.model_instances['user12'],
                    'organization': self.model_instances['co1'],
                }
            },
            Prefix: {
                'predefined_fields': {
                    'company_organisation': self.model_instances['co1'],
                    'member_organisation': self.model_instances['mo1'],
                }
            },
            Product: None,  # too many new relations without description, skipped for now
            Log: {
                'predefined_fields': {
                    'msg': 'Test message'
                }
            }
        }

        # alternative WRONG way to test without TestClient requests
        # This case django admin will use DEFAULT DATABASE (NOT A TEST ONE)
        # request = self.request_factory.get(reverse('admin:mo_admin'))
        # request.user = self.user
        # co_mo_admin_view = CompanyOrganisationCustomAdmin(CompanyOrganisation, AdminSite())
        # co_form_class = co_mo_admin_view.get_form(request)
        # co_form = co_form_class(data=post_data)
        # co_form.is_valid()
        # co_form.save()

        self.perform_adding_tests(models_config)

    def test_delete_all_models_for_mo_admin(self):
        """
        mo1_user1 should be able to change companies with his MOs
        """
        login_result = self.client.login(**self.main_user_credentials)
        self.assertTrue(login_result, 'Can\'t login with test user credentials')

        models_config = {
            Prefix: {
                'order': 1,
                'model_instance': self.model_instances['co1_prefix1'],
            },
            CompanyOrganisationOwner: {
                'order': 2,
                'model_instance': self.model_instances['co1_owner'],
            },
            CompanyOrganisationUser: {
                'order': 3,
                'model_instance': self.model_instances['co1_user1'],
            },
            CompanyOrganisation: {
                'order': 4,
                'model_instance': self.model_instances['co1'],
            },
            Product: {
                # too many new relations without description, skipped for now
                'order': 5
            },
            Log: {
                'order': 6,
                'model_instance': self.model_instances['co1_log1'],
            }
        }
        models_config = OrderedDict(
            sorted(models_config.items(), key=lambda items: items[1]['order'])
        )

        self.perform_deleting_tests(models_config)
