from django.urls import path

from appcraft_auth import views
from appcraft_auth.views import RefreshTokenAPIView

urlpatterns = [
    path('test', views.TestAPIView.as_view()),

    # email
    path('email', views.GenerateAuthCodeAPIView.as_view()),
    path('email/code', views.AuthenticateByCodeAPIView.as_view()),

    path('logout', views.LogOutAPIView.as_view()),
    path('token/refresh', RefreshTokenAPIView.as_view())
]
