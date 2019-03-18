import os
import random
import re
import tempfile
from mimetypes import guess_type
import io
import PIL.Image
import requests
import secretary
import subprocess

from django.utils.translation import gettext as _

from products.helpers.product_helper import is_valid_url
from products.models import Product


class CustomPDFRender(secretary.Renderer):
    """
    Default secretary renderer doesn't support image adjusting,
    each inserted image will have the same height/width as a placeholder
    """

    _default_image_mime_type = 'image/jpeg'  # when it's impossible to detect mime type

    def __init__(self, environment=None, **kwargs):
        super().__init__(environment, **kwargs)
        self.media_callback = self.multi_source_image_loader

        for attr in dir(self):
            if attr.startswith('custom_filter_') and callable(getattr(self, attr)):
                filter_name = attr.split('custom_filter_')[1]
                self.environment.filters[filter_name] = getattr(self, attr)

    # custom filters -->
    @staticmethod
    def custom_filter_trans(input_text):
        return _(input_text)

    @staticmethod
    def custom_filter_yes_no(input_value):
        return _('Yes') if input_value else _('No')
    # custom filters <--

    def multi_source_image_loader(self, media, *args, **kwargs):
        """
        load image from various sources: local, remote, etc
        kwargs contain "frame_attrs" and "image_attrs"
        (xml parameters for container and image)
        """

        loaders = (
            self.fs_loader,
            self.http_image_loader,
        )

        for loader_method in loaders:
            result = loader_method(media, *args, **kwargs)
            if result and not isinstance(result[0], self.environment.undefined):
                image_file = result[0]
                mime_type = result[1] if result[1] else self.detect_mime_type(image_file, media)

                self.adjust_image_parameters(
                    image=image_file,
                    mime_type=mime_type,
                    # the next 2 parameters will be adjusted inplace if required
                    frame_attrs=kwargs.get('frame_attrs'),
                    image_attrs=kwargs.get('image_attrs'),
                )
                return image_file, mime_type

        return None

    def detect_mime_type(self, image_file, image_path):
        """
        tries to detect mime type by image content and image path
        """

        # by file name
        mime_type = guess_type(image_path)[0]
        if mime_type:
            return mime_type

        # by image content
        image = PIL.Image.open(image_file)
        mime_type = PIL.Image.MIME.get(image.format)
        if mime_type:
            return mime_type

        # default fallback
        return self._default_image_mime_type

    def http_image_loader(self, media, *args, **kwargs):
        if is_valid_url(media):
            response = requests.get(media)
            image_file = io.BytesIO(response.content)
            mime_type = self.detect_mime_type(image_file, media)
            return image_file, mime_type
        return None

    @staticmethod
    def get_image_dimension(raw_value):
        regexp = re.search('(?P<value>[\d.]+)(?P<unit>\w+)', raw_value)
        if regexp:
            value_dict = regexp.groupdict()
            value_dict['value'] = float(value_dict['value'])
            return value_dict
        else:
            return None

    def adjust_image_parameters(self, image, mime_type, frame_attrs, image_attrs):
        """
        Adjust image container width/height according to the source image
        """

        pillow_image = PIL.Image.open(image)
        image_width, image_height = pillow_image.size  # int
        frame_height = self.get_image_dimension(frame_attrs.get('svg:height'))
        frame_width = self.get_image_dimension(frame_attrs.get('svg:width'))
        original_frame_height = frame_height['value']
        original_frame_width = frame_width['value']

        # apply the image ratio to container
        image_ratio = image_width / image_height

        # calculate a new width/height with preserving original image ratio
        if original_frame_width > original_frame_height:
            frame_width['value'] = original_frame_height * image_ratio
            # if new dimensions are exceeded the original, reduce both dimensions
            if frame_width['value'] > original_frame_width:
                frame_width['value'] = original_frame_width
                frame_height['value'] = frame_width['value'] / image_ratio
        else:
            frame_height['value'] = original_frame_width / image_ratio

        frame_attrs['svg:height'] = f'{frame_height["value"]:.2f}{frame_height["unit"]}'
        frame_attrs['svg:width'] = f'{frame_width["value"]:.2f}{frame_width["unit"]}'

        return frame_attrs


class LibreOfficeConverterException(Exception):
    pass


def render_to_pdf(template_name, context):
    """
    1. renders odt template to a temporary file
    2. converts it with the libreoffice command

    Notes (possible errors related to libreoffice):

    If libreoffice doesn't create .pdf files (only files like ".~lock.product-summary.pdf#")
     - close all libreoffice instances to use this converting method
     - remove the libreoffice profile directory for example "/home/user/.config/libreoffice"
     - if custom libreoffice env is used, remove both profiles to fix missing pdf files

    Libreoffice creates "/tmp/lu<alphanumeric>.tmp" files.
    For production use it's required to clenup them
    """

    tmp_directory = tempfile.TemporaryDirectory()
    tmp_odt_file_name = os.path.join(
        tmp_directory.name, f'pdf-export-{random.randint(1000, 9999)}.odt'
    )

    # debug, if you want to see all fields, uncomment the following lines
    # for field_name in [field.name for field in Product._meta.fields]:
    #     context['ui_attributes'][field_name] = {'ui_enabled': True}

    engine = CustomPDFRender()
    rendered_odt_string = engine.render(template_name, **context)

    with open(tmp_odt_file_name, 'wb') as rendered_odt:
        rendered_odt.write(rendered_odt_string)

    # a separated "env" allows to open multiple copies of libreoffice
    convert_command = (
        f'soffice --headless --convert-to pdf --outdir {tmp_directory.name} {tmp_odt_file_name} '
        f'-env:UserInstallation=file:///$HOME/.libreoffice-headless/'
    )
    convert_result = subprocess.run(convert_command.split(), check=False)
    pdf_report_file_path = tmp_odt_file_name.replace('.odt', '.pdf')

    if os.path.isfile(pdf_report_file_path):
        with open(pdf_report_file_path, 'rb') as rendered_pdf:
            pdf_file = io.BytesIO(rendered_pdf.read())
        tmp_directory.cleanup()
    else:
        # check method help text above if you encounter this error
        raise LibreOfficeConverterException(
            'Can\'t open the output .pdf file. '
            'Possible libreoffice profiles error, profiles removing may help in this situation'
        )

    return pdf_file
