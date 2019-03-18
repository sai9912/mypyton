from knox.auth import TokenAuthentication
from rest_framework import generics
from rest_framework.generics import GenericAPIView

from member_organisations.models import MemberOrganisation
from .generic_views import GenericBCMViews
from api.serializers.company_serializer import CompanySerializer, CompanyUploadSerializer
from company_organisations.models import CompanyOrganisation
from api.permissions import IsOwnerOrMOStaff, IsMOAdminOrOwner


class CompaniesListCreateAPIView(GenericBCMViews, generics.ListCreateAPIView):
    """
    get: List all Companies
    post: Add Company
    """
    serializer_class = CompanySerializer
    permission_classes = (IsOwnerOrMOStaff,)

    def get_queryset(self):
        member_organisation = self.request.user.profile.member_organisation
        return CompanyOrganisation.objects.filter(member_organisation=member_organisation).all()


class CompanyRetreiveAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    get: Get a filtered list of Companies
    """
    serializer_class = CompanySerializer
    lookup_field = 'uuid'
    permission_classes = (IsOwnerOrMOStaff,)

    def get_queryset(self):
        objects = CompanyOrganisation.objects.all()
        return objects


class CompaniesUploadAPIView(generics.UpdateAPIView):
    """
    upload a file with companies
    we use PUT here to retrieve a member organisation by built-in features
    TokenAuthentication is default auth type according to settings
    """

    queryset = MemberOrganisation.objects.all()
    serializer_class = CompanyUploadSerializer
    permission_classes = (IsMOAdminOrOwner, )
    lookup_url_kwarg = 'mo'
    lookup_field = 'slug'
