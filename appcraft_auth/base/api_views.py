from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from appcraft_auth.utils.datetime_utils import timestamp_to_datetime
from appcraft_auth.utils.other import chained_get, nonefy, has_latin


class SocialEntity:
    def __init__(
            self,
            first_name=None,
            last_name=None,
            middle_name=None,
            username=None,
            firebase_id=None,
            social_id=None,
            social_type=None,
            access_token=None,
            access_token_expiration=None,
            phone=None,
            email=None
    ) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        self.username = username
        self.phone = phone
        self.email = email
        self.firebase_id = firebase_id
        self.social_id = social_id
        self.social_type = social_type
        self.access_token = access_token
        self.access_token_expiration = access_token_expiration

    def get_kwargs(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'middle_name': self.middle_name,
            'username': self.username,
            'phone': self.phone,
            'email': self.email,
            'firebase_id': self.firebase_id,
            'social_id': self.social_id,
            'type': self.social_type,
            'access_token': self.access_token,
            'access_token_expiration': self.access_token_expiration
        }


class SocialDataMapper:
    @staticmethod
    def firebase(decoded_firebase_token):
        entity = SocialEntity()

        entity.firebase_id = decoded_firebase_token.get('uid', None)

        entity.social_type = chained_get(decoded_firebase_token, 'firebase', 'sign_in_provider', default='firebase')
        entity.access_token_expiration = timestamp_to_datetime(
            decoded_firebase_token.get('exp', None), milliseconds=False
        ) if decoded_firebase_token.get('exp') is not None else None

        entity.phone = decoded_firebase_token.get('phone_number')
        entity.email = decoded_firebase_token.get('email')
        entity.username = decoded_firebase_token.get('name')
        identities = chained_get(decoded_firebase_token, 'firebase', 'identities')
        if identities:
            # TODO проверить Apple и Facebook
            entity.social_id = chained_get(identities, entity.social_type, 0)
            entity.email = chained_get(identities, 'email', 0)
            entity.first_name = chained_get(identities, 'first_name', 0)
            entity.last_name = chained_get(identities, 'last_name', 0)

        # Проверка ФИО на латиницу, если используется, то не подставляем данные
        entity.first_name = nonefy(entity.first_name, has_latin(entity.first_name))
        entity.last_name = nonefy(entity.last_name, has_latin(entity.last_name))
        entity.middle_name = nonefy(entity.middle_name, has_latin(entity.middle_name))

        return entity


class BaseAuthAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = None
    method = None

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user, created = self.method(**serializer.validated_data)
            return Response(user.get_auth_data(created=created))

    # def post(self, request, *args, **kwargs):
    #     serializer = self.serializer_class(data=request.data)
    #     if serializer.is_valid(raise_exception=True):
    #         if request.user.is_authenticated:
    #             entity = SocialDataMapper.firebase(**serializer.validated_data)
    #             print(entity.get_kwargs())
    #             return Response(status=status.HTTP_201_CREATED)
    #         else:
    #             user, created = self.method(**serializer.validated_data)
    #             return Response(user.get_auth_data(created=created))


class BaseSecretKeyProviderAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = None
    method = None

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = {'request': request}
            data.update(serializer.validated_data)
            instance = self.method(**data)
            return Response({'key': str(instance.key)})
