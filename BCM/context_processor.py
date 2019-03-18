from .models import Language, LanguageByCountry
from django.conf import settings

def add_languages(request):
    context_data = {}
    if request.user.is_authenticated:
        try:
            country = request.user.profile.member_organisation.country
            language_by_country = country.languagebycountry_set.order_by('-default', 'language')
            languages = [item.language for item in language_by_country]
        except: # AttributeError:
            # GO admin might not have MO set, so no country
            languages = Language.objects.all()
        else:
            if language_by_country and language_by_country.first().default:
                # we have a default language for a country
                context_data['languages'] = languages
                return context_data
    else:
        languages = Language.objects.all()

    # move english to the first place if no default language was detected by a country
    # (otherwise all will see interface in German language by default)
    english = [language for language in languages if language.slug == 'en']
    if english:
        languages = english + [language for language in languages if language.slug != 'en']

    context_data['languages'] = languages
    return context_data

def global_settings(request):
    return {
        'DJANGO_ENV': settings.ENV,
    }
