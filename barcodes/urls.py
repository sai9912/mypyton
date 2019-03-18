from django.urls import path

from . import views

app_name = 'barcodes'
urlpatterns = [
    path('ajax/<bc_kind>/<gtin>/preview/', views.barcodes_preview, name='barcodes_preview'),
    path('ajax/<bc_kind>/<gtin>/generate/', views.barcodes_generate, name='barcodes_generate'),
    path('ajax/<bc_kind>/<gtin>/<dl_type>/', views.barcodes_image_download, name='barcodes_image_download'),
]
