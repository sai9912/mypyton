from countries_plus.models import Country
from django.core.management.base import BaseCommand

from BCM.models import Country as MO_country


class Command(BaseCommand):
    """
    management command to load countries
    """

    help = "Sync all countries from countries_plus into BCM_country"

    def handle(self, *args, **options):
        idx = 0
        for country in Country.objects.all():
            mo_country, country_created = MO_country.objects. \
                get_or_create(slug=country.iso, defaults={'name': country.name})
            if country_created:
                idx += 1
        print('created %d countries' % idx)
