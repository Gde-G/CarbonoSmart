from django.http import HttpRequest
from .forms import MyUserAllauthLoginForm


def get_login_form(request: HttpRequest):
    if request.user.is_authenticated:
        return {'login_form': None}
    else:
        form = MyUserAllauthLoginForm()
        return {'login_form': form}
