from django.conf import settings
from django.db import models

from appcraft_auth.abstract_models import BaseModel


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
