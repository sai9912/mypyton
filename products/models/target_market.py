from django.db import models


class ServiceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def get_id_from_code(self, code):
        try:
            item = TargetMarket.objects.get(code=code)
        except Exception as e:
            return None
        return item.id

    def find_by_country(self, country):
        if not country:
            return None

        try:
            target_market = TargetMarket.objects.get(market__iexact=country.name)
        except TargetMarket.DoesNotExist:
            return None
        return target_market

    def find_by_code(self, code):
        try:
            target_market = TargetMarket.objects.get(code=code)
        except TargetMarket.DoesNotExist:
            return None
        return target_market


class TargetMarket(models.Model):
    code = models.CharField(max_length=10, db_index=True, unique=True, null=False)
    market = models.CharField(max_length=75, null=False)

    objects = models.Manager()
    service = ServiceManager()

    def __str__(self):
        return '{%s}' % self.market
