import os

from django.core.management import BaseCommand

from users.models import CustomUser


class Command(BaseCommand):
    help = "Создание суперпользователя"

    def handle(self, *args, **options):
        email = os.getenv("CSU_EMAIL")
        password = os.getenv("CSU_PASSWORD")
        if not CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.create(email=email)
            user.is_staff = True
            user.is_active = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
