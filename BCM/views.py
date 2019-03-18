# we use 100 characters line length, isn't it?
from django.contrib.auth.views import LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login as auth_login
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView
from django.views.generic.base import RedirectView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from BCM.helpers.utils import get_nested_attribute
from users.helpers import is_user_mo_admin_or_owner
from . import models
from company_organisations.models import CompanyOrganisation
from BCM.forms import StaffMemberRegistration, StaffMemberLogin


def index_redirect(request):
    countries = models.Country.objects.all()
    user = request.user
    context = dict(countries=countries)
    if hasattr(user, 'profile') and user.profile.customer_role.endswith('-admin'):
        uuid = user.profile.customer_role.split("-")[0]
        companies = CompanyOrganisation.objects.filter(uuid__istartswith=f'{uuid}')
        context['companies'] = companies
    return render(request, 'bcm/generic.html', context)


def index(request):
    user = request.user
    if user.groups.filter(name='GO Admins'):
        return redirect(reverse('admin:go_admin'))
    elif user.groups.filter(name='MO Admins'):
        return redirect(reverse('admin:mo_admin'))
    if request.user.is_authenticated:
        return redirect(reverse('profile'))
    return render(request, 'bcm/generic.html')


@login_required
def after_login(request):
    return redirect("profile")


class StaffMemberRegisterView(CreateView):
    model = User
    form_class = StaffMemberRegistration
    template_name = "bcm/registration/staff_registration.html"
    success_url = None
    object = None

    def dispatch(self, request, *args, **kwargs):
        """
        Redirectsalready authenticated user
        """

        if request.user.is_authenticated:
            self.object = request.user
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """
        Redirect to GO/MO admin (detected by a selected registration type)
        """

        if self.object.groups.filter(name='GO Admins'):
            return reverse('admin:go_admin')
        elif self.object.groups.filter(name='MO Admins'):
            return reverse('admin:mo_admin')
        # TODO: add if user do not have groups


class StaffMemberLoginView(FormView):
    model = User
    form_class = StaffMemberLogin
    template_name = "bcm/registration/staff_login.html"
    success_url = None
    object = None

    def dispatch(self, request, *args, **kwargs):
        """
        Redirectsalready authenticated user
        """

        if request.user.is_authenticated:
            self.object = request.user
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.get_user()
        auth_login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        """
        Redirect to GO/MO admin (detected by a selected registration type)
        """

        if self.object.is_staff:
            return reverse('admin:index')
        elif self.object.groups.filter(name='GO Admins'):
            return reverse('admin_profile_js')
        elif is_user_mo_admin_or_owner(self.object) and self.object.groups.filter(name='MO Admins'):
            # more strict rule is used
            # MO admin should have at least one is_admin/owner permissions
            return reverse('admin_profile_js')
        else:
            return reverse('profile')


class SSORedirectView(RedirectView):
    permanent = False

    def dispatch(self, request, *args, **kwargs):
        """
        Redirectsalready authenticated user
        """
        if request.user.is_authenticated:
            self.object = request.user
            return HttpResponseRedirect(self.get_redirect_url())
        else:
            return HttpResponseRedirect("/")

    def get_redirect_url(self, *args, **kwargs):
        if self.object.groups.filter(name='GO Admins'):
            return reverse('admin:go_admin')
        elif self.object.groups.filter(name='MO Admins'):
            return reverse('admin:mo_admin')
        else:
            return '/'


class BCMLogoutView(LogoutView):
    user = None
    default_next_page = reverse_lazy('BCM:index')

    def dispatch(self, request, *args, **kwargs):
        # we have to store logged in user when he is still available
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)

    def get_next_page(self):
        next_url = get_nested_attribute(
            self.user,
            'profile.member_organisation.gs1_logout_url',
            default_value=self.default_next_page or super().get_next_page()
        )
        return next_url
