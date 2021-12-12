from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from appcraft_auth.models import SocialModel


class BaseAuthAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = None
    user_creation_method = None
    social_mapper_method = None
    is_social_auth = False

    def social_auth(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if request.user.is_authenticated:
                social_data = self.social_mapper_method(**serializer.validated_data).get_kwargs(user=request.user)
                SocialModel.objects.update_or_create(
                    social_id=social_data.get('social_id'),
                    defaults=social_data
                )
                return Response(status=status.HTTP_201_CREATED)
            else:
                user, created = self.user_creation_method(**serializer.validated_data)
                social_data = self.social_mapper_method(**serializer.validated_data).get_kwargs(user=user)
                social_instance, _ = SocialModel.objects.update_or_create(
                    social_id=social_data.get('social_id'),
                    defaults=social_data
                )
                social_instance.set_used_for_registration(created=created)
                return Response(user.get_auth_data(created=created, social_decoded_token=serializer.validated_data))

    def simple_auth(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user, created = self.user_creation_method(**serializer.validated_data)
            if self.social_mapper_method is not None:
                social_data = self.social_mapper_method(**serializer.validated_data).get_kwargs(user=user)
                social_instance, _ = SocialModel.objects.update_or_create(
                    social_id=social_data.get('social_id'),
                    defaults=social_data
                )
            return Response(user.get_auth_data(created=created))

    def post(self, request, *args, **kwargs):
        if self.is_social_auth:
            return self.social_auth(request, *args, **kwargs)
        else:
            return self.simple_auth(request, *args, **kwargs)


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
