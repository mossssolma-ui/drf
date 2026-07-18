from django.contrib import admin

from lms.models import Course, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "description", "owner")
    list_filter = ("title", "price", "owner")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("course", "title", "description", "owner", "video_url")
    list_filter = ("course", "title", "owner")

    class Meta:
        verbose_name = "Лекция"
        verbose_name_plural = "Лекции"
