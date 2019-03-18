from django.urls import path

from . import views

app_name = 'excel'
urlpatterns = [
    path('excel_export_select', views.excel_export_select, name='export_select'),
    path('excel_import_file', views.excel_import_file, name='import_file'),
]
