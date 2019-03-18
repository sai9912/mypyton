import importlib
import inspect
import json
from collections import OrderedDict
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from rest_framework.fields import BooleanField

from api import custom_fields
from api.utils import is_company_organisation
from barcodes.utilities import isValid
from member_organisations.models import (
    ProductTemplate, ProductPackaging, ProductAttribute
)
from prefixes.models import Prefix
from products.helpers.product_helper import get_translated_field_names_api
from products.models.country_of_origin import CountryOfOrigin
from products.models.dimension_uom import DimensionUOM
from products.models.language import Language
from products.models.net_content_uom import NetContentUOM
from products.models.product import Product, ProductImage
from products.models.sub_product import SubProduct
from products.models.target_market import TargetMarket
from products.models.weight_uom import WeightUOM
from services import prefix_service
from rest_framework_cache.serializers import CachedModelSerializer
from rest_framework_cache.registry import cache_registry
from rest_framework import serializers

logger = logging.getLogger()


def validate_company_organisation_has_no_permission(user, value):
    if value is not None and is_company_organisation(user):
        raise serializers.ValidationError(
            _('this field is read-only for Company organisation.'))
    return value


GS1_CLOUD_STATE_CHOICES = (
    ('DRAFT', 'DRAFT'),
    ('OPTED_OUT', 'OPTED_OUT'),
    ('ACTIVE', 'ACTIVE'),
)


class BaseProductSerializer(serializers.ModelSerializer):
    _image_upload = None  # "image_upload" is extracted to this attribute from data
    _max_upload_size = 2 * 1024 * 1024  # max upload size in MiB

    depth_uom = serializers.SlugRelatedField(
        slug_field='code', queryset=DimensionUOM.objects.all(), required=False
    )
    height_uom = serializers.SlugRelatedField(
        slug_field='code', queryset=DimensionUOM.objects.all(), required=False
    )
    width_uom = serializers.SlugRelatedField(
        slug_field='code', queryset=DimensionUOM.objects.all(), required=False
    )
    gross_weight_uom = serializers.SlugRelatedField(
        slug_field='code', queryset=WeightUOM.objects.all(), required=False
    )
    net_weight_uom = serializers.SlugRelatedField(
        slug_field='code', queryset=WeightUOM.objects.all(), required=False
    )
    net_content_uom = serializers.SlugRelatedField(
        slug_field='code', queryset=NetContentUOM.objects.all(), required=False
    )

    # i18n fields require custom empty data validation
    label_description_i18n = custom_fields.I18nCharField(required=False)
    description_i18n = custom_fields.I18nCharField(required=False)
    brand_i18n = custom_fields.I18nCharField(required=False)
    functional_name_i18n = custom_fields.I18nCharField(required=False)
    image_i18n = custom_fields.I18nCharField(required=False)

    gs1_cloud_state = serializers.ChoiceField(choices=GS1_CLOUD_STATE_CHOICES, required=False)
    image_upload = serializers.ImageField(required=False)

    class Meta:
        model = Product
        extra_kwargs = {
            'gs1_company_prefix': {'required': True},
        }
        fields = '__all__'

    @classmethod
    def get_function_by_name(cls, function_name, **kwargs):
        function_name = function_name.replace('\'', '')
        splitted_name = function_name.split('.')
        package_name = '.'.join(splitted_name[:-1])
        func_name = splitted_name[-1]
        # TODO: add try except
        package = importlib.import_module(package_name)
        func = getattr(package, func_name)

        # If we call this get_FUNCTION_by_name it should check not only
        # classes, but function also. :)
        if func and (inspect.isclass(func) or inspect.isfunction(func)):
            try:
                return func(**kwargs)
            except Exception as e:
                logger.exception(
                    msg=f'Exception: class: {cls.__name__}, exception: {e}'
                )
                raise serializers.ValidationError(_('Callable error'))
        else:
            raise serializers.ValidationError(_('Callable error'))


# TODO: this class is not used yet
class ExportProductSerializer(BaseProductSerializer):
    _gs1_cloud_related_fields = (
        'gtin', 'target_market', 'brand_i18n', 'label_description_i18n', 'company',
        'category', 'gln_of_information_provider',
    )

    class Meta:
        # required parameters should be repeated in each subclass
        model = Product
        extra_kwargs = {
            'gs1_company_prefix': {'required': True},
        }
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        read_only = self.Meta.read_only_fields

        # Serializer can be used as GET and PATCH.
        # For GET we using a list, so we don't need this read_only
        if self.instance:
            try:
                if self.instance.gs1_cloud_state == "ACTIVE":
                    [read_only.append(x)
                     for x in self._gs1_cloud_related_fields
                     if x not in read_only]
                else:
                    [read_only.remove(x)
                     for x in self._gs1_cloud_related_fields
                     if x in read_only and x != "gtin"]
                if self.instance and self.instance.image_i18n != "{}":
                    read_only.append("image_i18n")
            except Exception as err:
                pass


class ProductSerializer(BaseProductSerializer):
    _gs1_cloud_related_fields = (
        'gtin', 'target_market', 'brand_i18n', 'label_description_i18n', 'company', 'category',
        'gln_of_information_provider', 'category', 'image_i18n', 'gln_of_information_provider',
    )
    _default_field_validators = (
        # validators which will be applied to all fields
        # (maybe it's required to use "ui_form_validation_callable" instead of this?)
        'api.validators.product_validators.GenericUOMValidator',
    )

    not_attributes_fields =[]

    class Meta:
        # required parameters should be repeated in each subclass
        model = Product
        extra_kwargs = {
            'gs1_company_prefix': {'required': True},
        }
        exclude = (
            'bar_placement', 'created', 'discontinued_date', 'eff_date',
            'name_of_information_provider', 'pub_date', 'updated',
        )
        read_only_fields = ['member_organisation']

    def __init__(self, *args, **kwargs):
        product_template = kwargs.pop('product_template', None)
        super().__init__(*args, **kwargs)

        if product_template:
            self.apply_product_template(product_template)

    def apply_product_template(self, product_template):
        """
        Assign fields validation parameters by a given product template.
        """

        for attribute in product_template.attributes.all():
            field_name = attribute.get_fieldname()
            field = self.fields.get(field_name) or self.fields.get(f'{field_name}_i18n')
            if not field:
                continue

            field.ui_mandatory = attribute.ui_mandatory
            field.ui_enabled = attribute.ui_enabled
            field.ui_label_i18n = attribute.ui_label_i18n
            field.definition = attribute.definition

            if self.is_field_required(attribute, field):
                field.required = True
                field.allow_null = False

            if self.is_field_read_only(attribute):
                # it's impossible to have both mandatory and read only
                field.ui_mandatory = False

                field.ui_read_only = True
                field.read_only = True

            validators_paths = (
                attribute.ui_default_callable,
                attribute.ui_field_validation_callable,
                attribute.ui_form_validation_callable,
            )

            for callable_path in (validators_paths + self._default_field_validators):
                if callable_path:
                    field.validators.append(self.get_function_by_name(callable_path))

            if attribute.ui_label:
                field.meta_labels = {
                    x.split('_')[-1]: getattr(attribute, x)
                    for x in dir(attribute) if 'ui_label_' in x
                }

    def is_field_required(self, attribute, field):
        if isinstance(field, BooleanField):
            return False

        field_name = attribute.path.split('.')[-1]

        if hasattr(self, 'initial_data'):
            is_image_uploaded = self.initial_data.get('image_upload')
        else:
            is_image_uploaded = None

        if field_name == 'image_i18n' and is_image_uploaded:
            # if image_upload is specified remove required for image_i18n
            return False

        return attribute.ui_mandatory

    def is_field_read_only(self, attribute):
        if attribute.ui_read_only:
            return True

        if self.instance and self.instance.gs1_cloud_state == 'ACTIVE':
            # if instance is in "ACTIVE" GS1 state, gs1 cloud fields are locked for updating
            field_name = attribute.get_fieldname()
            if field_name == 'image_i18n' and getattr(self, 'instance', None):
                # if there is an image for the current language, image_i18n should be locked
                return bool(self.instance.image)
            return field_name in self._gs1_cloud_related_fields

    def validate_gs1_company_prefix(self, value):
        if self.instance is not None and value is not None:
            raise serializers.ValidationError(_('this field is not editable.'))

        try:
            return Prefix.objects.get(prefix=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(_('given prefix does not exist.'))

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        Override for customisation of labels
        Example from Thomas:
        'target_market':
        {
            'label':{'en':'Target Market'}, # all translations for this MO are here
            'is_ui_mandatory':True
         },
        """

        representation = super().to_representation(instance)
        final_representation = OrderedDict()

        for key, value in representation.items():
            if key.endswith('_i18n') and value:
                values = json.loads(value)
                labels = get_translated_field_names_api(key, values)
            elif key in self.not_attributes_fields:
                final_representation[key] = value
                continue
            else:
                values = value
                labels = {'en': key}

            result = {
                'ui_mandatory': getattr(self.fields[key], 'ui_mandatory', False),
                'ui_read_only': getattr(self.fields[key], 'ui_read_only', False),
                'ui_enabled': getattr(self.fields[key], 'ui_enabled', False),
                'ui_label_i18n': getattr(self.fields[key], 'ui_label_i18n', ''),
                'definition': getattr(self.fields[key], 'definition', ''),
                'label': labels,
                'value': values,
            }
            final_representation[key] = result
        return final_representation

    def validate_company_organisation(self, value):
        validate_company_organisation_has_no_permission(
            self.context['request'].user, value)

    def validate_owner(self, value):
        validate_company_organisation_has_no_permission(
            self.context['request'].user, value)

    def validate_image_upload(self, value):
        if value and value.size > self._max_upload_size:
            raise ValidationError(_(f'Maximum image size is {self._max_upload_size} bytes'))
        return value

    def validate_gs1_cloud_state(self, value):
        """
         - only staff user can switch status from ACTIVE to DRAFT
         - valid gs1_cloud states are controllef by field "choices=..."
        """

        locked_statuses = ('ACTIVE',)
        current_status = self.instance.gs1_cloud_state if self.instance else None
        user = self.context['request'].user

        is_locked_status_changed = all([
            current_status in locked_statuses,
            value != current_status,
        ])

        if is_locked_status_changed and not user.is_staff:
            # a user can't change status when it's set to ACTIVE
            raise ValidationError(_('You can\'t change this status, please ask for a support.'))

        return value

    def validate(self, data):
        """
        Check if Generated GTIn is valid
        data['gs1_company_prefix'] is Prefix validated on validate_gs1_company_prefix

        instance level validators (ui_form_validation_callable)
        can be called here with errors field errors
        ValidationError({'field_name': 'A field level error'})
        """

        if not self.instance:
            prefix = data['gs1_company_prefix']
            if prefix.is_suspended:
                raise serializers.ValidationError(
                    _('Prefix is not in ACTIVE state'))
            try:
                prefix.make_starting_from()
            except Exception:
                raise serializers.ValidationError(
                    _('not allowed to create products for this prefix.')
                )
            data['member_organisation'] = prefix.member_organisation
            data['company_organisation'] = prefix.company_organisation
            data['gtin'] = '0' + prefix.starting_from
            data['owner'] = self.context['request'].user
            if not isValid(data['gtin']) and len(data['gtin']) != 14:
                raise serializers.ValidationError(_('generated GTIN invalid.'))

            if Product.objects.filter(gtin=data['gtin']).exists():
                # if GTIN is already allocated,
                # if you want to remove this, check how errors look,
                # when you try to add more products than allowed to a prefix
                raise ValidationError(
                    _('Generated GTIN is already used, please check your prefixes.')
                )

        self._image_upload = data.pop('image_upload', None)
        return data

    def save_image(self, instance, data):
        """
        Image saving is possible in 2 ways: direct upload and url specifying.
          - image_upload is uploaded (remove previous)
          - image_i18n url is set
          - image_i18n + existing ProductImage
        """

        product_images = ProductImage.objects.filter(
            product=instance, language=instance.language)

        if self._image_upload:
            # if image is uploaded - remove existing image for a language
            [instance.delete() for instance in product_images]

            product_image = ProductImage.objects.create(
                product=instance, language=instance.language, image=self._image_upload
            )
            instance.refresh_from_db()
            # instance.image = product_image.image.url
            setattr(instance, f'image_{instance.language.slug}', product_image.image.url)
            instance.save()
            return product_image

        if 'image_i18n' in data and product_images.exists():
            # if any image type is received we have to replace an existing image for language
            # remove previously saved images if any, direct delete() call removes files from disk
            product_image = product_images.first()
            current_image_url = getattr(instance, 'image', None)
            if product_image.image.url != current_image_url:
                # if image url is the same remove all images for this product-language
                [instance.delete() for instance in product_images]

    def update(self, instance, validated_data):
        gtin = validated_data.get('gtin', None)
        if gtin and gtin != instance.gtin:
            try:
                Product.objects.get(gtin=gtin)
                raise serializers.ValidationError('GTIN exist')
            except:
                pass

        if 'company_organisation' in validated_data:
            validated_data['company_organisation'] = validated_data['company_organisation']

        if 'gs1_company_prefix' in validated_data:
            validated_data['gs1_company_prefix'] = validated_data['gs1_company_prefix'].prefix

        if self._image_upload:
            # don't reset image if there is uploaded file
            validated_data.pop('image_i18n', None)

        product = super(ProductSerializer, self).update(instance, validated_data)
        self.save_image(product, validated_data)
        return product

    def create(self, validated_data):
        prefix = validated_data['gs1_company_prefix']
        validated_data['gs1_company_prefix'] = prefix.prefix
        if self._image_upload:
            # don't reset image if there is uploaded file
            validated_data.pop('image_i18n', None)

        product = super(ProductSerializer, self).create(validated_data)
        self.save_image(product, validated_data)

        prefix.increment_starting_from()
        prefix_service.save(prefix)
        return product


class SubProductProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class SubProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubProduct
        fields = '__all__'

    sub_product = ProductSerializer()


class ProductWithSubProductsSerializer(ProductSerializer):
    not_attributes_fields = ["products"]
    products = SubProductSerializer(many=True)



class ProductAttributeSerializer(CachedModelSerializer):
    member_organisation = serializers.SlugField(source='member_organisation.slug')

    class Meta:
        model = ProductAttribute
        fields = '__all__'


class ProductTemplateSerializer(CachedModelSerializer):
    member_organisation = serializers.SlugField(source='member_organisation.slug')

    class Meta:
        model = ProductTemplate
        fields = (
            'id', 'name', 'order', 'package_level', 'attributes', 'member_organisation',
            'image_url', 'ui_label_i18n',
        )


class ProductTemplateDetailsSerializer(CachedModelSerializer):
    attributes = ProductAttributeSerializer(many=True, source='attributes.all')
    member_organisation = serializers.SlugField(
        source='member_organisation.slug')

    class Meta:
        model = ProductTemplate
        fields = (
            'name', 'order', 'package_level', 'attributes', 'member_organisation',
            'image_url', 'ui_label_i18n',
        )


class ProductPackagingSerializer(serializers.ModelSerializer):
    member_organisation = serializers.SlugField(source="member_organisation.slug")

    class Meta:
        model = ProductPackaging
        fields = (
            'id', 'code', 'order', 'member_organisation', 'image_url',
            'ui_label_i18n', 'ui_description_i18n', 'package_type'
        )


class ProductLanguageSerializer(CachedModelSerializer):
    """
    Serializes products_language
    """

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['name'] = _(representation.get('name'))
        return representation

    class Meta:
        model = Language
        fields = ('id', 'slug', 'name')


class ProductCountryOfOriginSerializer(CachedModelSerializer):

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['name'] = _(representation.get('name'))
        return representation

    class Meta:
        model = CountryOfOrigin
        fields = ('id', 'code', 'name')


class ProductTargetMarketSerializer(CachedModelSerializer):

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['market'] = _(representation.get('market'))
        return representation

    class Meta:
        model = TargetMarket
        fields = ('id', 'code', 'market')



class ProductDimensionUOMSerializer(CachedModelSerializer):
    """
    Serializes product_dimensions_uom
    """

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['uom'] = instance.uom
        return representation

    class Meta:
        model = DimensionUOM
        fields = ('id', 'abbr', 'code')


class ProductNetContentUOMSerializer(CachedModelSerializer):
    """
    Serializes product_net_content_uom
    """

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['uom'] = instance.uom
        return representation

    class Meta:
        model = NetContentUOM
        fields = ('id', 'abbr', 'code')


class ProductWeightUOMSerializer(CachedModelSerializer):
    """
    Serializes product_weight_uom
    """

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['uom'] = instance.uom
        return representation

    class Meta:
        model = WeightUOM
        fields = ('id', 'abbr', 'code')


# cache config
# cache_registry.register(ProductSerializer)
cache_registry.register(ProductAttributeSerializer)
cache_registry.register(ProductTemplateSerializer)
cache_registry.register(ProductLanguageSerializer)
cache_registry.register(ProductCountryOfOriginSerializer)
cache_registry.register(ProductTargetMarketSerializer)
cache_registry.register(ProductDimensionUOMSerializer)
cache_registry.register(ProductNetContentUOMSerializer)
cache_registry.register(ProductWeightUOMSerializer)
