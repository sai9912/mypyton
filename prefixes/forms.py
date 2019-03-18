from django import forms

class PrefixActionForm(forms.Form):
    select_prefix = forms.ChoiceField(widget=forms.RadioSelect) #, choices=(
    #    ('1','539123123'),
    #    ('5','53900012'),
    #    ('6','53900011')
    #))
    prefix_action = forms.ChoiceField(widget=forms.RadioSelect, choices=(
        # item actions
        ('new_product', 'New Product'),
        ('new_product_js', 'New Product (VueJS version)'),
        ('starting_gtin', 'Starting GTIN'),
        ('set_this', 'Set this active'),
        ('first_available', 'Set to first available'),
        ('export_available', 'Export available GTINs'),

        # location actions
        ('new_gln', 'New Location'),
        ('starting_gln', 'Starting GLN'),
        ('set_this_gln', 'Set this active'),
        ('first_available_gln', 'Set to first available'),
        ('export_available_gln', 'Export available GTINs') )
    )


class StartingNumberForm(forms.Form):
    starting_number = forms.CharField(label='New Starting number', required=True)
