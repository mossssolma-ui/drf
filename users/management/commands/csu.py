from django.core.management import BaseCommand

from users.models import CustomUser


class Command(BaseCommand):
    help = "Создание суперпользователя"

    def handle(self, *args, **options):
        user = CustomUser.objects.create(email="admin@example.com")
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.set_password("12345678qwe")
        user.save()
