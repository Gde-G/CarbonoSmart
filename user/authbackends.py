from django.contrib.auth.backends import BaseBackend
from .models import MyUser
from django.db.models import Q


class MyUserBackend(BaseBackend):

    def authenticate(self, request, username=None, password=None):
        try:
            # Username or Email Accepts
            user = MyUser.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username))

            if user.check_password(password):
                return user
        except MyUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return MyUser.objects.get(pk=user_id)
        except MyUser.DoesNotExist:
            return None
