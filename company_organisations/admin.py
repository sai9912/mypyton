# Register your models here.

from django.contrib import admin

from utils import RightSideAdminLinkInfo, RightSideLinksAdminMixin
from prefixes.actions import export_as_csv_action
from prefixes.admin import RelatedDropdownFilter
from .models import (
    CompanyOrganisation,
    CompanyOrganisationOwner,
    CompanyOrganisationUser,
)


class CompanyOrganisationCustomMixin(RightSideLinksAdminMixin):
    actions = (
        export_as_csv_action(
            'CSV Export',
            fields=[
                'id',
                'company',
                'uuid',
                'name',
                'member_organisation_id',
            ],
            all_objects=True
        ),
    )
    list_display_links = (
        'uuid',
        'company',
        'member_organisation'
    )
    list_display = (
        'uuid',
        'name',
        'company',
        'member_organisation',
    )

    search_fields = (
        'company',
    )
    list_filter = (
        ('member_organisation', RelatedDropdownFilter),
    )

    right_side_links = [
        RightSideAdminLinkInfo(
            name='users',
            url='auth/user/?q={obj.uuid}'
        ),
        RightSideAdminLinkInfo(
            name='products',
            url='products/product/?q={obj.uuid}'
        ),
        RightSideAdminLinkInfo(
            name='prefixes',
            url='prefixes/prefix/?q={obj.uuid}'
        ),
        RightSideAdminLinkInfo(
            name='impersonate as',
            url='company_organisations/companyorganisationuser/?q={obj.uuid}'
        ),
    ]


@admin.register(CompanyOrganisation)
class CompanyOrganisationAdmin(CompanyOrganisationCustomMixin,
                               admin.ModelAdmin):
    change_form_template = 'admin/custom_change_view.html'


@admin.register(CompanyOrganisationOwner)
class CompanyOrganisationOwnerAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization_user', 'organization',)
    list_display_links = ('id', 'organization_user',)


class CompanyOrganisationUserCustomMixin(RightSideLinksAdminMixin):
    """
    Mixin for CompanyOrganisationAdmin and CompanyOrganisationCustomAdmin
    """

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).select_related(
            'user', 'organization'
        )

    actions = (
        export_as_csv_action(
            'CSV Export',
            fields=[
                'user__username',
                'user__last_name',
                'user__email',
                'organization__company',
            ],
            all_objects=True
        ),
    )
    list_display = (
        'username',
        'last_name',
        'email',
        'company',
    )

    @staticmethod
    def company(obj):
        return obj.organization.company

    @staticmethod
    def username(obj):
        return obj.user.username

    @staticmethod
    def email(obj):
        return obj.user.email

    @staticmethod
    def last_name(obj):
        return obj.user.last_name

    search_fields = (
        'user__username',
        'user__email',
        'user__last_name',
        'organization__company',
        'organization__uuid',
    )

    list_filter = (
        ('organization__member_organisation', RelatedDropdownFilter),
    )

    right_side_links = [
        RightSideAdminLinkInfo(
            name='owner',
            url='auth/user/{obj.user_id}/change/'
        ),
        RightSideAdminLinkInfo(
            name='organization',
            url='company_organisations/companyorganisation/'
                '{obj.organization_id}/change'
        ),
    ]


@admin.register(CompanyOrganisationUser)
class CompanyOrganisationUserAdmin(CompanyOrganisationUserCustomMixin,
                                   admin.ModelAdmin):
    change_form_template = 'admin/custom_change_view.html'
