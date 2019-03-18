import os
import json
from django.test import TestCase

from barcodes.models import Label
from services import prefix_service
from BCM.models import Country
from member_organisations.models import MemberOrganisation
from django.contrib.auth.models import User
from django.conf import settings
from unittest import skip
import doctest
from . import barcode
from . import utilities, models
from .printers import (
    BarcodeManager,
    BarcodeManagerISBN,
    BarcodeManagerITF,
    BarcodePrinter,
    BarcodePrinterEAN13,
    BarcodePrinterISBN13,
    BarcodePrinterISBN13AddOn,
    BarcodePrinterITF14,
    BarcodePrinterRSS14,
    BarcodePrinterUPCA,
)


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(barcode))
    tests.addTests(doctest.DocTestSuite(utilities))
    tests.addTests(doctest.DocTestSuite(models))
    tests.addTests(doctest.DocTestSuite(BarcodeManager))
    tests.addTests(doctest.DocTestSuite(BarcodeManagerISBN))
    tests.addTests(doctest.DocTestSuite(BarcodeManagerITF))
    tests.addTests(doctest.DocTestSuite(BarcodePrinter))
    tests.addTests(doctest.DocTestSuite(BarcodePrinterEAN13))
    tests.addTests(doctest.DocTestSuite(BarcodePrinterISBN13))
    tests.addTests(doctest.DocTestSuite(BarcodePrinterISBN13AddOn))
    tests.addTests(doctest.DocTestSuite(BarcodePrinterITF14))
    tests.addTests(doctest.DocTestSuite(BarcodePrinterRSS14))
    tests.addTests(doctest.DocTestSuite(BarcodePrinterUPCA))
    return tests


class BarcodesPreviewTestCase(TestCase):
    url_ean13 = '/barcodes/ajax/EAN13/05390001200000/preview/'
    url_itf14 = '/barcodes/ajax/ITF14/05390001200000/preview/'
    url_upca = '/barcodes/ajax/UPCA/05390001200000/preview/'
    user = None

    def setUp_createAccount(self):
        country = Country(slug='BE', name='Belgium')
        country.save()
        member_organisation = MemberOrganisation(name='GS1',
                                                 slug='gs1',
                                                 is_active=1,
                                                 country=country)
        member_organisation.save()
        url = '/API/v0/AccountCreateOrUpdate/'
        data = {
            'uuid': '53900011',
            'email': '53900011@test.com',
            'company_prefix': '53900011,53900012',
            'company_name': 'GS1 Ireland',
            'credits': '39:20,43:100,44:100',
            'txn_ref': 'Test_1,Test_3,Test_2',
            'member_organisation': 'gs1'
        }
        response = self.client.post(url, data)
        assert response.status_code == 302
        self.client.get(response.url)
        self.user = User.objects.get(email='53900011@test.com')
        assert self.user is not None
        self.user.profile.agreed = True
        self.user.save()
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        prefix_service.make_active(user=self.user, prefix=prefix.prefix)

    def setUp(self):
        self.setUp_createAccount()

    def test_page_exits(self):
        response = self.client.get(self.url_ean13)
        assert response.status_code == 200
        self.assertContains(response,
                            'The family of EAN/UPC barcodes are used to '
                            'represent GTINs')

    def test_not_agreed(self):
        self.user.profile.member_organisation.gs1_terms_enable = True
        self.user.profile.member_organisation.save()
        self.user.profile.agreed = False
        self.user.profile.save()
        response = self.client.get(self.url_ean13)
        self.assertEquals(
            response.status_code,
            302
        )
        self.assertEquals(
            response.url,
            '/users/user_agreement_required?next=%s' % self.url_ean13
        )

    def test_check_wrong_kind(self):
        url = '/barcodes/ajax/EAN14/05390001200000/preview/'
        response = self.client.get(url)
        assert response.status_code == 200
        _key, content_type = response._headers['content-type']
        assert content_type == 'application/json'
        data = json.loads(response.content)
        assert not data['success']
        self.assertEquals(
            data['msg'],
            'Wrong barcode kind'
        )

    def test_check_wrong_gtin(self):
        wrong_gtins = [ '/barcodes/ajax/EAN13/0539000120000/preview/', # 13 digits
                        '/barcodes/ajax/EAN13/0539000120000A/preview/' ] # with symbol
        for url in wrong_gtins:
            response = self.client.get(url)
            assert response.status_code == 200
            _key, content_type = response._headers['content-type']
            assert content_type == 'application/json'
            data = json.loads(response.content)
            assert not data['success']
            self.assertEquals(
                data['msg'],
                'You entered a non valid GTIN number'
            )

    def test_barcode_image(self):
        response = self.client.get(self.url_ean13)
        assert response.status_code == 200
        self.assertContains(
            response,
            f'src="/static/bcgen/{self.user.id}/EAN13/05390001200000_preview.jpg"'
        )
        
    @skip
    def test_create_files(self):
        path_ps = os.path.join(
            settings.BARCODES_FILES_PATH,
            f'{self.user.id}',
            'EAN13',
            '05390001200000_preview.ps'
        )
        path_jpg = os.path.join(
            settings.BARCODES_FILES_PATH,
            f'{self.user.id}',
            'EAN13',
            '05390001200000_preview.jpg'
        )
        if os.path.exists(path_ps):
            os.unlink(path_ps)
        if os.path.exists(path_jpg):
            os.unlink(path_jpg)
        assert not os.path.exists(path_ps)
        assert not os.path.exists(path_jpg)
        response = self.client.get(self.url_ean13)
        assert response.status_code == 200
        assert os.path.exists(path_ps)
        assert os.path.exists(path_jpg)

    @skip
    def test_cache(self):
        path_ps = os.path.join(
            settings.BARCODES_FILES_PATH,
            f'{self.user.id}',
            'EAN13',
            '05390001200000_preview.ps'
        )
        path_jpg = os.path.join(
            settings.BARCODES_FILES_PATH,
            f'{self.user.id}',
            'EAN13',
            '05390001200000_preview.jpg'
        )

        if os.path.exists(path_ps):
            os.unlink(path_ps)
        if os.path.exists(path_jpg):
            os.unlink(path_jpg)
        assert not os.path.exists(path_ps)
        assert not os.path.exists(path_jpg)
        response = self.client.get(self.url_ean13)
        assert response.status_code == 200
        assert os.path.exists(path_ps)
        assert os.path.exists(path_jpg)
        os.unlink(path_ps)
        assert not os.path.exists(path_ps)
        response = self.client.get(self.url_ean13)
        assert response.status_code == 200
        assert not os.path.exists(path_ps)
        assert os.path.exists(path_jpg)

    def test_barcode_image_itf14(self):
        response = self.client.get(self.url_itf14)
        assert response.status_code == 200
        self.assertContains(
            response,
            'src="/static/bcgen/1/ITF14/05390001200000_preview.jpg"'
        )

    def test_barcode_image_upca(self):
        response = self.client.get(self.url_upca)
        assert response.status_code == 200
        self.assertContains(
            response,
            f'src="/static/bcgen/{self.user.id}/UPCA/05390001200000_preview'
            '.jpg"'
        )


@skip('Skipped for CircleCI pass')
class BarcodesDownloadTestCase(TestCase):
    url_png = '/barcodes/ajax/EAN13/05390001100065/raster/?size=1.00&bwr=0' \
              '.0000&resolution=300+dpi&file_type=png&ps_type=win&label_type' \
              '=&rqz=y'
    url_gif = '/barcodes/ajax/EAN13/05390001100065/raster/?size=1.00&bwr=0' \
              '.0000&resolution=300+dpi&file_type=gif&ps_type=win&label_type' \
              '=&rqz=y'
    url_jpg = '/barcodes/ajax/EAN13/05390001100065/raster/?size=1.00&bwr=0' \
              '.0000&resolution=300+dpi&file_type=jpg&ps_type=win&label_type' \
              '=&rqz=y'
    url_ps_win = '/barcodes/ajax/EAN13/05390001100065/ps/?size=1.00&bwr=0' \
                 '.0000&resolution=300+dpi&file_type=jpg&ps_type=win' \
                 '&label_type=&rqz=y'
    url_ps_mac = '/barcodes/ajax/EAN13/05390001100065/ps/?size=1.00&bwr=0' \
                 '.0000&resolution=300+dpi&file_type=jpg&ps_type=mac' \
                 '&label_type=&rqz=y'

    def setUp(self):
        country = Country(slug='BE', name='Belgium')
        country.save()
        member_organisation = MemberOrganisation(name='GS1',
                                                 slug='gs1',
                                                 is_active=1,
                                                 country=country)
        member_organisation.save()
        url = '/API/v0/AccountCreateOrUpdate/'
        data = {
            'uuid': '53900011',
            'email': '53900011@test.com',
            'company_prefix': '53900011,53900012',
            'company_name': 'GS1 Ireland',
            'credits': '39:20,43:100,44:100',
            'txn_ref': 'Test_1,Test_3,Test_2',
            'member_organisation': 'gs1'
        }
        response = self.client.post(url, data)
        assert response.status_code == 302
        self.client.get(response.url)
        user = User.objects.get(email='53900011@test.com')
        user.profile.agreed = True
        user.save()
        prefix = prefix_service.find_item(user=user, prefix='53900011')
        assert prefix.prefix == '53900011'
        prefix_service.make_active(user=user, prefix=prefix.prefix)

    def test_png(self):
        response = self.client.get(self.url_png)
        assert response.status_code == 200
        key, value = response._headers['content-type']
        assert value == 'image/png', value
        key, value = response._headers['content-length']
        assert value == '5606', value

    def test_gif(self):
        response = self.client.get(self.url_gif)
        assert response.status_code == 200
        key, value = response._headers['content-type']
        assert value == 'image/gif', value
        key, value = response._headers['content-length']
        assert value == '16598', value

    def test_jpg(self):
        response = self.client.get(self.url_jpg)
        assert response.status_code == 200
        key, value = response._headers['content-type']
        assert value == 'image/jpeg', value
        key, value = response._headers['content-length']
        assert value == '29543', value

    def test_ps_win(self):
        response = self.client.get(self.url_ps_win)
        assert response.status_code == 200
        key, value = response._headers['content-type']
        assert value == 'application/postscript', value
        key, value = response._headers['content-length']
        assert value == '80620', value

    def test_ps_mac(self):
        response = self.client.get(self.url_ps_mac)
        assert response.status_code == 200
        key, value = response._headers['content-type']
        assert value == 'application/postscript', value
        key, value = response._headers['content-length']
        assert value == '33408', value


class BarcodeGenerateTestCase(TestCase):

    def setUp(self):
        self.valid_urls = [
            f'/barcodes/ajax/{bc_kind}/{gtin}/generate/'
            for bc_kind, gtin in [
                ('EAN13', '00012345678905',),
                ('ITF14', '00012345678905',),
            ]
        ]
        self.invalid_urls = [
            f'/barcodes/ajax/{bc_kind}/{gtin}/generate/'
            for bc_kind, gtin in [
                ('Random', ''.join(str(x) for x in range(14, 28)),),
            ]
        ]
        self.user = User.objects.create(email='root@root.ru', username='root')
        profile = self.user.profile
        profile.agreed = True
        profile.save()
        self.client.force_login(self.user)

    def test_invalid_url(self):
        for url in self.invalid_urls:
            response = self.client.get(url)
            self.assertEquals(
                response.status_code,
                200
            )
            data = json.loads(response.content)
            assert not data['success']
            self.assertEquals(
                data['msg'],
                'Wrong barcode kind'
            )

    def test_valid_url_method_post(self):
        for i, url in enumerate(self.valid_urls):
            response = self.client.get(url)
            self.assertEquals(
                response.status_code,
                200
            )
            self.assertContains(
                response,
                self.get_text(i)
            )

    @staticmethod
    def get_text(i):
        if i == 0:  # EAN13
            return 'The family of EAN/UPC barcodes are used to represent'

        if i == 1:  # ITF14
            return 'The ITF 14 symbol is used for trade items not passing the'


class BarcodeImageDownloadTestCase(TestCase):

    def setUp(self):
        self.valid_urls = [
            f'/barcodes/ajax/{bc_kind}/{gtin}/{dl_type}/?label_type=code'
            for bc_kind, gtin, dl_type in [
                ('EAN13', '00012345678905', 'raster'),
                ('ITF14', '00012345678905', 'ps'),
                ('ITF14', '00012345678905', 'raster'),
            ]
        ]
        self.invalid_urls = [
            f'/barcodes/ajax/{bc_kind}/{gtin}/{dl_type}/'
            for bc_kind, gtin, dl_type in [
                ('Random', ''.join(str(x) for x in range(14, 28)), 'raster'),
            ]
        ]
        self.user = User.objects.create(email='root@root.ru', username='root')
        profile = self.user.profile
        profile.agreed = True
        profile.save()
        self.client.force_login(self.user)

    def test_invalid_urls(self):
        for url in self.invalid_urls:
            response = self.client.get(url)
            self.assertEquals(
                response.status_code,
                200
            )
            data = json.loads(response.content)
            assert not data['success']
            self.assertEquals(
                data['msg'],
                'Wrong barcode kind'
            )

    @skip('FileNotFoundError: No such file or directory')
    def test_valid_url_method_post(self):
        Label.objects.create(
            code='code',
            short_desc='short_desc',
            description='description',
            src='src',
            template='template',
            rows=1,
            cols=1,
            has_gap=True,
            ratio=1,
            width=1,
            height=1,
        )
        for i, url in enumerate(self.valid_urls):
            response = self.client.get(url)
            self.assertEquals(
                response.status_code,
                200
            )
