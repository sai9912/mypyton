import json
import pyexcel as pe
from django.utils.translation import gettext as _
from products.models.product import Product
from api.serializers.product_serializers import BaseProductSerializer
from member_organisations.models import ProductTemplate


def funny_letter(value):
    """
    This is silly test for callables inside Product template
    """
    if "a" in value:
        raise Exception("Forbidden letter detected")


def get_language(user):
    language = user.profile.language
    if not language:
        language = "en"
    return language


def language_mapping(template, user, reverse=False):
    language = get_language(user)
    translated_keys = {}
    for atri in template.attributes.all():
        field_name = atri.get_fieldname()
        label_dict = json.loads(atri.ui_label_i18n)
        translated = label_dict.get(language)
        if not translated:
            translated = label_dict.get("en")
        if not translated:
            translated = atri.ui_label
        if reverse:
            translated_keys[translated] = field_name
        else:
            translated_keys[field_name] = translated
    return translated_keys


def get_translated_values(value, user):
    language = get_language(user)
    try:
        value = json.loads(value)
        translated = value.get(language)
        if not translated:
            translated = value.get("en")
        if not translated:
            translated = value
        return translated
    except Exception as e:
        return value


def export(products, user, template):
    errors = []
    content = []
    keys = set(x.get_fieldname() for x in template.attributes.all())
    xls_keys = language_mapping(template, user)
    for product_obj in products:
        try:
            product = BaseProductSerializer(product_obj)
            res = {xls_keys.get(key): get_translated_values(value, user)
                   for key, value in product.data.items() if key in keys}
            res["template_name"] = template.name
        except Exception as e:
            errors.append({product["gtin"]: {'Exception': str(e)}})
            continue
        content.append(res)
    return content, errors


def export_range(export_type, gepir_export, file_type, filename, prefix, user, template):

    if export_type == 'products':
        products = Product.objects.filter(owner=user, gs1_company_prefix=prefix.prefix) \
                                  .order_by('package_level_id', 'gtin')
    elif export_type == 'starred':
        products = Product.objects.filter(owner=user, gs1_company_prefix=prefix.prefix, mark=1) \
                                  .order_by('package_level_id', 'gtin')
    else:
        raise Exception('Export type not available')
    (content, errors) = export(products, user, template)
    try:
        pe.save_as(records=content, dest_file_name=filename)
    except Exception as err:
        errors.append({"File save error": str(err)})
        print(err)
    return errors

    content, errors = export(products, user, template)

    try:
        pe.save_as(records=content, dest_file_name=filename)
    except Exception as err:
        errors.append({_("File save error"): str(err)})
    return errors


def import_products(prefix, user, imp_file, request):
    ws = pe.get_records(file_name=imp_file)
    errors = []
    record = ws[0]
    template_name = record.get("template_name")
    if not template_name:
        errors.append({_("file structure error"): {
                      _("File doesn't contain template information"): ""}})
        return errors
    template = ProductTemplate.objects.filter(name=template_name).first()
    if not template:
        errors.append({_("file structure error"): {
                      _("File does contain incorrect template name"): ""}})
        return errors

    xls_keys = language_mapping(template, user, reverse=True)
    mandatory_keys = {x.get_fieldname()
                      for x in template.get_csv_mandatory_attributes()}
    mandatory_keys.add("gtin")
    form_validators = template.get_all_form_validators()

    for record in ws:
        local_errors = []
        res = {}
        for key, value in record.items():
            if key == "template_name":
                continue

            x_key = xls_keys[key]
            if "i18n" in x_key:
                res[x_key] = json.dumps({get_language(user): str(value)})
            else:
                res[x_key] = str(value)

        res["gs1_company_prefix"] = prefix.prefix
        res["package_level"] = template.package_level.id
        res['member_organisation'] = prefix.member_organisation.pk
        res['company_organisation'] = prefix.company_organisation.pk
        res['owner'] = user.pk


        product = Product.objects.filter(gtin=res.get("gtin")).first()
        if product:
            product_data = BaseProductSerializer(
                product, data=res, context={"request": request})
        else:
            product_data = BaseProductSerializer(
                data=res, context={"request": request})
        valid = product_data.is_valid()
        if not valid:
            errors.append({"serialization errors": product_data.errors})
            continue

        res = product_data.validated_data

        for key in mandatory_keys:
            if key not in res.keys():
                errors.append({"Missing column {}".format(key): {}})

        for attribute in template.attributes.all():
            fieldname = attribute.get_fieldname()

            if attribute.csv_default_callable and not res[fieldname]:
                try:
                    res[fieldname] = BaseProductSerializer.get_function_by_name(
                        attribute.csv_default_callable)
                except Exception as err:
                    local_errors.append(
                        {"Field {} generate {}".format(fieldname, err): {}})
                    continue

            if attribute.csv_field_validation_callable:
                try:
                    BaseProductSerializer.get_function_by_name(
                        attribute.csv_field_validation_callable, value=res[fieldname])
                except Exception as err:
                    local_errors.append(
                        {"Field {} generate {}".format(fieldname, err): {}})
                    continue

        for validator in form_validators:
            try:
                BaseProductSerializer.get_function_by_name(
                    validator, value=res)
            except Exception as err:
                local_errors.append(
                    {"Row {} generate {}".format(res, err): {}})

        if not local_errors:
            product_data.save()
        else:
            errors.extend(local_errors)

    return errors
