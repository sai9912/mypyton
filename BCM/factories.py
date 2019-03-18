import factory.fuzzy
import factory


class CountryFactory(factory.django.DjangoModelFactory):

    name = factory.Faker('city')
    slug = factory.Faker('city')

    class Meta:
        model = 'BCM.Country'


class LanguageFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText()
    slug = factory.fuzzy.FuzzyText()

    class Meta:
        model = 'BCM.Language'


class LanguageByCountryFactory(factory.django.DjangoModelFactory):
    country = factory.SubFactory(CountryFactory)
    language = factory.SubFactory(LanguageFactory)

    class Meta:
        model = 'BCM.LanguageByCountry'
