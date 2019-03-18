from django import forms
from .models import Label

class GenerateForm(forms.Form):
    """
    Form to generate images
    """
    resolution = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'resolution'}),
        choices=(( '300 dpi',  '300 dpi'),
                 ( '600 dpi',  '600 dpi'),
                 ('1200 dpi', '1200 dpi'),
                 ('2400 dpi', '2400 dpi')),
    )
    file_type = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={'class': 'file-type-li', 'id': 'file_type'}),
        choices=(('png', 'png'),
                 ('gif', 'gif'),
                 ('jpg', 'jpg'))
    )

    '''
    ps_type = RadioField(
        "filetype", 
        validators=[Optional()], 
        widget=h_checkbox, 
        choices=(('win', 'Windows'), ('mac', 'Mac'))
    )
    label_type = SelectField(
        'label type', 
        validators=[Optional()]
    )
    def set_label_types(self, rows):
        self.label_type.choices = [(str(row.code), row.short_desc) for row in rows]
    '''


class FormPS(forms.Form):
    ps_type = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={'class': 'file-type-li', 'id': 'ps_type'}),
        choices=(('win', 'Windows'), ('mac', 'Mac'))
    )


class FormPDF(forms.Form):
    label_type = forms.ChoiceField(
        widget = forms.Select(attrs={'class': 'form-control', 'id': 'label_type'}),
        choices = Label.service.get_form_choices
    )


def _bwr():
    """Formats possible bwr sizes.
    >>> bwr = _bwr()
    >>> bwr[0]
    ('0.0000', '0.0000')
    """
    a = ['0.0000', '0.0005', '0.0010', '0.0015 (printer resolution 600 dpi)',
         '0.0020', '0.0025', '0.0030',
         '0.0035 (printer resolution 300 dpi)', '0.0040', '0.0045', '0.0050']
    #,'0.0055', '0.0060', '0.0065', '0.0070', '0.0075', '0.0080', '0.0085',
    # '0.0090', '0.0095', '0.0100']
    return [(e.split()[0], e) for e in a]


def _ean_upc_sizes():
    """Formats possible magnification levels for EAN.UPC barcodes.
    >>> sizes = _ean_upc_sizes()
    >>> sizes[0]
    ('0.80', '0.80')
    """
    a = [
        '0.80', '0.85', '0.90', '0.95', '1.00', '1.05', '1.10', '1.15', '1.20',
        '1.25', '1.30', '1.35', '1.40',
        '1.45', '1.50', '1.55', '1.60', '1.65', '1.70', '1.75', '1.80', '1.85',
        '1.90', '1.95', '2.00'
    ]
    return [(e, '%s' % e) for e in a]


class PreviewFormAjax(forms.Form):
    size = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'size'}),
        choices=_ean_upc_sizes()
    )
    debug = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'id': 'debug'}),
        required=False
    )
    rqz = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'id': 'rqz'}),
        required=False
    )
    marks = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'id': 'marks'}),
        required=False
    )
    bwr = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'bwr'}),
        choices=_bwr()
    )
