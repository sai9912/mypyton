from service import Service
from django.db import models


class ServiceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def find_item(self, **kwargs):
        try:
            item = PackageLevel.objects.get(kwargs)
        except:
            return None
        return item


class PackageLevel(models.Model):
    # Package level description
    level = models.CharField(max_length=100, default='')
    unit_descriptor = models.CharField(max_length=50)
    objects = models.Manager()
    service = ServiceManager()

    TRANSPORT_LOAD = 10
    MIXED_MODULE = 20
    PALLET = 30
    DISPLAY_SHIPPER = 40
    CASE = 50
    PACK = 60
    BASE = 70
    BAR_PLACEMENT = {70: 'products/static/products/site/wizard/pos.png',
                     60: 'products/static/products/site/wizard/pack.png',
                     50: 'products/static/products/site/wizard/case.png',
                     40: 'products/static/products/site/wizard/shipper.png',
                     30: 'products/static/products/site/wizard/pallet.png'}

    def __str__(self):
        return f'{self.id}-{self.unit_descriptor}'


PACKAGE_LEVELS = (
    # (str(TRANSPORT_LOAD), 'TRANSPORT_LOAD'),
    # (str(MIXED_MODULE), 'MIXED_MODULE'),
    (str(PackageLevel.PALLET), 'PALLET'),
    (str(PackageLevel.DISPLAY_SHIPPER), 'DISPLAY_SHIPPER'),
    (str(PackageLevel.CASE), 'CASE'),
    (str(PackageLevel.PACK), 'PACK_OR_INNER_PACK'),
    (str(PackageLevel.BASE), 'BASE_UNIT_OR_EACH')
)


class PackageLevelService(Service):
    def __init__(self):
        super().__init__(PackageLevel)
