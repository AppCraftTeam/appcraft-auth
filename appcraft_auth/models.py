from uuid import uuid4

from django.conf import settings
from django.db import models

from appcraft_auth.abstract_models import BaseModel
from appcraft_auth.errors.error_codes import AuthRelatedErrorCodes
from appcraft_auth.errors.exceptions import CustomAPIException
from appcraft_auth.managers.auth_letter_model_manager import AuthLetterModelManager


class JWTModel(BaseModel):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    access_token = models.CharField(
        max_length=255
    )

    refresh_token = models.CharField(
        max_length=255
    )

    def __str__(self):
        return self.access_token

    class Meta:
        db_table = 'appcraft_auth__jw_tokens'


class BlackListedTokenModel(BaseModel):
    class Type(models.IntegerChoices):
        access = 0,
        refresh = 1,

    type = models.PositiveIntegerField(
        choices=Type.choices
    )

    token = models.CharField(
        max_length=255,
        unique=True
    )

    def __str__(self):
        return self.token

    class Meta:
        db_table = 'appcraft_auth__black_listed_tokens'


class AuthLetterModel(BaseModel):
    email = models.EmailField(
        verbose_name='Отправлено на'
    )

    code_max_length = settings.APPCRAFT_AUTH_EMAIL_SETTINGS.get('CODE_LENGTH')

    code = models.CharField(
        max_length=code_max_length,
        verbose_name='Сгенерированный код'
    )

    key = models.CharField(
        max_length=256,
        verbose_name='Защитный ключ',
        default=uuid4
    )

    trials = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Количество попыток'
    )

    last_trial_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Время последней попытки входа',
        auto_now=True
    )

    remote_ip = models.CharField(
        null=True,
        blank=True,
        max_length=30
    )

    session_key = models.CharField(
        null=True,
        blank=True,
        max_length=100
    )

    def check_trials_count(self):
        if self.trials > 2:
            self.delete()
            raise CustomAPIException(error=AuthRelatedErrorCodes.TOO_FREQUENT_ATTEMPTS)

    def increment_trials_count(self):
        self.trials += 1
        self.save()

    def check_code(self, code):
        if self.code != code:
            raise CustomAPIException(error=AuthRelatedErrorCodes.INVALID_CREDENTIALS)

    objects = AuthLetterModelManager()

    class Meta:
        db_table = 'appcraft_auth__auth_letters'
        verbose_name = 'Код авторизации по email'
        verbose_name_plural = 'Коды авторизации по email'
