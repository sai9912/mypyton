import factory


class MemberOrganisationFactory(factory.django.DjangoModelFactory):

    country = factory.SubFactory('BCM.factories.CountryFactory')

    class Meta:
        model = 'member_organisations.MemberOrganisation'


class MemberOrganisationUserFactory(factory.DjangoModelFactory):
    organization = factory.SubFactory(
        'member_organisations.factories.MemberOrganisationFactory'
    )
    user = factory.SubFactory('auth.User')

    class Meta:
        model = 'member_organisations.MemberOrganisationUser'


class ProductTemplateFactory(factory.DjangoModelFactory):
    package_level = factory.SubFactory('products.factories.PackageLevelFactory')
    member_organisation = factory.SubFactory(
        'member_organisations.factories.MemberOrganisationFactory'
    )

    class Meta:
        model = 'member_organisations.ProductTemplate'


class ProductAttributeFactory(factory.DjangoModelFactory):
    member_organisation = factory.SubFactory(
        'member_organisations.factories.MemberOrganisationFactory'
    )

    class Meta:
        model = 'member_organisations.ProductAttribute'


class ProductPackagingFactory(factory.DjangoModelFactory):
    member_organisation = factory.SubFactory(
        'member_organisations.factories.MemberOrganisationFactory'
    )
    package_level = factory.SubFactory('products.factories.PackageTypeFactory')

    class Meta:
        model = 'member_organisations.ProductPackaging'


# class M2MTokenFactory(factory.DjangoModelFactory):
#     token = factory.SubFactory(
#         ''
#     )
#
#     class Meta:
#         model = 'member_organisations.M2MToken'
