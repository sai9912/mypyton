from django.contrib import admin
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from oidc_rp import views as oidc_views

from cloud.views import log_table
from activate.views import account_create_or_update
from users.views import (
    profile, profile_js, admin_profile_js, organization_user_detail, terms_of_service, spa
)


schema_view = get_schema_view(
    openapi.Info(  # TODO: Change this with properly data
        title="BCM API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.bcm.com/policies/terms/",
        contact=openapi.Contact(email="contact@bcm.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('API/v0/AccountCreateOrUpdate/', account_create_or_update),
    path('profile/', profile, name='profile'),
    path('profile-js/', profile_js, name='profile_js'),
    path('spa/', spa, name='spa'),
    path('admin-profile-js/', admin_profile_js, name='admin_profile_js'),
    path('log_table/<int:gtin>/', log_table, name='log_table'),
    path('activate/', include('activate.urls')),
    path('prefixes/', include('prefixes.urls')),
    path('products/', include('products.urls')),
    path('users/organization_user_detail/<organization_pk>/<user_pk>/', organization_user_detail, name='organization_user_detail'),
    path('users/', include('users.urls')),
    path('excel/', include('excel.urls')),
    path('admin/', admin.site.urls),
    path('terms/', terms_of_service, name='terms_of_service'),
    path('impersonate/', include('impersonate.urls')),
    path('rosetta/', include('rosetta.urls')),
    path('barcodes/', include('barcodes.urls')),
    path('frontend/', include('frontend.urls')),
    path('bcm-rq/', include('django_rq.urls')),  # django-rq task queue
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-i18n'),
    # <-- this is a override (FIXME together with SSO)
    path('oidc/callback/', oidc_views.OIDCAuthCallbackView.as_view(), name='oidc_auth_callback'),
    # <-- end FIXME
    path('oidc/', include('oidc_rp.urls')),
    path("", include(('BCM.urls', 'BCM'), namespace='BCM')),
    path('api/v1/', include('api.urls')),
    path('api/schema/', schema_view.with_ui('swagger', cache_timeout=None), name='api-docs')
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
