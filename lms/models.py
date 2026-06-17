from django.conf import settings
from django.db import models


class Course(models.Model):
    """Данные курса"""

    title = models.CharField(max_length=100, verbose_name="Название", help_text="Введите название курса")
    preview = models.ImageField(
        upload_to="lms/courses/preview/",
        blank=True,
        null=True,
        verbose_name="Превью курса",
        help_text="Загрузите превью курса",
    )
    description = models.TextField(
        blank=True, null=True, verbose_name="Описание курса", help_text="Введите описание курса"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="courses",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Владелец",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Цена курса")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ["title"]


class Lesson(models.Model):
    """Данные урока"""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Курс")
    title = models.CharField(max_length=100, verbose_name="Название", help_text="Введите название урока")
    description = models.TextField(
        blank=True, null=True, verbose_name="Описание урока", help_text="Введите описание урока"
    )
    preview = models.ImageField(
        upload_to="lms/lessons/preview/",
        blank=True,
        null=True,
        verbose_name="Превью урока",
        help_text="Загрузите превью урока",
    )
    video_url = models.URLField(
        max_length=300, blank=True, null=True, verbose_name="Ссылка на видео", help_text="Укажите ссылку на видео"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="lessons",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Владелец",
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["title"]


class Subscription(models.Model):
    """Подписка"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions", verbose_name="Пользователь"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="subscriptions", verbose_name="Курс")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")

    def __str__(self):
        return f"{self.user.email} - {self.course.title}"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ("user", "course")
