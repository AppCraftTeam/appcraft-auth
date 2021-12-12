from rest_framework.exceptions import NotFound

from appcraft_auth.models import SocialModel


class SocialEntity:
    def __init__(
            self,
            first_name=None,
            last_name=None,
            username=None,
            firebase_id=None,
            social_id=None,
            provider=None,
            access_token=None,
            access_token_expiration=None,
            phone=None,
            email=None
    ) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.phone = phone
        self.email = email
        self.firebase_id = firebase_id
        self.social_id = social_id
        self.provider = provider
        self.access_token = access_token
        self.access_token_expiration = access_token_expiration

    def get_kwargs(self, user=None):
        return {
            'user': user,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'phone': self.phone,
            'email': self.email,
            'social_id': self.social_id,
            'provider': self.get_auth_provider_choice()
        }

    def get_auth_provider_choice(self):
        # todo facebook и instagram нужно проверить
        providers = {
            'google.com': SocialModel.Providers.GOOGLE.value,
            'apple.com': SocialModel.Providers.APPLE.value,
            'phone': SocialModel.Providers.PHONE.value,
            'facebook.com': SocialModel.Providers.FACEBOOK.value,
            'instagram.com': SocialModel.Providers.INSTAGRAM.value,
            'vk.com': SocialModel.Providers.VK.value,
            'wechat': SocialModel.Providers.WECHAT.value
        }
        return providers.get(self.provider)
