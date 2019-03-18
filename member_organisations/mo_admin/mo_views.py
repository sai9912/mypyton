from django.db.models import Q
from django.urls import reverse
from django.utils.safestring import mark_safe

from company_organisations.admin import (
    CompanyOrganisationCustomMixin,
    CompanyOrganisationUserCustomMixin,
)
from member_organisations.helpers.mo_admin_helpers import (
    get_allowed_mo_for_mo_admin,)

from member_organisations.custom_admin.base_views import (
    BaseCustomAdminMethods,
    BaseM2MTokenAdmin,
)
from member_organisations.models import MemberOrganisationUser
from products.admin import ProductCustomMixin
from users.admin import UserCustomMixin
from prefixes.admin import PrefixCustomMixin

URL_PREFIX = 'mo_admin'


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
        elif request.user.groups.filter(name='MO Admins').exists():
            allowed_organizations = get_allowed_mo_for_mo_admin(request.user, is_admin=True)
            queryset = (
                queryset.filter(
                    member_organisations_memberorganisation__in=allowed_organizations
                )
                .exclude(groups__name="GO Admins")
                .exclude(is_superuser=True)
                .exclude(is_staff=True)
            )
            return queryset


class AuditLogCustomAdmin(BaseCustomAdminMethods):
    url_prefix = URL_PREFIX

    search_fields = (
        'username',
    )

    @classmethod
    def get_audit__log_queryset(cls, request, queryset):
        # todo: there are no fields to filter this model!
        return queryset


class CompanyOrganisationCustomAdmin(CompanyOrganisationCustomMixin,
                                     BaseCustomAdminMethods):

    url_prefix = URL_PREFIX
    related_models_actions = {
        # it's possible to enable/disable links for related models here
        'member_organisation': {
            'can_add_related': False,
            'can_change_related': False,
            'can_delete_related': False,
        }
    }

    @classmethod
    def get_company_organisations__companyorganisation_queryset(cls, request, queryset):
        """
        name convention:
            "get_{model._meta.app_label}__{model._meta.model_name}_queryset".lower()

        if a method doesn't exist you'll recieve the exception
        with a required method and class names
        """

        allowed_organizations = get_allowed_mo_for_mo_admin(request.user)
        queryset = queryset.filter(member_organisation__in=allowed_organizations)
        return queryset

    @classmethod
    def get_bcm__country_queryset(cls, request, queryset):
        allowed_organizations = get_allowed_mo_for_mo_admin(request.user)
        queryset = queryset.filter(member_organisation__in=allowed_organizations)
        return queryset

    @classmethod
    def get_member_organisations__memberorganisation_queryset(cls, request, queryset):
        allowed_organizations = get_allowed_mo_for_mo_admin(request.user)
        queryset = queryset.filter(pk__in=allowed_organizations)
        return queryset


class CompanyOrganisationOwnerCustomAdmin(BaseCustomAdminMethods):
    url_prefix = URL_PREFIX
    list_display_links = ('user', )
    list_display = ('user', 'organization', 'member_organisation')

    def user(self, obj):
        return obj.organization_user.user
    user.admin_order_field = 'organization_user__user'

    def member_organisation(self, obj):
        return obj.organization.member_organisation
    member_organisation.admin_order_field = 'organization__member_organisation'

    def has_actions_permission(self, request, original_method):
        if request.user.is_superuser:
            return True
        elif get_allowed_mo_for_mo_admin(request.user, is_admin=True):
            return original_method(request)
        return False

    def has_add_permission(self, request):
        return self.has_actions_permission(request, super().has_add_permission)

    def has_delete_permission(self, request, obj=None):
        return self.has_actions_permission(request, super().has_add_permission)

    @classmethod
    def get_company_organisations__companyorganisationowner_queryset(cls, request, queryset):
        """
        queryset filtering for CO owners changelist
        link: "/mo_admin/company_organisations_companyorganisationowner/"
        """

        # filter by organization, company organization should belong to request.user MO
        allowed_organizations = get_allowed_mo_for_mo_admin(request.user, is_admin=True)
        queryset = queryset.filter(organization__member_organisation__in=allowed_organizations)

        # filter by user, organization user should belong to CO, which belong to request.user MO
        queryset = queryset.filter(
            organization_user__organization__member_organisation__in=allowed_organizations
        )
        return queryset

    @classmethod
    def get_company_organisations__companyorganisationuser_queryset(cls, request, queryset):
        """
        queryset filtering for CO owners edit/add: CO user FK
        link: "/mo_admin/company_organisations_companyorganisationowner/<number>/<change/add>"
        """

        allowed_organizations = get_allowed_mo_for_mo_admin(request.user)
        queryset = queryset.filter(organization__member_organisation__in=allowed_organizations)
        return queryset

    @classmethod
    def get_company_organisations__companyorganisation_queryset(cls, request, queryset):
        """
        queryset filtering for CO owners edit/add: CO FK
        link: "/mo_admin/company_organisations_companyorganisationowner/<number>/<change/add>"
        """

        allowed_organizations = get_allowed_mo_for_mo_admin(request.user)
        queryset = queryset.filter(member_organisation__in=allowed_organizations)
        return queryset


class CompanyOrganisationUserCustomAdmin(CompanyOrganisationUserCustomMixin,
                                         BaseCustomAdminMethods):

    url_prefix = URL_PREFIX

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

    def has_actions_permission(self, request, original_method):
        if request.user.is_superuser:
            return True
        elif get_allowed_mo_for_mo_admin(request.user, is_admin=True):
            return original_method(request)
        return False

    def has_add_permission(self, request):
        return self.has_actions_permission(request, super().has_add_permission)

    def has_delete_permission(self, request, obj=None):
        return self.has_actions_permission(request, super().has_add_permission)

    @classmethod
    def get_company_organisations__companyorganisationuser_queryset(cls, request, queryset):
        """
        queryset filtering for CO users changelist
        link: "/mo_admin/company_organisations_companyorganisationuser/"
        """

        allowed_organizations = get_allowed_mo_for_mo_admin(request.user, is_admin=True)
        queryset = queryset.filter(organization__member_organisation__in=allowed_organizations)
        return queryset

    @classmethod
    def get_auth__user_queryset(cls, request, queryset):
        queryset = UserCustomAdmin.get_auth__user_queryset(request, queryset)
        return queryset

    @classmethod
    def get_company_organisations__companyorganisation_queryset(cls, request, queryset):
        allowed_organizations = get_allowed_mo_for_mo_admin(request.user)
        queryset = queryset.filter(member_organisation__in=allowed_organizations)
        return queryset

    def response_post_save_add(self, request, obj):
        member_organisation = obj.organization.member_organisation
        # assign member organization to user is it was created by a mo admin
        # cause mo admin doesn't have access to member organizations users
        mo_user, is_created = MemberOrganisationUser.objects.get_or_create(
            user=obj.user, organization=member_organisation
        )

        return super().response_post_save_add(request, obj)


class PrefixCustomAdmin(PrefixCustomMixin, BaseCustomAdminMethods):
    url_prefix = URL_PREFIX
    list_display_links = ('prefix',)

    @classmethod
    def get_prefixes__prefix_queryset(cls, request, queryset):
        allowed_organizations = get_allowed_mo_for_mo_admin(request.user)
        queryset = queryset.filter(member_organisation__in=allowed_organizations)
        return queryset

    @classmethod
    def get_company_organisations__companyorganisation_queryset(cls, request, queryset):
        allowed_organizations = get_allowed_mo_for_mo_admin(request.user)
        queryset = queryset.filter(member_organisation__in=allowed_organizations)
        return queryset

    @classmethod
    def get_member_organisations__memberorganisation_queryset(cls, request, queryset):
        allowed_organizations = get_allowed_mo_for_mo_admin(request.user)
        queryset = queryset.filter(pk__in=allowed_organizations)
        return queryset

    @classmethod
    def get_prefixes__prefixstatus_queryset(cls, request, queryset):
        return queryset  # not a mo/co related model


class ProductCustomAdmin(ProductCustomMixin, BaseCustomAdminMethods):
    url_prefix = URL_PREFIX

    @classmethod
    def get_products__product_queryset(cls, request, queryset):
        allowed_organizations = get_allowed_mo_for_mo_admin(request.user)
        queryset = queryset.filter(member_organisation__in=allowed_organizations)
        return queryset

    @classmethod
    def get_products__subproduct_queryset(cls, request, queryset):
        allowed_organizations = get_allowed_mo_for_mo_admin(request.user)
        queryset = queryset.filter()
        return queryset

    @classmethod
    def get_auth__user_queryset(cls, request, queryset):
        allowed_organizations = get_allowed_mo_for_mo_admin(request.user)
        queryset = queryset.filter(
            member_organisations_memberorganisation__in=allowed_organizations
        )
        return queryset

    @classmethod
    def get_member_organisations__memberorganisation_queryset(cls, request, queryset):
        allowed_organizations = get_allowed_mo_for_mo_admin(request.user)
        queryset = queryset.filter(pk__in=allowed_organizations)
        return queryset

    @classmethod
    def get_company_organisations__companyorganisation_queryset(cls, request, queryset):
        allowed_organizations = get_allowed_mo_for_mo_admin(request.user)
        queryset = queryset.filter(member_organisation__in=allowed_organizations)
        return queryset

    """
    prefix:
        Prefix.prefix == Product.gs1_company_prefix (String comparison)
        Product.gs1_company_prefix -> Prefix.prefix -> Prefix.MemberOrganisation
        filter by: mo_admin.MemberOrganisation == Prefix.MemberOrganisation
        troubles: "max_length=12" vs max_length=75 for char fields

    category:
        description: "Global Product Classification"
        Product.category, string type
        troubles: there are no matches with other models fields

    package_level and package_type:
        products parameters, for now used only in Product,
        (something like quick-filter/search could be added to Product model by these fields)

    country_of_origin and target_market:
        the same as above, quick-filter/search could be added to these fields
    """

    @classmethod
    def get_products__dimensionuom_queryset(cls, request, queryset):
        # todo: check this queryset
        return queryset

    @classmethod
    def get_products__weightuom_queryset(cls, request, queryset):
        # todo: check this queryset
        return queryset

    @classmethod
    def get_products__netcontentuom_queryset(cls, request, queryset):
        # todo: check this queryset
        return queryset

    @classmethod
    def get_products__countryoforigin_queryset(cls, request, queryset):
        # todo: check this queryset
        return queryset

    @classmethod
    def get_products__targetmarket_queryset(cls, request, queryset):
        # todo: check this queryset
        return queryset

    @classmethod
    def get_products__language_queryset(cls, request, queryset):
        # todo: check this queryset
        return queryset

    @classmethod
    def get_products__packagelevel_queryset(cls, request, queryset):
        # todo: check this queryset
        return queryset

    @classmethod
    def get_products__packagetype_queryset(cls, request, queryset):
        # todo: check this queryset
        return queryset


class M2MTokenCustomAdmin(BaseM2MTokenAdmin, BaseCustomAdminMethods):
    url_prefix = URL_PREFIX

    list_display = ('description', 'user', 'member_organisation', 'created', )
    list_display_links = ('description', )
    readonly_fields = ('token', )

    @classmethod
    def get_member_organisations__m2mtoken_queryset(cls, request, queryset):
        if request.user.is_superuser:
            return queryset
        elif request.user.groups.filter(name='MO Admins').exists():
            allowed_organizations = get_allowed_mo_for_mo_admin(request.user, is_admin=False)
            queryset = queryset.filter(
                token__user__member_organisations_memberorganisation__in=allowed_organizations
            )
            return queryset


class MemberOrganisationCustomAdmin(BaseCustomAdminMethods):
    url_prefix = URL_PREFIX

    list_display = ('name', 'country', 'slug', 'gs1_prefix_regex', 'gs1_logo_path')

    @classmethod
    def get_member_organisations__memberorganisation_queryset(cls, request, queryset):
        queryset = queryset.filter(
            Q(organization_users__user=request.user, organization_users__is_admin=True) |
            Q(owner__organization_user__user=request.user)
        ).distinct()
        return queryset

    @classmethod
    def get_bcm__country_queryset(cls, request, queryset):
        # todo: there are no fields to filter this model!

        return queryset
