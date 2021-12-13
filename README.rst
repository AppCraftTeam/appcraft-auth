appcraft_auth
=====


Quick start


1. Run ``pip install appcraft-auth``

2. appcraft_auth app is based on restframework-simplejwt package, so you also have to specify authentication classes and
other settings related to it https://django-rest-framework-simplejwt.readthedocs.io/en/latest/getting_started.html

3. For app to work properly - your settings.AUTH_USER_MODEL should be inherited from AppCraftAuthUserModel

4. Add "appcraft_auth" to your INSTALLED_APPS::

        INSTALLED_APPS = [
            ...
            'appcraft_auth',
            ...
        ]


5. Add "appcraft_auth.middleware.BlacklistedTokensMiddleware" in the end of your
middleware settings::

         MIDDLEWARE = [
            ...
            'appcraft_auth.middleware.BlacklistedTokensMiddleware'
        ]


6. Include the appcraft_auth URLconf in your project urls.py::

        urlpatterns = [
            ...
            path('api/appcraft_auth/', include('appcraft_auth.urls'))
            ...
        ]

7. Run ``python manage.py migrate`` to create the appcraft_auth models.

8. For authentication based on firebase token,  appcraft_auth provides opportunity to set
a sequence of authorised sign in providers. Thus authentication with firebase token provided from not specified sign in provider
will throw an exception. Set in settings.py a sequence of authorized providers::

        FIREBASE_AUTHORIZED_SIGN_IN_PROVIDERS = tuple or list e.g['phone', 'google.com', 'apple.com', 'facebook.com']


9. If you want to use authentication based on unique code being sent via email, first in settings.py
specify the email backend : https://docs.djangoproject.com/en/4.0/topics/email/#smtp-backend.

Also add "proxy_set_header X-Real-IP $remote_addr;" in the nginx configuration,
in order to restrict abuses of getting unique codes by request made form the same ip address for different emails.

Moreover if you want the email to be sent as an html, create it and be sure you have included the "code" variable there.

Then specify appcraft_auth email settings like this::

        APPCRAFT_AUTH_EMAIL_SETTINGS = {
            'CODE_LENGTH': integer describing the unique code length | optional
            'AUTH_LETTER_SUBJECT': string to be used as email subject | optional
            'TEMPLATE_NAME' : string | html_template_name_to_be_sent | optional
            'REPEAT_INTERVAL' : timedelta | the interval to wait before making request to get code | optional
            'MAX_TRIALS_PERIOD' : timedelta | period of maximal trials to get unique code for the same email | optional
            'MAX_TRIALS_PER_PERIOD' : integer | max trials limit to get unique code for the same email | optional
        }




10. If you want to use authentication based on VK access token, 'social_django' in INSTALLED_APPS
(the package will be already provided with appcraft_auth other requirements)
After having specify all settings related to that package https://pypi.org/project/social-auth-app-django ,
include in social auth pipelines  appcraft_auth pipelines::

        SOCIAL_AUTH_PIPELINE = (
            ...
            'appcraft_auth.pipelines.do_auth',
        )

11. For authentication based on sms code sms aero settings::

        SMS_AERO_EMAIL = os.getenv('SMS_AERO_EMAIL')
        SMS_AERO_API_KEY = os.getenv('SMS_AERO_API_KEY')

12. For wechat auth activation set following settings::

        WECHAT_APP_ID = os.getenv('WECHAT_APP_ID')
        WECHAT_APP_SECRET = os.getenv('WECHAT_APP_SECRET')


13. appcraft_auth app keeps all tokens in db. If you want to remove them periodically, register appcraft_auth.tasks.clear_outdated_tokens
function and include in celery beat schedule. This will remove all token instances based on simple jwt access token lifetime setting.