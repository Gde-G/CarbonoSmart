from django import forms
from .models import Company
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible


class CompanyForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible())

    class Meta:
        model = Company
        fields = ['name', 'website', 'contact_name', 'contact_email',
                  'country', 'contact_phone', 'topic_about', 'content']


class CaptchaForm(forms.BaseForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible())
