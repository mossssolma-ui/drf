from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from lms.models import Course, Lesson


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True")
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = None
    email = models.EmailField(unique=True, verbose_name="Email", help_text="Укажите почту")
    phone_number = models.CharField(
        max_length=15, blank=True, null=True, verbose_name="Телефон", help_text="Укажите телефон"
    )
    city = models.CharField(max_length=50, blank=True, null=True, help_text="Укажите страну")
    avatar = models.ImageField(
        upload_to="users/avatars/", blank=True, null=True, verbose_name="Аватар", help_text="Загрузите аватар"
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-email"]

    def __str__(self):
        return self.email


class Payment(models.Model):
    class PayMethod(models.TextChoices):
        CASH = "cash", "Наличные"
        TRANSFER = "transfer", "Перевод на счет"
        STRIPE = "stripe", "Банковская карта (Stripe)"

    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Ожидает оплаты"
        PAID = "paid", "Оплачено"
        FAILED = "failed", "Ошибка оплаты"
        CANCELED = "canceled", "Отменена оплата"

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="payments", verbose_name="Пользователь"
    )
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата платежа")
    paid_course = models.ForeignKey(
        Course, on_delete=models.CASCADE, verbose_name="Оплаченный курс", null=True, blank=True
    )
    paid_lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, verbose_name="Оплаченный урок", null=True, blank=True
    )
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма оплаты")
    payment_method = models.CharField(
        max_length=30, choices=PayMethod.choices, default=PayMethod.TRANSFER, verbose_name="Способ оплаты"
    )
    status = models.CharField(
        max_length=30, choices=StatusChoices.choices, default=StatusChoices.PENDING, verbose_name="Статус платежа"
    )
    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID сессии",
    )
    stripe_product_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID продукта в Stripe",
        help_text="Идентификатор созданного продукта в Stripe",
    )

    stripe_price_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID цены в Stripe",
        help_text="Идентификатор созданной цены в Stripe",
    )

    stripe_payment_link = models.URLField(max_length=500, blank=True, null=True, verbose_name="Ссылка на оплату")
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name="Дата подтверждения оплаты")

    def __str__(self):
        return f"{self.user} - {self.payment_amount}руб. - {self.get_status_display()}"

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-payment_date"]
