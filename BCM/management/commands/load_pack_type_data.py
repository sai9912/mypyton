import json

from os.path import join

from django.core.management import BaseCommand

import openpyxl

from member_organisations.models import MemberOrganisation, ProductPackaging
from products.models.package_type import PackageType

IMPORT_DEBUG = False


class Command(BaseCommand):
    # load_pack_type_data
    help = "Command to load packaging type data"

    def add_arguments(self, parser):
        parser.add_argument('excel_file', nargs='?', default='deployment/deployment-v1-2018-03/UI_presets_v2.xlsx',
                            type=str)

    def handle(self, *args, **options):
        file = options['excel_file']
        wb2 = openpyxl.load_workbook(file)
        package_type_sheet = wb2['package_types']
        print('*' * 80) if IMPORT_DEBUG else 0
        print("Running Load Package Type Data Command. Initial Object Count: {count}".format(
                count=ProductPackaging.objects.count())) if IMPORT_DEBUG else 0
        for index, row in enumerate(package_type_sheet.iter_rows()):
            if index == 0:
                continue
            # field preset at excel sheet
            # locale	package_type	image_url	description	ui_label_translated
            mo_slug = row[0].value
            package_level_id = row[1].value
            package_code = row[2].value
            locale = row[3].value
            image_url = row[5].value
            # package type and description are different as per locale for same product
            package_type = row[4].value
            description = row[6].value
            # what is the use of this field?
            ui_label_translated = row[7].value
            if not (mo_slug or package_level_id or package_code or package_type):
                continue
            mo_slug = mo_slug.lower()
            package_code = package_code.lower()

            try:
                mo = MemberOrganisation.objects.get(slug=mo_slug)
            except MemberOrganisation.DoesNotExist:
                print("member organization doesnot exit: ", mo_slug) if IMPORT_DEBUG else 0
            else:
                name = "{mo_slug}-{code}-{package_level_id}".format(
                        code=package_code,
                        mo_slug=mo_slug,
                        package_level_id=package_level_id)

                if not name or not package_level_id:
                    # name and package_level are required field so
                    continue

                package_code_obj, created = PackageType.objects.get_or_create(code=package_code)

                pp, created = ProductPackaging.objects.get_or_create(
                        package_level_id=package_level_id,
                        member_organisation_id=mo.pk,
                        package_type_id=package_code_obj.pk,

                        defaults=dict(
                                name=name,
                        )
                )
                if image_url:
                    pp.image_url = image_url

                if not pp.ui_label:
                    # set first language label as primary label
                    pp.ui_label = package_type or ''
                if not pp.ui_description:
                    # set first language description as primary description
                    pp.ui_description = description or ''

                if locale:
                    label_key = 'ui_label_{language}'.format(language=locale)
                    setattr(pp, label_key, package_type)

                    description_key = 'ui_description_{language}'.format(language=locale)
                    setattr(pp, description_key, description)
                pp.save()

        print("Loading Package TypeData Completed. Final Count: {count}".format(
                count=ProductPackaging.objects.count()
        )) if IMPORT_DEBUG else 0
        print('*' * 80) if IMPORT_DEBUG else 0
