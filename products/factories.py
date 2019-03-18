import string

import factory.fuzzy
import factory
import json
from random import choice
from string import  ascii_letters, digits


class CountryOfOriginFactory(factory.DjangoModelFactory):
    code = factory.fuzzy.FuzzyText()
    name = factory.fuzzy.FuzzyText()

    class Meta:
        model = 'products.CountryOfOrigin'


class DimensionUOMFactory(factory.DjangoModelFactory):
    uom_i18n = factory.LazyFunction(
        lambda: json.dumps(
            {'en': ''.join(choice(ascii_letters + digits) for _ in range(10))})
    )
    abbr = factory.fuzzy.FuzzyText()
    code = factory.fuzzy.FuzzyText()

    class Meta:
        model = 'products.DimensionUOM'


class GtinTargetMarketFactory(factory.DjangoModelFactory):
    product = factory.SubFactory('products.factories.ProductFactory')
    target_market = factory.SubFactory('products.factories.TargetMarketFactory')
    gtin = factory.fuzzy.FuzzyText()

    class Meta:
        model = 'products.GtinTargetMarket'


class LanguageFactory(factory.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText(length=4)
    slug = factory.fuzzy.FuzzyText()

    class Meta:
        model = 'products.Language'


class NetContentUOMFactory(factory.DjangoModelFactory):
    uom_i18n = factory.LazyFunction(
        lambda: json.dumps(
            {'en': ''.join(choice(ascii_letters + digits) for _ in range(10))})
    )
    abbr = factory.fuzzy.FuzzyText()
    code = factory.fuzzy.FuzzyText()

    class Meta:
        model = 'products.NetContentUOM'


class PackageLevelFactory(factory.DjangoModelFactory):
    level = factory.fuzzy.FuzzyText()
    unit_descriptor = factory.fuzzy.FuzzyText()

    class Meta:
        model = 'products.PackageLevel'


class PackageTypeFactory(factory.DjangoModelFactory):
    member_organisation = factory.SubFactory(
        'member_organisations.factories.MemberOrganisationFactory'
    )
    code = factory.fuzzy.FuzzyText()
    type_i18n = factory.LazyFunction(
        lambda: json.dumps(
            {'en': ''.join(choice(ascii_letters + digits) for _ in range(10))})
    )
    description_i18n = factory.LazyFunction(
        lambda: json.dumps(
            {'en': ''.join(choice(ascii_letters + digits) for _ in range(10))})
    )
    image_path = factory.fuzzy.FuzzyText()

    class Meta:
        model = 'products.PackageType'


class ProductFactory(factory.DjangoModelFactory):
    owner = factory.SubFactory('users.factories.UserFactory')
    company_organisation = factory.SubFactory(
        'company_organisations.factories.CompanyOrganisationFactory'
    )
    member_organisation = factory.SubFactory(
        'member_organisations.factories.MemberOrganisationFactory'
    )
    package_level = factory.SubFactory(
        'products.factories.PackageLevelFactory'
    )
    package_type = factory.SubFactory(
        'products.factories.PackageTypeFactory'
    )
    depth_uom = factory.SubFactory(
        'products.factories.DimensionUOMFactory'
    )
    width_uom = factory.SubFactory(
        'products.factories.DimensionUOMFactory'
    )
    height_uom = factory.SubFactory(
        'products.factories.DimensionUOMFactory'
    )
    net_content_uom = factory.SubFactory(
        'products.factories.NetContentUOMFactory'
    )
    gross_weight_uom = factory.SubFactory(
        'products.factories.WeightUOMFactory'
    )
    net_weight_uom = factory.SubFactory(
        'products.factories.WeightUOMFactory'
    )
    country_of_origin = factory.SubFactory(
        'products.factories.CountryOfOriginFactory'
    )
    target_market = factory.SubFactory(
        'products.factories.TargetMarketFactory'
    )
    language = factory.SubFactory(
        'products.factories.LanguageFactory'
    )

    gtin = factory.fuzzy.FuzzyText(chars=string.digits)

    class Meta:
        model = 'products.Product'


class ProductImageFactory(factory.DjangoModelFactory):
    product = factory.SubFactory('products.factories.ProductFactory')
    language = factory.SubFactory('products.factories.LanguageFactory')
    image = factory.django.ImageField()

    class Meta:
        model = 'products.ProductImage'


class SubProductFactory(factory.DjangoModelFactory):
    product = factory.SubFactory('products.factories.ProductFactory')
    sub_product = factory.SubFactory('products.factories.ProductFactory')

    class Meta:
        model = 'products.SubProduct'


class TargetMarketFactory(factory.DjangoModelFactory):
    code = factory.fuzzy.FuzzyText()
    market = factory.fuzzy.FuzzyText()

    class Meta:
        model = 'products.TargetMarket'


class WeightUOMFactory(factory.DjangoModelFactory):
    uom_i18n = factory.LazyFunction(
        lambda: json.dumps(
            {'en': ''.join(choice(ascii_letters + digits) for _ in range(10))})
    )
    abbr = factory.fuzzy.FuzzyText()
    code = factory.fuzzy.FuzzyText()

    class Meta:
        model = 'products.WeightUOM'
