import json
import logging

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import BaseCommand
from django.db import IntegrityError
# create management commands to populate site admins. GO Admins are coming from
# gs1go-admin user role, everyone else would require a specific country-based
# group (mo-admin). The login / register forms illustrate the principle.
# First MO admin is always the group admin
from itsdangerous import URLSafeTimedSerializer

from barcodes.utilities import normalize
from company_organisations.models import CompanyOrganisation
from member_organisations.models import MemberOrganisation
from services import users_service, prefix_service


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='?', default='deployment/deployment-v1-2018-03/mo_users.json', type=str)

    def handle(self, *args, **options):
        """
        python manage.py load_company_user deployment/deployment-v1-2018-03/mo_users.json
        :return:
        """
        filename = options['filename']

        try:
            with open(filename) as json_data:
                data = json.load(json_data)
        except Exception as e:
            print('\n**************\nUnable to load json file. {0}. \n\n\nException message: '.format(filename),
                  e.message)
        else:

            companies_data = data.get('companies')
            if companies_data:
                for company_data in companies_data:

                    if not 'uuid' in company_data:
                        continue
                    try:
                        # expected value: email, company_name, member_organization, uuid, company_prefix
                        email = company_data.get('email')
                        company_name = company_data.get('company_name')
                        try:
                            member_organisation = MemberOrganisation.objects.get(
                                slug=company_data.get('role'))
                        except MemberOrganisation.DoesNotExist:
                            member_organisation = None

                        # get company
                        company_organisation, company_organisation_created = CompanyOrganisation.objects.get_or_create(
                            uuid=company_data.get('uuid'), defaults={
                                'member_organisation': member_organisation,
                                'name': company_data.get('name')
                            }
                        )
                        #print("Company  Created:- " if company_organisation_created else "Company Updated:- ",
                        #      u' '.join(
                        #          [company_organisation.uuid]).encode('utf-8').strip())

                        # update company name if any
                        if company_name:
                            company_organisation.company = company_name
                            company_organisation.save()

                        auth_user, auth_user_created = users_service.get_or_create(email=email,
                                                                                   defaults={
                                                                                       'username': email,
                                                                                       'member_organisation': member_organisation,
                                                                                       'company_organisation': company_organisation
                                                                                   })

                        auth_user.save()
                        # print('Create New User:- ' if auth_user_created else 'Updated User:- ', auth_user.email)
                        company_organisation = users_service.get_company_organisation(auth_user)

                    except Exception as e:
                        print(company_data)
                        print(str(e))
                        continue

                    log_message = 'logging in: ' + str(auth_user.email) + '::' + str(company_organisation.company)
                    log_extra = {
                        'user': auth_user.email,
                        'company': company_organisation.company
                    }
                    logging.getLogger().info(log_message, extra=log_extra)
                    logging.getLogger('audit').info(log_message, extra=log_extra)

                    # if user's organisation has prefix override, use it
                    # if not use prefixes provided by the form
                    if company_organisation.prefix_override:
                        form_prefix = company_organisation.prefix_override
                        form_prefixes = form_prefix.split(',')
                    else:
                        form_prefixes = company_data.get('prefixes')

                    prefixes = prefix_service.find(user=auth_user).all()
                    prefixes_list = [p.prefix for p in prefixes]

                    # set gln to be first prefix
                    if len(prefixes_list) > 0:
                        first_prefix = prefixes_list[0]
                        derived_gln = normalize("EAN13", first_prefix)
                        company_organisation.gln = derived_gln
                        company_organisation.save()

                    for prfx in form_prefixes:
                        # if not re.match(settings.GS1_PREFIX_START_REGEX, prfx[:3]) or len(prfx) < 6:
                        #     if prfx.find('20') == 0:  # we will not complain about variable weight
                        #         continue
                        #     else:
                        #         return jsonify(success=False, message='Invalid prefix %s' % prfx)
                        if prfx not in prefixes_list:
                            try:
                                prefix = prefix_service.create(user=auth_user, prefix=prfx)
                            except IntegrityError:
                                print('\n\n*** ERROR:  Prefix {0} has been allocated for another user\n\n'.format(prfx))
                                continue
                            try:
                                prefix.make_starting_from()
                            except:
                                prefix.starting_from = None
                            prefix_service.save(prefix)
                        else:
                            i = prefixes_list.index(prfx)
                            if prefixes[i].is_suspended:
                                prefixes[i].is_suspended = False
                                prefix_service.save(prefixes[i])

                    for prfx in prefixes_list:
                        if prfx not in form_prefixes:
                            prefix = prefix_service.find(user=auth_user, prefix=prfx).first()
                            prefix.is_suspended = True
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
                            print('\n\nERROR: No working prefix found\n\n')
                            continue

                    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
                    token = serializer.dumps([auth_user.email, company_organisation.uuid])
                    logging.getLogger().debug('Created token: %s' % token)
                    # print('-' * 50)
        # print("\n\n***************** Loading Companies User from File Finished *****************\n\n")
