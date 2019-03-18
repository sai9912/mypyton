import json
import os
import re
from argparse import RawTextHelpFormatter

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.test import Client
from django.urls import reverse
from knox.models import AuthToken
from knox.settings import CONSTANTS

from company_organisations.models import CompanyOrganisation
from member_organisations.models import M2MToken
from prefixes.models import Prefix


class Command(BaseCommand):
    help = 'Integration test for prefix status functionality'
    client = None
    mo_username = None
    data = None

    def add_arguments(self, parser):
        default_json_file = os.path.join(
            settings.BASE_DIR,
            'member_organisations/management/commands/prefix_status_test.json'
        )
        parser.add_argument('json_file_path', nargs='?', default=default_json_file)

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super().__init__(stdout, stderr, no_color)
        self.client = Client(enforce_csrf_checks=False)

    def load_json_data(self, json_file_path):
        with open(json_file_path) as f:
            data = f.read()
        return json.loads(data)

    def handle(self, *args, **options):
        self.data = self.load_json_data(options['json_file_path'])
        self.mo_username = self.data['mo_username']
        user_data = self.data['user']
        product_data = self.data['product']

        # 1. mo login
        self.stdout.write(self.style.HTTP_INFO(
            'You can override data by specifying json file as first argument')
        )
        print('current data:\n{json_data}\n'.format(json_data=json.dumps(self.data, indent=4)))

        self.stdout.write(self.style.HTTP_INFO(
            f'\n\n1. Login to django admin with username: {self.mo_username}')
        )
        # print(f'\n\n1. Login to django admin with username: {self.mo_username}')
        input(f'Press enter to continue..')
        result = self.login(self.mo_username)
        print(f'Done')

        # 2. M2M token
        self.stdout.write(self.style.HTTP_INFO(
            f'\n\n2. Retrieving M2M token from django admin: {self.mo_username}')
        )
        input(f'Press enter to continue..')
        mo_token = self.retrieve_m2m_token()
        print(f'Token string: {mo_token}')
        print(f'Done')

        # 3. create company/prefix
        self.stdout.write(self.style.HTTP_INFO(f'\n\n3. Create the company/prefix'))
        input(f'Press enter to continue..')
        response = self.create_company(user_data)
        print(f'Done')

        # 4. co login and retrieve a token
        self.stdout.write(self.style.HTTP_INFO(f'\n\n4. Login with API and retrieve CO token'))
        input(f'Press enter to continue..')
        response = self.api_login(user_data['email'], user_data['password'])
        co_token = response['token']
        print(f'Response: {json.dumps(response, indent=4)}')
        print(f'Done')

        # 5. add product
        self.stdout.write(self.style.HTTP_INFO(f'\n\n5. Add a product with enabled prefix'))
        input(f'Press enter to continue..')
        response = self.add_product(product_data, co_token)
        print(f'Response: {json.dumps(response, indent=4)}')
        print(f'Done')

        # 6. prefix deactivation
        self.stdout.write(self.style.HTTP_INFO(f'\n\n6. Prefix deactivation'))
        input(f'Press enter to continue..')
        response = self.set_prefix_parameters(
            co_token, user_data['company_prefix'], is_suspended=True
        )
        print(f'Response: {json.dumps(response, indent=4)}')
        print(f'Done')

        # 7. adding new product (denied with suspended prefix)
        self.stdout.write(self.style.HTTP_INFO(f'\n\n7. Add a product with disabled prefix'))
        input(f'Press enter to continue..')
        product_data = self.add_product(product_data, co_token)
        print(f'Response: {json.dumps(product_data, indent=4)}')
        print(f'Done')

        # 8. remove all created instances
        self.stdout.write(self.style.HTTP_INFO(f'\n\n8. Remove all created instances'))
        input(f'Press enter to continue..')
        self.remove_user_related_instances(self.mo_username, remove_all=False)
        self.remove_user_related_instances(user_data['email'], remove_all=True)
        self.remove_company_related_instances(user_data)
        print(f'Done')

    def login(self, username):
        """
        Force user login without username/password
        :return:
        """

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'Can\'t find user: "{username}"')

        self.client.force_login(user)
        response = self.client.get(reverse('admin:mo_admin'))

        if response.status_code != 200:
            raise CommandError(
                f'Can\'t access to mo admin index page, status code: {response.status_code}'
            )

        return True

    def api_login(self, username, password):
        """
        API login with username/password
        :return: token string
        """

        post_data = {
            'username': username,
            'password': password,
        }
        print('POST ', reverse('api:login'))
        print(json.dumps(post_data, indent=4), '\n')
        response = self.client.post(reverse('api:login'), data=post_data)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def retrieve_m2m_token(self):
        """
        create new m2m token for a currently logged in user, and return it
        note: token is retrieved from messages, only way to get it here
        """

        moadmin_m2m_token_add_url = reverse('admin:mo_admin_member_organisations_m2mtoken_add')
        response = self.client.post(
            moadmin_m2m_token_add_url,
            data={'description': 'integration test'}
        )
        # save it for the further usage: <strong></strong>
        token_regexp = re.findall(
            r'save it for the further usage: <strong>(\w+)</strong>',
            response.cookies['messages'].value
        )
        if token_regexp:
            return token_regexp[0]
        else:
            return None

    def create_company(self, user_data):
        print('POST ', reverse('api:register'))
        print(json.dumps(user_data, indent=4), '\n')

        response = self.client.post(reverse('api:register'), data=user_data)
        if response.status_code != 201:
            print(f'Can\'t create company')
        return response.json()

    def add_product(self, product_data, token):
        """
        Post a new product to created company
        :param product_data: post data
        :param token: token string
        :return:
        """

        auth_token = AuthToken.objects.filter(
            token_key=token[:CONSTANTS.TOKEN_KEY_LENGTH]
        ).first()
        user = auth_token.user
        company_organisation = user.company_organisations_companyorganisation.first()
        member_organisation = company_organisation.member_organisation

        product_data['owner'] = user.pk
        product_data['company_organisation'] = company_organisation.pk
        product_data['member_organisation'] = member_organisation.pk

        headers = {'HTTP_AUTHORIZATION': f'Token {token}'}

        print('POST ', reverse('api:product-list'))
        print('HEADERS ', json.dumps(headers, indent=4), '\n')
        print(json.dumps(product_data, indent=4), '\n')

        response = self.client.post(
            reverse('api:product-list'), data=product_data, **headers
        )

        return response.json()

    def set_prefix_parameters(self, token, prefix, **kwargs):
        """
        Update prefix parameters, any parameter can be updated with kwargs
        """

        headers = {
            'HTTP_AUTHORIZATION': f'Token {token}',
            # 'HTTP_CONTENT-TYPE': f'application/json',
        }

        print('PATCH ', reverse('api:prefixes-detail', args=(prefix,)))
        print('HEADERS ', json.dumps(headers, indent=4), '\n')
        print(json.dumps(kwargs, indent=4), '\n')

        response = self.client.patch(
            reverse('api:prefixes-detail', args=(prefix,)),
            data=json.dumps(kwargs),
            content_type='application/json',
            **headers,
        )
        return response.json()

    def remove_user_related_instances(self, username, remove_all=False):
        """
        Remove user related instances which were created by this test command
        """

        auth_token = AuthToken.objects.filter(user__username=username).first()
        user = auth_token.user
        M2MToken.objects.filter(token__user=user).delete()
        AuthToken.objects.filter(user=user).delete()

        if remove_all:
            user.product_set.all().delete()
            user.delete()

    def remove_company_related_instances(self, user_data):
        """
        Remove company/products related instances which were created by this test command
        """

        Prefix.objects.filter(prefix=user_data['company_prefix']).delete()
        CompanyOrganisation.objects.filter(uuid=user_data['uuid']).delete()
