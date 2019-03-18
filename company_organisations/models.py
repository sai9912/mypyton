from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from django.db import models
from organizations.abstract import (AbstractOrganization,
                                    AbstractOrganizationUser,
                                    AbstractOrganizationOwner)

from BCM.models import Country
from member_organisations.models import MemberOrganisation


class CompanyOrganisation(AbstractOrganization):
    """
    Company Organisation
    """
    name = models.CharField(
        max_length=200,
        help_text=_("The name of the organization"),
        blank=True,
    )
    member_organisation = models.ForeignKey(MemberOrganisation, on_delete=models.CASCADE, related_name="companies")

    uuid = models.CharField(max_length=50, unique=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, default=None, null=True)
    company = models.CharField(max_length=100, default='', blank=True)

    street1 = models.CharField(max_length=100, default='')
    street2 = models.CharField(max_length=100, default='', blank=True)

    city = models.CharField(max_length=50, default='')
    state = models.CharField(max_length=50, default='', blank=True)
    zip = models.CharField(max_length=20, default='')
    phone = models.CharField(max_length=20, default='')
    gln = models.CharField(max_length=13, default='')
    vat = models.CharField(max_length=12, default='', blank=True)

    credit_points_balance = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    # users = db.relationship('User', back_populates='organisation')
    # prefixes = db.relationship('Prefix', back_populates='organisation', cascade='all, delete-orphan')

    prefix_override = models.CharField(
        max_length=100,
        default='',
        blank=True
    )  # to add additional prefixes overriding anything that DK sends

    gln_capability = models.BooleanField(default=False)

    def __str__(self):
        return "{} ({})".format(self.uuid, self.name)

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'


class CompanyOrganisationUser(AbstractOrganizationUser):

    def clean(self):
        super().clean()
        user_companies = self.user.company_organisations_companyorganisation.all()
        if not self.pk and user_companies:
            raise ValidationError(
                _('User can\'t have multiple companies, assigned companies: {companies}'.format(
                    companies=', '.join([f'"{company.uuid}"' for company in user_companies])
                ))
            )

    def __str__(self):
        return f'"{self.user}" user of "{self.organization}"'

    class Meta:
        verbose_name = 'Company user'


class CompanyOrganisationOwner(AbstractOrganizationOwner):

    class Meta:
        verbose_name = 'Company admin'

    def __str__(self):
        return f'"{self.organization_user.user}" owner of "{self.organization}"'
