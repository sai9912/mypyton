from django.db import models
from .product import Product
from .target_market import TargetMarket


class ServiceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def create(self, product, target_market):
        gtin_target_market = GtinTargetMarket(gtin=product.gtin,
                                              target_market=target_market,
                                              product=product)
        gtin_target_market.save()

    def get_target_markets_all(self, product):
        target_markets = GtinTargetMarket.objects.filter(product=product)
        return target_markets

    def get_target_markets_other(self, product):
        target_markets = ( GtinTargetMarket.objects.filter(product=product)
                                                   .exclude(target_market=product.target_market)
                                                   .order_by('target_market'))
        return target_markets

    def clone_product(self, product, cloned_product):
        target_markets = GtinTargetMarket.objects.filter(product=product)
        for target_market in target_markets:
            self.create(cloned_product, target_market.target_market)

    def add_target_market(self, product, target_market_code):
        target_market = TargetMarket.objects.get(code=target_market_code)
        self.create(product, target_market)

    def delete_target_market(self, product, target_market):
        item = GtinTargetMarket.objects.filter(product=product, target_market=target_market)
        item.delete()

    def change_target_market(self, product, target_market):
        item = GtinTargetMarket.objects.get(product=product, target_market=product.target_market)
        target_market_new = TargetMarket.objects.get(code=target_market)
        item.target_market = target_market_new
        item.save()

    def get_by_products_list(self, products_list):
        items = GtinTargetMarket.objects.filter(product__in=products_list).order_by('target_market')
        return items


class GtinTargetMarket(models.Model):
    product = models.ForeignKey(
        Product,
        null=True,
        on_delete=models.CASCADE,
        related_name='gtin_target_market'
    )
    gtin = models.CharField(
        max_length=14,
        default='',
        blank=True,
        db_index=True
    )
    target_market = models.ForeignKey(
        TargetMarket,
        null=True,
        on_delete=models.CASCADE
    )

    objects = models.Manager()
    service = ServiceManager()

    class Meta:
        unique_together = ('gtin', 'target_market')


gtin_target_market_service = GtinTargetMarket.service
