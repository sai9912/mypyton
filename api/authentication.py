from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication, SessionAuthentication
from rest_framework import exceptions
from .models import ApiKeys
from django.utils.translation import ugettext as _


# TODO: this code is not used yet
class ApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        key = request.META.get('X-API-Key')
        if not key:
            return None

        try:
            api_key = ApiKeys.objects.get(key=key)
            user = AnonymousUser()
        except ApiKeys.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('The API Key is not valid'))

        return user, None


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening
