from rest_framework import serializers
from products.models.sub_product import SubProduct
from products.models.product import Product
from django.utils.translation import gettext as _


class SubProductSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(slug_field='gtin', read_only=True)
    sub_product = serializers.SlugRelatedField(slug_field='gtin', read_only=True)
    class Meta:
        model = SubProduct
        fields = '__all__'

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(_('Quantity should be greater than 0'))
        return value

    def get_subproduct(self):
        try:
            product = Product.objects.get(gtin=self.initial_data['product'])
        except:
            raise serializers.ValidationError(_('Invalid product gtin'))

        try:
            sub_product = Product.objects.get(gtin=self.initial_data['sub_product'])
        except:
            raise serializers.ValidationError(_('Invalid subproduct gtin'))

        try:
            subproduct = SubProduct.objects.get(product=product, sub_product=sub_product)
        except:
            raise serializers.ValidationError(_('Product have no subproduct'))

        return subproduct
