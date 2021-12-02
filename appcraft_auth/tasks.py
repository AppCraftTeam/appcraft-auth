from celery import shared_task
from django.conf import settings
from django.utils import timezone

from appcraft_auth.models import JWTModel, BlackListedTokenModel


@shared_task
def clear_outdated_tokens():
    out_date = settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME')
    JWTModel.objects.filter(
        created_at__lt=timezone.now() - out_date
    ).delete()

    BlackListedTokenModel.objects.filter(
        created_at__lt=timezone.now() - out_date
    ).delete()
