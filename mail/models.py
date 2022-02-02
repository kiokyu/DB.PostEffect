from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
