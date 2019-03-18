from django.contrib import admin
from .models import Country, Language, LanguageByCountry


class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ['name', 'slug']


class LanguageByCountryAdmin(admin.ModelAdmin):
    list_display = ('country', 'language', 'default')
    pass


admin.site.register(Country, CountryAdmin)
admin.site.register(Language)
admin.site.register(LanguageByCountry, LanguageByCountryAdmin)
