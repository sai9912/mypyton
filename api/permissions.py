from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from api import utils
from company_organisations.models import CompanyOrganisation
from django.contrib.auth.models import User

from member_organisations.models import (
    MemberOrganisation, MemberOrganisationOwner, MemberOrganisationUser
)
from users.helpers import is_user_mo_admin_or_owner


class IsOwnerOrMOStaff(permissions.IsAuthenticated):
    """
    Custom permission to only allow owners of an object to see and edit it.
    Admin users however have access to all.
    """

    def has_permission(self, request, view):
        user = request.user

        if user.groups.filter(name='GO Admins').exists():
            # GO Admins are always allowed
            return True

        # company scope (prefixes)
        if view.kwargs.get('uuid'):
            queryset = CompanyOrganisation.objects.filter(uuid=view.kwargs.get('uuid'))
            if not queryset.exists():
                return False  # no such company
            company_organisation = queryset.first()
            if user.profile.member_organisation != company_organisation.member_organisation:
                return False  # company's MO is not user's MO

        if not super(IsOwnerOrMOStaff, self).has_permission(request, view):
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.groups.filter(name='GO Admins').exists():
            # GO Admins are always allowed
            return True

        if isinstance(obj, User):
            obj = obj.profile

        if utils.is_member_organisation_staff(user):
            return obj.member_organisation.users.filter(pk=user.pk).exists()

        if utils.is_company_organisation(user):
            if isinstance(obj, CompanyOrganisation):
                return obj.users.filter(pk=user.pk).exists()
            else:
                return obj.get_company_organisation().users.filter(pk=user.pk).exists()

        return False


class IsMOUser(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        # is authenticated
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        """
        If user belongs to a member organisation
        valid for objects:
            - MemberOrganisation
            - CompanyOrganisation
        """

        if obj.slug == 'gs1go':
            return True
        user = request.user
        if isinstance(obj, MemberOrganisation):
            return obj.users.filter(pk=user.pk).exists()
        elif isinstance(obj, CompanyOrganisation):
            return obj.member_organisation.users.filter(pk=user.pk).exists()

        return False


class IsMOAdminOrOwner(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        """
        If user is admin or an owner of any member organisation
        """

        if not super().has_permission(request, view):  # is authenticated
            return False

        if is_user_mo_admin_or_owner(request.user):
            # If user is an admin or an owner of any member organisation
            return True

        return False

    def get_member_organisations(self, obj):
        """
        source objects can have various types (MemberOrganisation, User, etc),
        here member organisations is retrieved from a source object
        """

        if isinstance(obj, MemberOrganisation):
            return [obj]
        elif isinstance(obj, User):
            # check if a target user has the same member organisation as request.user
            return list(obj.member_organisations_memberorganisation.all())
        else:
            # add a member_organisation retrieving rule for your object type
            raise PermissionDenied('Wrong object type for permissions checking')

    def has_object_permission(self, request, view, obj):
        """
        User is allowed if he has admin rights for MemberOrganisationUser
        or if he is the only owner of a MemberOrganisation (only one owner is possible for mo)
        """

        if request.user.groups.filter(name='GO Admins').exists():
            # GO Admins are always allowed
            return True

        member_organisations = self.get_member_organisations(obj)

        is_mo_admin = MemberOrganisationUser.objects.filter(
            is_admin=True,
            user=request.user,
            organization__in=member_organisations,
        )
        if is_mo_admin:
            return True

        is_mo_owner = MemberOrganisationOwner.objects.filter(
            organization_user__user=request.user,
            organization__in=member_organisations,
        )

        if is_mo_owner:
            return True

        return False


class IsSelfUser(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        # is authenticated
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        """
        Check is user update himself
        """

        return isinstance(obj, User) and request.user == obj
