from django.urls import path

from appcraft_auth import views
from appcraft_auth.views import RefreshTokenAPIView

urlpatterns = [
    path('test', views.TestAPIView.as_view()),

    # email
    path('email', views.GenerateEmailAuthCodeAPIView.as_view()),
    path('email/code', views.AuthenticateByEmailCodeAPIView.as_view()),

    # phone
    path('sms/send', views.SendSMSAPIView.as_view()),
    path('sms', views.AuthBySMSCodeAPIView.as_view()),

    # python-social-auth
    path('vk', views.VkAuthAPIView.as_view()),

    # logging out and token refresh
    path('logout', views.LogOutAPIView.as_view()),
    path('token/refresh', RefreshTokenAPIView.as_view())
]
