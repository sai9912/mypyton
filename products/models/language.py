from django.db import models


class ServiceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def get_id_from_code(self, slug):
        try:
            item = Language.objects.get(slug=slug)
        except Exception as e:
            return None
        return item.id

    def find_by_slug(self, slug):
        try:
            language = Language.objects.get(slug__iexact=slug)
        except Language.DoesNotExist:
            return None
        return language


class Language(models.Model):
    slug = models.CharField(max_length=5, db_index=True, unique=True, null=False)
    name = models.CharField(max_length=75, null=False)

    objects = models.Manager()
    service = ServiceManager()

    def __str__(self):
        return f'{self.name}'
