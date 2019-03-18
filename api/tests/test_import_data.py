import os

from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from knox.models import AuthToken
from rest_framework.test import APITestCase

from BCM.models import Country
from member_organisations.models import MemberOrganisation, MemberOrganisationUser


class ProductListAPITestCase(APITestCase):
    fixtures = (
        '../../fixtures/BCM_country.json',
        '../../fixtures/prefixes.prefixstatuses.json',
    )

    @classmethod
    def setUpTestData(cls):
        cls.mo = MemberOrganisation.objects.create(
            name='gs1ie', country=Country.objects.get(slug='IE')
        )

        cls.mo_user = User.objects.create(
            username='test@test.com',
            email='test@test.com',
            is_active=True
        )
        cls.mo_user.profile.member_organisation = cls.mo
        cls.mo_user.save()

        cls.mo_admin = MemberOrganisationUser.objects.create(
            user=cls.mo_user, organization=cls.mo, is_admin=True
        )

    def setUp(self):
        self.token = AuthToken.objects.create(User.objects.get(username='test@test.com'))
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_import(self):
        """
        Each next step depends on the previous data,
        therefore we test all files in one case
        """

        # 1. Companies
        source_file_path = os.path.join(
            settings.BASE_DIR,
            'deployment/test_files/mo_import_companies.xlsx'
        )
        import_file = open(source_file_path, 'rb')
        response = self.client.put(
            reverse('api:company-upload', args=(self.mo.slug,)),
            {'import_file': import_file},
            format='multipart'
        )
        self.assertEqual(response.data['upload_details']['success_count'], 10)

        # 2. Prefixes
        source_file_path = os.path.join(
            settings.BASE_DIR,
            'deployment/test_files/mo_import_prefixes.xlsx'
        )
        import_file = open(source_file_path, 'rb')
        response = self.client.put(
            reverse('api:prefixes-upload', args=(self.mo.slug,)),
            {'import_file': import_file},
            format='multipart'
        )
        self.assertEqual(response.data['upload_details']['success_count'], 10)

        # 3. Users
        source_file_path = os.path.join(
            settings.BASE_DIR,
            'deployment/test_files/mo_import_users.xlsx'
        )
        import_file = open(source_file_path, 'rb')
        response = self.client.put(
            reverse('api:user-upload', args=(self.mo.slug,)),
            {'import_file': import_file},
            format='multipart'
        )
        self.assertEqual(response.data['upload_details']['success_count'], 10)
