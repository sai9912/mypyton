from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from BCM.helpers.translation_helpers import TranslatedFieldsMixin
from member_organisations.models import MemberOrganisationRelation


class ServiceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def get_form_choices(self):
        try:
            choices = [(row.abbr, row.uom) for row in NetContentUOM.objects.all()]
            choices.insert(0, ('', ''))
        except:
            return []
        return choices

    def get_id_from_code(self, code):
        try:
            item = NetContentUOM.objects.get(code=code)
        except Exception as e:
            return None
        return item.id


class NetContentUOM(models.Model, TranslatedFieldsMixin):
    # Net content unit of measure
    uom_i18n = models.CharField(max_length=200, default='')
    abbr = models.CharField(max_length=10, default='')
    code = models.CharField(max_length=10, default='')
    mo_relations = GenericRelation(MemberOrganisationRelation)
    objects = models.Manager()
    service = ServiceManager()

    def __str__(self):
        return self.uom
