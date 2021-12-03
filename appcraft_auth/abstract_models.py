from uuid import uuid4

from django.apps import apps
from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework_simplejwt.tokens import RefreshToken

from appcraft_auth.errors.error_codes import AuthRelatedErrorCodes
from appcraft_auth.errors.exceptions import CustomAPIException
from appcraft_auth.managers.auth_user_model_manager import AuthUserModelManager


class BaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        unique=True
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True


class AppCraftAuthUserModel(AbstractUser, BaseModel):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    username = None

    email = models.EmailField(
        unique=True
    )

    class Gender(models.IntegerChoices):
        MAN = 0
        WOMAN = 1
        OTHER = 2

    gender = models.PositiveIntegerField(
        choices=Gender.choices,
        null=True,
        blank=True
    )

    vk_id = models.IntegerField(
        null=True,
        blank=True
    )

    # AUTHENTICATION
    @classmethod
    def auth_firebase(cls, decoded_firebase_token: dict):
        auth_method = cls.get_auth_method_by_sign_in_provider(
            sign_in_provider=decoded_firebase_token.get('firebase').get('sign_in_provider'))

        user, created = auth_method(decoded_firebase_token=decoded_firebase_token)
        return user.get_auth_data(created=created)

    @classmethod
    def get_auth_method_by_sign_in_provider(cls, sign_in_provider: str):
        methods = {
            'google.com': cls.objects.update_or_create_by_firebase_google_auth,
            'apple.com': cls.objects.update_or_create_by_firebase_apple_auth,
            # 'facebook.com' : self.update_or_create_by_firebase_facebook_auth,
        }

        auth_method = methods.get(sign_in_provider)
        if not auth_method:
            raise CustomAPIException(error=AuthRelatedErrorCodes.UNAUTHORIZED_AUTH_PROVIDER)
        return auth_method

    def get_auth_data(self, created=bool) -> dict:
        data = {
            'user_id': self.id,
            'is_active': self.is_active,
            'first_login': created
        }
        data.update(self.get_tokens())
        return data

    def get_tokens(self) -> dict:
        if not self.is_active:
            raise AuthenticationFailed
        data = {}

        tokens = RefreshToken.for_user(user=self)
        data['access_token'] = str(tokens.access_token)
        data['refresh_token'] = str(tokens)

        jwt_model = apps.get_model('appcraft_auth.JWTModel')
        jwt_model.objects.update_or_create(
            user=self,
            defaults=data
        )

        return data

    def __str__(self):
        return self.email

    objects = AuthUserModelManager()

    class Meta:
        abstract = True
