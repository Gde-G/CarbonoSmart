from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, ReadOnlyPasswordHashField, AuthenticationForm,  SetPasswordForm, PasswordChangeForm, PasswordResetForm
from django.core.exceptions import ValidationError
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible
from allauth.account.forms import LoginForm, SignupForm, ChangePasswordForm, ResetPasswordKeyForm
from allauth.account.forms import ResetPasswordForm as AllauthResetPasswordForm
from allauth.account.forms import SetPasswordForm as AllauthSetPasswordForm

from .models import MyUser


class MyUserCreationForm(UserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password Confirmarion', widget=forms.PasswordInput)
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible())

    class Meta(UserCreationForm.Meta):
        model = MyUser
        fields = UserCreationForm.Meta.fields + \
            ('username', 'email')

    def clean_password2(self) -> str:
        return super().clean_password2()

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class MyUserSocialAccountSetForm(SetPasswordForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible())

    class Meta(UserChangeForm.Meta):
        model = MyUser
        fields = ['new_password1', 'new_password2']


class MyUserUpdateForm(UserChangeForm):
    password = ReadOnlyPasswordHashField()
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible())

    class Meta(UserChangeForm.Meta):
        model = MyUser
        fields = ('first_name', 'last_name',
                  'username', 'email', 'profile_img')


class MyUserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(MyUserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible())
    remember = forms.BooleanField(required=False)


class MyUserChangePasswordForm(PasswordChangeForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible())

    class Meta:
        model = MyUser
        fields = ['old_password', 'new_password1', 'new_password2']


class MyUserResetPasswordForm(SetPasswordForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible())

    class Meta:
        model = MyUser
        fields = ['new_password1', 'new_password2']


class MyUserRecoverPasswordForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible())


class MyUserAllauthLoginForm(LoginForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible())


class MyUserAllauthSignUpForm(SignupForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible())


class MyUserAllauthChangePassword(ChangePasswordForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible())


class MyUserAllauthResetPasswordForm(AllauthResetPasswordForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible())


class MyUserAllauthSetPassword(AllauthSetPasswordForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible())


class MyUserAllauthResetPasswordKeyForm(ResetPasswordKeyForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible())
