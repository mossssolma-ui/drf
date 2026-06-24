# users/tasks.py
from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


@shared_task
def block_inactive_users():
    """блок неактивных пользователей"""
    month = timezone.now() - timedelta(days=30)

    count_users = User.objects.filter(
        last_login__lt=month,
        is_active=True,
    ).update(is_active=False)

    if count_users > 0:
        return f"Заблокировано {count_users} неактивных пользователей"
    return "Нет неактивных пользователей"
