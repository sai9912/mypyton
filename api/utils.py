from django.conf import settings


def query_user_company_organisation(user):
    return user.company_organisations_companyorganisation


def query_user_member_organisation(user):
    return user.groups.filter(name='MO Admins')


def query_user_global_organisation(user):
    return user.groups.filter(name='GO Admins')


def get_user_company_organisation(user):
    return query_user_company_organisation(user).first()


def get_user_member_organisation(user):
    return query_user_member_organisation(user).first()


def get_user_global_organisation(user):
    return query_user_global_organisation(user).first()


def is_company_organisation(user):
    return query_user_company_organisation(user).exists()


def is_member_organisation_staff(user):
    return query_user_member_organisation(user).exists()


def is_global_organisation(user):
    return query_user_global_organisation(user).exists()


def check_m2m_token(user, m2m_token):
    '''
    >>> from django.contrib.auth.models import User, AnonymousUser
    >>> user = User.objects.create(email='root@root.ru', username='example123')
    >>> check_m2m_token(user, '')
    True
    >>> check_m2m_token(AnonymousUser(), '')
    True
    '''
    if user.is_anonymous:
        if settings.ANONYMOUS_LOGIN_ALLOWED:
            return True         # to tests
        else:
            if not user.profile.member_organisation.login_api_secure:
                return True
            else:
                return False
    try:
        if not user.profile.member_organisation.login_api_secure:
            return True
    except Exception:
        if settings.ANONYMOUS_LOGIN_ALLOWED:
            return True         # to tests
        else:
            return False

    if not m2m_token:
        return False

    auth_token_exist = user.auth_token_set.filter(pk=m2m_token).exists()
    if auth_token_exist:
        return True
    return False


def get_generic_filtered_queryset(model, user):
    queryset = model.objects.all()

    try:
        member_organisation = user.profile.member_organisation
    except AttributeError:
        return queryset
    else:
        filtered_queryset = model.objects.filter(
            mo_relations__member_organisation=member_organisation
        )

    return filtered_queryset or queryset
