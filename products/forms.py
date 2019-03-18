import json
from django import forms
from django.utils.translation import get_language, gettext as _

from barcodes import utilities as barcode_utilities
from core import flash
from .models.target_market import TargetMarket
from .models.country_of_origin import CountryOfOrigin
from .models.language import Language
from .models.dimension_uom import DimensionUOM
from .models.weight_uom import WeightUOM
from .models.product import Product
from .models.package_type import PackageType
from .models.net_content_uom import NetContentUOM


# used in /products/add or /products/<id>/edit
class PackageLevelForm(forms.Form):
    package_level = forms.ChoiceField(widget=forms.RadioSelect)

    def set_package_levels(self, rows):
        self.fields['package_level'].choices = [
            (str(row.id), row.level) for row in rows]


# used in /products/add/<id>/basic or /products/<id>/edit/basic
class PackageTypeForm(forms.Form):
    package_type = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}))
    bar_placement = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'bar_placement'}))

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', None)
        super().__init__(*args, **kwargs)

        if prefix:
            package_types = PackageType.objects.filter(
                ui_enabled=True, member_organisation=prefix.member_organisation
            ).order_by('code')

            self.fields['package_type'].choices = [
                (str(row.id), row.type) for row in package_types
            ]

def choices_countries_of_origin():
    rows = CountryOfOrigin.objects.order_by('name').all()
    choices = [(row.code, row.name) for row in rows]
    return choices


class ProductDetailForm(forms.Form):
    gtin = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'gtin'})
    )

    bar_placement = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'bar_placement'})
    )

    package_level = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'package_level'})
    )

    package_type = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'package_type'})
    )

    # Company Name
    company = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'company'}),
        required=False
    )
    company_i18n = forms.CharField(required=False)

    # Label Description
    label_description = forms.CharField(  # 'Label Description', [Required("Label Description: This field is required.")])
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'label_description'}),
        required=False
    )
    label_description_i18n = forms.CharField(required=False)

    # Brand
    brand = forms.CharField(  # 'Brand', [Required("Brand: This field is required.")])
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'brand'}),
        required=False
    )
    brand_i18n = forms.CharField(required=False)

    # Sub brand
    sub_brand = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'sub_brand'}),
        required=False
    )

    # Product Type/Functional Name
    functional_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'functional_name'}),
        required=False
    )
    functional_name_i18n = forms.CharField(required=False)

    # Variant
    variant = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'variant'}),
        required=False
    )

    # Product/Trade Item Description
    description = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'id': 'description'}),
        required=False
    )
    description_i18n = forms.CharField(required=False)

    # Global Product Classification
    category = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'category'}),
        required=True
    )

    # Company/Internal Product Code or SKU
    sku = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'sku'}),
        required=False
    )

    # Country Of Origin
    country_of_origin = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'country_of_origin'}),
        choices=lambda: [(row.code, row.name)
                         for row in CountryOfOrigin.objects.order_by('name').all()],
        required=False
    )

    # Target Market
    target_market = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'target_market'}),
        choices=lambda: [(row.code, row.market)
                         for row in TargetMarket.objects.order_by('market')],
        required=False
    )

    # Language
    language = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'language'}),
        choices=lambda: [(row.slug, row.name)
                         for row in Language.objects.order_by('name')],
        required=False
    )

    # GLN of Information provider
    gln_of_information_provider = forms.CharField(  # '', [Regexp('^[0-9]{13}$', message="Should be 13 digits."), check_gln])
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'id': 'gln_of_information_provider'}),
        required=True
    )

    # The item is a Base Unit
    is_bunit = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'id': 'is_bunit'}),
        required = False
    )

    # The item is a Consumer Unit
    is_cunit = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'id': 'is_cunit'}),
        required = False
    )

    # The item is a Dispatch Unit
    is_dunit = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'id': 'is_dunit'}),
        required = False
    )

    # The item is a Variable Weight Product
    is_vunit = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'id': 'is_vunit'}),
        required = False
    )

    # The item is an Invoice Unit
    is_iunit = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'id': 'is_iunit'}),
        required = False
    )

    # The item is an Orderable Unit
    is_ounit = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'id': 'is_ounit'}),
        required = False
    )

    # Gross Weight
    gross_weight = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'id': 'gross_weight'}),
        required=False
    )
    gross_weight_uom = forms.ChoiceField(
        widget=forms.Select(
            attrs={'class': 'form-control', 'id': 'gross_weight_uom'}),
        choices=WeightUOM.service.get_form_choices,
        required=False
    )

    # Net Weight
    net_weight = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'id': 'net_weight'}),
        required=False
    )
    net_weight_uom = forms.ChoiceField(
        widget=forms.Select(
            attrs={'class': 'form-control', 'id': 'net_weight_uom'}),
        choices=WeightUOM.service.get_form_choices,
        required=False
    )

    # Depth
    depth = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'depth'}),
        required=False
    )
    depth_uom = forms.ChoiceField(
        widget=forms.Select(
            attrs={'class': 'form-control', 'id': 'depth_uom'}),
        choices=DimensionUOM.service.get_form_choices,
        required=False
    )

    # Width
    width = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'width'}),
        required=False
    )
    width_uom = forms.ChoiceField(
        widget=forms.Select(
            attrs={'class': 'form-control', 'id': 'width_uom'}),
        choices=DimensionUOM.service.get_form_choices,
        required=False
    )

    # Height
    height = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'id': 'height'}),
        required=False
    )
    height_uom = forms.ChoiceField(
        widget=forms.Select(
            attrs={'class': 'form-control', 'id': 'height_uom'}),
        choices=DimensionUOM.service.get_form_choices,
        required=False
    )

    # External image URL (if hosted)
    website_url = forms.URLField(  # URLField('', [Optional(), URL(require_tld=True, message=u'Invalid URL.')])
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'id': 'website_url'}),
        required=False
    )

    @staticmethod
    def get_current_language():
        current_language = get_language()
        # get_language can return language in the following format: 'en-us'
        if current_language and '-' in current_language:
            current_language = current_language[0:current_language.find('-')]
            current_language = current_language.lower()

        return current_language or 'en'

    def full_clean(self):
        """
        Used for i18n fields
        """

        super().full_clean()

        if not hasattr(self, 'cleaned_data'):
            return

        i18n_keys = [key for key in self.cleaned_data.keys() if '_i18n' in key]
        for i18n_key in i18n_keys:
            # 1. if i18n fields are set, skip data converting
            # in other words i18n fields have a higher priority
            if self.cleaned_data[i18n_key]:
                continue

            # 2. find a non localized field and covert it to i18n json field
            field_name = [
                item for item in self.cleaned_data.keys()
                if i18n_key.startswith(item) and item != i18n_key
            ]
            if field_name:
                field_name = field_name[0]
            else:
                continue

            self.cleaned_data[i18n_key] = json.dumps({
                # double 'en' will be removed if 'en' is current
                'en': self.cleaned_data[field_name],
                self.get_current_language(): self.cleaned_data[field_name],
            })

    def is_valid(self, show_flash=False):
        '''
        Validation function, we are not using djando validation
        :return:
        '''

        verified = super(ProductDetailForm, self).is_valid()

        gtin = '0' + self.data.get('gtin', '')  # todo: check this '0'

        if not barcode_utilities.isValid(gtin) and len(gtin) != 14:
            if show_flash:
                flash(show_flash, 'You entered a non valid GTIN number (error #001)', 'danger')
            self.errors['gtin'] = ('You entered a non valid GTIN number (error #001)',)
            verified = False

        # bar_placement
        # package_level_id = self.data.get('package_level_id', None)
        # package_type_id = self.data.get('package_type_id', None)

        # Company Name
        # company = self.data.get('company', None)

        # Label Description
        label_description = self.data.get('label_description', None)
        if not label_description:
            if show_flash:
                flash(show_flash, 'Label description field is required.', 'danger')
            self.errors['label_description'] = ['This field is required.']
            verified = False

        # Brand
        brand = self.data.get('brand', None)
        if not brand:
            if show_flash:
                flash(show_flash, 'Brand field is required.', 'danger')
            self.errors['brand'] = ['This field is required.']
            verified = False

        # Sub brand
        # sub_brand = self.data.get('sub_brand', None)

        # Product Type/Functional Name
        functional_name = self.data.get('functional_name', None)
        if not functional_name:
            if show_flash:
                flash(
                    show_flash, 'Product Type/Functional Name field is required.', 'danger')
            self.errors['functional_name'] = ['This field is required.']
            verified = False

        # Variant
        # variant = self.data.get('variant', None)

        # Product/Trade Item Description
        description = self.data.get('description', None)
        if not description:
            if show_flash:
                flash(
                    show_flash, 'Product/Trade Item Description field is required.', 'danger')
            self.errors['description'] = ['This field is required.']
            verified = False

        # Global Product Classification
        category = self.data.get('category', None)
        if not category:
            if show_flash:
                flash(
                    show_flash, 'Global Product Classification field is required.', 'danger')
            self.errors['category'] = ['This field is required.']
            verified = False

        # Company/Internal Product Code or SKU
        # sku = self.data.get('sku', None)

        # Country Of Origin
        # country_of_origin = self.data.get('country_of_origin', None)

        # Target Market
        # target_market = self.data.get('target_market', None)

        # Language
        # language = self.data.get('language', None)

        # GLN of Information provider
        # gln_of_information_provider = self.data.get('gln_of_information_provider', None)

        # The item is a Base Unit
        # is_bunit = self.data.get('is_bunit', False)

        # The item is a Consumer Unit
        is_cunit = True if self.data.get('is_cunit', False) else False
        # The item is a Dispatch Unit
        is_dunit = True if self.data.get('is_dunit', False) else False
        # The item is a Variable Weight Product
        is_vunit = True if self.data.get('is_vunit', False) else False
        # The item is an Invoice Unit
        is_iunit = True if self.data.get('is_iunit', False) else False
        # The item is an Orderable Unit
        is_ounit = True if self.data.get('is_ounit', False) else False
        if not (is_cunit or is_dunit or is_vunit or is_iunit or is_ounit):
            self.errors['optionalFields'] = [
                'Options: At least one option must be selected.']
            if show_flash:
                flash(
                    show_flash, 'Options: At least one option must be selected.', 'danger')
            verified = False

        # Gross Weight
        gross_weight = self.data.get('gross_weight', None)
        gross_weight_uom = self.data.get('gross_weight_uom', '')
        if gross_weight_uom != '':
            error_fl = False
            if gross_weight == '':
                error_fl = True
            try:
                if float(gross_weight) <= 0 or abs(float(gross_weight)) >= 10 ** 6:
                    error_fl = True
            except (ValueError, TypeError):
                error_fl = True
            if error_fl:
                error_message = 'Gross weight must be a positive number greater than zero and less than 1000000.00'
                self.errors['gross_weight'] = [error_message]
                if show_flash:
                    flash(show_flash, error_message, 'danger')
                verified = False

        # Net Weight
        net_weight = self.data.get('net_weight', None)
        net_weight_uom = self.data.get('net_weight_uom', '')
        if net_weight_uom != '':
            error_fl = False
            if net_weight == '':
                error_fl = True
            try:
                if float(net_weight) <= 0 or abs(float(net_weight)) >= 10 ** 6:
                    error_fl = True
            except (ValueError, TypeError):
                error_fl = True
            if error_fl:
                error_message = 'Net weight must be a positive number greater than zero and less than 1000000.00'
                self.errors['net_weight'] = [error_message]
                if show_flash:
                    flash(show_flash, error_message, 'danger')
                verified = False

        # Depth
        depth = self.data.get('depth', None)
        depth_uom = self.data.get('depth_uom', '')
        if depth_uom != '':
            error_fl = False
            if depth == '':
                error_fl = True
            try:
                if float(depth) <= 0 or abs(float(depth)) >= 10 ** 6:
                    error_fl = True
            except (ValueError, TypeError):
                error_fl = True
            if error_fl:
                error_message = 'Depth must be a positive number greater than zero and less than 1000000.00'
                self.errors['depth'] = [error_message]
                if show_flash:
                    flash(show_flash, error_message, 'danger')
                verified = False

        # Width
        width = self.data.get('width', None)
        width_uom = self.data.get('width_uom', '')
        if width_uom != '':
            error_fl = False
            if width == '':
                error_fl = True
            try:
                if float(width) <= 0 or abs(float(width)) >= 10 ** 6:
                    error_fl = True
            except (ValueError, TypeError):
                error_fl = True
            if error_fl:
                error_message = 'Width must be a positive number greater than zero and less than 1000000.00'
                self.errors['width'] = [error_message]
                if show_flash:
                    flash(show_flash, error_message, 'danger')
                verified = False

        # Height
        height = self.data.get('height', None)
        height_uom = self.data.get('height_uom', '')
        if height_uom != '':
            error_fl = False
            if height == '':
                error_fl = True
            try:
                if float(height) <= 0 or abs(float(height)) >= 10 ** 6:
                    error_fl = True
            except (ValueError, TypeError):
                error_fl = True
            if error_fl:
                error_message = 'Height must be a positive number greater than zero and less than 1000000.00'
                self.errors['height'] = [error_message]
                if show_flash:
                    flash(show_flash, error_message, 'danger')
                verified = False

        # External image URL (if hosted)
        # website_url = self.data.get('website_url', None)

        '''
        (TODO)
        if form.package_level_id.data == str(PackageLevel.BASE) and hasattr(form, 'net_weight'):
            if form.net_weight_uom.data and not form.net_weight.data:
                form.net_weight.errors = [error]
                found_error = True
            try:
                if float(form.net_weight.data) <= 0 or abs(float(form.net_weight.data)) >= 10 ** 6:
                    form.net_weight.errors = [error]
                    found_error = True
            except (ValueError, TypeError):
                form.net_weight.data = None

        if form.package_level_id.data == str(
                PackageLevel.BASE) and form.net_content_uom.data and not form.net_content.data:
            form.net_content.errors = [error]
            found_error = True
        try:
            if form.package_level_id.data == str(PackageLevel.BASE) and (
                    float(form.net_content.data) <= 0 or abs(float(form.net_content.data)) >= 10 ** 6):
                form.net_content.errors = [error]
                found_error = True
        except (ValueError, TypeError):
            form.net_content.data = None
        '''

        return verified and super().is_valid()

'''
def check_values(request, template_name, form, **kwargs):
    error = 'It must be a positive number greater than zero and less than 1000000.00'
    found_error = False
    if form.depth_uom.data and not form.depth.data:
        form.depth.errors = [error]
        found_error = True
    try:
        if float(form.depth.data) <= 0 or abs(float(form.depth.data)) >= 10 ** 6:
            form.depth.errors = [error]
            found_error = True
    except (ValueError, TypeError):
        form.depth.data = None
    if form.width_uom.data and not form.width.data:
        form.width.errors = [error]
        found_error = True
    try:
        if float(form.width.data) <= 0 or abs(float(form.width.data)) >= 10 ** 6:
            form.width.errors = [error]
            found_error = True
    except (ValueError, TypeError):
        form.width.data = None
    if form.height_uom.data and not form.height.data:
        form.height.errors = [error]
        found_error = True
    try:
        if float(form.height.data) <= 0 or abs(float(form.height.data)) >= 10 ** 6:
            form.height.errors = [error]
            found_error = True
    except (ValueError, TypeError):
        form.height.data = None

    if found_error:
        return render(request, template_name, form=form, **kwargs)
'''


class FilterForm(forms.Form):
    base = forms.BooleanField(                              # Base unit
        required=False,
        initial=True
    )

    pack = forms.BooleanField(                              # Inner pack
        required=False,
        initial=True
    )

    case = forms.BooleanField(                              # Case
        required=False,
        initial=True
    )

    pallet = forms.BooleanField(                            # Pallet
        required=False,
        initial=True
    )

    # mixed_module = BooleanField('Mixed module', default='False')

    display_shipper = forms.BooleanField(                   # Display shipper
        required=False,
        initial=True
    )

    # transport_load = BooleanField('Transport load', default='False')

    brand = forms.CharField(                                # Brand
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Brand'}),
        required=False
    )

    gtin = forms.CharField(                                 # GTIN
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'GTIN'}),
        required=False
    )

    description = forms.CharField(                          # Description
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Description'}),
        required=False
    )

    sku = forms.CharField(                                  # SKU
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'SKU'}),
        required=False
    )

    target_market = forms.ChoiceField(                      # Target market field
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=(('tm1', 'TM1'),
                 ('tm2', 'TM2'),
                 ('tm3', 'TM3')),
        # initial='tm3',
        required=False
    )

    sort_field = forms.ChoiceField(                         # Sort field
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=(('gtin', 'GTIN'),
                 ('sku', 'SKU'),
                 ('description', 'Description'),
                 ('created', 'Created'),
                 ('updated', 'Updated')),
        initial='gtin',
        required=False
    )

    sort_mode = forms.ChoiceField(                          # Sort direction
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=(('asc', _('Ascending')),
                 ('desc', _('Descending'))),
        initial='desc',
        required=False
    )

    prefixes = forms.ChoiceField(                           # Prefixes
         widget=forms.Select(attrs={'class': 'form-control', 'style': 'display:inline;width:inherit'}),
         choices=( ('0', 'All'), ),
         initial='0',        # We only search in active prefix
         required = False
    )

    mark = forms.BooleanField(                              # Mark
        required=False,
        initial=False
    )

    def set_prefixes(self, rows):
        self.fields['prefixes'].choices[1:] = []
        self.fields['prefixes'].choices.extend(
            [(str(row.prefix), str(row.prefix)) for row in rows]
        )
        self.base_fields['prefixes'].choices[1:] = []
        self.base_fields['prefixes'].choices.extend(
            [(str(row.prefix), str(row.prefix)) for row in rows]
        )


class ProductForm(ProductDetailForm):
    package_type = forms.ChoiceField(
        widget=forms.Select(
            attrs={'class': 'form-control', 'id': 'package_type'}),
        choices=PackageType.service.get_form_choices,
        required=False
    )

    package_level = forms.ChoiceField(
        widget=forms.Select(
            attrs={'class': 'form-control', 'id': 'package_level'}),
        # choices=PackageLevel.service.get_form_choices,
        required=False
    )

    # Net Content
    net_content = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'id': 'net_content'}),
        required=False
    )
    net_content_uom = forms.ChoiceField(
        widget=forms.Select(
            attrs={'class': 'form-control', 'id': 'net_content_uom'}),
        choices=NetContentUOM.service.get_form_choices(),
        required=False
    )

    # Current state
    gs1_cloud_state = forms.ChoiceField(
        widget=forms.Select(
            attrs={'class': 'form-control', 'id': 'net_content_uom'}),
        choices=[('ACTIVE', 'ACTIVE'), ('INACTIVE', 'INACTIVE')],
        required=False
    )

    def __init__(self, data, **kwargs):

        super(ProductForm, self).__init__(data)

        if isinstance(data, Product):
            product = data
            data = {}
            for field in product._meta.get_fields():
                try:
                    if field.name in ['net_weight_uom', 'gross_weight_uom']:
                        data[field.name] = getattr(product, field.name).code
                    elif field.name in ['depth_uom', 'width_uom', 'height_uom', 'net_content_uom',]:
                        data[field.name] = getattr(product, field.name).code
                    elif field.name in ['country_of_origin', 'target_market']:
                        data[field.name] = getattr(product, field.name).code
                    elif field.name == 'language':
                        data[field.name] = getattr(product, field.name).slug
                    elif field.name == 'package_type':
                        data[field.name] = getattr(product, field.name).code
                    else:
                        data[field.name] = getattr(product, field.name)
                except:
                    data[field.name] = ''

        super().__init__(data)


class SubProductsForm(forms.Form):
    sub_products = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'sub_products'}),
        required=False
    )


class ProductCaseForm(ProductDetailForm):
    pass


class ProductCaseDetailForm(ProductCaseForm):
    # GLN of Information provider
    pass
