from rest_framework import generics
from knox.auth import TokenAuthentication

from api.permissions import IsMOUser
from api.serializers.mo_serializer import MemberOrganisationSerializer
from member_organisations.models import MemberOrganisation


class MemberOrganisationRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = MemberOrganisationSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsMOUser,)
    http_method_names = ('get', )
    lookup_field = 'slug'

    def get_queryset(self):
        return MemberOrganisation.objects.all()
