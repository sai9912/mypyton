from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from .generic_views import GenericBCMViews
from users.models import Profile
from member_organisations.models import MemberOrganisation
from rest_framework import generics
from django.contrib.auth.models import User
from api.serializers.user_serializer import (
    UserSerializer, UserUpdateSerializer, UserUploadSerializer
)
from api.permissions import IsOwnerOrMOStaff, IsSelfUser, IsMOAdminOrOwner


class UsersListCreateAPIView(GenericBCMViews, generics.ListCreateAPIView):
    """
    get: List all Users
    """
    serializer_class = UserSerializer
    permission_classes = (IsMOAdminOrOwner,)

    def get_queryset(self):
        """
        List users based on the logged-in user
        """
        mo = MemberOrganisation.objects.get(users=self.request.user)
        if self.user_type_query:
            return User.objects.filter(profile__member_organisation__slug=mo.slug)
        return User.profile.objects.all()


class UserRetreiveAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Only MO admin or MO owner can use this API now,
    the same data is returned by the "/accounts/login/" API for user own data.
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'profile__uid'
    permission_classes = (IsMOAdminOrOwner, )


class UserUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserUpdateSerializer
    queryset = User.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'user_id'
    permission_classes = (IsSelfUser, )  # todo: permissions for staff
    http_method_names = ['get', 'patch', 'head', 'options', ]


class UserCreateByCompanyAPIView(GenericBCMViews, generics.ListCreateAPIView):
    """
    post: Create User
    """

    serializer_class = UserSerializer
    # permission_classes = (IsOwnerOrMOStaff, )
    permission_classes = (IsMOAdminOrOwner, )

    def get_queryset(self):
        member_organisation = self.request.user.profile.member_organisation
        return User.objects.filter(member_organisation=member_organisation).all()

    def get_serializer(self, *args, **kwargs):
        if self.kwargs.get('uuid'):
            return self.serializer_class(
                context={'request': self.request, 'uuid': self.kwargs.get('uuid')},
                *args, **kwargs
            )
        return self.serializer_class(context={'request': self.request}, *args, **kwargs)


class UserUploadAPIView(generics.UpdateAPIView):
    """
    upload a file with companies
    we use PUT here to retrieve a member organisation by built-in features
    TokenAuthentication is default auth type according to settings
    """

    queryset = MemberOrganisation.objects.all()
    serializer_class = UserUploadSerializer
    permission_classes = (IsMOAdminOrOwner,)
    lookup_url_kwarg = 'mo'
    lookup_field = 'slug'
