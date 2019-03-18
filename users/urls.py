from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('static_views_terms', views.static_views_terms, name='static_views.terms'),
    path('locations_locations_list', views.locations_locations_list, name='locations.locations_list'),
    path('user_agreement_required', views.user_agreement_required, name='user_agreement_required'),
    path('api/auth/<str:token>/', views.api_auth, name='api_auth'),
    path('settings/', views.settings_page, name='settings'),
]
