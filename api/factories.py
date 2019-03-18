from factory import fuzzy
import factory

class ApiKeyFactory(factory.DjangoModelFactory):
    description = fuzzy.FuzzyText(length=20)
    key = fuzzy.FuzzyText(length=10)

    class Meta:
        model = 'api.ApiKeys'
