from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from appcraft_auth.abstract_managers import AppCraftAuthUserModelManager


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
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'username'

    # сделано специально так
    # есть случат, когда через авторизацию по соц-сетям мы не получаем имейл,
    # поэтому оставляю username, пускай записывается значение по умолчанию
    username = models.CharField(
        max_length=50,
        unique=True,
        default=uuid4
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=16,
        null=True,
        blank=True,
        unique=True
    )

    apple_user_id = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    vk_id = models.IntegerField(
        null=True,
        blank=True
    )

    wechat_open_id = models.CharField(
        max_length=100,
        null=True,
        blank=True
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

    # AUTHENTICATION
    def get_auth_data(self, created: bool = False) -> dict:
        data = {
            'id': self.id,
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
        self.create_jwt(**data)
        return data

    def get_access_token(self, refresh_token: str) -> dict:
        refresh = RefreshToken(refresh_token)
        data = {'access_token': str(refresh.access_token)}
        self.blacklist_access_tokens_by_refresh_token(refresh_token=refresh_token)
        self.create_jwt(refresh_token=refresh_token, **data)
        return data

    def create_jwt(self, access_token: str, refresh_token: str):
        from appcraft_auth.models import JWTModel
        JWTModel.objects.create(user=self, refresh_token=refresh_token, access_token=access_token)

    @staticmethod
    def blacklist_access_tokens_by_refresh_token(refresh_token: str):
        from appcraft_auth.models import JWTModel
        active_access_tokens_by_refresh_tokens = JWTModel.objects.filter(refresh_token=refresh_token)
        blacklist = []
        from appcraft_auth.models import BlackListedTokenModel
        for instance in active_access_tokens_by_refresh_tokens:
            blacklist.append(BlackListedTokenModel(access_token=instance.access_token))

        BlackListedTokenModel.objects.bulk_create(blacklist)

    def __str__(self):
        return self.email

    objects = AppCraftAuthUserModelManager()

    class Meta:
        abstract = True
