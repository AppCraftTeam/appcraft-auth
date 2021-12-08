import string

import requests
from django.conf import settings
from firebase_admin import auth as firebase_auth
from firebase_admin.auth import InvalidIdTokenError
from rest_framework import serializers

from appcraft_auth.errors.error_codes import AuthRelatedErrorCodes
from appcraft_auth.errors.exceptions import CustomAPIException
from appcraft_auth.models import AuthLetterModel, SmsModel


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class AuthLetterSerializer(serializers.ModelSerializer):
    key = serializers.UUIDField(required=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        try:
            auth_letter_instance = AuthLetterModel.objects.get(key=attrs.get('key'))
            auth_letter_instance.check_trials_count()
            auth_letter_instance.increment_trials_count()
            auth_letter_instance.check_code(code=attrs.get('code'))
            return {'auth_letter_instance': auth_letter_instance}
        except AuthLetterModel.objects.DoesNotExist:
            raise CustomAPIException(error=AuthRelatedErrorCodes.INVALID_CREDENTIALS)

    class Meta:
        model = AuthLetterModel
        fields = ['code', 'key']


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class PhoneSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        for item in attrs.get('phone'):
            if item not in string.digits:
                raise CustomAPIException(error=AuthRelatedErrorCodes.ONLY_INTEGERS_ARE_ALLOWED_IN_PHONE_NUMBER)
        return {'phone': f'''+{attrs.get('phone')}'''}

    class Meta:
        model = SmsModel
        fields = ['phone']


class CheckSmsSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        sms_model = SmsModel.check_sms(**attrs)
        return {'sms_model_instance': sms_model}

    class Meta:
        model = SmsModel
        fields = ['code', 'key']


class VKTokenSerializer(serializers.Serializer):
    vk_access_token = serializers.CharField()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        return {'access_token': attrs.get('vk_access_token')}


class FirebaseTokenSerializer(serializers.Serializer):
    invalid_firebase_token = CustomAPIException(error=AuthRelatedErrorCodes.INVALID_FIREBASE_TOKEN)
    firebase_token = serializers.CharField()

    def validate_firebase_token(self, value):
        try:
            decoded_token = firebase_auth.verify_id_token(value)
            if decoded_token is None:
                raise self.invalid_firebase_token
        except ValueError as e:
            print(e)
            raise self.invalid_firebase_token
        except InvalidIdTokenError as e:
            print(e)
            raise self.invalid_firebase_token

        return decoded_token

    def validate(self, attrs):
        attrs = super().validate(attrs)
        return {
            'decoded_firebase_token': attrs.get('firebase_token')
        }


class WechatCodeSerializer(serializers.Serializer):
    wechat_code = serializers.CharField()

    def validate(self, attrs):
        url = 'https://api.weixin.qq.com/sns/oauth2/access_token'

        query_params = {
            'appid': settings.WECHAT_APP_ID,
            'secret': settings.WECHAT_APP_SECRET,
            'code': attrs['wechat_code'],
            'grant_type': 'authorization_code'
        }

        response = requests.get(
            url=url,
            params=query_params).json()

        if 'errcode' in response:
            raise CustomAPIException(error=AuthRelatedErrorCodes.INVALID_WECHAT_CODE)

        return {'wechat_open_id': response.get('openid')}
