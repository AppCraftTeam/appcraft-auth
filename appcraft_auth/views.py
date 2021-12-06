from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from social_core.exceptions import AuthTokenRevoked
from social_django.utils import load_backend, load_strategy

from appcraft_auth.base.api_views import BaseAuthAPIView
from appcraft_auth.errors.error_codes import AuthRelatedErrorCodes
from appcraft_auth.errors.exceptions import CustomAPIException
from appcraft_auth.models import BlackListedTokenModel, AuthLetterModel, SmsModel
from appcraft_auth.serializers import RefreshTokenSerializer, EmailSerializer, AuthLetterSerializer, PhoneSerializer, \
    CheckSmsSerializer, VKTokenSerializer
from appcraft_auth.utils.request_utils import get_access_token


class TestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # data = {}
        # tokens = RefreshToken.for_user(user=get_user_model().objects.first())
        # data['access_token'] = str(tokens.access_token)
        # data['refresh_token'] = str(tokens)
        return Response('ok')


class GenerateEmailAuthCodeAPIView(BaseAuthAPIView):
    permission_classes = [AllowAny]
    serializer_class = EmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            instance = AuthLetterModel.objects.create_by_email(
                email=serializer.validated_data.get('email'),
                request=request
            )
            return Response({'key': str(instance.key)})


class AuthenticateByEmailCodeAPIView(BaseAuthAPIView):
    serializer_class = AuthLetterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user, created = get_user_model().objects.get_or_create_by_auth_letter_instance(**serializer.validated_data)
            return Response(user.get_auth_data(created=created))


class SendSMSAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PhoneSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            sms_model = SmsModel.create(**serializer.validated_data)
            sms_model.send_sms()
            return JsonResponse({'key': sms_model.key})


class AuthBySMSCodeAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = CheckSmsSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            sms_model = SmsModel.check_sms(**serializer.validated_data)
            user, created = get_user_model().objects.get_or_create_by_phone(sms_model_instance=sms_model)
            return Response(user.get_auth_data(created=created))


class VkAuthAPIView(BaseAuthAPIView):
    @staticmethod
    def post(request, *args, **kwargs):
        serializer = VKTokenSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            backend = load_backend(load_strategy(request), 'vk-oauth2', 'social/login')
            try:
                return backend.do_auth(**serializer.validated_data)
            except AuthTokenRevoked:
                raise CustomAPIException(error=AuthRelatedErrorCodes.INVALID_VK_ACCESS_TOKEN)


class LogOutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def delete(request, *args, **kwargs):
        access_token = get_access_token(request=request)
        BlackListedTokenModel.objects.create(access_token=access_token)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RefreshTokenAPIView(APIView):
    serializer_class = RefreshTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = get_user_model().objects.get_by_refresh_token(**serializer.validated_data)
            return Response(user.get_access_token(**serializer.validated_data))
