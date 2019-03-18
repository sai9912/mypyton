from BCM.models import LanguageByCountry
from django.core.management import BaseCommand
from member_organisations.models import ProductAttribute, ProductTemplate, MemberOrganisation
from openpyxl import Workbook
from os.path import join

__author__ = 'Narayan Kandel'

IMPORT_DEBUG = False

pa_column_field_mapping = {
    "id": 1,
    "pk": 2,
    "language": 3,
    "path": 4,
    "definition": 5,
    "ui_mandatory": 6,
    "ui_enabled": 7,
    "ui_read_only": 8,
    "ui_default_callable": 9,
    "ui_field_validation_callable": 10,
    "ui_form_validation_callable": 11,
    "ui_label_i18n": 12,
    "csv_mandatory": 13,
    "csv_default_callable": 14,
    "csv_field_validation_callable": 15,
    "csv_form_validation_callable": 16,
    "codelist_validation": 17,
}

pt_column_field_mapping = {
    "id": 1,
    "pk": 2,
    "language": 3,
    "name": 4,
    "order": 5,
    "package_level": 6,
    "attributes": 7,
    "mo_slug": 8,
    "image_url": 9,
    "ui_label_i18n": 10,
}


class Command(BaseCommand):
    help = "Command to dump templates"

    def add_arguments(self, parser):
        parser.add_argument('mo_slug', nargs='?', default='gs1se', type=str)
        parser.add_argument(
            'path',
            nargs='?',
            default='deployment/deployment-v1-2018-03-products-dev/UI_presets_v2_templates_gs1se.xlsx',
            type=str
        )

    def handle(self, *args, **options):
        """
        step:
            first filter attribute related to mo_slug and save them at attribute tab
            then filter template and store them on template tab
        :param args:
        :param options:
        :return:
        """
        mo_slug = options.get('mo_slug')
        path = options.get('path')
        try:
            mo = MemberOrganisation.objects.get(slug=mo_slug)
        except MemberOrganisation.DoesNotExist:
            pass
        else:
            default_language = mo.get_default_language_slug()
            product_attribute_ids = set(
                list(ProductTemplate.objects
                     .filter(member_organisation_id=mo.pk)
                     .values_list('attributes', flat=True)))

            product_attributes = ProductAttribute.objects.filter(id__in=product_attribute_ids)
            # write to sheet

            wb = Workbook()
            ws1 = wb.active
            ws1.title = "attribute_data"

            # first row header
            header = [
                "id",
                "pk",
                'language',
                'path',
                'definition',
                'ui_mandatory',
                'ui_enabled',
                'ui_read_only',
                'ui_default_callable',
                'ui_field_validation_callable',
                'ui_form_validation_callable',
                'ui_label',
                'csv_mandatory',
                'csv_default_callable',
                'csv_field_validation_callable',
                'csv_form_validation_callable',
                'codelist_validation']
            ws1.append(header)

            for row, pa in enumerate(product_attributes, start=2):
                ws1.append([
                    pa.pk,
                    pa.pk,
                    default_language,
                    pa.path,
                    pa.definition,
                    'true' if pa.ui_mandatory else 'false',
                    'true' if pa.ui_enabled else 'false',
                    'true' if pa.ui_read_only else 'false',
                    pa.ui_default_callable,
                    pa.ui_field_validation_callable,
                    pa.ui_form_validation_callable,
                    pa.ui_label,
                    'true' if pa.csv_mandatory else 'false',
                    pa.csv_default_callable,
                    pa.csv_field_validation_callable,
                    pa.csv_form_validation_callable,
                    pa.codelist_validation
                ])
                translated_keys = set(pa.__dict__.keys()) - {'_state', 'id', 'path', 'definition', 'ui_mandatory',
                                                             'ui_enabled', 'ui_read_only', 'ui_default_callable',
                                                             'ui_field_validation_callable',
                                                             'ui_form_validation_callable', 'ui_label', 'ui_label_en',
                                                             'csv_mandatory', 'csv_default_callable',
                                                             'csv_field_validation_callable',
                                                             'csv_form_validation_callable', 'codelist_validation'}
                for k in translated_keys:
                    # write to sheet if only value exist
                    if getattr(pa, k):
                        field_name, language = k.rsplit("_", 1)
                        # how do we restore value? based on pk
                        if field_name in pa_column_field_mapping and language != default_language:
                            blank_row = ['', ] * 17
                            blank_row[pa_column_field_mapping['id'] - 1] = pa.pk
                            blank_row[pa_column_field_mapping['pk'] - 1] = pa.pk
                            blank_row[pa_column_field_mapping['language'] - 1] = language
                            blank_row[pa_column_field_mapping[field_name] - 1] = getattr(pa, k)
                            ws1.append(blank_row)
                        else:
                            print("field name not found at mapping: ", field_name, k) if IMPORT_DEBUG else 0
            # now process product templates
            ws2 = wb.create_sheet()
            ws2.title = "template_data"

            pt_header = [
                "id",
                "pk",
                "language",
                "name",
                "order",
                "package_lavel",
                "attributes",
                "mo_slug",
                "image_url",
                "ui_label",
            ]
            ws2.append(pt_header)
            product_templates = ProductTemplate.objects.filter(member_organisation_id=mo.pk)

            for pt in product_templates:

                ws2.append([
                    pt.pk,
                    pt.pk,
                    default_language,
                    pt.name,
                    pt.order,
                    pt.package_level_id,
                    ", ".join(map(str, pt.attributes.all().values_list('pk', flat=True))),
                    pt.member_organisation.slug,
                    pt.image_url,
                    pt.ui_label
                ])

                translated_keys = set(pt.__dict__.keys()) - {'_state', 'id', 'name', "order", "package_level_id",
                                                             "member_organisation_id", "image_url", "ui_label",
                                                             "ui_label_en"}
                for k in translated_keys:
                    # write to sheet if only value exist
                    if getattr(pt, k):
                        field_name, language = k.rsplit("_", 1)
                        # how do we restore value? based on pk
                        if field_name in pt_column_field_mapping and language != default_language:
                            blank_row = ['', ] * 10
                            blank_row[pt_column_field_mapping['id'] - 1] = pt.pk
                            blank_row[pt_column_field_mapping['pk'] - 1] = pt.pk
                            blank_row[pt_column_field_mapping['language'] - 1] = language
                            blank_row[pt_column_field_mapping[field_name] - 1] = getattr(pt, k)
                            ws2.append(blank_row)
                        else:
                            print("field name not found at mapping: ", field_name, k) if IMPORT_DEBUG else 0
            wb.save(path)
