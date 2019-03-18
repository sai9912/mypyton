from django.urls import path

from . import views

app_name = 'frontend'

urlpatterns = [
    path('index.html', views.index, name='frontend')
]
