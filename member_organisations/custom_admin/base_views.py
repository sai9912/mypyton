from django.contrib import admin, messages
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from knox.models import AuthToken

from knox.settings import CONSTANTS as KNOX_CONSTANTS
from member_organisations.custom_admin.modified_model_admin import ModifiedMethodsModelAdmin
from django.contrib.auth.decorators import user_passes_test


class BaseCustomAdminMethods(ModifiedMethodsModelAdmin):
    url_prefix = '__URL_PREFIX_IS_NOT_DEFINED__'  # override this attribute in subclass
    change_list_template = 'admin/{url_prefix}/change_list.html'
    change_form_template = 'admin/{url_prefix}/change_form.html'
    add_form_template = 'admin/{url_prefix}/change_form.html'
    delete_confirmation_template = 'admin/{url_prefix}/delete_confirmation.html'
    delete_selected_confirmation_template = 'admin/{url_prefix}/delete_selected_confirmation.html'
    related_models_actions = None
    raise_not_implemented_queryset_exception = True
    required_django_group = None  # todo: implement group requirements
    request = None

    # it's possible to enable/disable links for related models here
    # by default all related model actions are disabled
    #
    # related_models_actions = {
    #     # it's possible to enable/disable links for related models here
    #     'member_organisation': {
    #         'can_add_related': False,
    #         'can_change_related': False,
    #         'can_delete_related': False,
    #     }
    # }

    app_label = None
    model_name = None

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)

        if not self.related_models_actions:
            self.related_models_actions = dict()

        # update django template paths with "self.url_prefix"
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if (attr_name.endswith('_template') and
                    isinstance(attr, str) and attr.endswith('.html')):
                setattr(self, attr_name, attr.format(url_prefix=self.url_prefix))

        self.app_label = self.model._meta.app_label
        self.model_name = self.model._meta.model_name

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = self.filter_queryset_by_permissions(request, queryset=queryset)
        return queryset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        form_field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if not form_field:
            return None

        form_field.queryset = self.filter_queryset_by_permissions(
            request, queryset=form_field.queryset
        )
        return form_field

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        form_field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if not form_field:
            return None

        form_field.queryset = self.filter_queryset_by_permissions(
            request, queryset=form_field.queryset
        )
        return form_field

    def filter_queryset_by_permissions(self, request, queryset):
        method_name = (
            f'get_{queryset.model._meta.app_label}__{queryset.model._meta.model_name}_queryset'
        ).lower()

        if callable(getattr(self, method_name, None)):
            filtered_queryset = getattr(self, method_name)(request, queryset)
        else:
            if self.raise_not_implemented_queryset_exception:
                # default behaviour, if a filter queryset isn't specified,
                # raise errors with additional information
                raise NotImplementedError(f'Not implemented "{self}.{method_name}()"')
            else:
                # "default to allow" case, just return an original queryset
                filtered_queryset = queryset

        if request.user.is_superuser:
            # filtered queryset is calculated due to check possible errors by a superuser
            # like: a not implemented filter queryset method
            return queryset
        else:
            return filtered_queryset

    def get_changelist(self, request, **kwargs):
        from member_organisations.custom_admin.change_list import CustomAdminChangeList
        CustomAdminChangeList.url_prefix = self.url_prefix
        return CustomAdminChangeList

    def get_custom_urls(self, required_django_group_name):
        app_label = self.app_label
        model_name = self.model_name

        def check_permissions(user):
            if user.is_superuser:
                # django superuser is allowed always
                return True
            # user must have a required group for admin sections ("MO Admins", "GO Admins")
            return user.groups.filter(name=required_django_group_name).exists()

        custom_urls = [
            path(
                f'{self.url_prefix}/{app_label}/{model_name}/',
                user_passes_test(check_permissions)(self.custom_admin_changelist_view),
                name=f'{self.url_prefix}_{app_label}_{model_name}_changelist'
            ),
            path(
                f'{self.url_prefix}/{app_label}/{model_name}/add/',
                user_passes_test(check_permissions)(self.custom_admin_add_view),
                name=f'{self.url_prefix}_{app_label}_{model_name}_add',
            ),
            path(
                f'{self.url_prefix}/{app_label}/{model_name}/<path:object_id>/change/',
                user_passes_test(check_permissions)(self.custom_admin_change_view),
                name=f'{self.url_prefix}_{app_label}_{model_name}_change',
            ),
            path(
                f'{self.url_prefix}/{app_label}/{model_name}/<path:object_id>/delete/',
                user_passes_test(check_permissions)(self.custom_admin_delete_view),
                name=f'{self.url_prefix}_{app_label}_{model_name}_delete',
            ),
        ]

        return custom_urls

    def get_urls_context(self, request, args=None):
        extra_context = dict()
        extra_context['custom_admin_add_url'] = reverse(
            f'admin:{self.url_prefix}_{self.app_label}_{self.model_name}_add'
        )
        extra_context['custom_admin_changelist_url'] = reverse(
            f'admin:{self.url_prefix}_{self.app_label}_{self.model_name}_changelist'
        )

        if request:
            # required to have request in "self"
            # example: CompanyOrganisationUserCustomAdmin.impersonate_user
            self.request = request

        if args:
            extra_context['custom_admin_delete_url'] = reverse(
                f'admin:{self.url_prefix}_{self.app_label}_{self.model_name}_delete',
                args=args
            )
            extra_context['custom_admin_change_url'] = reverse(
                f'admin:{self.url_prefix}_{self.app_label}_{self.model_name}_change',
                args=args
            )
        return extra_context

    def custom_admin_changelist_view(self, request, extra_context=None):
        extra_context = self.get_urls_context(request)
        return super().changelist_view(request, extra_context)

    def custom_admin_add_view(self, request, form_url='', extra_context=None):
        extra_context = self.get_urls_context(request)
        return super().add_view(request, form_url, extra_context)

    def custom_admin_change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = self.get_urls_context(request, args=(object_id, ))
        return super().change_view(request, object_id, form_url, extra_context)

    def custom_admin_delete_view(self, request, object_id, extra_context=None):
        extra_context = self.get_urls_context(request, args=(object_id,))
        return super().delete_view(request, object_id, extra_context)


class BaseM2MTokenAdmin(admin.ModelAdmin):
    def user(self, obj):
        return obj.token.user
    user.admin_order_field = 'token__user'

    def created(self, obj):
        return obj.token.created
    created.admin_order_field = 'token__created'

    def member_organisation(self, obj):
        mo = obj.token.user.member_organisations_memberorganisation.first()
        mo_by_company = obj.token.user.company_organisations_companyorganisation.first()
        mo_by_company = mo_by_company.member_organisation if mo_by_company else None
        return mo or mo_by_company

    def save_model(self, request, obj, form, change):
        """
        Auto generate token for new instances
        """

        if not obj.pk:
            token_string = AuthToken.objects.create(request.user, expires=None)
            token_instance = AuthToken.objects.filter(
                token_key=token_string[:KNOX_CONSTANTS.TOKEN_KEY_LENGTH]
            ).first()
            obj.token = token_instance

            messages.add_message(
                request, messages.WARNING,
                mark_safe(
                    f'ATTENTION! Token is created, this is the last chance to save it '
                    f'for the further usage: <strong>{token_string}</strong>'
                )
            )

        super().save_model(request, obj, form, change)
