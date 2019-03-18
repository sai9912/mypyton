from . import TestCase
from services import prefix_service
from products.models.package_level import PackageLevel
from products.models.package_type import PackageType


class PageAddProductPackageTypeTestCase(TestCase):
    url = '/products/add_product_package_type/'
    user = None

    def setUp(self):
        self.user = self.setUp_createAccount()

        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.prefix == '53900011'
        prefix_service.make_active(user=self.user, prefix=prefix.prefix)
        package_level = PackageLevel(
            id='70',
            level='Consumer Unit (Base Unit/Each) e.g. bottle of beer',
            unit_descriptor='BASE_UNIT_OR_EACH'
        )
        package_level.save()
        response = self.client.post('/products/add/', {'package_level': '70'})
        assert response.status_code == 302
        assert response.url == '/products/add_product_package_type/'

    def test_page_exist(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'Base Unit / Each')

    def test_select_tray_press_next(self):
        member_organisation = self.user.member_organisations_memberorganisation.first()
        package_type = PackageType(
            id=14,
            type_i18n='{"en": "Tray"}',
            code='PU',
            member_organisation=member_organisation,
            ui_enabled=1,
        )
        package_type.save()
        response = self.client.post(
            self.url,
            {
                'package_type': '14',
                'bar_placement': '/static/products/site/wizard/proddesc/BG.png'
            }
        )
        assert response.status_code == 302
        assert response.url == '/products/add/details/'
