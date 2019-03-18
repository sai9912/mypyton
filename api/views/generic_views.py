from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from knox.auth import TokenAuthentication
from rest_framework.exceptions import NotFound, ValidationError
from api.utils import is_member_organisation_staff, is_company_organisation
from api.permissions import IsOwnerOrMOStaff
from company_organisations.models import CompanyOrganisation
from member_organisations.models import MemberOrganisation


class GenericBCMViews(object):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsOwnerOrMOStaff,)

    @property
    def user_type_query(self):

        if self.request.user.groups.filter(name='GO Admins'):
            # go admins are allowed to retrieve all items (empty filter for querysets)
            return {}

        if is_member_organisation_staff(self.request.user):
            try:
                return {
                    # replace get -> filter + '__in' when multiple organizations will be allowed
                    'member_organisation': MemberOrganisation.objects.get(
                        users=self.request.user
                    )
                }
            except ObjectDoesNotExist:
                raise NotFound('Defined member organisation does not exist.')
            except MultipleObjectsReturned:
                organisations = MemberOrganisation.objects.filter(users=self.request.user)
                organisations = ', '.join([f"'{item.slug}'" for item in organisations])
                raise ValidationError(
                    f'Multiple organizations for the same user are not allowed: {organisations}'
                )

        if is_company_organisation(self.request.user):
            try:
                # replace get --> filter + '__in' when multiple organizations will be allowed
                return {
                    'company_organisation': CompanyOrganisation.objects.get(
                        users=self.request.user
                    )
                }
            except ObjectDoesNotExist:
                raise NotFound('Defined company does not exist.')
            except MultipleObjectsReturned:
                companies = CompanyOrganisation.objects.filter(users=self.request.user)
                companies = ', '.join([f"'{item.uuid}'" for item in companies])
                raise ValidationError(
                    f'Multiple companies for the same user are not allowed: {companies}'
                )
