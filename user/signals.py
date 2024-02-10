from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
