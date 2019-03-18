
from django.core.management import BaseCommand

import openpyxl

from member_organisations.models import MemberOrganisation, ProductTemplate


IMPORT_DEBUG = False


class Command(BaseCommand):
    # load_pack_level_data
    help = "Command to load packaging level translations"

    def add_arguments(self, parser):
        parser.add_argument('excel_file', nargs='?', default='deployment/deployment-v1-2018-03/UI_presets_v1.xlsx',
                            type=str)

    def handle(self, *args, **options):
        file = options['excel_file']
        wb2 = openpyxl.load_workbook(file)
        package_level_sheet = wb2['package_levels']
        print('*'*80) if IMPORT_DEBUG else 0
        print("Running Load Package Level Data Command. Initial Object Count: {count}".format(
                count=ProductTemplate.objects.count())) if IMPORT_DEBUG else 0
        print("Creating Fixture ....") if IMPORT_DEBUG else 0

        for index, row in enumerate(package_level_sheet.iter_rows()):
            if index == 0:
                continue

            name = row[0].value
            mo_slug = row[1].value
            package_level_id = row[2].value
            language = row[3].value
            image_url = row[4].value
            ui_label = row[5].value
            ui_label_translated = row[6].value
            if not (name or mo_slug or package_level_id or language or image_url or ui_label or ui_label_translated):
                continue

            mo_slug = mo_slug.lower()
            name = name.lower()

            try:
                mo = MemberOrganisation.objects.get(slug=mo_slug)
            except MemberOrganisation.DoesNotExist:
                print("member organization doesnot exit: ", mo_slug)
            else:
                if not name or not package_level_id:
                    # name and package_level are required field so
                    continue

                pt, created = ProductTemplate.objects.get_or_create(
                        member_organisation_id=mo.pk,
                        name=name,
                        package_level_id=package_level_id)
                if image_url:
                    pt.image_url = image_url

                if not pt.ui_label:
                    # if ui_label is not set first then set it other wise don't change it
                    pt.ui_label = ui_label
                if language:
                    key = 'ui_label_{cd}'.format(cd=language)
                    setattr(pt, key, ui_label)
                pt.save()

        print("Loading Package Level Data Completed. Final Count: {count}".format(
                count=ProductTemplate.objects.count()
        )) if IMPORT_DEBUG else 0
        print('*'*80) if IMPORT_DEBUG else 0