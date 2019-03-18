import random
import factory


class CompanyOrganisationFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(lambda: random.randint(1000000, 10000000))
    member_organisation = factory.SubFactory(
        'member_organisations.factories.MemberOrganisationFactory'
    )
    country = factory.SubFactory('BCM.factories.CountryFactory')

    class Meta:
        model = 'company_organisations.CompanyOrganisation'
