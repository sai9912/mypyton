import os
import tempfile
from io import BytesIO

import requests
from django.conf import settings
from PIL import Image

from products.helpers.product_helper import is_valid_url


def delete_product_image(image, user_id):
    pass


def get_image_dimensions(imagename):
    if is_valid_url(imagename):
        response = requests.get(imagename)
        img = Image.open(BytesIO(response.content))
    else:
        img = Image.open(imagename)

    dpi = img.info.get('dpi', (72.0, 72.0))
    width, height = img.size
    ratio = width / float(height)
    width *= 300.0 / dpi[0]
    height *= 300.0 / dpi[0]
    max_width = 85.66 * 11.81
    max_height = 75.68 * 11.81
    cell_ratio = max_width / max_height
    if ratio < cell_ratio:
        height = max_height
        width = height * ratio
    else:
        width = max_width
        height = width / ratio
    return (width / 11.81), (height / 11.81)


def upload_image(request, product):
    def validate_file(filename):
        ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'gif', 'png'}
        return '.' in filename and filename.lower().rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    img_file = request.FILES['upload']
    if img_file and validate_file(img_file.name):
        ext = img_file.name.lower().rsplit('.', 1)[1]

        # check that the dir exists
        if not os.path.exists(settings.PRODUCT_IMAGE_DIR):
            os.makedirs(settings.PRODUCT_IMAGE_DIR)

        tfile = tempfile.NamedTemporaryFile(dir=settings.PRODUCT_IMAGE_DIR, suffix=".%s" % ext, delete=False)
        for chunk in img_file.chunks():
            tfile.write(chunk)
        tfile.close()

        if product.image:
            try:
                image_path = os.path.join(settings.PRODUCT_IMAGE_DIR, product.image)
                os.unlink(image_path)
            except Exception:
                pass

        product.image = tfile.name.rsplit('/', 1)[1]
        product.save()
