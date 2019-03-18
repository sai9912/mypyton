from rest_framework import generics, status
from rest_framework.exceptions import APIException
from api.serializers.prefix_serializer import PrefixSerializer, PrefixUploadSerializer
from api.permissions import IsOwnerOrMOStaff, IsMOAdminOrOwner
from member_organisations.models import MemberOrganisation
from prefixes.models import Prefix
from .generic_views import GenericBCMViews


class PrefixModifyAPIView(GenericBCMViews, generics.UpdateAPIView):
    queryset = Prefix.objects.all()
    lookup_field = 'prefix'
    lookup_url_kwarg = 'prefix'
    serializer_class = PrefixSerializer

    def update(self, request, *args, **kwargs):
        if self.kwargs.get('action'):
            # todo: uncomment and add additional logic here when it will be required
            # todo: serializer is adjusted to handle status changes by the "action" parameter
            # kwargs['partial'] = True
            # request.data['action'] = self.kwargs.get('action')
            raise APIException(
                'Actions for Prefixes are not implemented yet',
                status.HTTP_501_NOT_IMPLEMENTED
            )

        return super().update(request, *args, **kwargs)


class PrefixesListCreateAPIView(GenericBCMViews, generics.ListCreateAPIView):
    """
    get: List all Prefixes for the given company
    post: Create Prefix for the given company
    """
    serializer_class = PrefixSerializer
    permission_classes = (IsOwnerOrMOStaff, )

    def get_serializer(self, *args, **kwargs):
        if self.kwargs.get('uuid'):
            return self.serializer_class(
                context={'request': self.request, 'uuid': self.kwargs.get('uuid')},
                *args, **kwargs
            )
        return self.serializer_class(context={'request': self.request}, *args, **kwargs)

    def get_queryset(self):
        """
        Query Prefixes by logged User's company
        If company does not exist return 404
        """

        if self.user_type_query is None:
            return Prefix.objects.none()
        else:
            return Prefix.objects.filter(**self.user_type_query)


class PrefixesRetrieveAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    get: Retrieve the given Prefix
    patch: Partial update given Prefix (Means that does not require any required fields)
    put: Fully update given Prefix (Means that require all the required fields even those that already was filled)
    delete: Delete the given Prefix
    """
    serializer_class = PrefixSerializer
    lookup_field = 'prefix'
    permission_classes = (IsOwnerOrMOStaff,)
    queryset = Prefix.objects.all()


class PrefixesUploadAPIView(generics.UpdateAPIView):
    """
    upload a file with companies
    we use PUT here to retrieve a member organisation by built-in features
    TokenAuthentication is default auth type according to settings
    """

    queryset = MemberOrganisation.objects.all()
    serializer_class = PrefixUploadSerializer
    permission_classes = (IsMOAdminOrOwner, )
    lookup_url_kwarg = 'mo'
    lookup_field = 'slug'
