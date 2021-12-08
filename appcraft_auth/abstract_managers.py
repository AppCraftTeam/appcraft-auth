import jwt
from django.conf import settings
from django.contrib.auth.models import UserManager
from rest_framework.exceptions import NotFound

from appcraft_auth.errors.error_codes import AuthRelatedErrorCodes
from appcraft_auth.errors.exceptions import CustomAPIException
from appcraft_auth.social_auth.utils import map_vk_gender


class AppCraftAuthUserModelManager(UserManager):
    def get_by_refresh_token(self, refresh_token: str):
        try:
            user_id = jwt.decode(
                refresh_token,
                key=settings.SECRET_KEY,
                algorithms=['HS256']).get('user_id')
            try:
                return self.get(id=user_id)
            except self.model.DoesNotExist:
                raise CustomAPIException(error=AuthRelatedErrorCodes.INVALID_REFRESH_TOKEN)
        except (jwt.exceptions.ExpiredSignatureError,
                jwt.exceptions.InvalidSignatureError,
                jwt.exceptions.DecodeError):
            raise CustomAPIException(error=AuthRelatedErrorCodes.INVALID_REFRESH_TOKEN)

    def get_or_create_by_auth_letter_instance(self, auth_letter_instance):
        email = auth_letter_instance.email.lower()
        instance, created = self.get_or_create(email=email)
        auth_letter_instance.delete()
        return instance, created

    def get_or_create_by_sms_model(self, sms_model_instance):
        instance, created = self.get_or_create(phone=sms_model_instance.phone)
        sms_model_instance.delete()
        return instance, created

    def get_or_create_by_vk_token(self, social_data: dict):
        # todo try to get also phone number
        vk_id = social_data['response']['id']
        email = social_data['details']['email']

        defaults = {
            'gender': map_vk_gender(social_data['response'].get('sex'), self.model.Gender),
            'first_name': social_data.get('response').get('first_name'),
            'last_name': social_data.get('response').get('last_name')
        }

        email_exists = bool(email)
        if email_exists:
            defaults['vk_id'] = vk_id
            return self.update_or_create(email=email, defaults=defaults)
        else:
            defaults['email'] = email
            return self.update_or_create(vk_id=vk_id, defaults=defaults)

    def get_or_create_by_firebase_token(self, decoded_firebase_token: dict):
        sign_in_provider = decoded_firebase_token.get('firebase').get('sign_in_provider')

        if sign_in_provider not in settings.FIREBASE_AUTHORIZED_SIGN_IN_PROVIDERS:
            raise CustomAPIException(error=AuthRelatedErrorCodes.UNAUTHORIZED_AUTH_PROVIDER)

        methods = {
            'phone': self.get_or_create_by_firebase_phone_auth,
            'google.com': self.update_or_create_by_firebase_google_auth,
            'apple.com': self.update_or_create_by_firebase_apple_auth,
            # 'facebook.com' : self.update_or_create_by_firebase_facebook_auth,
        }
        method = methods.get(sign_in_provider)
        return method(decoded_firebase_token=decoded_firebase_token)

    def update_or_create_by_firebase_apple_auth(self, decoded_firebase_token: dict):
        apple_user_id = decoded_firebase_token.get('user_id')
        email = decoded_firebase_token.get('email')
        if email:
            return self.update_or_create(email=email, defaults={'apple_user_id': apple_user_id})
        else:
            return self.get_or_create(apple_user_id=apple_user_id)

    def update_or_create_by_firebase_google_auth(self, decoded_firebase_token: dict):
        email = decoded_firebase_token.get('firebase').get('identities').get('email')[0]
        defaults = {
            'first_name': (decoded_firebase_token.get('name').split(' '))[0],
            'last_name': (decoded_firebase_token.get('name').split(' '))[1]
        }

        return self.update_or_create(email=email, defaults=defaults)

    def get_or_create_by_firebase_phone_auth(self, decoded_firebase_token: dict):
        return self.get_or_create(phone=decoded_firebase_token.get('phone_number'))

    def update_or_create_by_firebase_facebook_auth(self, decoded_firebase_token: dict):
        pass

    def get_or_create_by_wechat_open_id(self, wechat_open_id):
        return self.get_or_create(wechat_open_id=wechat_open_id)
