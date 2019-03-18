from django.urls import path

from . import views

app_name = 'activate'
urlpatterns = [
    path('AccountCreateOrUpdate/', views.account_create_or_update, name='account_create_or_update'),
]
