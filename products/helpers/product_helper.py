from django.contrib.staticfiles import finders
from django.core.exceptions import SuspiciousFileOperation, ValidationError
from django.core.validators import URLValidator

from BCM.helpers.utils import get_nested_attribute
from BCM.models import Language
from ..models.package_level import PackageLevel


def get_completeness(query):
    prdcts = query.all()
    completeness = 0
    if prdcts:
        for prdct in prdcts:
            completeness += prdct.completeness
        completeness = int(completeness / len(prdcts))
    return completeness


def filter_list(all_in_range, form):
    form.is_valid()     # process cleaned data

    if not form.cleaned_data['base']:
        all_in_range = all_in_range.exclude(package_level_id=PackageLevel.BASE)

    if not form.cleaned_data['pack']:
        all_in_range = all_in_range.exclude(package_level_id=PackageLevel.PACK)

    if not form.cleaned_data['case']:
        all_in_range = all_in_range.exclude(package_level_id=PackageLevel.CASE)

    if not form.cleaned_data['pallet']:
        all_in_range = all_in_range.exclude(package_level_id=PackageLevel.PALLET)

    # if not form.mixed_module.data:
    #     all_in_range = all_in_range.filter(models.Product.package_level_id != models.MIXED_MODULE)

    if not form.cleaned_data['display_shipper']:
        all_in_range = all_in_range.exclude(package_level_id=PackageLevel.DISPLAY_SHIPPER)

    # if not form.transport_load.data:
    #     all_in_range = all_in_range.filter(models.Product.package_level_id != models.TRANSPORT_LOAD)

    if form.cleaned_data['brand']:
        all_in_range = all_in_range.filter(brand_i18n__icontains=form.cleaned_data['brand'])

    if form.cleaned_data['gtin']:
        all_in_range = all_in_range.filter(gtin__icontains=form.cleaned_data['gtin'])

    if form.cleaned_data['description']:
        all_in_range = all_in_range.filter(description_i18n__icontains=form.cleaned_data['description'])

    if form.cleaned_data['sku']:
        all_in_range = all_in_range.filter(sku__icontains=form.cleaned_data['sku'])

    #if form.prefixes.data != "0":
    #    prefix = prefix_service.get(form.prefixes.data)
    #    all_in_range = all_in_range.filter(Product.gs1_company_prefix == str(prefix.prefix))

    if form.cleaned_data['mark']:
        all_in_range = all_in_range.filter(mark=1)

    if form.cleaned_data['target_market']:
        all_in_range = all_in_range.filter(
            target_market__code=form.cleaned_data['target_market']
        )

    return all_in_range


def make_filter(form):
    ret = {}
    for key in form.cleaned_data:
        value = form.cleaned_data[key]
        ret.update({key: value})
    return ret


def get_product_languages(instance):
    """
    Only one language allowed for now (maybe it will be changed later so we return a list):
        1. if there is specified language, use it
        2. if no language detected, use english
    """

    language_slug = instance.language.slug if instance and instance.language else None
    language = Language.objects.filter(slug=language_slug).first()

    if language:
        return [language]
    else:
        # we expect english exists in the database
        return [Language.objects.get(slug='en')]


def get_translated_field_names_api(field_name, field_values):
    """
    Extract field data in required format: language-value dicts for gs1 api
    [
        {"en": "description"},
        {"fr": "description_fr"},
    ]
    """

    name_template = field_name[:field_name.find('_i18n')]
    labels = {
        lang: f'{name_template}_{lang}'
        for lang, value in field_values.items()
    }
    return labels if labels else {'en': f'{name_template}_en'}


def get_translated_field_values_gs1_api(instance, languages, field_name):
    """
    Extract field data in required format: language-value dicts for gs1 api
    [
        {"language" : "en", "value": "GS1 Global Office"},
        {"language" : "fr", "value": "Bureau Mondial De GS1"}
    ]
    """

    return [
        {
            'language': language.slug,
            'value': getattr(instance, f'{field_name}_{language.slug}', '--'),
        }
        for language in languages
    ]


def prepare_instance_data(fields_map, instance, translated_fields=None):
    """
    Adjust instance fields to required format for an API request

    :param fields_map: dict {'target_field_name': 'source_field_name.subfield' }
    :param instance: any model instance
    :param translated_fields: fields to convert with "get_translated_field_values"
    :return: prepared API ready dict
    """

    data = dict()

    if not translated_fields:
        translated_fields = (
            'brand', 'label_description', 'company_organisation.name', 'image',
            # 'functional_name', 'description',
        )

    allowed_languages = get_product_languages(instance)

    for target_name, source_name in fields_map.items():
        if not source_name:
            data[target_name] = None
            continue

        if source_name in translated_fields:
            data[target_name] = get_translated_field_values_gs1_api(
                instance, allowed_languages, source_name
            )
        else:
            data[target_name] = get_nested_attribute(instance, source_name)

    return data


def gs1_fields_changed(fields_map, instance, original_instance):
    """
    we don't upload to gs1 if required fields are not changed
    """

    test_fields = list(fields_map.values())
    test_fields.append('gs1_cloud_state')

    for field_name in test_fields:
        if not field_name:
            continue

        new_value = get_nested_attribute(instance, field_name)
        original_value = get_nested_attribute(original_instance, field_name)

        if new_value != original_value:
            return True

    return False


def image_upload_directory(product_image, source_file_name):
    """
    Generate path for the ProductImage.image file field

    :param product_image: ProductImage instance
    :param source_file_name: uploaded file name
    :return: path for the uploading files
    """

    product = product_image.product
    assert product, 'ProductImage.product field must be set to assign an upload path.'

    upload_path = 'product_images/{mo_slug}/{company_uuid}/{gtin}/{file_name}'.format(
        mo_slug=product.member_organisation.slug or '_undefined_mo',
        company_uuid=product.company_organisation.uuid or '_undefined_company',
        gtin=product.gtin or '_undefined_gtin',
        file_name=source_file_name
    )
    return upload_path


def get_assoc_products_by_products_list(products_):
    from products.models.sub_product import SubProduct

    assoc_products = []
    products = products_ or []

    for p in products:
        if p.package_level_id != 70:
            subproducts = SubProduct.objects.filter(product=p).all()
            sub_p = []

            for subproduct in subproducts:
                sub_product = subproduct.sub_product
                sub_p.append({'id': sub_product.id,
                              'package_level': {'id': sub_product.package_level_id},
                              'brand': sub_product.brand,
                              'description': sub_product.description,
                              'gtin': sub_product.gtin,
                              'gs1_company_prefix': sub_product.gs1_company_prefix,
                              'bar_type': sub_product.bar_type,
                              'quantity': subproduct.quantity})
            assoc_products.append({'p_id': p.id,
                                   'sub_p': sub_p})
    return assoc_products


def get_static_file_full_path(file_path):
    """
    retrieves a full path for static files with wrong relative paths
    ("media", "static" parts are redundant here):

    - '/media/product_images/gs1go/gs1go-01/09501101730007/test_image.png'
    - '/static/site/img/no-image.gif'
    """

    path_parts = file_path.split('/')
    if file_path.startswith('/'):
        # static file can't start with '/'
        path_parts = path_parts[1:]

    while path_parts:
        current_path = '/'.join(path_parts)
        try:
            search_result = finders.find(current_path)
        except SuspiciousFileOperation:
            return None

        if search_result:
            return search_result

        # try to remove a level and search again
        path_parts = path_parts[1:]

    return None


def is_valid_url(url):
    """
    Check if url is valid
    """

    if not url:
        return None

    url_validator = URLValidator()
    try:
        url_validator(url)
    except ValidationError:
        return None
    else:
        return True

