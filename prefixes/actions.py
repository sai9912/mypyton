import csv
from django.http import HttpResponse

def export_as_csv_action(description="Export selected objects as CSV file",
                         fields=None, all_objects=False, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    >>> export_as_csv = export_as_csv_action(fields=['email'])
    >>> from django.contrib.auth.models import User
    >>> user = User.objects.create(email='root@root.r1231u', username='root123')
    >>> export_as_csv.short_description
    'Export selected objects as CSV file'
    >>> modeladmin = User.objects.all()
    >>> response = export_as_csv(modeladmin, None, queryset=User.objects.all())
    >>> response.content.startswith(b'email')
    True
    >>> export_as_csv = export_as_csv_action(all_objects=True, header=False)
    >>> response = export_as_csv(modeladmin, None, queryset=User.objects.all())
    >>> response.content.startswith(b'1,,None')
    True
    """
    def export_as_csv(modeladmin, request, queryset):

        opts = modeladmin.model._meta

        nonlocal fields

        if fields:
            field_names = [
                field.replace('__', ' ')
                for field in fields
            ]
        else:
            fields = [field.name for field in opts.fields]
            field_names = [
                field.replace('__', ' ')
                for field in fields
            ]

        response = HttpResponse()
        response['Content-Disposition'] = (
            'attachment; filename=%s.csv' % str(opts).replace('.', '_')
        )

        writer = csv.writer(response)

        if header:
            writer.writerow(field_names)

        if all_objects:
            if request:
                # for custom admin we need to have a filtered queryset
                changelist_instance = modeladmin.get_changelist_instance(request)
                queryset = changelist_instance.get_queryset(request)
            else:
                queryset = queryset.model.objects.all()

        for data in queryset.values_list(*fields):
            data = [str(i) for i in data]
            writer.writerow(data)
        return response

    export_as_csv.short_description = description
    return export_as_csv
