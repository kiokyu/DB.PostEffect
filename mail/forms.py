from django import forms
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.contrib.auth.forms import UsernameField
from django.contrib.auth.hashers import (
    UNUSABLE_PASSWORD_PREFIX, identify_hasher,
)
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.text import capfirst
from django.utils.translation import gettext, gettext_lazy as _

UserModel = get_user_model()


class MyUserCreationForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': _('The two password fields didn’t match.'),
    }
    password1 = forms.CharField(
        label=_("Введите пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        label=_("Подтвердите пароль"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )

    email = forms.EmailField\
        (max_length=254,
         help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ("username", "email", "password", )
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs['autofocus'] = True

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error('password2', error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
