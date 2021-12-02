=====
appcraft_auth
=====

Appcraft Auth is a Django app to handle all commune use cases for social auth.

Quick start
-----------

1. Add "appcraft_auth" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'appcraft_auth',
    ]



2. Add "appcraft_auth.middleware.BlacklistedTokensMiddleware" in the end of your
middleware settings likes this::

     MIDDLEWARE = [
        ...
        'appcraft_auth.middleware.BlacklistedTokensMiddleware'
    ]


3. Include the appcraft_auth URLconf in your project urls.py like this::

    urlpatterns = [
        ...
        path('api/appcraft_auth/', include('appcraft_auth.urls'))
        ...
    ]

4. In settings.py in REST_FRAMEWORK config specify authentication classes like this::

      REST_FRAMEWORK = {
            ...
            'DEFAULT_AUTHENTICATION_CLASSES': (
                'rest_framework_simplejwt.authentication.JWTAuthentication',
            )
            ...
      }

5. In settings.py specify simple jwt settings at least like this::

    SIMPLE_JWT = {
        'ACCESS_TOKEN_LIFETIME': time_up_to_you,
        'REFRESH_TOKEN_LIFETIME': time_up_to_you,
        'SIGNING_KEY': your_project_secret_key,
        'AUTH_HEADER_TYPES': list_or_tuple_of_types
    }


6. In settings.py specify celery and celery beat configuration. Add in your celery beat schedule
appcraft_auth tasks like this::

    CELERY_BEAT_SCHEDULE = {
    ...
        'clear_outdated_tokens': {
            'task': 'appcraft_auth.tasks.clear_outdated_tokens',
            'schedule': crontab(minute='0', hour='0')
        },
    ...
    }

7. Run ``python manage.py migrate`` to create the appcraft_auth models.

