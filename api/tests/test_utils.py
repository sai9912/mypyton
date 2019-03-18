from django.contrib.auth.models import Group
from test_plus import TestCase

from api.utils import (
    is_global_organisation,
    get_user_global_organisation,
    get_generic_filtered_queryset,
)
from member_organisations.factories import MemberOrganisationFactory
from member_organisations.models import MemberOrganisationRelation
from products.factories import DimensionUOMFactory
from products.models import DimensionUOM
from users.factories import UserFactory


class UtilsTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_global_organisation(self):
        assert not is_global_organisation(user=self.user)
        group = Group.objects.create(name='GO Admins')
        self.user.groups.add(group)
        assert is_global_organisation(user=self.user)

        assert get_user_global_organisation(self.user) == group


    def test_get_generic_filtered_queryset(self):
        model = DimensionUOM
        instance = DimensionUOMFactory()
        member_organisation = MemberOrganisationFactory()
        self.user.profile.member_organisation = member_organisation
        self.user.profile.save()
        MemberOrganisationRelation.objects.create(
            member_organisation=member_organisation,
            object=instance
        )
        queryset = get_generic_filtered_queryset(model=model, user=self.user)
        assert instance.id in queryset.values_list('id', flat=TestCase)
