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
    class Meta:
        model = SmsModel
        fields = ['phone']


class CheckSmsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmsModel
        fields = ['code', 'key']
