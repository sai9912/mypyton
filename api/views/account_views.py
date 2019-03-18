import logging
import re

from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import IntegrityError
from django.contrib.auth import login, user_logged_out
from django.http import HttpResponseForbidden

from drf_yasg.utils import swagger_auto_schema
from knox.models import AuthToken
from knox.auth import TokenAuthentication
from knox.views import LoginView as KnoxLoginView

from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.user_serializer import UserSerializer
from api.authentication import CsrfExemptSessionAuthentication
from api.utils import check_m2m_token
from api.serializers.account_serializers import AccountCreateOrUpdateSerializer
from barcodes.utilities import normalize
from services import prefix_service
from services import users_service
from users.helpers import get_api_auth
from member_organisations.models import MemberOrganisation


class UserLoginView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, TokenAuthentication)

    @swagger_auto_schema(request_body=AuthTokenSerializer)
    def post(self, request, *args, **kwargs):
        """logs in the user"""
        data = request.data
        # m2m_token = data.get('m2m_token', None)
        # if not check_m2m_token(request.user, m2m_token):
        #     return Response({
        #         'user': '',
        #         'token': ''
        #     })

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = AuthToken.objects.create(user)
        login(request, user)  # this sets csrftoken and sessionid cookies

        prefixes = prefix_service.find(user=user).all()
        if len(prefixes) == 1:
            user.profile.product_active_prefix = prefixes[0]
            user.profile.save()

        return Response({
            'user': UserSerializer(user).data,
            'token': token
        })

    def get(self, request):
        """ validates if user is still logged in, in which case returns app token"""
        if request.user.is_authenticated:
            token = AuthToken.objects.create(request.user)
            return Response({
                'user': UserSerializer(request.user, context={'request': request}).data,
                'token': token
            })
        return HttpResponseForbidden()


class UserRenewView(KnoxLoginView):
    serializer_class = AuthTokenSerializer


class CurrentUserInfo(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return Response({
                'user': UserSerializer(request.user, context={'request': request}).data
            })
        return HttpResponseForbidden()


class UserLogoutView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        request._auth.delete()
        user_logged_out.send(sender=request.user.__class__,
                             request=request, user=request.user)
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class UserLogoutAllView(APIView):
    """
    post: Log the user out of all sessions.
    I.E. deletes all auth tokens for the user.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        request.user.auth_token_set.filter(m2m_tokens__isnull=True).delete()
        user_logged_out.send(sender=request.user.__class__,
                             request=request, user=request.user)
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class ProtectedDataView(APIView):
    """Return protected data main page."""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """Process GET request and return protected data."""

        data = {
            'data': 'THIS IS THE PROTECTED STRING FROM SERVER',
        }

        return Response(data, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    lookup_field = "username"


class TermsOfServiceAPI(APIView):
    """
    Simple serializer for `terms of services`
    Took date from static files and transform it into json.
    """

    def get(self, request, format=None):
        res = {}

        try:
            slug = request.user.profile.member_organisation.slug
            f = open('static/legal/terms_%s.txt' % slug, 'rt')
        except:
            f = open('static/legal/terms_gs1go.txt', 'rt')
        res["terms"] = f.read()
        f.close()

        res["date_terms"] = settings.DATE_TERMS

        with open("static/legal/terms_cloud.txt") as terms_file:
            res["terms_cloud"] = "".join(terms_file.readlines())

        res["date_terms_cloud"] = settings.DATE_TERMS_CLOUD
        return Response(res)


class AccountCreateAPIView(generics.CreateAPIView):
    serializer_class = AccountCreateOrUpdateSerializer
    authentication_classes = [TokenAuthentication,]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            member_organisation = MemberOrganisation.objects.get(
                slug=request.data['member_organisation']
            )
        except:
            return Response(
                {'data': 'Unknown member_organisation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if member_organisation.login_api_auth_only:
            try:
                company_organisation, auth_user = self.perform_login(serializer)
            except Exception:
                return Response(
                    {'data': 'Unknown user'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            company_organisation, auth_user = self.perform_create(serializer)

        member_organisation = auth_user.profile.member_organisation

        self.push_info_to_logger(auth_user, company_organisation)

        if member_organisation.login_api_secure:
            try:
                token_user = request._auth.user
                assert token_user.profile.member_organisation == auth_user.profile.member_organisation
            except AssertionError as e:
                return Response(
                    {'data': 'm2m token mismatch'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # return if we are in read-only mode
        if member_organisation.login_api_auth_only:
            return Response(
                get_api_auth(auth_user.email),
                status=status.HTTP_200_OK
            )

        # if user's organisation has prefix override, use it
        # if not use prefixes provided by the form
        if not company_organisation.prefix_override:
            form_prefix = serializer.validated_data.get('company_prefix', None)
        else:
            form_prefix = company_organisation.prefix_override
        if form_prefix is not None:
            form_prefixes = form_prefix.split(',')
        else:
            form_prefixes = []

        prefixes = prefix_service.find(user=auth_user).all()
        prefixes_list = [v for v in prefixes.values_list('prefix', flat=True)]

        # set gln to be first prefix
        if len(prefixes_list) > 0:
            first_prefix = prefixes_list[0]
            derived_gln = normalize("EAN13", first_prefix)
            company_organisation.gln = derived_gln

        # if we are in read-write copy country from MO to the company
        self.set_country_and_save(company_organisation, member_organisation)

        for prfx in form_prefixes:
            if not re.match(member_organisation.gs1_prefix_regex, prfx[:3]) or len(prfx) < 6:
                if prfx.find('20') == 0:  # we will not complain about variable weight
                    continue
                else:
                    return Response(status=400, data=f'Invalid prefix {prfx}')

            if prfx not in prefixes_list:
                try:
                    prefix = prefix_service.create(user=auth_user, prefix=prfx)
                except IntegrityError:
                    return Response(
                        status=400,
                        data=f'Prefix {prfx} has been allocated for another user'
                    )
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
            # else:
            #     return Response(status=400, data='No working prefix found')

        return Response(
            get_api_auth(auth_user.email),
            status=status.HTTP_201_CREATED
        )

    def perform_create(self, serializer):
        return serializer.save()

    @staticmethod
    def perform_login(serializer):
        email = serializer.validated_data['email']
        auth_user = users_service.get_no_create(email=email)
        company_organisation = users_service.get_company_organisation(auth_user)
        return company_organisation, auth_user

    def push_info_to_logger(self, auth_user, company_organisation):

        log_message = (
            f'logging in: {auth_user.email}::{company_organisation.company}'
        )
        log_extra = {
            'user': auth_user.email,
            'company': company_organisation.company,
            'ip_address': self.request.environ.get('REMOTE_ADDR')
        }
        logging.getLogger().info(log_message, extra=log_extra)
        logging.getLogger('audit').info(log_message, extra=log_extra)

    def set_country_and_save(self, company_organisation, member_organisation):
        company_organisation.country = member_organisation.country
        company_organisation.save()
