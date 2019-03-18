from test_plus import TestCase

from company_organisations.factories import CompanyOrganisationFactory
from prefixes.models import Prefix
from products.factories import ProductFactory
from users.factories import UserFactory, ProfileFactory
from ..factories import PrefixFactory, PrefixStatusFactory


class PrefixModelTestCase(TestCase):

    def setUp(self):
        self.prefix = PrefixFactory()

    def test_get_queryset(self):
        assert Prefix.service.all() == None
        co = self.prefix.company_organisation
        self.prefix.save()
        user = ProfileFactory(company_organisation=co).user
        assert Prefix.service.all(user=user).first() == self.prefix

    def test_check_instance(self):

        prefix_status = PrefixStatusFactory()
        error = None
        try:
            Prefix.service.check_instance(prefix_status)
        except ValueError as e:
            error = e
        assert error is not None

        assert Prefix.service.check_instance(self.prefix)

    def test_create(self):

        user = UserFactory()
        prefix = Prefix.service.create(user=user)

        assert prefix

    def test_save(self):
        error = None
        user = UserFactory()
        try:
            Prefix.service.save(self.prefix, user=UserFactory())
        except ValueError as e:
            error = e
        assert error
        user.profile.company_organisation = self.prefix.company_organisation
        user.profile.save()
        Prefix.service.save(self.prefix, user=user)

    def test_delete(self):
        Prefix.service.delete(self.prefix)
        assert not Prefix.objects.filter(id=self.prefix.id).exists()
        user = UserFactory()
        prefix = PrefixFactory()
        user.profile.company_organisation = prefix.company_organisation
        user.profile.save()

        Prefix.service.delete(prefix, user=user)

        assert not Prefix.objects.filter(id=prefix.id).exists()

        prefix = PrefixFactory()
        error = None

        try:
            Prefix.service.delete(prefix, user=user)
        except ValueError as e:
            error = e
        assert error

    def test_find_item(self):
        user = UserFactory()
        user.profile.company_organisation = self.prefix.company_organisation
        user.profile.save()
        prefix = Prefix.service.find_item(
            user=user,
            company_organisation=user.profile.company_organisation
        )
        assert prefix == self.prefix

        prefix = Prefix.service.find_item(
            user=user,
            wrong_field=user.profile.company_organisation
        )
        assert prefix is None

    def test_make_get_active(self):
        assert Prefix.service.get_active() is None
        str_prefix = self.prefix.prefix
        user = UserFactory()
        Prefix.service.make_active(user=user, prefix=str_prefix)

        user.refresh_from_db()
        assert Prefix.service.get_active(user) == self.prefix

    def test_find_suspended(self):
        prefix_status = PrefixStatusFactory(is_suspended=True)
        user = ProfileFactory(
            company_organisation=self.prefix.company_organisation
        ).user
        self.prefix.status = prefix_status
        self.prefix.save()

        assert Prefix.service.find_suspended(user).first() == self.prefix

    def test_find_transferred(self):
        prefix_status = PrefixStatusFactory(is_transferred=True)
        user = ProfileFactory(
            company_organisation=self.prefix.company_organisation
        ).user
        self.prefix.status = prefix_status
        self.prefix.save()

        assert Prefix.service.find_transferred(user).first() == self.prefix

    def test_get_mo_and_co_methods(self):
        assert self.prefix.get_member_organisation() == self.prefix.member_organisation
        assert self.prefix.get_company_organisation() == self.prefix.company_organisation

    def test_is_upc(self):
        self.prefix.prefix = '1' + self.prefix.prefix[1:]
        self.prefix.save()
        assert not self.prefix.is_upc()

        self.prefix.prefix = '0000123'
        self.prefix.save()
        assert self.prefix.is_upc()

    def test_get_available_gtins(self):
        gtin = '08339355934961'
        product = ProductFactory(gtin=gtin)
        answer = self.prefix.get_available_gtins(products=[product])
        assert gtin not in answer

    def test_get_available_glns(self):
        uuid = '06504783863950'
        co = CompanyOrganisationFactory(uuid=uuid, gln='10')
        answer = self.prefix.get_available_glns(locations=[co])
        assert uuid not in answer, answer
