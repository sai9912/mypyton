from collections import OrderedDict

from django.contrib.admin import AdminSite
from django.contrib.auth.models import User

from audit.models import Log
from company_organisations.models import (
    CompanyOrganisation, CompanyOrganisationOwner, CompanyOrganisationUser
)
from member_organisations.models import M2MToken
from member_organisations.models import MemberOrganisation
from prefixes.models import Prefix, PrefixStatus
from products.models.product import Product
from . import mo_views


# {app_label: <list-of-mo-admin-views-for-required-models>}
apps_config = OrderedDict([
    ('audit', [
        # we could override admin.site with a custom instance, it would bring standard urls
        # like add_url, but for now it's easier to adjust templates and replace urls there
        mo_views.AuditLogCustomAdmin(Log, AdminSite()),
    ]),
    ('member_organisations', [
        mo_views.M2MTokenCustomAdmin(M2MToken, AdminSite()),
        mo_views.MemberOrganisationCustomAdmin(MemberOrganisation, AdminSite())
    ]),
    ('company_organisations', [
        mo_views.CompanyOrganisationCustomAdmin(CompanyOrganisation, AdminSite()),
        mo_views.CompanyOrganisationOwnerCustomAdmin(CompanyOrganisationOwner, AdminSite()),
        mo_views.CompanyOrganisationUserCustomAdmin(CompanyOrganisationUser, AdminSite()),
    ]),
    ('prefixes', [
        mo_views.PrefixCustomAdmin(Prefix, AdminSite()),
        # mo_views.PrefixStatusCustomAdmin(PrefixStatus, AdminSite()),
    ]),
    ('products', [
        mo_views.ProductCustomAdmin(Product, AdminSite()),
    ]),
    ('auth', [
        mo_views.UserCustomAdmin(User, AdminSite()),
    ]),
    # there was no Barcode model when last checked
])

config = {
    'required_django_group_name': 'MO Admins',
    'apps_config': apps_config,
}
