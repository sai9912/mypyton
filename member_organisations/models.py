from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from knox.models import AuthToken
from organizations.abstract import (
    AbstractOrganization, AbstractOrganizationUser, AbstractOrganizationOwner
)

from BCM.helpers.translation_helpers import TranslatedFieldsMixin
from BCM.models import Country
from BCM.models import LanguageByCountry


class MemberOrganisation(AbstractOrganization):
    """
    GS1 Member Organisation
    """

    country = models.OneToOneField(
        to=Country,
        related_name="member_organisation",
        primary_key=True,
        on_delete=models.CASCADE,
    )
    gs1_prefix_regex = models.CharField(
        verbose_name='GS1_PREFIX_REGEX',
        max_length=100,
        default='.*'
    )
    # logo
    gs1_logo_path = models.CharField(
        verbose_name='gs1_logo_path',
        max_length=100,
        default='/static/site/logo/gs1-logo.png'
    )
    gs1_logo_height = models.CharField(
        verbose_name='gs1_logo_height',
        max_length=20,
        default='105px'
    )
    gs1_logo_width = models.CharField(
        verbose_name='gs1_logo_width',
        max_length=20,
        default='171px'
    )

    gs1_cloud_username = models.CharField(
        verbose_name='GS1_CLOUD_USERNAME',
        max_length=100,
        default='',
        blank=True
    )
    gs1_cloud_secret = models.CharField(
        verbose_name='GS1_CLOUD_SECRET',
        max_length=100,
        default='',
        blank=True
    )
    # previously known as "gs1_cloud_ip_gln"
    gs1_cloud_ds_gln = models.CharField(
        verbose_name='GS1_CLOUD_DS_GLN',
        max_length=100,
        default='',
        blank=True
    )
    gs1_cloud_endpoint = models.CharField(
        verbose_name='GS1_CLOUD_ENDPOINT',
        max_length=100,
        default='https://cloud.stg.gs1.org/api/v1/',
        blank=True
    )
    gs1_cloud_disclaimer = models.TextField(
        verbose_name=_('GS1 Cloud Disclaimer'), default='TODO: add text ...'
    )
    gs1_barcode_production_disclaimer = models.TextField(
        verbose_name=_('GS1 Barcode Production Disclaimer'),
        default='TODO: add text ...'
    )
    simplified_barcode_generation = models.BooleanField(default=True)
    gs1_enable_clone_button = models.BooleanField(default=False)
    gs1_enable_cloud_opt_out = models.BooleanField(default=False)

    # training
    gs1_help_url_1 = models.CharField(max_length=100, default='/')
    gs1_help_label_1 = models.CharField(max_length=100, default='Training and Resources')

    # support
    gs1_help_url_2 = models.CharField(max_length=100, default='/')
    gs1_help_label_2 = models.CharField(max_length=100, default='Support')

    # help
    gs1_help_url_3 = models.CharField(max_length=100, default='/')
    gs1_help_label_3 = models.CharField(max_length=100, default='Help')

    # gs1 control panel
    gs1_dashboard_url = models.CharField(
        max_length=100, default='https://www.gs1.org/services/activate'
    )
    gs1_dashboard_label = models.CharField(
        max_length=100, default=_('GS1 Dashboard')
    )

    # logo
    gs1_logo_url = models.CharField(max_length=100, default='/')

    # logout
    gs1_logout_url = models.CharField(max_length=100, default='/')

    gs1_enable_advanced_dashboard = models.BooleanField(default=False)
    gs1_enable_user_settings = models.BooleanField(default=False)
    gs1_enable_import_export = models.BooleanField(default=False)
    gs1_disable_hiearchy = models.BooleanField(default=False)
    gs1_disable_pdf_labels = models.BooleanField(default=False, editable=False)
    gs1_enable_pdf_print_summary = models.BooleanField(default=False, editable=False)

    gs1_terms_enable = models.BooleanField(default=False)  # shows 'agree to terms' for the new users
    gs1_terms_updated = models.DateField(null=True, blank=True)  # terms updated date
    gs1_terms_version = models.CharField(max_length=20, null=True, blank=True)  # terms version

    login_api_secure = models.BooleanField(default=False)
    barcode_credits = models.BooleanField(default=False)
    login_api_auth_only = models.BooleanField(default=False)
    show_leading_digit = models.BooleanField(default=True)  # shows leading digit for GTIN14 in BASE
    display_prefix_as_range = models.BooleanField(default=True)  # shows prefix as range, UI top-right
    display_prefix_info = models.BooleanField(default=True)  # displays prefix orange info-box
    display_account_info = models.BooleanField(default=True)  # displays grey account info-box

    class Meta:
        verbose_name = 'Member organisation'

    def get_default_language_slug(self):
        language_for_mo = LanguageByCountry.objects.filter(country=self.country)
        language_count = language_for_mo.count()
        default_language = None
        if language_count:
            default_language = language_for_mo.first().language
        elif language_count > 1:
            if language_for_mo.filter(default=True).exists():
                default_language = language_for_mo.filter(default=True).first().language
            else:
                default_language = language_for_mo.first().language
        return default_language.slug.lower() if default_language else 'en'


class MemberOrganisationUser(AbstractOrganizationUser):
    def clean(self):
        super().clean()
        user_member_organisations = self.user.member_organisations_memberorganisation.all()
        if not self.pk and user_member_organisations:
            raise ValidationError(
                _('User can\'t have multiple organizations, '
                  'assigned organizations: {organizations}'.format(
                    organizations=', '.join([f'"{mo.slug}"' for mo in user_member_organisations])
                ))
            )

    def __str__(self):
        return f'"{self.user}" user of "{self.organization}"'

    class Meta:
        verbose_name = "MO staff"
        verbose_name_plural = "MO staff"


class MemberOrganisationOwner(AbstractOrganizationOwner):
    def __str__(self):
        return f'"{self.organization_user.user}" owner of "{self.organization}"'

    class Meta:
        verbose_name = "MO admin"


class ProductTemplate(models.Model, TranslatedFieldsMixin):
    name = models.CharField(
        verbose_name='Name',
        max_length=100
    )
    order = models.IntegerField(
        verbose_name='Order',
        default=0
    )
    package_level = models.ForeignKey(
        to='products.PackageLevel',
        on_delete=models.CASCADE
    )
    attributes = models.ManyToManyField(
        to='member_organisations.ProductAttribute',
        related_name='product_templates'
    )
    member_organisation = models.ForeignKey(
        to='member_organisations.MemberOrganisation',
        related_name='product_templates',
        on_delete=models.CASCADE
    )
    image_url = models.URLField(
        verbose_name='Image URL',
        max_length=250,
        blank=True
    )
    ui_label_i18n = models.TextField(
        'UI label',
        default='{}')

    def __str__(self):
        return f'{self.name}'

    def get_ui_mandatory_attributes(self):
        return self.attributes.filter(ui_mandatory=True)

    def get_csv_mandatory_attributes(self):
        return self.attributes.filter(csv_mandatory=True)

    def get_all_form_validators(self):
        return {
            x.csv_form_validation_callable
            for x in self.attributes.exclude(csv_form_validation_callable="")
        }

    @cached_property
    def attributes_dict(self):
        attributes = serializers.serialize('python', self.attributes.all())
        attributes = {
            item['fields']['path'].split('.')[-1]: item['fields']
            for item in attributes
        }
        return attributes


class ProductAttribute(models.Model, TranslatedFieldsMixin):
    path = models.CharField(
        verbose_name='Path',
        max_length=250,
        default=''
    )
    definition_i18n = models.TextField(
        verbose_name='Definition'
    )

    member_organisation = models.ForeignKey(
        to='member_organisations.MemberOrganisation',
        related_name='product_attributes',
        on_delete=models.CASCADE,
        null=True,
    )

    # -- UI part --

    ui_mandatory = models.BooleanField(
        verbose_name='Is UI mandatory',
        default=True
    )
    ui_enabled = models.BooleanField(
        verbose_name='Is UI enabled',
        default=True
    )
    ui_read_only = models.BooleanField(
        verbose_name='Is UI read only',
        default=False
    )

    # a custom callable to be used when field
    # is not provided (example: default GLN)
    ui_default_callable = models.CharField(
        verbose_name='UI default callable',
        max_length=100,
        default='',
        blank=True
    )

    # a custom callable to be used when validating the field
    ui_field_validation_callable = models.CharField(
        verbose_name='UI field validation callable',
        max_length=100,
        default='',
        blank=True
    )

    # a custom callable to be used when validation the form
    ui_form_validation_callable = models.CharField(
        verbose_name='UI form validation callable',
        max_length=100,
        default='',
        blank=True
    )

    ui_label_i18n = models.TextField(
        verbose_name='UI label',
        default='{}'
    )

    # -- CSV part --

    csv_mandatory = models.BooleanField(
        verbose_name='CSV mandatory',
        default=True
    )

    # a custom callable to be used when field is not provided
    #  (example: default GLN or company name)
    csv_default_callable = models.CharField(
        verbose_name='CSV default callable',
        max_length=100,
        default='',
        blank=True
    )

    # a custom callable to be used when validating the field
    csv_field_validation_callable = models.CharField(
        verbose_name='CSV field validation callable',
        max_length=100,
        default='',
        blank=True
    )

    # a custom callable to be used when validating the form
    csv_form_validation_callable = models.CharField(
        verbose_name='CSV form validation callable',
        max_length=100,
        default='',
        blank=True
    )

    # -- validation code-list for both UI and CSV import --
    codelist_validation = models.CharField(
        verbose_name='codelist validation',
        max_length=100,
        default='',
        blank=True
    )

    def __str__(self):
        return f'{self.path}'

    def get_fieldname(self):
        return self.path.split(".")[-1]


class ProductPackaging(models.Model, TranslatedFieldsMixin):
    code = models.CharField(max_length=10, default='')
    order = models.IntegerField(verbose_name='Order', default=0)
    member_organisation = models.ForeignKey(
        to='member_organisations.MemberOrganisation',
        related_name='product_packaging',
        on_delete=models.CASCADE
    )
    image_url = models.TextField(
        verbose_name='Image URL',
        max_length=250,
        blank=True
    )
    ui_label_i18n = models.TextField(verbose_name='UI label', default='{}')
    ui_description_i18n = models.TextField(
        verbose_name='UI description',
        default='{}'
    )
    package_type = models.ForeignKey(
        to='products.PackageType',
        related_name='product_packaging',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Product packaging"
        verbose_name_plural = "Product packaging"

    def __str__(self):
        return f'{self.code}'


class M2MToken(models.Model):
    description = models.CharField(
        verbose_name='Description',
        max_length=250,
        default=''
    )
    token = models.OneToOneField(
        to=AuthToken,
        on_delete=models.PROTECT,
        related_name='m2m_tokens'
    )

    def __str__(self):
        return f'{self.description} - {self.token.user}'

    def delete(self, using=None, keep_parents=False):
        deletion_result = super().delete(using, keep_parents)
        if self.token:
            self.token.delete()
        return deletion_result


class MemberOrganisationRelation(models.Model):
    """
    This model allows to filter UOM (or any other model instance) by a member organisation.
    """

    member_organisation = models.ForeignKey(
        'member_organisations.MemberOrganisation',
        related_name='memberorganisation_relations',
        on_delete=models.CASCADE
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey('content_type', 'object_id')
