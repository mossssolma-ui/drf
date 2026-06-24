from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import Course, Subscription


@shared_task
def send_course_update_email(user_email, course_title):
    """Отправка письма пользователю об обновлении курса"""
    try:
        send_mail(
            subject=f"Обновление курса {course_title}",
            message=f"Курс {course_title} был обновлен!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
        )
        return f"Письмо отправлено {user_email}"
    except Exception as e:
        return f"Ошибка отправки письма {user_email}: {e}"


@shared_task
def send_subscribers_update_email(course_id):
    """Отправка писем всем подписчикам курса об обновлении"""
    try:
        course = Course.objects.get(pk=course_id)
        subscriptions = Subscription.objects.filter(course=course).select_related("user")

        if not subscriptions:
            return f"У курса {course.title} нет подписчиков"

        for subscription in subscriptions:
            user_email = subscription.user.email
            if user_email:
                send_course_update_email.delay(user_email, course.title)

        return f"Уведомления отправлены {subscriptions.count()} подписчикам курса {course.title}"
    except Course.DoesNotExist:
        return f"Курс с id {course_id} не существует"
