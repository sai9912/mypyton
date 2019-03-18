from django import forms


class AgreeRequiredForm(forms.Form):
    url_next = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    terms_version = forms.CharField(
        widget=forms.HiddenInput(),
        required = False
    )
    agree = forms.BooleanField(initial=False)
