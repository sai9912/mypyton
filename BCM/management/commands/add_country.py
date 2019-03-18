from countries_plus.models import Country
from django.core.management.base import BaseCommand
from languages_plus.utils import associate_countries_and_languages

from BCM.models import Country as MO_country, Language as MO_language, LanguageByCountry
from member_organisations.models import MemberOrganisation



class Command(BaseCommand):
    """

    management command to load company users (similar as in BCM/flask app

    """

    help = "Creates MO country, languages and MO from CLI"

    def add_arguments(self, parser):
        parser.add_argument('iso3', nargs='?', type=str)

    def handle(self, *args, **options):
        associate_countries_and_languages()

        iso3 = options['iso3']
        country = Country.objects.get(iso3=iso3)

        # create country
        mo_country, country_created = MO_country.objects.get_or_create(name=country.name, slug=country.iso)

        # create first language
        primary_language = country.primary_language()
        mo_language, language_created = MO_language.objects.get_or_create(slug=primary_language.iso,
                                                                          name=primary_language.name)
        # associate language and country
        LanguageByCountry.objects.get_or_create(language=mo_language, country=mo_country)

        # create MO organisation
        mo_name = "GS1 {}".format(country.name)
        mo_slug = "gs1{}".format(country.iso).lower()
        LanguageByCountry.objects.get_or_create(language=mo_language, country=mo_country)
        member_organisation, mo_created = MemberOrganisation.objects.get_or_create(slug=mo_slug,
                                                                                   defaults={'name': mo_name,
                                                                                             'country': mo_country})
        if mo_created and mo_slug != member_organisation.slug:
            member_organisation.slug = mo_slug
            member_organisation.save()
