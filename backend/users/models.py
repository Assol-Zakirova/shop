import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from users.managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True, default=datetime.date.today)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    REQUIRED_FIELDS = ['phone']
    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email
