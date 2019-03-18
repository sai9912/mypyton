from django.db import models


class ServiceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def get_id_from_code(self, code):
        try:
            item = CountryOfOrigin.objects.get(code=code)
        except Exception as e:
            return None
        return item.id

    def find_by_country(self, country):
        try:
            country_of_origin = CountryOfOrigin.objects.get(name__iexact=country.name)
        except Exception as e:
            return None
        return country_of_origin


class CountryOfOrigin(models.Model):
    code = models.CharField(
        max_length=10,
        db_index=True,
        unique=True,
        null=False
    )
    name = models.CharField(
        max_length=75,
        null=False
    )

    objects = models.Manager()
    service = ServiceManager()

    def __str__(self):
        return '{%s}' % self.name
