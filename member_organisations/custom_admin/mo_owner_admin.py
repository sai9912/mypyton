from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path, reverse, NoReverseMatch

from member_organisations.go_admin.config import config as go_admin_config
from member_organisations.helpers.mo_admin_helpers import mo_redirect_to_login
from member_organisations.mo_admin.config import config as mo_admin_config


class MemberOrganisationOwnerAdmin(admin.ModelAdmin):
    list_display = ('organization_user', 'organization')

    # apps which processed by hidden from main list
    hidden_apps = ('auth',)

    def get_urls(self):

        urls = super().get_urls()
        custom_urls = [
            path('mo_admin/', self.mo_admin_index, name='mo_admin'),
            path('go_admin/', self.go_admin_index, name='go_admin'),
        ]

        # retrieving custom urls for all apps and all required models (go admin)
        custom_urls += self.get_custom_urls_for_config(**mo_admin_config)
        # retrieving custom urls for all apps and all required models (mo admin)
        custom_urls += self.get_custom_urls_for_config(**go_admin_config)

        return custom_urls + urls  # urls order matters!

    @classmethod
    def get_custom_urls_for_config(cls, apps_config, required_django_group_name, **kwargs):
        """
        Retrieving custom urls for all apps and all required models go admin
        """

        custom_urls = list()
        for app_label, admin_views in apps_config.items():
            for admin_view in admin_views:
                custom_urls += admin_view.get_custom_urls(required_django_group_name)

        return custom_urls

    @classmethod
    def get_reverse_url(cls, url_prefix, app_label, model_name, action, default=''):
        try:
            return reverse(f'admin:{url_prefix}_{app_label}_{model_name}_{action}')
        except NoReverseMatch:
            return default

    def get_app_list(self, request, apps_config, url_prefix):
        """
        Retrieves allowed app list, update urls to custom admin views
        """

        app_list = [
            item for item in self.admin_site.get_app_list(request)
            if (item.get('app_label') in apps_config.keys()
                and item.get('app_label') not in self.hidden_apps)
        ]

        for app in app_list:
            app_label = app.get('app_label', '')
            app['app_url'] = '#'  # prevent direct urls to base django admin
            allowed_model_names = [
                admin_item.model._meta.model_name
                for admin_item in apps_config[app_label]
            ]
            app['models'] = [
                model for model in app.get('models', [])
                if model.get('object_name', '').lower() in allowed_model_names
            ]

            for model in app.get('models', []):
                model_name = model.get('object_name', '').lower()
                model['admin_url'] = self.get_reverse_url(
                    url_prefix, app_label, model_name, action='changelist'
                )
                model['add_url'] = self.get_reverse_url(
                    url_prefix, app_label, model_name, action='add'
                )

        return app_list

    def mo_admin_index(self, request):
        """
        index page for mo admin, displays list of required apps
        :param request:
        :return:
        """

        is_mo_admin = request.user.groups.filter(name='MO Admins').exists()
        if not is_mo_admin and not request.user.is_superuser:
            return mo_redirect_to_login(request)

        context = dict(
            # Include common variables for rendering the admin template.
            self.admin_site.each_context(request),
            app_list=self.get_app_list(
                request, mo_admin_config['apps_config'], url_prefix='mo_admin'
            ),
        )
        return TemplateResponse(request, 'admin/mo_admin/index.html', context)

    def go_admin_index(self, request):
        """
        index page for mo admin, displays list of required apps
        :param request:
        :return:
        """

        is_go_admin = request.user.groups.filter(name='GO Admins').exists()
        if not is_go_admin and not request.user.is_superuser:
            return mo_redirect_to_login(request)

        context = dict(
            # Include common variables for rendering the admin template.
            self.admin_site.each_context(request),
            app_list=self.get_app_list(
                request, go_admin_config['apps_config'], url_prefix='go_admin'
            ),
        )
        return TemplateResponse(request, 'admin/go_admin/index.html', context)

    list_filter = ['organization', ]
