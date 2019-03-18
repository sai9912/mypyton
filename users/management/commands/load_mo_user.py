import json

from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db import IntegrityError

# create management command to load company users (similar as in BCM/flask app)
from member_organisations.models import MemberOrganisation
from users.models import Profile


class Command(BaseCommand):
    help = "Loads MO users (testers and admins from json file)"

    def add_arguments(self, parser):
        parser.add_argument('filename',  nargs='?', default='deployment/deployment-v1-2018-03/mo_admins.json', type=str)

    def handle(self, *args, **options):
        """
        python manage.py load_mo_user deployment/deployment-v1-2018-03/mo_admins.json
        :param args:
        :param options:
        :return:
        """
        filename = options['filename']
        # print("\n\n***************** Loading Admin User from File *****************\n\n")
        # print("Reading Data From:- ", filename)
        try:
            with open(filename) as json_data:
                data = json.load(json_data)
        except Exception as e:
            print('\n**************\nUnable to load json file. {0}. \n\n\nException message: '.format(filename), e.message)
        else:
            organisations = data.get('organisations')
            if not organisations:
                print("seems like invalid file")
                return
            for member_organization_slug, users in organisations.items():
                # print('-'*50)
                go_user = False

                if member_organization_slug == 'gs1go':
                    go_user = True

                try:
                    member_organization = MemberOrganisation.objects.get(slug=member_organization_slug)
                except ObjectDoesNotExist:
                    print("Unable to get Member-Organization with slug: ", member_organization_slug)
                    continue
                for user_data in users:
                    default_data = dict(username=user_data['email'],)
                    user, created = User.objects.get_or_create(email=user_data['email'], defaults=default_data)
                    user.set_password(user_data.get('password', 'default_password'))

                    if 'name' in user_data:
                        splitted_names = user_data['name'].rsplit(" ", 1)

                        if len(splitted_names) == 2:
                            first_name, last_name = splitted_names
                            user.first_name = first_name
                            user.last_name = last_name
                        else:
                            user.first_name = user_data['name']
                    user.save()

                    #
                    if hasattr(user, 'profile'):
                        profile = user.profile
                        profile.customer_role = user_data.get('user_role')
                    else:
                        profile = Profile.objects.create(user=user, customer_role=user_data.get('user_role'))

                    # explcitly set MO on admin profile
                    profile.member_organisation = member_organization
                    profile.save()

                    # print('create new user: {0}'.format(user.email) if created \
                    #     else 'updated user: {0}'.format(user.email))

                    if go_user:
                        go_admin_group, is_created = Group.objects.get_or_create(name='GO Admins')
                        user.groups.add(go_admin_group)

                    mo_admin_group, is_created = Group.objects.get_or_create(name='MO Admins')
                    user.groups.add(mo_admin_group)
                    # make admin if it is first user?
                    # upd: it seems all mo_admin should be admins
                    member_organization.get_or_add_user(user, is_admin=True)
                # print('-'*50)
        # print("\n\n***************** Loading Admin User from File Finished *****************\n\n")
