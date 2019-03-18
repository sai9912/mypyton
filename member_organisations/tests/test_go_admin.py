from collections import OrderedDict

from django.test import TestCase

from member_organisations.custom_admin.base_admin_tests import BaseAdminTestCase

from member_organisations.models import MemberOrganisation
from company_organisations.models import (
    CompanyOrganisation, CompanyOrganisationOwner, CompanyOrganisationUser
)
from BCM.models import Country
from audit.models import Log
from prefixes.models import Prefix
from products.models.product import Product


class GOAdminTestCase(BaseAdminTestCase, TestCase):
    url_prefix = 'go_admin'
    group_name = 'GO Admins'

    def setUp(self):
        super().setUp()
        self.model_instances = self.create_required_instances()

    def test_add_all_models_for_go_admin(self):
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
            MemberOrganisation: {
                'predefined_fields': {
                    'country': Country.objects.get(name='Germany'),
                }
            },
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

        self.perform_adding_tests(models_config)

    def test_delete_all_models_for_go_admin(self):
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
            MemberOrganisation: {
                'order': 5,
                'model_instance': self.model_instances['mo1'],
            },
            Product: {
                # too many new relations without description, skipped for now
                'order': 6,
            },
            Log: {
                'order': 7,
                'model_instance': self.model_instances['co1_log1'],
            }
        }
        models_config = OrderedDict(
            sorted(models_config.items(), key=lambda items: items[1]['order'])
        )

        self.perform_deleting_tests(models_config)
