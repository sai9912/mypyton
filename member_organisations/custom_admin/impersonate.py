
IMPERSONATE_GROUPS = ('MO Admins', 'GO Admins')


def is_impersonation_allowed(request):
    """
    Custom permissions checker for impersonate
    (check an impersonate "CUSTOM_ALLOW" setting in django settings)


    :param request:
    :return:
    """

    user = request.user

    if user.is_superuser and user.is_active:
        return True

    if user.is_authenticated and user.is_active:
        return user.groups.filter(name__in=IMPERSONATE_GROUPS).exists()

    return False
