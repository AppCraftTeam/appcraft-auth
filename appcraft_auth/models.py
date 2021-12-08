import json
from random import randint
from uuid import uuid4

import requests
from django.conf import settings
from django.db import models
from django.utils import timezone

from appcraft_auth.abstract_models import BaseModel
from appcraft_auth.errors.error_codes import AuthRelatedErrorCodes
from appcraft_auth.errors.exceptions import CustomAPIException
from appcraft_auth.managers import AuthLetterModelManager


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
    access_token = models.CharField(
        max_length=255
    )

    def __str__(self):
        return self.access_token

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


class SmsModel(BaseModel):
    class Status(models.IntegerChoices):
        SENT = 0
        ACTIVATED = 1
        CANCELED = 2
        EXPIRED = 3

    TOKEN_LIFETIME_MINUTE = 3

    phone = models.CharField(max_length=15)
    code = models.CharField(max_length=8)
    key = models.CharField(max_length=255)
    status = models.IntegerField(
        choices=Status.choices,
        default=Status.SENT
    )

    @classmethod
    def create(cls, phone, request=None):
        code = cls.generate_code(6)
        cls.objects.filter(phone=phone, status=cls.Status.SENT).update(status=cls.Status.CANCELED)
        instance = cls.objects.create(phone=phone, code=code, key=uuid4())
        instance.send_sms()
        return instance

    @classmethod
    def generate_code(cls, chars_long: int = 6):
        code = ''
        for i in range(chars_long):
            code += str(randint(0, 9))
        return code

    @classmethod
    def check_sms(cls, code, key):
        sms_model = cls.objects.filter(code=code, key=key, status=cls.Status.SENT).last()

        if sms_model is None:
            raise CustomAPIException(error=AuthRelatedErrorCodes.SMS_INVALID_CODE_OR_KEY)

        if (timezone.now() - sms_model.created_at).seconds >= cls.TOKEN_LIFETIME_MINUTE * 60:
            sms_model.status = cls.Status.EXPIRED
            sms_model.save()
            raise CustomAPIException(error=AuthRelatedErrorCodes.SMS_LIFETIME_EXPIRED)

        sms_model.status = cls.Status.ACTIVATED
        sms_model.save()

        return sms_model

    def send_sms(self):
        response = requests.get(
            'https://%s:%s@gate.smsaero.ru/v2/sms/send?number=%s&text=%s&sign=SMS Aero&channel=INFO' % (
                settings.SMS_AERO_EMAIL, settings.SMS_AERO_API_KEY, self.phone, self.code))
        if not response.status_code == 200:
            raise CustomAPIException(
                error=AuthRelatedErrorCodes.FAILED_SEND_SMS,
                text=json.loads(response.content).get('message')
            )

    def __str__(self):
        return 'Телефон: %s, СМС: %s' % (self.phone, self.code)

    class Meta:
        db_table = 'appcraft_auth_sms_models'
        verbose_name = 'SMS'
        verbose_name_plural = 'SMS'
