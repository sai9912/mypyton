from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from utils import RightSideAdminLinkInfo, RightSideLinksAdminMixin
from prefixes.actions import export_as_csv_action
from prefixes.admin import RelatedDropdownFilter
from .models import Profile

User = get_user_model()


class ProfileCustomMixin:
    """
    Mixin for ProfileModelAdmin
    """

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).select_related(
            'user', 'company_organisation'
        )

    actions = (
        export_as_csv_action(
            'CSV Export',
            fields=[
                'uid',
                'user__username',
                'user__last_name',
                'user__email',
                'company_organisation',
            ],
            all_objects=True
        ),
    )
    list_display = (
        'username',
        'last_name',
        'email',
        'company_organisation',
    )

    @staticmethod
    def username(profile):
        return profile.user.username

    @staticmethod
    def email(profile):
        return profile.user.email

    @staticmethod
    def last_name(profile):
        return profile.user.last_name

    search_fields = (
        'user__username',
        'user__email',
        'user__last_name',
    )

    list_filter = (
        ('company_organisation', RelatedDropdownFilter),
    )


@admin.register(Profile)
class ProfileModelAdmin(ProfileCustomMixin, admin.ModelAdmin):
    pass


class UserCustomMixin(RightSideLinksAdminMixin):

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).select_related(
            'profile__company_organisation',
            'profile',
            'profile__member_organisation',
        )

    actions = (
        export_as_csv_action(
            'CSV Export',
            fields=[
                'id',
                'username',
                'last_name',
                'email',
                'profile__company_organisation',
            ],
            all_objects=True
        ),
    )
    list_display = (
        'username',
        'last_name',
        'email',
        'organisation',
    )

    @staticmethod
    def organisation(user):
        return str(user.profile.company_organisation)

    search_fields = (
        'username',
        'email',
        'company_organisations_companyorganisation__uuid',
    )

    list_filter = (
        (
            'profile__company_organisation__member_organisation',
            RelatedDropdownFilter
        ),
    )
    readonly_fields = [
        'prefixes',
    ]

    def get_fields(self, request, obj=None):
        if not getattr(self, 'url_prefix', False):
            return None
        return [
                   'prefixes',
               ] + list(super().get_fields(request, obj))

    def get_readonly_fields(self, request, obj=None):
        if not getattr(self, 'url_prefix', False):
            return super().get_readonly_fields(request, obj)
        return [
                   'prefixes',
               ] + list(super().get_readonly_fields(request, obj))

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Prefixes', {'fields': readonly_fields}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    @staticmethod
    def prefixes(user):
        prefixes = user.profile.company_organisation.prefix_set.all()
        return ','.join(pr.prefix for pr in prefixes)

    right_side_links = [
        RightSideAdminLinkInfo(
            name='logs',
            url='audit/log/?q={obj.username}'
        ),
        RightSideAdminLinkInfo(
            name='impersonate as',
            url='company_organisations/'
                'companyorganisationuser/?q={obj.username}'
        ),
    ]


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(UserCustomMixin, BaseUserAdmin):
    change_form_template = 'admin/custom_change_view.html'
