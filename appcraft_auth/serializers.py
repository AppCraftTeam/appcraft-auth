import jwt
from django.conf import settings
from jwt import InvalidSignatureError
from rest_framework import serializers
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from appcraft_auth.errors.error_codes import AuthRelatedErrorCodes
from appcraft_auth.errors.exceptions import CustomAPIException
from appcraft_auth.models import BlackListedTokenModel


class CustomTokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    access_token = serializers.CharField()

    @staticmethod
    def blacklist_access_token(access_token: str):
        BlackListedTokenModel.objects.get_or_create(
            type=BlackListedTokenModel.Type.access,
            token=access_token
        )

    def validate_access_token(self, value):
        try:
            jwt.decode(value, key=settings.SECRET_KEY, algorithms=['HS256'])
            self.blacklist_access_token(access_token=value)
            return value
        except InvalidSignatureError:
            raise CustomAPIException(error=AuthRelatedErrorCodes.INVALID_ACCESS_TOKEN)

    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh_token'])

        data = {'access_token': str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            data['refresh_token'] = str(refresh)

        return data
