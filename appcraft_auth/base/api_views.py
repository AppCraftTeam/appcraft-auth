from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class BaseAuthAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = None
    method = None

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user, created = self.method(**serializer.validated_data)
            return Response(user.get_auth_data(created=created))


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