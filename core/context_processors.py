from django.http import HttpRequest


def check_cookie(request: HttpRequest):
    if 'consent' in request.COOKIES.keys():
        return {"consent": True}
    else:
        return {"consent": False}
