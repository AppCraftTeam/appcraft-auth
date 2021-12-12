from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from appcraft_auth.mappers import SocialDataMapper
from appcraft_auth.models import SocialModel


def do_auth(backend, user, *args, **kwargs):
    kwargs.pop('storage')
    kwargs.pop('strategy')
    # todo
    #  при попытке return user, created случается краш
    #  при попытке return user.get_auth_data(created=created) во вьюхе возвращается None почему-то
    #  а вот так все работает. Странно почему верхние 2 варианта не работают, особенно второй
    #  как будет время попытаться разобраться
    if backend.name == 'vk-oauth2':
        if user.is_anonymous:
            user, created = get_user_model().objects.get_or_create_by_vk_token(kwargs)
            social_data = SocialDataMapper().vk(kwargs).get_kwargs(user=user)
            SocialModel.objects.update_or_create(
                social_id=social_data.get('social_id'),
                defaults=social_data
            )
            return Response(user.get_auth_data(created=created, social_decoded_token=kwargs))
        else:
            social_data = SocialDataMapper().vk(kwargs).get_kwargs(user=user)
            SocialModel.objects.update_or_create(
                social_id=social_data.get('social_id'),
                defaults=social_data
            )
            return Response(user.get_auth_data(social_decoded_token=kwargs))
    else:
        raise NotImplementedError('Unknown backend for python-social-auth')
