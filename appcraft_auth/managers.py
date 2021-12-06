from datetime import timedelta

import jwt
from django.conf import settings
from django.contrib.auth.models import UserManager
from django.core.mail import EmailMessage
from django.db.models import Manager
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils import timezone

from appcraft_auth.errors.error_codes import AuthRelatedErrorCodes
from appcraft_auth.errors.exceptions import CustomAPIException
from appcraft_auth.utils.int_utils import generate_random_digits


class AuthLetterModelManager(Manager):
    def get_ip_and_session_key(self, email, request):
        remote_ip = request.headers.get('X-Real-Ip', None)

        session_key = request.session.session_key
        if not session_key:
            request.session.save()

        if remote_ip:
            queryset = self.filter(remote_ip=remote_ip, session_key=session_key)
            if queryset.exclude(email=email).filter(
                    created_at__range=(timezone.now() - timedelta(hours=1), timezone.now())).exists():
                raise CustomAPIException(error=AuthRelatedErrorCodes.TOO_FREQUENT_ATTEMPTS)

        return remote_ip, session_key

    def create_by_email(self, email, request):
        self.check_frequency(email=email)
        remote_ip, session_key = self.get_ip_and_session_key(email=email, request=request)

        instance = self.create(
            email=email,
            code=generate_random_digits(length=self.code_length),
            remote_ip=remote_ip,
            session_key=session_key
        )

        self.send_email(email=instance.email, code=instance.code)
        return instance

    def get_email_body(self, code: int):
        template_name = self.template_name
        body = code
        if template_name:
            try:
                body = render_to_string(self.template_name, context={'code': code})
            except TemplateDoesNotExist:
                pass
        return body

    def send_email(self, email, code):
        email = EmailMessage(
            subject=self.auth_letter_subject,
            body=self.get_email_body(code=code),
            from_email=settings.EMAIL_HOST_USER,
            to=[email]
        )

        try:
            email.send()
        except Exception as e:
            raise CustomAPIException(error=AuthRelatedErrorCodes.FAILED_TO_SEND_EMAIL)

    def check_frequency(self, email):
        now = timezone.now()
        queryset = self.filter(email=email)
        queryset.filter(created_at__lt=self.max_trials_period).delete()

        if queryset.filter(email=email, created_at__range=(self.repeat_interval, now)).exists() or \
                queryset.filter(created_at__range=(self.max_trials_period, now)).count() > self.max_trials_per_period:
            raise CustomAPIException(error=AuthRelatedErrorCodes.TOO_FREQUENT_ATTEMPTS)

    @property
    def email_auth_settings(self):
        try:
            return settings.APPCRAFT_AUTH_EMAIL_SETTINGS
        except AttributeError:
            raise ValueError('Specify APPCRAFT_AUTH_EMAIL_SETTINGS in settings.py')

    @property
    def code_length(self):
        code_length = self.email_auth_settings.get('CODE_LENGTH')
        return code_length if code_length else 4

    @property
    def template_name(self):
        return self.email_auth_settings.get('TEMPLATE_NAME')

    @property
    def auth_letter_subject(self):
        auth_letter_subject = self.email_auth_settings.get('AUTH_LETTER_SUBJECT')
        if not auth_letter_subject:
            raise ValueError('Specify auth letter subject in settings.py in APPCRAFT_AUTH_EMAIL_SETTINGS')
        return auth_letter_subject

    @property
    def repeat_interval(self):
        interval = self.email_auth_settings.get('REPEAT_INTERVAL')
        if interval:
            return timezone.now() - interval
        else:
            return timezone.now() - timedelta(minutes=1)

    @property
    def max_trials_period(self):
        max_trials_period = self.email_auth_settings.get('MAX_TRIALS_PERIOD')
        if max_trials_period:
            return timezone.now() - max_trials_period
        else:
            return timezone.now() - timedelta(days=1)

    @property
    def max_trials_per_period(self):
        max_trials_per_period = self.email_auth_settings.get('MAX_TRIALS_PER_PERIOD')
        return max_trials_per_period if max_trials_per_period else 4


class AuthUserModelManager(UserManager):
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

    def get_or_create_by_phone(self, sms_model_instance):
        instance, created = self.get_or_create(phone=sms_model_instance.phone)
        sms_model_instance.delete()
        return instance, created
