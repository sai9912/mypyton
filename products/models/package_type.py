from django.db import models

from BCM.helpers.translation_helpers import TranslatedFieldsMixin
from member_organisations.models import MemberOrganisation


class ServiceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def get_form_choices(self):
        choices = [(row.code, row.type) for row in PackageType.objects.order_by('code')]
        return choices

    def get_id_from_code(self, code):
        try:
            item = PackageType.objects.get(code=code)
        except Exception as e:
            return None
        return item.id


class PackageType(models.Model, TranslatedFieldsMixin):
    code = models.CharField(max_length=10, default='')
    type_i18n = models.TextField(default='{}')
    description_i18n = models.TextField(default='{}')
    member_organisation = models.ForeignKey(MemberOrganisation, null=True, on_delete=models.CASCADE)
    ui_enabled = models.BooleanField(default=False)
    image_path = models.CharField(max_length=70, default='')

    objects = models.Manager()
    service = ServiceManager()

    class Meta:
        unique_together = ('member_organisation', 'code')

    def __str__(self):
        return f'{self.code} ({self.member_organisation})'
