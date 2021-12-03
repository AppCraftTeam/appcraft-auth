from django.contrib.auth.models import UserManager
from django.db import transaction


class AuthUserModelManager(UserManager):
    with transaction.atomic():
        def get_or_create_by_auth_letter_instance(self, auth_letter_instance) -> dict:
            email = auth_letter_instance.email.lower()
            instance, created = self.get_or_create(email=email)
            auth_letter_instance.delete()
            return instance.get_auth_data(created=created)
