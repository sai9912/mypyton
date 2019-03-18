from django.urls import reverse
from django.utils.safestring import mark_safe

from company_organisations.admin import (
    CompanyOrganisationCustomMixin,
    CompanyOrganisationUserCustomMixin,
)
from member_organisations.admin_mixins import MemberOrganisationCustomMixin
from member_organisations.custom_admin.base_views import (
    BaseCustomAdminMethods,
    BaseM2MTokenAdmin,
)

from products.admin import ProductCustomMixin

from users.admin import UserCustomMixin
from prefixes.admin import PrefixCustomMixin

URL_PREFIX = 'go_admin'


class UserCustomAdmin(UserCustomMixin, BaseCustomAdminMethods):
    fieldsets = None
    fields = ('username', 'email', 'first_name', 'last_name', 'is_active')
    readonly_fields = ('username', 'email', 'first_name', 'last_name')

    url_prefix = URL_PREFIX
    raise_not_implemented_queryset_exception = True

    def member_organisation(self, obj):
        return obj.member_organisations_memberorganisation.first()
    member_organisation.admin_order_field = 'member_organisations_memberorganisation'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @classmethod
    def get_auth__user_queryset(cls, request, queryset):
        if request.user.is_superuser:
            return queryset

        has_go_admin = request.user.member_organisations_memberorganisationuser.first()
        has_go_admin = has_go_admin.is_admin if has_go_admin else None

        if has_go_admin:
            return queryset.exclude(is_superuser=True).exclude(is_staff=True)
        else:
            return queryset.none()


class CountryCustomAdmin(BaseCustomAdminMethods):
    url_prefix = URL_PREFIX
    raise_not_implemented_queryset_exception = False


class LanguageCustomAdmin(BaseCustomAdminMethods):
    url_prefix = URL_PREFIX
    raise_not_implemented_queryset_exception = False


class LanguageByCountryCustomAdmin(BaseCustomAdminMethods):
    url_prefix = URL_PREFIX
    raise_not_implemented_queryset_exception = False
    list_display = ('__str__', 'language', 'country')


class MemberOrganisationCustomAdmin(BaseCustomAdminMethods):
    url_prefix = URL_PREFIX
    raise_not_implemented_queryset_exception = False

    related_models_actions = {
        # EXAMPLE: it's possible to enable/disable links for related models here
        'member_organisation': {
            'can_add_related': False,
            'can_change_related': False,
            'can_delete_related': False,
        }
    }


# MemberOrganisationCustomMixin removed
# MemberOrganisationUser has no field named 'country'
class MemberOrganisationUserCustomAdmin(BaseCustomAdminMethods):
    url_prefix = URL_PREFIX
    raise_not_implemented_queryset_exception = True

    @classmethod
    def get_member_organisations__memberorganisationuser_queryset(cls, request, queryset):
        has_go_admin = request.user.member_organisations_memberorganisationuser.first()
        has_go_admin = has_go_admin.is_admin if has_go_admin else None

        if has_go_admin:
            return queryset
        else:
            return queryset.none()

    @classmethod
    def get_auth__user_queryset(cls, request, queryset):
        return queryset

    @classmethod
    def get_member_organisations__memberorganisation_queryset(cls, request, queryset):
        return queryset


class MemberOrganisationOwnerCustomAdmin(BaseCustomAdminMethods):
    url_prefix = URL_PREFIX
    raise_not_implemented_queryset_exception = True
    list_display_links = ('user', )
    list_display = ('user', 'organization')

    def user(self, obj):
        return obj.organization_user.user
    user.admin_order_field = 'organization_user__user'

    @classmethod
    def get_member_organisations__memberorganisationowner_queryset(cls, request, queryset):
        has_go_admin = request.user.member_organisations_memberorganisationuser.first()
        has_go_admin = has_go_admin.is_admin if has_go_admin else None

        if has_go_admin:
            return queryset
        else:
            return queryset.none()

    @classmethod
    def get_member_organisations__memberorganisationuser_queryset(cls, request, queryset):
        return queryset

    @classmethod
    def get_member_organisations__memberorganisation_queryset(cls, request, queryset):
        return queryset


class CompanyOrganisationCustomAdmin(CompanyOrganisationCustomMixin,
                                     BaseCustomAdminMethods):

    url_prefix = URL_PREFIX
    raise_not_implemented_queryset_exception = False


class CompanyOrganisationOwnerCustomAdmin(BaseCustomAdminMethods):
    url_prefix = URL_PREFIX
    raise_not_implemented_queryset_exception = False
    list_display_links = ('user', )
    list_display = ('user', 'organization', 'member_organisation')

    def user(self, obj):
        return obj.organization_user.user
    user.admin_order_field = 'organization_user__user'

    def member_organisation(self, obj):
        return obj.organization.member_organisation
    member_organisation.admin_order_field = 'organization__member_organisation'


class CompanyOrganisationUserCustomAdmin(CompanyOrganisationUserCustomMixin,
                                         BaseCustomAdminMethods):
    url_prefix = URL_PREFIX
    raise_not_implemented_queryset_exception = False


    def get_list_display(self, request):
        list_display = tuple(super().get_list_display(request))
        return list_display + ('impersonate_user',)
    def impersonate_user(self, obj):
        # self.request is available here from
        # .custom_admin_changelist_view() -> .get_urls_context()
        impersonate_url = reverse('impersonate-start', args=(obj.user.pk, ))
        return mark_safe(f'<a class="button" href="{impersonate_url}">Impersonate</a>')

    def member_organisation(self, obj):
        return obj.organization.member_organisation
    member_organisation.admin_order_field = 'organization__member_organisation'


class PrefixCustomAdmin(PrefixCustomMixin, BaseCustomAdminMethods):
    url_prefix = URL_PREFIX
    list_display_links = ('prefix',)
    raise_not_implemented_queryset_exception = False


class ProductCustomAdmin(ProductCustomMixin, BaseCustomAdminMethods):
    url_prefix = URL_PREFIX
    raise_not_implemented_queryset_exception = False


class AuditLogCustomAdmin(BaseCustomAdminMethods):
    url_prefix = URL_PREFIX
    raise_not_implemented_queryset_exception = False
    search_fields = (
        'username',
    )

class M2MTokenCustomAdmin(BaseM2MTokenAdmin, BaseCustomAdminMethods):
    url_prefix = URL_PREFIX
    raise_not_implemented_queryset_exception = False

    list_display = ('description', 'user', 'member_organisation', 'created', )
    list_display_links = ('description', )
    readonly_fields = ('token', )

    # created.admin_order_field = 'token__created'
