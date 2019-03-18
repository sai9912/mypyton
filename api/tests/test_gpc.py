from django.test import TestCase
from django.contrib.auth.models import User
from knox.models import AuthToken
from rest_framework.reverse import reverse


class GPCTest(TestCase):
    user = None
    auth_token = None
    user_credentials = None

    def setUp(self):
        self.user_credentials = {
            'user1': {
                'username': 'user1',
                'password': 'pass1',
            }
        }
        user = self.create_django_user(self.user_credentials['user1'])
        self.auth_token = AuthToken.objects.create(user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def create_django_user(self, user_credentials):
        user = User.objects.create(**user_credentials)
        user.set_password(user_credentials['password'])
        user.save()
        return user

    def test_gpc_search_brick_non_authorized(self):
        api_url = reverse('api:gpc-list')
        data = {'brick': 'tele'}

        response = self.client.get(api_url, data)
        self.assertEqual(response.status_code, 401, 'Non 401 response for brick search')

    def test_gpc_search_brick_authorized(self):
        api_url = reverse('api:gpc-list')
        headers = {'HTTP_AUTHORIZATION': f'Token {self.auth_token}'}
        data = {'brick': 'tele'}

        response = self.client.get(api_url, data, **headers)
        self.assertEqual(response.status_code, 200, 'Non 200 response for brick search')
        self.assertTrue(
            response.json()[0].get('test_environment'),  # response: [{'test_environment': True}]
            'Non 200 response for brick search'
        )

    def test_gpc_search_brick_code_non_authorized(self):
        api_url = reverse('api:gpc-list')
        data = {'brick_code': '12345'}

        response = self.client.get(api_url, data)
        self.assertEqual(response.status_code, 401, 'Non 401 response for brick code search')

    def test_gpc_search_brick_code_authorized(self):
        api_url = reverse('api:gpc-list')
        headers = {'HTTP_AUTHORIZATION': f'Token {self.auth_token}'}
        data = {'brick_code': '12345'}

        response = self.client.get(api_url, data, **headers)
        self.assertEqual(response.status_code, 200, 'Non 200 response for brick code search')
        self.assertTrue(
            response.json()[0].get('test_environment'),  # response: [{'test_environment': True}]
            'Non 200 response for brick search'
        )

    def test_gpc_search_both_authorized(self):
        api_url = reverse('api:gpc-list')
        headers = {'HTTP_AUTHORIZATION': f'Token {self.auth_token}'}
        data = {'brick': 'tele', 'brick_code': '12345'}

        response = self.client.get(api_url, data, **headers)
        self.assertEqual(response.status_code, 400, 'Non 400 response for both search')
        self.assertIn(
            'choose one', response.json()[0],
            'Wrong status text for "both parameters specified" error'
        )

    def test_gpc_search_none_authorized(self):
        api_url = reverse('api:gpc-list')
        headers = {'HTTP_AUTHORIZATION': f'Token {self.auth_token}'}
        data = {}

        response = self.client.get(api_url, data, **headers)
        self.assertEqual(response.status_code, 400, 'Non 400 response for both search')
        self.assertIn(
            'no query parameters specified', response.json()[0],
            'Wrong status text for "no parameters specified" error'
        )

