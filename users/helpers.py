import logging
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, reverse
from itsdangerous import URLSafeTimedSerializer
from django.utils.translation import get_language, activate, LANGUAGE_SESSION_KEY, ugettext as _
from django.contrib import messages

from member_organisations.models import MemberOrganisationOwner


def user_agreement_required(func):
    @login_required
    def wrapper(request, *args, **kwargs):
        path = request.path
        user = request.user
        new_language = request.GET.get('new_language', None)
        if new_language and new_language != user.profile.language:
            user.profile.language = new_language
            user.profile.save()
        else:
            current_language = get_language()
            try:
                country = request.user.profile.member_organisation.country
                language_by_country = country.languagebycountry_set.order_by('-default', 'language')
                user_languages = [item.language.slug for item in language_by_country]
                if not current_language in user_languages:
                    activate(user.profile.language)
                    request.session['pref_language'] = user.profile.language
                    request.session[LANGUAGE_SESSION_KEY] = user.profile.language
            except: # AttributeError:
                pass

        if (not user.profile.member_organisation or
                not user.profile.member_organisation.gs1_terms_enable or
                user.profile.agreed):
            return func(request, *args, **kwargs)
        else:
            return redirect(reverse('users:user_agreement_required') + '?next=' + path)

    return wrapper


def is_user_mo_admin_or_owner(user):
    """
    If user is admin or an owner of any member organisation
    """

    if user.groups.filter(name='GO Admins').exists():
        return True

    if user.member_organisations_memberorganisationuser.filter(is_admin=True).exists():
        return True

    if MemberOrganisationOwner.objects.filter(organization_user__user=user).exists():
        # note: it's possible to be a mo owner, but not to be an admin for this mo!
        # therefore we check for ownership expilictly
        return True

    return False


def mo_admin_required(func):
    @login_required
    def wrapper(*args, **kwargs):
        request = args[0]
        user = request.user

        if is_user_mo_admin_or_owner(user):
            return func(*args, **kwargs)

        messages.add_message(
            request,
            messages.ERROR,
            _('You don\'t have required permissions to view this page')
        )
        return redirect(reverse('BCM:login') + '?next=' + request.path)

    return wrapper


def get_api_auth(email):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    token = serializer.dumps({'email': email})
    logging.getLogger().debug('Created token: %s' % token)
    auth_url = reverse('users:api_auth', args=(token,))
    return auth_url
