import logging
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render, reverse, redirect
from django.conf import settings
from django.db.models import Count
from django.contrib.auth import login
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from services import prefix_service, users_service
from products.models.product import Product
from users.helpers import user_agreement_required, mo_admin_required
from .forms import AgreeRequiredForm
from knox.models import AuthToken
from django.http import JsonResponse, HttpRequest, HttpResponseForbidden
from api.serializers.user_serializer import UserSerializer
from prefixes.utils import get_range_data
from django.views.generic import TemplateView


@user_agreement_required
def profile(request):
    current_user = request.user

    company_organisation = users_service.get_company_organisation(current_user)

    member_organisation = current_user.profile.member_organisation

    prefixes = prefix_service.all(user=current_user)

    # set products count
    result = Product.objects.values('gs1_company_prefix').annotate(count=Count('gs1_company_prefix'))
    for prefix in prefixes:
        for row in result:
            if prefix.prefix == row['gs1_company_prefix']:
                setattr(prefix, 'products', row['count'])

    alerts = False
    terms_alert = False
    terms_version = settings.TERMS_VERSION

    profile = current_user.profile
    if request.method == 'POST':
        if request.POST.get('agree'):
            profile.agreed = True
            profile.agreed_date = timezone.now()
            profile.agreed_version = terms_version
            profile.save()

    if not profile.agreed:
        alerts = True
        terms_alert = True

    config = {'GS1_GLN_CAPABILITY': settings.GS1_GLN_CAPABILITY}

    context = {
        'current_user': current_user,
        'config': config,
        'alerts': alerts,
        'terms_alert': terms_alert,
        'terms_version': terms_version,
        'prefixes': prefixes,
        'range_data': get_range_data(request)
    }
    if company_organisation:
        # MemberOrganization admin might not have company organization so
        context.update({
            'uuid': company_organisation.uuid,
            'company_name': company_organisation.company,
            'organisation_active': company_organisation.active,
            'company_organisation': company_organisation
        })

    # decide where to redirect after auth_token has been set
    if not member_organisation or not member_organisation.gs1_enable_advanced_dashboard:
       return redirect('profile_js')

    return render(request, 'user/profile.html', context)


@user_agreement_required
def profile_js(request):
    context = {}
    return render(request, 'user/profile_js.html', context)

@user_agreement_required
def spa(request):
    context = {}
    if request.user:
        token = AuthToken.objects.create(request.user)  # create knox token for UI
        request.session['auth_token'] = token
        request.session['is_impersonate'] = request.user.is_impersonate

    return render(request, 'spa/index.html', context)


@mo_admin_required
def admin_profile_js(request):
    context = {}
    return render(request, 'admin/profile_js.html', context)


@user_agreement_required
def settings_page(request):
    company = request.user.profile.company_organisation

    company_users = company.users.all()

    context = {
        'company_users': company_users
    }

    return render(request, 'user/settings.html', context)


def user_agreement_required(request):

    url_next = request.GET.get('next', reverse('profile'))
    if request.method == 'POST':
        form = AgreeRequiredForm(request.POST)
        if form.is_valid():
            if request.user.profile.member_organisation.gs1_terms_version:
                terms_version = request.user.profile.member_organisation.gs1_terms_version
            else:
                terms_version = ''
            try:
                terms_updated = request.user.profile.member_organisation.gs1_terms_updated.strftime('%Y/%m/%d')
            except:
                terms_updated = ''
            terms_version_updated = (terms_version + ' ' + terms_updated).strip()
            if form.cleaned_data['agree'] and form.cleaned_data['terms_version'] == terms_version_updated:
                profile = request.user.profile
                profile.agreed = True
                profile.agreed_version = terms_version_updated
                profile.agreed_date = timezone.now()
                profile.save()
                url_next = form.cleaned_data['url_next']
                return redirect(url_next)
    form = AgreeRequiredForm()

    if request.user.profile.member_organisation.gs1_terms_version:
        terms_version = request.user.profile.member_organisation.gs1_terms_version
    else:
        terms_version = ''
    try:
        terms_updated = request.user.profile.member_organisation.gs1_terms_updated.strftime('%Y/%m/%d')
    except:
        terms_updated = ''
    terms_version_updated = terms_version + ' ' + terms_updated

    form.initial['url_next'] = url_next
    form.initial['terms_version'] = terms_version_updated

    try:
        slug = request.user.profile.member_organisation.slug
        f = open('static/legal/terms_%s.txt' % slug, 'rt')
    except:
        f = open('static/legal/terms_gs1go.txt', 'rt')
    terms_text = f.read()
    f.close()

    context = {
        'form': form,
        'terms_version': terms_version_updated,
        'terms_text': terms_text
    }
    return render(request, 'user/user_agreement_required.html', context)


def api_auth(request, token):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        logging.getLogger().debug('Received token: %s' % token)
        data = serializer.loads(token, max_age=30)
        email = data['email']
    except SignatureExpired:
        return render(request, 'activate/token_expired.html', status=403)
    user = users_service.find(email=email, customer_role='gs1ie')
    if not user:
        return render(request, 'activate/user_not_found.html', status=404)

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    # it seems it's useless cause if you don't save a token,
    # only token digest will be available which actually is a hash to this token
    token = AuthToken.objects.create(user)  # create knox token for UI

    if user.profile.login_count is None:
        login_count = 1
    else:
        login_count = user.profile.login_count + 1
    users_service.update(user.profile, login_count=login_count)

    return redirect(reverse('profile'))


def static_views_terms(request):
    return redirect('/terms')


def locations_locations_list(request):
    return HttpResponse('locations.locations_list')


def organization_user_detail(request, organization_pk, user_pk):
    # This is should be link to lib/python3.6/site-packages/organizations
    # we are not use django-organizations in the INSTALLED_APPS
    # so redirect to user admin
    url = f'/admin/auth/user/{user_pk}/change/'
    return redirect(url)



def terms_of_service(request):
    try:
        if request.user.profile.member_organisation.gs1_terms_version:
            version_terms = request.user.profile.member_organisation.gs1_terms_version
        else:
            version_terms = ''
        try:
            date_terms = request.user.profile.member_organisation.gs1_terms_updated.strftime('%Y/%m/%d')
        except:
            date_terms = ''
        slug = request.user.profile.member_organisation.slug
        f = open('static/legal/terms_%s.txt' % slug, 'rt')
        text_terms = f.read()
        f.close()
    except:
        version_terms = ''
        date_terms = settings.DATE_TERMS
        f = open('static/legal/terms.txt', 'rt')
        text_terms = f.read()
        f.close()

    context = {'version_terms': version_terms,
               'date_terms': date_terms,
               'date_terms_cloud': settings.DATE_TERMS_CLOUD,
               'text_terms': text_terms
               }

    return render(request, 'user/terms.html', context)
