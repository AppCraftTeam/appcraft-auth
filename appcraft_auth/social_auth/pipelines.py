from django.contrib.auth import get_user_model
from rest_framework.response import Response


def do_auth(backend, *args, **kwargs):
    if backend.name == 'vk-oauth2':
        user, created = get_user_model().objects.get_or_create_by_vk(kwargs)
        # todo
        #  при попытке return user, created случается краш
        #  при попытке return user.get_auth_data(created=created) во вьюхе возвращается None почему-то
        #  а вот так все работает. Странно почему верхние 2 варианта не работают, особенно второй
        #  как юудет время попытаться разобраться
        return Response(user.get_auth_data(created=created))
    else:
        raise NotImplementedError('Unknown backend for python-social-auth')
