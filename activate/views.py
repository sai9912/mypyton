import logging
import re
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import IntegrityError
from django.shortcuts import render, redirect, reverse
# from django.http import Http404
from django.conf import settings
from barcodes.utilities import normalize
from company_organisations.models import CompanyOrganisation
from member_organisations.models import MemberOrganisation
from services import users_service, prefix_service
from .forms import AccountCreateOrUpdateForm
from core import jsonify
from users.helpers import get_api_auth
from prefixes.models import Prefix
from django.views.decorators.csrf import csrf_exempt
from api.utils import check_m2m_token


@csrf_exempt
def account_create_or_update(request):

    auth_only = False

    if request.method == 'POST':
        form = AccountCreateOrUpdateForm(request.POST)
        if form.is_valid():
            try:
                if not request.user.is_anonymous:
                    m2m_token = form.cleaned_data.get('m2m_token', '')
                    if not check_m2m_token(request.user, m2m_token):
                        return redirect(reverse('BCM:login'))

                try:
                    member_organisation = MemberOrganisation.objects.get(
                        slug=form.cleaned_data.get('member_organisation'))
                except MemberOrganisation.DoesNotExist:
                    member_organisation = None

                # core data
                email = form.cleaned_data.get('email')
                company_name = form.cleaned_data.get('company_name')

                # get company
                company_organisation, company_organisation_created = CompanyOrganisation.objects.get_or_create(
                    uuid=form.data.get('uuid'),
                    member_organisation=member_organisation
                )

                # update company name if any
                if company_name:
                    company_organisation.company = company_name
                    company_organisation.name = company_name
                    company_organisation.save()

                auth_user, auth_user_created = users_service.get_or_create(email=email,
                                                                           defaults={
                                                                               'username': email,
                                                                               'customer_role': 'gs1ie',
                                                                               'member_organisation': member_organisation,
                                                                               'company_organisation': company_organisation
                                                                           })

                auth_user.save()

                company_organisation = users_service.get_company_organisation(auth_user)
            except Exception as e:
                return jsonify(success=False, message=str(e))

            log_message = 'logging in: ' + str(auth_user.email) + '::' + str(company_organisation.company)
            log_extra = {'user': auth_user.email,
                         'company': company_organisation.company,
                         'ip_address': request.environ.get('REMOTE_ADDR')}
            logging.getLogger().info(log_message, extra=log_extra)
            logging.getLogger('audit').info(log_message, extra=log_extra)

            if form.data.get('company_prefix', '') == 13 * '0':
                auth_only = True

            if not auth_only:
                # if user's organisation has prefix override, use it
                # if not use prefixes provided by the form
                if not company_organisation.prefix_override:
                    form_prefix = form.data.get('company_prefix', '')
                else:
                    form_prefix = company_organisation.prefix_override
                form_prefixes = form_prefix.split(',')

                prefixes = prefix_service.find(user=auth_user).all()
                prefixes_list = list(prefixes.values_list('prefix', flat=True))

                # set gln to be first prefix
                if len(prefixes_list) > 0:
                    first_prefix = prefixes_list[0]
                    derived_gln = normalize("EAN13", first_prefix)
                    company_organisation.gln = derived_gln
                    company_organisation.save()

                for prfx in form_prefixes:
                    if not re.match(member_organisation.gs1_prefix_regex, prfx[:3]) or len(prfx) < 6:
                        if prfx.find('20') == 0:  # we will not complain about variable weight
                            continue
                        else:
                            return jsonify(success=False, message='Invalid prefix %s' % prfx)
                    if prfx not in prefixes_list:
                        try:
                            prefix = prefix_service.create(user=auth_user,
                                                           prefix=prfx,
                                                           status_id=Prefix.ACTIVE)
                        except IntegrityError:
                            return jsonify(success=False, message='Prefix %s has been allocated for another user' % prfx)
                        try:
                            prefix.make_starting_from()
                        except:
                            prefix.starting_from = None
                        prefix_service.save(user=auth_user, prefix=prefix)
                    else:
                        i = prefixes_list.index(prfx)
                        if prefixes[i].is_suspended:
                            prefixes[i].is_suspended = False
                            prefix_service.save(prefixes[i])

                for prfx in prefixes_list:
                    if prfx not in form_prefixes:
                        prefix = prefix_service.find(user=auth_user, prefix=prfx).first()
                        prefix.is_suspended = True
                        # prefix.is_active = False
                        prefix_service.save(prefix)

                # Check active prefix and set accordingly
                user_active_prefix = auth_user.profile.product_active_prefix
                if not user_active_prefix:
                    prefix = prefix_service.find(
                        user=auth_user, is_suspended=False
                    ).order_by('prefix').first()

                    if prefix:
                        prefix_service.make_active(user=auth_user, prefix=prefix.prefix)
                        prefix_service.save(prefix)
                    else:
                        return jsonify(success=False, message='No working prefix found')

            return redirect(get_api_auth(auth_user.email))
    else:
        form = AccountCreateOrUpdateForm()

    try:
        m2m_token_set = request.user.auth_token_set.all()
        m2m_token = m2m_token_set[0].digest
    except Exception:
        m2m_token = ''

    context = {'current_user': request.user,
               'm2m_token': m2m_token,
               'active_page': '',
               'form': form}
    return render(request, 'activate/AccountCreateOrUpdate.html', context)
