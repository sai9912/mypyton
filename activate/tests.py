from django.test import TestCase
from BCM.models import Country
from member_organisations.models import MemberOrganisation
from services import users_service, prefix_service, logs_service
from django.contrib.auth.models import User as AuthUser
from prefixes.models import Prefix


class Gs1IeTestCase(TestCase):
    url = '/API/v0/AccountCreateOrUpdate/'

    post_data = {       'uuid': '53900011',
                       'email': '53900011@test.com',
              'company_prefix': '53900011,53900012',
                'company_name': 'GS1 Ireland',
                     'credits': '39:20,43:100,44:100',
                     'txn_ref': 'Test_1,Test_3,Test_2',
         'member_organisation': 'gs1' }

    def setUp(self):
        country, is_created = Country.objects.get_or_create(slug='BE', name='Belgium')
        member_organisation = MemberOrganisation(name='GS1',
                                                 slug='gs1',
                                                 is_active=1,
                                                 country=country)
        member_organisation.save()

    def test_page_exist(self):
        response = self.client.get(self.url)
        assert response.status_code == 200

    def test_page_is_AccountCreateOrUpdate(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'AccountCreateOrUpdate')

    def test_page_post(self):
        response = self.client.post(self.url, self.post_data)
        assert response.status_code == 302

    def test_page_empty_post(self):
        response = self.client.post(self.url, {})
        assert response.status_code == 200
        self.assertContains(response, 'AccountCreateOrUpdate')

    def test_users_data(self):
        self.client.post(self.url, self.post_data)
        auth_user = AuthUser.objects.filter(email='53900011@test.com').first()
        assert auth_user is not None
        company_organisation = users_service.get_company_organisation(auth_user)
        assert company_organisation.uuid == '53900011'
        assert company_organisation.company == 'GS1 Ireland'

    def test_prefixes_data(self):
        self.client.post(self.url, self.post_data)
        prefixes = Prefix.objects.all()
        assert len(prefixes) == 2
        assert prefixes[0].prefix == '53900011'
        assert prefixes[1].prefix == '53900012'

    def test_audit_data(self):
        self.client.post(self.url, self.post_data)
        audit = logs_service.all()
        assert len(audit) == 1
        assert audit[0].logger == 'audit'
        assert audit[0].level == 'INFO'
        assert audit[0].msg == 'logging in: 53900011@test.com::GS1 Ireland'
        assert audit[0].username == '53900011@test.com'

    def test_m2m_token_ok(self):
        post_data = self.post_data.copy()
        response = self.client.post(self.url, post_data)
        assert response.status_code == 302
        response = self.client.get(response.url)
        member_organisation = response.wsgi_request.user.profile.member_organisation
        member_organisation.login_api_secure = True
        member_organisation.save()
        m2m_token_set = response.wsgi_request.user.auth_token_set.all()
        m2m_token = m2m_token_set[0].digest
        post_data['m2m_token'] = m2m_token
        response = self.client.post(self.url, post_data)
        assert response.status_code == 302
        assert response.url[:16] == '/users/api/auth/'

    def test_m2m_token_empty(self):
        post_data = self.post_data.copy()
        response = self.client.post(self.url, post_data)
        assert response.status_code == 302
        response = self.client.get(response.url)
        member_organisation = response.wsgi_request.user.profile.member_organisation
        member_organisation.login_api_secure = True
        member_organisation.save()
        m2m_token = ''
        post_data['m2m_token'] = m2m_token
        response = self.client.post(self.url, post_data)
        assert response.status_code == 302
        assert response.url == '/login'

    def test_m2m_token_non_secure(self):
        post_data = self.post_data.copy()
        response = self.client.post(self.url, post_data)
        assert response.status_code == 302
        response = self.client.get(response.url)
        member_organisation = response.wsgi_request.user.profile.member_organisation
        assert member_organisation.login_api_secure == False
        m2m_token = ''
        post_data['m2m_token'] = m2m_token
        response = self.client.post(self.url, post_data)
        assert response.status_code == 302
        assert response.url[:16] == '/users/api/auth/'

    def test_m2m_token_wrong(self):
        post_data = self.post_data.copy()
        response = self.client.post(self.url, post_data)
        assert response.status_code == 302
        response = self.client.get(response.url)
        member_organisation = response.wsgi_request.user.profile.member_organisation
        member_organisation.login_api_secure = True
        member_organisation.save()
        auth_token = 'Wrong_token'
        post_data['auth_token'] = auth_token
        response = self.client.post(self.url, post_data)
        assert response.status_code == 302
        assert response.url == '/login'
