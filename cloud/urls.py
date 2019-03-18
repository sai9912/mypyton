from django.urls import path

from . import views

app_name = 'cloud'
urlpatterns = [
    path('log_table/<int:gtin>/', views.log_table, name='log_table'),
]
