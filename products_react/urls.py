from django.urls import path

from . import views

app_name = 'products_react'
urlpatterns = [
    path('<int:product_id>/fulledit/', views.fulledit, name='fulledit'),
]
