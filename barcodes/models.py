from django.db import models


class ServiceManager(models.Manager):
    """
    >>> Label.objects.create(
    ...     code='code 1',
    ...     short_desc='short_desc 1',
    ...     description='description',
    ...     src='src',
    ...     template='template',
    ...     rows=1,
    ...     cols=1,
    ...     has_gap=False,
    ...     ratio=1,
    ...     width=1,
    ...     height=1)
    <Label: {short_desc 1}>
    >>> Label.service.get_form_choices()
    [('code 1', 'short_desc 1')]
    >>> Label.service.first(code='code 1')
    <Label: {short_desc 1}>
    >>> Label.service.first(code='code 2')
    """
    def get_form_choices(self):
        choices = [(row.code, row.short_desc) for row in Label.objects.order_by('pk')]
        return choices

    def first(self, code):
        try:
            label = Label.objects.get(code=code)
        except:
            return None
        return label


class Label(models.Model):
    code = models.CharField(max_length=15)
    short_desc = models.CharField(max_length=50)
    description = models.TextField()
    src = models.TextField()
    template = models.TextField()
    rows = models.IntegerField()
    cols = models.IntegerField()
    has_gap = models.BooleanField()
    ratio = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()

    objects = models.Manager()
    service = ServiceManager()

    def __str__(self):
        return '{%s}' % self.short_desc


label_service = Label.service
