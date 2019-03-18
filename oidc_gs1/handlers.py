from member_organisations.models import MemberOrganisation
from company_organisations.models import CompanyOrganisation
from services import users_service
from BCM.models import Country
from django.contrib.auth.models import Group


def login_handler(OIDCUser, claims):
    # user
    user_id = claims.get('http://gs1.org/claims/crm-UserID')
    email = claims.get('http://gs1.org/claims/crm-Email')
    first_name = claims.get('http://gs1.org/claims/crm-FirstName')
    last_name = claims.get('http://gs1.org/claims/crm-LastName')

    # GO Admin / GO User, MO Admin / MO User, Company Admin / Company User
    upm_role = claims.get('http://gs1.org/claims/crm-CloudUPMRole')

    # testing
    if email == 'info@reiseurope.com':
        upm_role = 'MO Admin'

    # company
    gs1mo = claims.get('http://gs1.org/claims/crm-CompanyMO')
    company_id = claims.get('http://gs1.org/claims/crm-CompanyID')
    company_name = claims.get('http://gs1.org/claims/crm-CompanyName')
    country = claims.get('http://gs1.org/claims/crm-AddressCountry')

    mo_slug = 'gs1go'

    # get MO
    member_organisation = MemberOrganisation.objects.get(slug=mo_slug)
    uuid = '%s:%s' % (mo_slug, company_id)
    uid = '%s:%s' % (mo_slug, user_id)

    # user
    user = OIDCUser.user
    user.first_name = first_name
    user.last_name = last_name
    user.save()

    # create a company
    company_organisation = None # MO's do not have companies
    if upm_role in ['Company Admin', 'Company User']:
        try:
            company_country = Country.objects.get(name=country)
        except:
            company_country = None
        company_org_default_data = dict(company=company_name,
                                        name=company_name,
                                        member_organisation=member_organisation,
                                        country=company_country,
                                        slug=uuid)
        company_organisation, created = CompanyOrganisation.objects.update_or_create(uuid=uuid,
                                                                                     defaults=company_org_default_data)

        # user - company_org link
        is_admin = upm_role == 'Company Admin'
        company_organisation.get_or_add_user(user, is_admin=is_admin)

    if upm_role in ['GO Admin', 'GO User', 'MO Admin', 'MO User']:
        # user - company_org link
        is_admin = upm_role in ('GO Admin', 'MO Admin')

        member_organisation.get_or_add_user(user, is_admin=is_admin)

        if upm_role in ('GO Admin', 'GO User'):
            go_group = Group.objects.get(name='GO Admins')
            go_group.user_set.add(user)

        if upm_role in ('MO Admin', 'MO User'):
            go_group = Group.objects.get(name='MO Admins')
            go_group.user_set.add(user)

    # user profile
    profile = OIDCUser.user.profile
    profile.uid = uid
    if not profile.login_count:
        profile.login_count = 0
    profile.login_count += 1
    profile.member_organisation = member_organisation
    if company_organisation:
        profile.company_organisation = company_organisation
    profile.customer_role = upm_role
    profile.agreed = True
    profile.save()
