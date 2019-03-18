import json
from test_plus import TestCase

from BCM.factories import LanguageFactory as BCMLanguageFactory
from BCM.models import Country
from audit.models import CloudLog
from member_organisations.models import MemberOrganisation
from users.factories import UserFactory
from ..tasks import update_gs1_cloud_product
from ..models import (
    CountryOfOrigin,
    DimensionUOM,
    Language,
    NetContentUOM,
    PackageType,
    TargetMarket,
)
from ..factories import (
    CountryOfOriginFactory,
    DimensionUOMFactory,
    NetContentUOMFactory,
    PackageTypeFactory,
    TargetMarketFactory,
    LanguageFactory,
    ProductFactory,
)
from unittest import skip

class ModelServicesTestCase(TestCase):

    @staticmethod
    def test_get_id_from_code():

        attr = 'get_id_from_code'

        factories = (
            CountryOfOriginFactory,
            DimensionUOMFactory,
            LanguageFactory,
            NetContentUOMFactory,
            PackageTypeFactory,
            TargetMarketFactory,
        )
        # create instances
        for factory in factories:
            factory()

        models = (
            (DimensionUOM, 'code'),
            (CountryOfOrigin, 'code'),
            (Language, 'slug'),
            (NetContentUOM, 'code'),
            (PackageType, 'code'),
            (TargetMarket, 'code'),
        )

        for model_class, field in models:
            instance = model_class.objects.first()
            field_value = getattr(instance, field)
            get_id_from_code = getattr(model_class.service, attr)
            instance_id = get_id_from_code(field_value)
            assert instance_id == instance.id

        for model_class, field in models:
            field_value = 'random_string'
            get_id_from_code = getattr(model_class.service, attr)
            instance_id = get_id_from_code(field_value)
            assert instance_id is None


class TasksTestCase(TestCase):

    def setUp(self):
        country = Country.objects.create(slug='IE', name='Ireland')
        self.member_organisation = MemberOrganisation.objects.create(
            name='GS1IE', slug='gs1ie', is_active=1, country=country,
        )
        self.user = UserFactory()
        self.user.profile.member_organisation = self.member_organisation
        self.user.profile.save()
        self.user.refresh_from_db()
        self.instance = ProductFactory()
        self.instance_original = ProductFactory()
        BCMLanguageFactory(slug='en')

    def test_update_gs1_cloud_product(self):
        response = update_gs1_cloud_product(
            self.instance,
            self.instance_original,
            self.user
        )
        assert response == {'api_response_status': None, 'response_text': None}
        assert not CloudLog.objects.filter(username=self.user.email).exists()

    @skip
    def test_update_gs1_cloud_product_is_active(self):
        self.instance.gs1_cloud_state = 'ACTIVE'
        self.instance.save()
        response = update_gs1_cloud_product(
            self.instance,
            self.instance_original,
            self.user
        )
        assert response['api_response_status'] == 200, response
        data = json.loads(response['response_text'])
        assert data['status'] == 5, response
        cloud_log =  CloudLog.objects.filter(username=self.user.email).first()
        assert cloud_log
        assert cloud_log.key == self.instance.gtin, cloud_log.key

    def test_update_gs1_cloud_product_draft(self):
        self.instance.gs1_cloud_state = 'DRAFT'
        self.instance.save()
        response = update_gs1_cloud_product(
            self.instance,
            self.instance_original,
            self.user
        )
        assert response['info']
        assert not CloudLog.objects.filter(username=self.user.email).exists()

    @skip
    def test_update_gs1_cloud_original_product_is_active(self):
        self.instance.gs1_cloud_state = 'DRAFT'
        self.instance.save()
        self.instance_original.gs1_cloud_state = 'ACTIVE'
        self.instance_original.save()

        response = update_gs1_cloud_product(
            self.instance,
            self.instance_original,
            self.user
        )
        assert response['api_response_status'] == 200, response
        data = json.loads(response['response_text'])
        assert data['status'] == 4
        cloud_log =  CloudLog.objects.filter(username=self.user.email).first()
        assert cloud_log
        assert cloud_log.key == self.instance.gtin, cloud_log.key
