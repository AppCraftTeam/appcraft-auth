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



7. If you want need to use authentication based on email and sent code, first specify
the email backend like this::

        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', True)
        EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', False)
        EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        EMAIL_PORT = os.getenv('EMAIL_PORT', 587)
        EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
        EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

Then in settings.py file specify APPCRAFT_AUTH_EMAIL_SETTINGS like this::

        APPCRAFT_AUTH_EMAIL_SETTINGS = {
            'CODE_LENGTH': e.g. 6 (optional)
            'AUTH_LETTER_SUBJECT': 'subject up to you',
            'TEMPLATE_NAME' : 'html_template_name_to_be_sent' (optional)
            'REPEAT_INTERVAL' : timedelta(set here interval up to you) (e.g timedelta(minutes=1)) (optional),
            'MAX_TRIALS_PERIOD' : timedelta(set here interval up to you) (e.g timedelta(days=1)) (optional),
            'MAX_TRIALS_PER_PERIOD' : e.g. 6 (optional)
        }
Your template should contain the "code" variable.

Аlso add "proxy_set_header X-Real-IP $remote_addr;" in your nginx configuration,
in order to restrict abuses of getting codes based from the same ip address for different emails.



8. Run ``python manage.py migrate`` to create the appcraft_auth models.

