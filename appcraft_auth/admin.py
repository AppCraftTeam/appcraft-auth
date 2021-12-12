from django.conf import settings
from django.contrib import admin

from appcraft_auth.models import JWTModel, BlackListedTokenModel, AuthLetterModel, SmsModel, SocialModel

if settings.DEBUG:
    admin.site.register(JWTModel)
    admin.site.register(BlackListedTokenModel)


    @admin.register(AuthLetterModel)
    class AuthLetterModelAdmin(admin.ModelAdmin):
        list_display = ['id', 'email', 'code', 'key', 'trials', 'created_at', 'last_trial_at']


    @admin.register(SmsModel)
    class SmsModelAdmin(admin.ModelAdmin):
        list_display = ['id', 'status', 'phone', 'code', 'key']


    @admin.register(SocialModel)
    class SocialModelAdmin(admin.ModelAdmin):
        list_display = ['id', 'user', 'social_id', 'provider']
