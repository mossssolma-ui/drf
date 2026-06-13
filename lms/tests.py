from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, Lesson, Subscription
from users.models import CustomUser


class LessonTestCase(APITestCase):
    """Тестирование CRUD для lesson"""

    def setUp(self):
        self.moderator_group, _ = Group.objects.get_or_create(name="moderator")

        self.user = CustomUser.objects.create_user(email="user@test.com", password="Test12345!")

        self.moderator = CustomUser.objects.create_user(email="moderator@test.com", password="Test12345!")
        self.moderator.groups.add(self.moderator_group)

        self.course = Course.objects.create(
            title="Математические основы информатики",
            description="Изучите системы счисления. Познакомитесь с алгеброй логики и логическими выражениями",
            owner=self.user,
        )
        self.lesson = Lesson.objects.create(
            title="Системы счисления",
            course=self.course,
            owner=self.user,
            video_url="https://www.youtube.com/watch?v=DtAUNxOwrG8",
        )

    def test_lesson_retrieve(self) -> None:
        """Тест просмотр лекции владельцем"""
        self.client.force_authenticate(user=self.user)
        url = reverse("lms:lesson-get", args=(self.lesson.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("title"), self.lesson.title)

    def test_lesson_retrieve_moderator(self):
        """Тест просмотр лекции модератором"""
        self.client.force_authenticate(user=self.moderator)
        url = reverse("lms:lesson-get", args=(self.lesson.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("title"), self.lesson.title)

    def test_lesson_create(self) -> None:
        """Тест создание лекции владельцем"""
        self.client.force_authenticate(user=self.user)
        url = reverse("lms:lesson-create")
        data = {
            "title": "Введение в алгебру логики. Свойства логических операций",
            "description": "Познакомитесь с конъюнкцией, дизъюнкцией, инверсией",
            "course": self.course.pk,
            "video_url": "https://www.youtube.com/watch?v=b1hggt96R_Y",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.all().count(), 2)

    def test_lesson_create_no_valid_url(self) -> None:
        """Тест создание лекции с неправильным URL"""
        self.client.force_authenticate(user=self.user)
        url = reverse("lms:lesson-create")
        data = {
            "title": "Введение в алгебру логики. Свойства логических операций",
            "description": "Познакомитесь с конъюнкцией, дизъюнкцией, инверсией",
            "course": self.course.pk,
            "video_url": "https://www.youtube.en/watch?v=b1hggt96R_Y",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Lesson.objects.all().count(), 1)

    def test_lesson_create_moderator(self) -> None:
        """Тест модератор не может создать лекцию"""
        self.client.force_authenticate(user=self.moderator)
        url = reverse("lms:lesson-create")
        data = {
            "title": "Лекцию создал модератор",
            "description": "",
            "course": self.course.pk,
            "video_url": "https://www.youtube.com/watch?v=b1hggt96R_Y",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_update(self) -> None:
        """Тест редактирование лекции владельцем"""
        self.client.force_authenticate(user=self.user)
        url = reverse("lms:lesson-update", args=(self.lesson.pk,))
        data = {
            "title": "Представление вещественных чисел",
            "description": "",
            "course": self.course.pk,
        }
        response = self.client.patch(url, data)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("title"), "Представление вещественных чисел")

    def test_lesson_update_moderator(self) -> None:
        """Тест редактирование лекции модератором"""
        self.client.force_authenticate(user=self.moderator)
        url = reverse("lms:lesson-update", args=(self.lesson.pk,))
        data = {
            "title": "Представление вещественных чисел 2",
            "description": "обновил модератор",
            "course": self.course.pk,
        }
        response = self.client.patch(url, data)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("title"), "Представление вещественных чисел 2")

    def test_lesson_delete(self) -> None:
        """Тест удаление лекции владельцем"""
        self.client.force_authenticate(user=self.user)
        url = reverse("lms:lesson-delete", args=(self.lesson.pk,))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.all().count(), 0)

    def test_lesson_delete_moderator(self) -> None:
        """Тест модератор не может удалить лекцию"""
        self.client.force_authenticate(user=self.moderator)
        url = reverse("lms:lesson-delete", args=(self.lesson.pk,))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_list(self) -> None:
        """Тест список лекций"""
        self.client.force_authenticate(user=self.user)
        url = reverse("lms:lesson-list")
        response = self.client.get(url)
        data = response.json()
        result = {
            "count": Lesson.objects.all().count(),
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": self.lesson.pk,
                    "title": self.lesson.title,
                    "description": self.lesson.description,
                    "preview": None,
                    "video_url": self.lesson.video_url,
                    "course": self.course.pk,
                    "owner": self.user.pk,
                }
            ],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)

class SubscriptionTestCase(APITestCase):
    """Тест подписки на курс"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(email="user@test.com", password="Test12345!")
        self.course = Course.objects.create(title="Тестовый курс", owner=self.user)
        self.subscription_url = reverse("lms:subscription")

    def test_subscribe_course(self):
        """Тест подписка на курс"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.subscription_url, {"course_id": self.course.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "подписка добавлена")
        self.assertEqual(response.data.get("is_subscribed"), True)
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_unsubscribe_course(self):
        """Тест отписка от курса"""
        self.client.force_authenticate(user=self.user)

        self.client.post(self.subscription_url, {"course_id": self.course.id})
        response = self.client.post(self.subscription_url, {"course_id": self.course.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "подписка удалена")
        self.assertEqual(response.data.get("is_subscribed"), False)
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_subscribe_unauthenticated(self):
        """Тест для подписки нужна авторизация"""
        response = self.client.post(self.subscription_url, {"course_id": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
