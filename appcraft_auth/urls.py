from django.urls import path

from appcraft_auth import views
from appcraft_auth.views import RefreshTokenAPIView

urlpatterns = [
    # email
    path('email', views.GenerateEmailAuthCodeAPIView.as_view()),
    path('email/code', views.AuthenticateByEmailCodeAPIView.as_view()),

    # phone
    path('sms/send', views.SendSMSAPIView.as_view()),
    path('sms', views.AuthBySMSCodeAPIView.as_view()),

    # python-social-auth
    path('vk', views.VkAuthAPIView.as_view()),

    # firebase
    path('firebase', views.FirebaseAuthAPIView.as_view()),

    # wechat
    path('wechat', views.WeChatAuthAPIView.as_view()),

    # logging out and token refresh
    path('logout', views.LogOutAPIView.as_view()),
    path('token/refresh', RefreshTokenAPIView.as_view())
]
