import hashlib
import requests
from django.conf import settings
from django.core.cache import cache
from knox.auth import TokenAuthentication
from requests.auth import HTTPBasicAuth
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotAuthenticated, APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from api.filters import GPCBrickFilterBackend
from api.serializers.gpc_serializer import GPCSerializer
from BCM.helpers import test_helpers


class GPCListAPIView(APIView):
    """
    get: filtered list of gpc bricks by query parameters "brick" and "brick_code"
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    filter_backends = (GPCBrickFilterBackend,)  # dummy, just for help in swagger
    serializer_class = GPCSerializer  # dummy, just for help in swagger
    cache_key_template = 'bcm_external_api_gpc_response_{url_digest}'
    default_cache_timeout = settings.EXTERNAL_APIS['GPC']['DEFAULT_CACHE_TIMEOUT']
    is_test_environment = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_test_environment = test_helpers.is_test_environment()

    def get(self, request, *args, **kwargs):
        """
        Requests examples:

        brick substring:
            https://wsup.gs1.org/api/GPC?brick=tele
        brick code starts with "1000107":
            https://wsup.gs1.org/api/GPC/BricksByCode?brickCode=1000107
        """

        search_params = self.get_search_parameters(request)
        external_api_url = self.get_api_url(search_params)
        cached_result = self.get_cached_result(external_api_url)
        if cached_result:
            return Response(cached_result)

        result = self.get_data_from_gpc(external_api_url)
        self.set_cached_result(external_api_url, result)
        return Response(result)

    def get_data_from_gpc(self, external_api_url):
        """
        retrieve real data from gpc or fake data for tests
        """

        if self.is_test_environment:
            return [{'test_environment': True}]

        try:
            session = self.get_requests_session()
            response = session.get(external_api_url)
        except requests.RequestException as error:
            raise APIException(str(error), status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            if response.status_code != 200:
                raise APIException(
                    f'Wrong external api response status code: {response.status_code}'
                )

            result = response.json()
            if not isinstance(result, list):
                raise APIException('Wrong response from external api (not a list was returned)')

        return result

    def get_cached_result(self, external_api_url):
        """
        Return cached result if cache is enabled and results are available
        """

        if self.is_test_environment:
            return None

        if settings.EXTERNAL_APIS['GPC']['USE_CACHE']:
            url_digest = hashlib.sha1(external_api_url.encode()).hexdigest()
            cache_key = self.cache_key_template.format(url_digest=url_digest)
            return cache.get(cache_key)
        else:
            return None

    def set_cached_result(self, external_api_url, data):
        """
        Set cached result if cache is enabled
        """

        if self.is_test_environment:
            return None

        if settings.EXTERNAL_APIS['GPC']['USE_CACHE']:
            url_digest = hashlib.sha1(external_api_url.encode()).hexdigest()
            cache_key = self.cache_key_template.format(url_digest=url_digest)
            return cache.set(cache_key, data, self.default_cache_timeout)
        else:
            return None

    #@classmethod
    def get_api_url(self, search_params):
        language = self.request.user.profile.language
        if search_params.get('brick'):
            try:
                url = settings.BRICK[language]
            except:
                url = settings.BRICK['en']
            return url + search_params['brick']
        elif search_params.get('brick_code'):
            try:
                url = settings.BRICK_CODE[language]
            except:
                url = settings.BRICK_CODE['en']
            return url + search_params['brick_code']
        else:
            return None

    @classmethod
    def get_requests_session(cls):
        """
        Authorization for GPC API
        """

        api_user = settings.EXTERNAL_APIS['GPC']['USER']
        api_password = settings.EXTERNAL_APIS['GPC']['PASSWORD']
        if not any([api_user, api_password]):
            raise NotAuthenticated(
                'Please specify GPC API credentials in \'settings.EXTERNAL_APIS\''
            )

        session = requests.Session()
        session.auth = HTTPBasicAuth(api_user, api_password)
        return session

    def get_search_parameters(self, request):
        params = dict()
        params['brick'] = self.validate_param('brick', request.query_params.getlist('brick'))
        params['brick_code'] = self.validate_param(
            'brick_code', request.query_params.getlist('brick_code')
        )

        if not any(params.values()):
            raise ValidationError(
                f'There are no query parameters specified, '
                f'please specify \'brick\' or \'brick_code\''
            )
        if all(params.values()):
            raise ValidationError(
                f'\'brick\' and \'brick_code\' can\'t be specified at once,'
                f'please choose one'
            )
        return params

    @classmethod
    def validate_param(cls, param_name, source_values):
        values = list(set(source_values))
        if len(values) > 1:
            raise ValidationError(
                f'Multiple {param_name}s were specified, please specify only one'
            )
        elif len(values) == 1:
            return values[0]
        else:
            return None
