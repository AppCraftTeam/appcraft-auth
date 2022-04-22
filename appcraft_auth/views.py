from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from social_core.exceptions import AuthTokenRevoked
from social_django.utils import load_backend, load_strategy

from appcraft_auth.base.api_views import BaseAuthAPIView, BaseSecretKeyProviderAPIView
from appcraft_auth.errors.error_codes import AuthRelatedErrorCodes
from appcraft_auth.errors.exceptions import CustomAPIException
from appcraft_auth.mappers import SocialDataMapper
from appcraft_auth.models import BlackListedTokenModel, AuthLetterModel, SmsModel
from appcraft_auth.serializers import RefreshTokenSerializer, EmailSerializer, AuthLetterSerializer, PhoneSerializer, \
    CheckSmsSerializer, VKTokenSerializer, FirebaseTokenSerializer, WechatCodeSerializer, CustomSocialLoginSerializer
from appcraft_auth.utils.request_utils import get_access_token


class GenerateEmailAuthCodeAPIView(BaseSecretKeyProviderAPIView):
    serializer_class = EmailSerializer
    method = AuthLetterModel.objects.create_by_email


class AuthenticateByEmailCodeAPIView(BaseAuthAPIView):
    serializer_class = AuthLetterSerializer
    user_creation_method = get_user_model().objects.get_or_create_by_auth_letter_instance


class SendSMSAPIView(BaseSecretKeyProviderAPIView):
    serializer_class = PhoneSerializer
    method = SmsModel.create


class AuthBySMSCodeAPIView(BaseAuthAPIView):
    serializer_class = CheckSmsSerializer
    user_creation_method = get_user_model().objects.get_or_create_by_sms_model
    social_mapper_method = SocialDataMapper().sms_aero


class FirebaseAuthAPIView(BaseAuthAPIView):
    serializer_class = FirebaseTokenSerializer
    user_creation_method = get_user_model().objects.get_or_create_by_firebase_token
    social_mapper_method = SocialDataMapper().firebase
    is_social_auth = True


class AppleAuthAPIView(BaseAuthAPIView):
    serializer_class = CustomSocialLoginSerializer
    user_creation_method = get_user_model().objects.get_or_create_by_apple_token
    social_mapper_method = SocialDataMapper().apple
    is_social_auth = True


class WeChatAuthAPIView(BaseAuthAPIView):
    serializer_class = WechatCodeSerializer
    user_creation_method = get_user_model().objects.get_or_create_by_wechat_open_id


class VkAuthAPIView(BaseAuthAPIView):
    @staticmethod
    def post(request, *args, **kwargs):
        serializer = VKTokenSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            backend = load_backend(load_strategy(request), 'vk-oauth2', 'social/login')
            try:
                return backend.do_auth(user=request.user, **serializer.validated_data)
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
