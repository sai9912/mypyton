from django.core.management import BaseCommand

from member_organisations.models import MemberOrganisation, ProductTemplate, ProductAttribute, ProductPackaging

IMPORT_DEBUG = True


class Command(BaseCommand):
    """
    python manage.py remove_templates
    """

    def add_arguments(self, parser):
        parser.add_argument('mo_slug', nargs='?', default='', type=str)

    def handle(self, *args, **options):
        mo_slug = options.get('mo_slug')
        try:
            mo = MemberOrganisation.objects.get(slug=mo_slug)
        except MemberOrganisation.DoesNotExist:
            pass
        else:
            product_templates = ProductTemplate.objects.filter(member_organisation_id=mo.pk)
            product_attributes = set()
            for template in product_templates:
                product_attributes |= set(template.attributes.all().values_list('pk', flat=True))

            # delete attributes
            ProductAttribute.objects.filter(id__in=product_attributes).delete()

            # delete templates
            product_templates_count = product_templates.count()
            product_templates.delete()

            if IMPORT_DEBUG and product_templates_count:
                print('{attr} ProductAttribute and {c} ProductTemplate related to {mo} are removed'
                      .format(attr=len(product_attributes), c=product_templates_count, mo=mo_slug))

            # delete orphaned attributes
            product_attributes = ProductAttribute.objects.filter(member_organisation_id=mo.pk)
            product_attributes_count = product_attributes.count()
            product_attributes.delete()
            if IMPORT_DEBUG and product_attributes_count:
                print('{attr} orphaned ProductAttribute related to {mo} are removed'
                      .format(attr=product_attributes_count, mo=mo_slug))

            # delete prod packaging too
            ProductPackaging.objects.filter(member_organisation=mo.pk).delete()
