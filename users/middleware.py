from django.urls import reverse
from knox.models import AuthToken
from knox.settings import CONSTANTS
from django.utils import timezone


class AuthTokenGenerateMiddleware:
    # add your view name here if you need to have a user token,
    # it will be placed to user session and could be rendered with templates
    allowed_view_names = [
        # 'profile_js',
        # 'admin_profile_js',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def is_token_required(self, request):
        return (
            request.user.is_authenticated and
            request.resolver_match.url_name in self.allowed_view_names
        )

    def process_view(self, request, view_func, views_args, view_kwargs):

        if not self.is_token_required(request):
            return

        token = request.session.get('auth_token')

        if token:
            auth_tokens = AuthToken.objects.filter(token_key=token[:CONSTANTS.TOKEN_KEY_LENGTH])
            # check all available tokens
            for auth_token in auth_tokens:
                if auth_token.expires is not None:
                    if auth_token.expires < timezone.now():
                        continue
                return  # we have a valid token, no further actions required

        # no tokens were found, generate one and save to session
        token = AuthToken.objects.create(request.user)
        request.session['auth_token'] = token
