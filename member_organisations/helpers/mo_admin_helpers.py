from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import resolve_url
from django.urls import Resolver404, resolve

from member_organisations.models import MemberOrganisationOwner, MemberOrganisation


def get_allowed_mo_for_mo_admin(user, is_admin=False):
    if user.is_superuser:
        return MemberOrganisation.objects.all()

    mo_user_conditions = {'is_admin': True} if is_admin else {}
    member_organization_user_ids = (
        user.member_organisations_memberorganisationuser.filter(**mo_user_conditions)
        .values_list('organization', flat=True)
    )
    member_organization_owner_ids = (  # mo where the current user is owner
        MemberOrganisationOwner.objects
            .filter(organization__owner__organization_user__user=user)
            .values_list('organization', flat=True)
    )

    allowed_organizations = (
            set(member_organization_user_ids) | set(member_organization_owner_ids)
    )

    return allowed_organizations


def mo_redirect_to_login(request):
    path = request.build_absolute_uri()
    resolved_login_url = resolve_url(settings.LOGIN_URL)
    return redirect_to_login(path, resolved_login_url, REDIRECT_FIELD_NAME)


def get_object_from_popup_referrer(request, model_class):
    """
    retrieves product template from referrer when product attribute is edited in popup
    (m2m inlines)
    """

    if not request.GET.get('_popup'):
        return None

    referer_parts = request.META.get('HTTP_REFERER', '').split('/')
    if len(referer_parts) < 4:
        return None

    try:
        popup_referer_path = '/'.join(referer_parts[3:])
        popup_referer_path = '/' + popup_referer_path
        resolver = resolve(popup_referer_path)
    except Resolver404:
        return None
    else:
        product_template_id = resolver.kwargs.get('object_id')
        # if instance wasn't saved, template is will be None
        return model_class.objects.filter(id=product_template_id).first()
