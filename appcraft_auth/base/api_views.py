from rest_framework.views import APIView


class BaseAuthAPIView(APIView):
    permission_classes = []
    serializer_class = None
