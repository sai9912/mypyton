import os
from rest_framework import serializers
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from rest_framework.exceptions import MethodNotAllowed, APIException
from rest_framework.fields import empty

from barcodes.models import Label
from barcodes.preview import Preview
from barcodes.utilities import Storage, make_omlet, get_barcode_type, generate_download_file
from products.models import Product


class BarcodePreviewSerializer(serializers.ModelSerializer):
    barcode_type = serializers.SerializerMethodField(read_only=True)
    barcode = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = ('gtin', 'barcode_type', 'barcode',)

    def create(self, validated_data):
        raise MethodNotAllowed('POST')

    def update(self, instance, validated_data):
        raise MethodNotAllowed('PUT')

    def get_barcode_type(self, instance):
        """
        Calculates barcode type
        actually Product model has bar_type attribute,
        but it seems it doesn't reflect an actual status
        """

        return get_barcode_type(instance.gtin, instance.package_level_id)

    def get_barcode(self, instance):
        barcode_kind = self.get_barcode_type(instance)
        if not barcode_kind:
            raise APIException('Can\'t detect a barcode kind')

        request = self.context['request']

        barcode = Storage({
            'gtin': str(instance.gtin),
            'omlet': 'preview',
            'id': str(instance.gtin),
            'bwr': 0.0000,
            'size': 1.5,
            'kind': barcode_kind,
            'pmk': '',
            'price': None,
            'name': None,
            'debug': '',
            'rqz': 'y',
        })

        image_preview_path = os.path.join(
            settings.BARCODES_FILES_PATH, str(request.user.id), barcode_kind
        )

        image_preview = Preview(
            request, barcode, debug='', watermark=True, path=image_preview_path
        )

        if not os.path.exists(image_preview.img_fqn):
            image_preview.generate()

        return static(image_preview.image)


class BarcodeGenerateSerializer(serializers.ModelSerializer):
    """
    Preview/download an actual barcode serializer.
    Note: data is coming from GET here (not POST), check BarcodeListCreateAPIView
    """

    gtin = serializers.CharField(read_only=True)
    barcode_type = serializers.SerializerMethodField(read_only=True)
    barcode = serializers.SerializerMethodField(read_only=True)

    # input parameters for barcode generating
    download_type = serializers.CharField(
        write_only=True, default=None, allow_null=True, allow_blank=True,
    )
    size = serializers.FloatField(write_only=True, default=1.0)
    bwr = serializers.FloatField(write_only=True, default=0.0)
    rqz = serializers.BooleanField(write_only=True, default=True)

    resolution = serializers.CharField(write_only=True, default='300 dpi', allow_blank=True)
    file_type = serializers.CharField(write_only=True, default='gif', allow_blank=True)
    ps_type = serializers.CharField(write_only=True, default='win', allow_blank=True)
    label_type = serializers.CharField(write_only=True, default='', allow_blank=True)

    marks = serializers.BooleanField(write_only=True, default=False)
    debug = serializers.BooleanField(write_only=True, default=False)

    class Meta:
        model = Product
        fields = (
            'gtin', 'barcode_type', 'barcode',
            'download_type', 'size', 'bwr', 'rqz', 'resolution', 'file_type', 'ps_type',
            'label_type', 'marks', 'debug',
        )

    def create(self, validated_data):
        raise MethodNotAllowed('POST')

    def update(self, instance, validated_data):
        raise MethodNotAllowed('PUT')

    def get_field_value(self, field_name):
        """
        Returns a supplied field value or default
        """

        value = None

        if hasattr(self, '_validated_data'):
            value = self.validated_data.get(field_name, empty)

        # special comparison with "empty", cause False, None, etc could be valid values
        if value is empty:
            return self.fields[field_name].default
        else:
            return value

    def get_barcode_type(self, instance):
        """
        Calculates barcode type
        actually Product model has bar_type attribute,
        but it seems it doesn't reflect an actual status
        """

        return get_barcode_type(instance.gtin, instance.package_level_id)

    def get_barcode(self, instance):
        """
        Whether download or just display a preview (without a watermark)
        """

        download_type = self.get_field_value('download_type')
        if download_type:
            return self.generate_barcode_file(instance)
        else:
            return self.generate_barcode_preview(instance)

    def generate_barcode_preview(self, instance):
        request = self.context['request']
        barcode_kind = self.get_barcode_type(instance)
        if not barcode_kind:
            raise APIException('Can\'t detect a barcode kind')

        # input parameters (default values are used for fields, check fields defenitions)
        size = self.get_field_value('size')
        bwr = self.get_field_value('bwr')
        rqz = self.get_field_value('rqz')
        marks = self.get_field_value('marks')
        debug = self.get_field_value('debug')

        barcode = Storage({
            'gtin': instance.gtin,
            'omlet': None,
            'id': instance.gtin,
            'bwr': bwr,
            'size': size,
            'kind': barcode_kind,
            'pmk': marks,
            'price': None,
            'name': None,
            'debug': debug,
            'rqz': rqz,
        })

        barcode.omlet = make_omlet(barcode)

        image_path = os.path.join(
            settings.BARCODES_FILES_PATH, str(request.user.id), barcode_kind
        )
        barcode = Preview(
            request,
            barcode,
            debug=debug,
            watermark=False,
            path=image_path,
            res=settings.BARCODES_GENERATE_RES
        )
        barcode.generate()
        return static(barcode.image)

    def generate_barcode_file(self, instance):
        """
        Legacy barcode generating method is used
        """

        input_parameters = {
            'dl_type': self.get_field_value('download_type'),
            'bc_kind': self.get_barcode_type(instance),
            'gtin': instance.gtin,
            'user_id': self.context['request'].user.id,

            'size': self.get_field_value('size'),
            'bwr': self.get_field_value('bwr'),
            'resolution': self.get_field_value('resolution'),
            'file_type': self.get_field_value('file_type'),
            'ps_type': self.get_field_value('ps_type'),
            'label_type': self.get_field_value('label_type'),
            'rqz': self.get_field_value('rqz'),
            'debug': self.get_field_value('debug'),
            'marks': self.get_field_value('marks'),
        }

        result = generate_download_file(input_parameters)
        if result.get('success'):
            return result.get('static_file_path')
        else:
            raise APIException(result.get('msg', 'Barcode generating: unknown server error'))


class BarcodeLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        exclude = ('template', )
