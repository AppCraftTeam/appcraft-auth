from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from appcraft_auth.models import BlackListedTokenModel
from appcraft_auth.serializers import CustomTokenRefreshSerializer
from appcraft_auth.utils.request_utils import get_access_token


class TestAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = {}
        tokens = RefreshToken.for_user(user=get_user_model().objects.get(id=1))
        data['access_token'] = str(tokens.access_token)
        data['refresh_token'] = str(tokens)
        return Response(data)


class LogOutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def delete(request, *args, **kwargs):
        access_token = get_access_token(request=request)
        BlackListedTokenModel.objects.create(
            type=BlackListedTokenModel.Type.access,
            token=access_token
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class RefreshTokenAPIView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer