from appcraft_auth.entities import SocialEntity
from appcraft_auth.utils.datetime_utils import timestamp_to_datetime
from appcraft_auth.utils.other import chained_get


class SocialDataMapper:
    def firebase(self, decoded_firebase_token):
        entity = SocialEntity()

        entity.provider = chained_get(decoded_firebase_token, 'firebase', 'sign_in_provider', default='firebase')
        entity.access_token_expiration = timestamp_to_datetime(
            decoded_firebase_token.get('exp', None), milliseconds=False
        ) if decoded_firebase_token.get('exp') is not None else None

        entity.phone = decoded_firebase_token.get('phone_number')
        entity.email = decoded_firebase_token.get('email')
        entity.username = decoded_firebase_token.get('name')
        identities = chained_get(decoded_firebase_token, 'firebase', 'identities')
        if identities:
            entity.social_id = chained_get(identities, entity.provider, 0)
            entity.email = chained_get(identities, 'email', 0)
            entity.first_name = chained_get(identities, 'first_name', 0)
            entity.last_name = chained_get(identities, 'last_name', 0)
        else:
            entity.social_id = decoded_firebase_token.get('uid', None)

        # Проверка ФИО на латиницу, если используется, то не подставляем данные
        # entity.first_name = nonefy(entity.first_name, has_latin(entity.first_name))
        # entity.last_name = nonefy(entity.last_name, has_latin(entity.last_name))
        # entity.middle_name = nonefy(entity.middle_name, has_latin(entity.middle_name))

        return entity

    def vk(self, vk_decoded_token):
        entity = SocialEntity()
        entity.social_id = chained_get(vk_decoded_token, 'response', 'id')
        entity.provider = 'vk.com'
        entity.phone = chained_get(vk_decoded_token, 'details', 'phone')
        entity.email = chained_get(vk_decoded_token, 'details', 'email')
        entity.first_name = chained_get(vk_decoded_token, 'response', 'first_name')
        entity.last_name = chained_get(vk_decoded_token, 'response', 'last_name')
        entity.username = chained_get(vk_decoded_token, 'response', 'username')

        # Проверка ФИО на латиницу, если используется, то не подставляем данные
        # entity.first_name = None if has_latin(entity.first_name) else entity.first_name
        # entity.last_name = None if has_latin(entity.last_name) else entity.last_name
        # entity.middle_name = None if has_latin(entity.middle_name) else entity.middle_name
        return entity

    def sms_aero(self, sms_model_instance):
        entity = SocialEntity()

        # SMS Aero заменяет авторизацию по телефону через Firebase
        # Поэтому social_id из Firebase и SMS Aero будет номер телефона
        entity.social_id = sms_model_instance.phone
        entity.provider = 'phone'  # Ставим тип как из Firebase
        entity.phone = sms_model_instance.phone

        return entity
