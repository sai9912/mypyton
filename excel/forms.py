from django import forms


EXPORT_CHOICES = (
    ('products', 'Export all products in this range'),
    ('starred', 'Export starred products in this range'),
    # ('GTIN', 'Export available GTINs '),
    # ('GTIN-with-attributes', 'Export available GTINs with attributes'),
)

EXPORT_FILE_TYPES = (
    ('xls', 'Excel xls'),
    ('xlsx', 'Excel xlsx'),
    ('ods', 'Open document ods'),
    ('csv', 'Comma seperated file csv'),
    ('json', 'json')
)


class ExportForm(forms.Form):

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop("queryset", None)
        super(ExportForm, self).__init__(*args, **kwargs)
        self.fields["available_templates"] = forms.ModelChoiceField(
            queryset=queryset,
            required=True,
            widget=forms.Select(
                attrs={'class': 'form-control', 'id': 'available_templates'})
        )

    export_type = forms.ChoiceField(
        widget = forms.Select(attrs={'class': 'form-control', 'id': 'export_type'}),
        choices = EXPORT_CHOICES,
        required = False
    )

    file_type = forms.ChoiceField(
        widget = forms.Select(attrs={'class': 'form-control', 'id': 'file_type'}),
        choices = EXPORT_FILE_TYPES,
        required = False
    )

    gepir_export = forms.BooleanField(
        widget = forms.CheckboxInput(attrs={'class': 'form-control', 'id': 'gepir_export'}),
        required = False
    )


class ImportForm(forms.Form):
    import_file = forms.FileField(
        widget = forms.FileInput(attrs={'class': 'form-control', 'id': 'import_file', 'accept': '.xlsx'}),
        required = True
    )
