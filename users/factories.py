from django.conf import settings
import factory.fuzzy
import factory
from django.db.models.signals import post_save


__all__ = (
    'UserFactory',
    'ProfileFactory',
)


class UserFactory(factory.django.DjangoModelFactory):

    username = factory.Faker('name')

    class Meta:
        model = settings.AUTH_USER_MODEL


@factory.django.mute_signals(post_save)
class ProfileFactory(factory.DjangoModelFactory):

    user = factory.SubFactory(UserFactory)
    member_organisation = factory.SubFactory(
        'member_organisations.factories.MemberOrganisationFactory'
    )
    company_organisation = factory.SubFactory(
        'company_organisations.factories.CompanyOrganisationFactory'
    )
    product_active_prefix = factory.SubFactory(
        'prefixes.factories.PrefixFactory'
    )

    class Meta:
        model = 'users.Profile'


class AuthTokenFactory(factory.DjangoModelFactory):

    user = factory.SubFactory(UserFactory)

    class Meta:
        model = 'knox.AuthToken'

