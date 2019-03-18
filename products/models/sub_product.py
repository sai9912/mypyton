from django.db import models
from .product import Product


class ServiceManager(models.Manager):
    def create(self, product_id, sub_product_id, quantity):
        subproduct = SubProduct(
            product_id=product_id,
            sub_product_id=sub_product_id,
            quantity=quantity)
        subproduct.save()
        return subproduct

    def get_associated(self, product):
        products = SubProduct.objects.filter(product=product).order_by('id').all()
        return products

    def delete_id(self, user, product_id, sub_product_id):
        product = Product.service.get_my_product(user, product_id)
        if not product:
            return False
        try:
            subproduct = SubProduct.objects.get(product_id=product_id, sub_product_id=sub_product_id)
            subproduct.delete()
        except Exception:
            return False
        return True

    def get_or_create_id(self, user, product_id, subproduct_id):
        product = Product.service.get_my_product(user, product_id)
        if not product:
            return None, False
        subproduct, created = SubProduct.objects.get_or_create(product_id=product_id, sub_product_id=subproduct_id)
        return subproduct, created


class SubProduct(models.Model):
    # A product's sub_products can be accessed with [a.sub_product for a in product.associated_sub_products]
    product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE, related_name='products')

    # A sub_product's products can be accessed with [a.product for a in sub_product.associated_products]
    sub_product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE, related_name='sub_products')

    quantity = models.IntegerField(default=0)

    class Meta:
        unique_together = ('product', 'sub_product')

    objects = models.Manager()
    service = ServiceManager()

    def __str__(self):
        return self.sub_product.gtin

    def clean(self):
        if self.product.package_level.get_short_name() == 'Each':
            raise self.ValidationError('This product is not a container')
        elif self.sub_product.package_level.id <= self.product.package_level.id:
            raise self.ValidationError('%s cannot cantain %s' %
                                  (self.product.package_level.get_short_name(),
                                   self.sub_product.package_level.get_short_name()))

        if self.product.package_level.get_short_name() == 'Pack':
            if self.sub_product.net_content > 12:
                raise self.ValidationError('Pack over-filled')
        elif self.product.package_level.get_short_name() == 'Case':
            if self.sub_product.net_content > 144:
                raise self.ValidationError('Case over-filled')
        elif self.product.package_level.get_short_name() == 'Pallet':
            if self.sub_product.net_content > 2880:
                raise self.ValidationError('Pallet over-filled')
