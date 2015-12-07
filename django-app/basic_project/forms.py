from django import forms
from nocaptcha_recaptcha.fields import NoReCaptchaField
from django.conf import settings


class SignupForm(forms.Form):
    if hasattr(settings, 'NORECAPTCHA_SITE_KEY') and\
       hasattr(settings, 'NORECAPTCHA_SECRET_KEY'):
        captcha = NoReCaptchaField()

    def signup(self, request, user):
        pass

