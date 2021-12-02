from django.core.handlers.wsgi import WSGIRequest


def get_access_token(request: WSGIRequest) -> str or None:
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return
    return auth_header.split(' ')[-1]
