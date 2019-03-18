from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("signup", views.StaffMemberRegisterView.as_view(), name="signup"),
    path("login", views.StaffMemberLoginView.as_view(), name="login"),
    path("sso_redirect", views.SSORedirectView.as_view(), name="sso_redirect"),
    path("logout", views.BCMLogoutView.as_view(), name="logout"),
    path("", views.index, name="index"),
    path("after_login", views.after_login, name="after_login"),
    path("accounts/login/", views.index_redirect),
    path("", views.index_redirect, name="index_redirect"),
]
