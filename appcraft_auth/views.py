from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from appcraft_auth.base.api_views import BaseAuthAPIView
from appcraft_auth.models import BlackListedTokenModel, AuthLetterModel
from appcraft_auth.serializers import CustomTokenRefreshSerializer, EmailSerializer, AuthLetterSerializer
from appcraft_auth.utils.request_utils import get_access_token


class TestAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = {}
        tokens = RefreshToken.for_user(user=get_user_model().objects.get(id=1))
        data['access_token'] = str(tokens.access_token)
        data['refresh_token'] = str(tokens)
        return Response(data)


class GenerateAuthCodeAPIView(BaseAuthAPIView):
    serializer_class = EmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            instance = AuthLetterModel.objects.create_by_email(
                email=serializer.validated_data.get('email'),
                request=request
            )
            return Response({'key': str(instance.key)})


class AuthenticateByCodeAPIView(BaseAuthAPIView):
    serializer_class = AuthLetterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            auth_letter_instance = AuthLetterModel.objects.check_auth_letter(**serializer.validated_data)
            return Response(data=get_user_model().objects.get_or_create_by_auth_letter_instance(
                auth_letter_instance=auth_letter_instance))


class LogOutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def delete(request, *args, **kwargs):
        access_token = get_access_token(request=request)
        BlackListedTokenModel.objects.create(
            type=BlackListedTokenModel.Type.access,
            token=access_token
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class RefreshTokenAPIView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
