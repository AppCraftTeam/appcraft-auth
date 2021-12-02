from django.conf import settings
from django.contrib import admin

from appcraft_auth.models import JWTModel, BlackListedTokenModel

if settings.DEBUG:
    admin.site.register(JWTModel)
    admin.site.register(BlackListedTokenModel)
