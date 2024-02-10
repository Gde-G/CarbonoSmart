from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email, user_field, user_username
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from allauth.account.utils import user_email, user_field, user_username

from django.http import HttpRequest
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import get_template
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from .tokens import account_activation_token
from .utils import download_file_from_url


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super(SocialAccountAdapter, self).save_user(
            request, sociallogin, form)

        user.is_active = True

        url = sociallogin.account.get_avatar_url()
        # here you should download file from provided url, the code is below
        avatar = download_file_from_url(url)
        if avatar:

            user.profile_img = avatar

        user.save()
        return user
