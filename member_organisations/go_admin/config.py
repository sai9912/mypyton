from collections import OrderedDict

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User

from audit.models import Log
from member_organisations.models import (
    MemberOrganisation, MemberOrganisationUser, MemberOrganisationOwner,
    M2MToken)
from company_organisations.models import (
    CompanyOrganisation, CompanyOrganisationOwner, CompanyOrganisationUser
)
from BCM.models import Country, Language, LanguageByCountry
from prefixes.models import Prefix, PrefixStatus
from products.models.product import Product
from . import go_views


# {app_label: <list-of-mo-admin-views-for-required-models>}
apps_config = OrderedDict([
    ('audit', [
        # we could override admin.site with a custom instance, it would bring standard urls
        # like add_url, but for now it's easier to adjust templates and replace urls there
        go_views.AuditLogCustomAdmin(Log, AdminSite()),
    ]),
    ('BCM', [
        go_views.CountryCustomAdmin(Country, AdminSite()),
        go_views.LanguageCustomAdmin(Language, AdminSite()),
        go_views.LanguageByCountryCustomAdmin(LanguageByCountry, AdminSite()),
    ]),
    ('member_organisations', [
        go_views.MemberOrganisationCustomAdmin(MemberOrganisation, AdminSite()),
        go_views.MemberOrganisationUserCustomAdmin(MemberOrganisationUser, AdminSite()),
        go_views.MemberOrganisationOwnerCustomAdmin(MemberOrganisationOwner, AdminSite()),
        go_views.M2MTokenCustomAdmin(M2MToken, AdminSite()),
    ]),
    ('company_organisations', [
        go_views.CompanyOrganisationCustomAdmin(CompanyOrganisation, AdminSite()),
        go_views.CompanyOrganisationOwnerCustomAdmin(CompanyOrganisationOwner, AdminSite()),
        go_views.CompanyOrganisationUserCustomAdmin(CompanyOrganisationUser, AdminSite()),
    ]),
    ('prefixes', [
        go_views.PrefixCustomAdmin(Prefix, AdminSite()),
        # go_views.PrefixStatusCustomAdmin(PrefixStatus, AdminSite()),
    ]),
    ('products', [
        go_views.ProductCustomAdmin(Product, AdminSite()),
    ]),
    ('auth', [
        go_views.UserCustomAdmin(User, AdminSite()),
    ]),

])

config = {
    'required_django_group_name': 'GO Admins',
    'apps_config': apps_config,
    # 'user_custom_admin': UserCustomAdmin(User, AdminSite()),
}
