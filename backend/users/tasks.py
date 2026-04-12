from celery import shared_task
from time import sleep
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_email(email, code):
    print("SENDING...")
    send_mail(
        "Регистрация в shop_api",
        f"ваш код для подтверждения: {code}",
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )
    print("SENT.")
    return "OK"

@shared_task
def send_birthday_message():
    print("SENDING...")
    send_mail(
        "happy birthday!",
        "с вылуплением",
        settings.EMAIL_HOST_USER,
        ["zakirovaassol@gmail.com"],
        fail_silently=False,
    )
    print("SENT.")
    return "OK"

@shared_task
def send_welcome_email(email):
    send_mail(
        "Добро пожаловать!",
        "Спасибо за регистрацию 🎉",
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )
    return "OK"

from datetime import datetime
import os
from django.conf import settings

@shared_task 
def log_user_login(email): 
    with open("logins.txt", "a") as f: 
        f.write(f"{email} logged in at {datetime.now()}\n")
    return "Logged"

from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()
from django.db.models import Q
@shared_task
def delete_inactive_users():
    threshold_date = now() - timedelta(days=30)

    inactive_users = User.objects.filter(
    Q(last_login__lt=threshold_date) | Q(last_login__isnull=True)
)

    count = inactive_users.count()
    inactive_users.delete()

    print(f"Deleted {count} inactive users")