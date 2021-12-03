from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/appcraft_auth/', include('appcraft_auth.urls')),
]
