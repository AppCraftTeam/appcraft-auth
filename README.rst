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

2. Include the appcraft_auth URLconf in your project urls.py like this::

    path('appcraft_auth/', include('appcraft_auth.urls')),

3. Run ``python manage.py migrate`` to create the appcraft_auth models.

