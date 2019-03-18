import string

import factory.fuzzy
import factory



class PrefixStatusFactory(factory.DjangoModelFactory):

    name = factory.Faker('name')

    class Meta:
        model = 'prefixes.PrefixStatus'


class PrefixFactory(factory.DjangoModelFactory):
    prefix = factory.fuzzy.FuzzyText(length=10 , chars=string.digits)

    status = factory.SubFactory(PrefixStatusFactory)
    member_organisation = factory.SubFactory(
        'member_organisations.factories.MemberOrganisationFactory'
    )
    company_organisation = factory.SubFactory(
        'company_organisations.factories.CompanyOrganisationFactory'
    )

    class Meta:
        model = 'prefixes.Prefix'

