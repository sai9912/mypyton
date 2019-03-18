from django.contrib.auth.models import User, Group
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from BCM.models import Country
from company_organisations.models import CompanyOrganisation
from member_organisations.models import MemberOrganisation
from prefixes.models import Prefix


class GenericTestCase:
    @classmethod
    def setUpTestData(cls):
        country = Country(slug='IE', name='Ireland')
        country.save()
        cls.member_organisation = MemberOrganisation(name='GS1', slug='gs1', is_active=1, country=country)
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
        cls.profile = cls.user.profile
        cls.profile.member_organisation_id = 1
        cls.profile.save()
        cls.token = cls.get_token_from_data({'username': 'test', 'password': 'password'})

    @classmethod
    def get_new_company_data(cls):
        data = {
            'uuid': '53900012',
            'company': 'GS1 Ireland',
            'name': 'GS1 Ireland',
            'country': 'IE'
        }
        return data

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
            "starting_from": "5390001100003",
            "company_organisation": cls.company_orgnisation,
            "member_organisation": cls.member_organisation,
            "description": "Some description prefix"
        }
        generic_data.update(data)
        prefix = Prefix.objects.create(**generic_data)
        cls.user.profile.product_active_prefix = prefix
        cls.user.profile.save()
        return prefix

    @classmethod
    def get_changed_prefix_data(cls):
        changed_prefix_data = {
            "prefix": "723372372",
            # "is_active": True,
            "is_suspended": False,
            "is_special": "",
            "starting_from": "5390001100003",
            "company_organisation": cls.company_orgnisation,
            "member_organisation": cls.member_organisation,
            "description": "Changed prefix data"
        }
        return changed_prefix_data

    @classmethod
    def get_new_user_data(cls):
        new_user_data = {
            'uid': 'abba-123',
            'email': 'newuser@test.com',
            'first_name': 'newuser',
            'last_name': '',
            'advanced_tab': True,
            'agreed': True,
            'agreed_date': '2018-01-01T00:00',
            'agreed_version': '1.0'
        }
        return new_user_data

    def check_fields(self, data):
        excludes = [
            'member_organisation', 'member_organisation_id', 'is_staff', 'is_superuser',
            'gtins_capacity',
        ]
        for key in data:
            if key in excludes:
                continue
            if key not in self.fields:
                return False
        for field in self.fields:
            if not field in data.keys():
                return False
        return True


class CompanyMatchGS1CloudAPITestCase(GenericTestCase, APITestCase):
    fields = [
        'uuid', 'name', 'country', 'company', 'street1', 'street2', 'city', 'state', 'zip',
        'phone', 'gln', 'vat', 'credit_points_balance', 'active', 'prefix_override',
        'gln_capability', 'member_organisation',
    ]

    def setUp(self):
        super(CompanyMatchGS1CloudAPITestCase, self).setUp()
        self.prefix = self.create_sample_prefix()

    def test_Companies_List(self):
        # GET /api/v1/companies/
        response = self.client.get('/api/v1/companies/')
        assert response.status_code == 200
        assert len(response.data) == 1
        assert self.check_fields(response.data[0])

    def test_Company_Details(self):
        # GET /api/v1/companies/{uuid}/
        response = self.client.get('/api/v1/companies/53900011/')
        assert response.status_code == 200
        assert self.check_fields(response.data)

    def test_Add_Company(self):
        # POST /api/v1/companies/
        new_company_data = self.get_new_company_data()
        response = self.client.get('/api/v1/companies/')
        assert response.status_code == 200
        assert len(response.data) == 1
        response = self.client.post('/api/v1/companies/', new_company_data)
        assert response.status_code == 201
        assert self.check_fields(response.data)
        response = self.client.get('/api/v1/companies/')
        assert response.status_code == 200
        assert len(response.data) == 2
        assert self.check_fields(response.data[0])
        assert self.check_fields(response.data[1])

    def test_Modify_Company(self):
        # PUT /api/v1/companies/{uuid}/
        new_company_data = self.get_new_company_data()
        response = self.client.put('/api/v1/companies/53900011/', new_company_data)
        assert response.status_code == 200
        assert self.check_fields(response.data)
        response = self.client.get('/api/v1/companies/53900012/')
        assert response.status_code == 200
        assert self.check_fields(response.data)

    def test_Edit_Company(self):
        # PATCH /api/v1/companies/{uuid}/
        response = self.client.patch('/api/v1/companies/53900011/', {'company': 'New company name'})
        assert response.status_code == 200
        assert self.check_fields(response.data)
        assert response.data['company'] == 'New company name'

    def test_Delete_Company(self):
        # DELETE /api/v1/companies/{uuid}/
        response = self.client.delete('/api/v1/companies/53900011/')
        assert response.status_code == 204


class PrefixMatchGS1CloudAPITestCase(GenericTestCase, APITestCase):
    fields = ['prefix', 'range', 'status', 'is_suspended', 'is_special', 'starting_from',
              'starting_from_gln', 'member_organisation', 'company_organisation', 'description',
              'gtins_available', 'gtins_allocated']

    def setUp(self):
        super(PrefixMatchGS1CloudAPITestCase, self).setUp()
        self.prefix = self.create_sample_prefix()

    def test_Prefixes_List(self):
        # GET /api/v1/prefixes/
        response = self.client.get('/api/v1/prefixes/')
        assert response.status_code == 200
        assert len(response.data) == 1
        assert self.check_fields(response.data[0])

    def test_Prefix_Details(self):
        # GET /api/v1/prefixes/{prefix}/
        response = self.client.get('/api/v1/prefixes/723372372/')
        assert response.status_code == 200
        assert self.check_fields(response.data)

    # TODO
    def test_Add_Prefix(self):
        # POST /api/v1/companies/{uuid}/prefixes/
        # New prefix should be created via *Company API* not via Prefix API !!!
        # changed_data = self.get_changed_prefix_data()
        # response = self.client.post('/api/v1/prefixes/', changed_data)
        assert True

    def test_Modify_Prefix(self):
        # PUT /api/v1/prefixes/{prefix}/
        changed_data = self.get_changed_prefix_data()
        response = self.client.put('/api/v1/prefixes/723372372/', changed_data)
        assert response.status_code == 200
        assert self.check_fields(response.data)
        assert response.data['description'] == changed_data['description']

    def test_Edit_Prefix(self):
        # PATCH /api/v1/prefixes/{prefix}/
        response = self.client.patch(
            '/api/v1/prefixes/723372372/', {'description': 'New description'}
        )
        assert response.status_code == 200
        assert self.check_fields(response.data)
        assert response.data['description'] == 'New description'

    def test_Delete_Prefix(self):
        # DELETE /api/v1/prefixes/{prefix}/
        response = self.client.delete('/api/v1/prefixes/723372372/')
        assert response.status_code == 204


class UserMatchGS1CloudAPITestCase(GenericTestCase, APITestCase):
    fields = [
        'id', 'uid', 'email', 'first_name', 'last_name', 'member_organisation',
        'company_organisation', 'advanced_tab', 'agreed', 'agreed_date', 'agreed_version',
        'product_active_prefix', 'language', 'agreed_barcode_disclaimer', 'barcode_disclaimer',
        'simplified_barcode_generation',
    ]

    @classmethod
    def setUpClass(cls):
        super(UserMatchGS1CloudAPITestCase, cls).setUpClass()
        cls.profile.uid = 'test-123'
        cls.profile.save()

    def setUp(self):
        super(UserMatchGS1CloudAPITestCase, self).setUp()
        self.prefix = self.create_sample_prefix()

    def test_Users_List(self):
        # GET /api/v1/users/
        response = self.client.get('/api/v1/users/')
        assert response.status_code == 200
        assert len(response.data) == 1
        assert self.check_fields(response.data[0])

    def test_User_Details(self):
        # GET /api/v1/users/{uid}/
        response = self.client.get('/api/v1/users/test-123/')
        assert response.status_code == 200
        assert self.check_fields(response.data)

    def test_Add_User(self):
        # POST /api/v1/companies/{{uuid}}/users/
        data = {'uid': 'abc123', 'email': 'test@test.com'}
        response = self.client.post('/api/v1/companies/53900011/users/', data)
        assert response.status_code == 201
        assert self.check_fields(response.data)

    def test_Modify_User(self):
        # PUT /api/v1/users/{uid}/
        new_user_data = self.get_new_user_data()
        response = self.client.put('/api/v1/users/test-123/', new_user_data)
        assert response.status_code == 200
        assert self.check_fields(response.data)
        response = self.client.get('/api/v1/users/test-123/')
        assert response.status_code == 200
        assert self.check_fields(response.data)
        assert response.data['email'] == new_user_data['email']
        assert response.data['first_name'] == new_user_data['first_name']

    def test_Edit_User(self):
        # PATCH /api/v1/users/{uuid}/
        response = self.client.patch('/api/v1/users/test-123/', {'email': 'new_email@test.com'})
        assert response.status_code == 200
        assert self.check_fields(response.data)
        assert response.data['email'] == 'new_email@test.com'
        response = self.client.patch('/api/v1/users/test-123/', {'agreed': True,
                                                                 'agreed_version': 'v1.0',
                                                                 'agreed_date': '2018-01-01T00:00:00Z'})
        assert response.status_code == 200
        assert self.check_fields(response.data)
        assert response.data['agreed']
        assert response.data['agreed_version'] == 'v1.0'
        assert response.data['agreed_date'] == '2018-01-01T00:00:00Z'

    def test_Delete_User(self):
        # DELETE /api/v1/users/{uuid}/
        response = self.client.delete('/api/v1/users/test-123/')
        assert response.status_code == 204
