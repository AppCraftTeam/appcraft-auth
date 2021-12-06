from django.http import JsonResponse

from appcraft_auth.errors.error_codes import AuthRelatedErrorCodes
from appcraft_auth.models import BlackListedTokenModel
from appcraft_auth.utils.request_utils import get_access_token


class BlacklistedTokensMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        access_token = get_access_token(request=request)
        if access_token and BlackListedTokenModel.objects.filter(access_token=access_token).exists():
            return JsonResponse(
                data={'detail': 'access token is in black list'},
                status=AuthRelatedErrorCodes.ACCESS_TOKEN_IS_IN_BLACK_LIST.value
            )

        return self.get_response(request)
