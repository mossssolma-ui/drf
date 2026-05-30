import random
from datetime import datetime, timedelta

from django.core.management import BaseCommand

from lms.models import Course, Lesson
from users.models import CustomUser, Payment


class Command(BaseCommand):
    help = "Наполнение данными модели Payments"

    def add_arguments(self, params):
        params.add_argument(
            "--count",
            type=int,
            default=10,
            help="Введите нужное количество платежей",
        )
        params.add_argument("--clear", action="store_true", help="Очистка таблицы в БД перед заполнением")

    def handle(self, *args, **kwargs):
        count = kwargs["count"]
        clear = kwargs["clear"]

        if clear:
            Payment.objects.all().delete()
            self.stdout.write(self.style.WARNING("Все платежи удалены"))

        if not CustomUser.objects.exists():
            users = self.create_test_users()
            self.stdout.write(self.style.WARNING(f"Создано {len(users)} пользователей"))
        else:
            users = list(CustomUser.objects.all())

        if not Course.objects.exists():
            courses = self.create_test_courses()
            self.stdout.write(self.style.WARNING(f"Создано {len(courses)} курсов"))
        else:
            courses = list(Course.objects.all())

        if not Lesson.objects.exists() and courses:
            lessons = self.create_test_lessons(courses)
            self.stdout.write(self.style.WARNING(f"Создано {len(lessons)} уроков"))
        else:
            lessons = list(Lesson.objects.all())

        if not users:
            self.stdout.write(self.style.ERROR("Нет пользователей для создания платежей"))
            return

        if not courses and not lessons:
            self.stdout.write(self.style.ERROR("Нет курсов и уроков для создания платежей"))
            return

        created_count = 0
        for i in range(count):
            payment_data = self.get_random_payment(users, courses, lessons)
            if not payment_data:
                continue
            pay = Payment.objects.create(**payment_data)
            created_count += 1

            paid_item = payment_data["paid_course"] if payment_data["paid_course"] else payment_data["paid_lesson"]
            self.stdout.write(
                self.style.SUCCESS(
                    f"Платеж {i + 1}: {pay.user.email} - {paid_item} - {pay.payment_amount} руб. - {pay.payment_date}"
                )
            )

        self.stdout.write(self.style.SUCCESS(f"\nСоздано {created_count} новых платежей из {count} запрошенных"))

    def create_test_users(self):
        users = []
        user_data = [
            {"email": "user1@example.com", "password": "pass123", "phone": "+79781234567", "city": "Москва"},
            {"email": "user2@example.com", "password": "pass123", "phone": "+79781234568", "city": "СПб"},
            {"email": "user3@example.com", "password": "pass123", "phone": "+79781234569", "city": "Симферополь"},
            {"email": "user4@example.com", "password": "pass123", "phone": "+79781234570", "city": "Севастополь"},
            {"email": "user5@example.com", "password": "pass123", "phone": "+79781234571", "city": "Красноперекопск"},
        ]

        for data in user_data:
            user = CustomUser.objects.create_user(
                email=data["email"], password=data["password"], phone_number=data["phone"], city=data["city"]
            )
            users.append(user)

        return users

    def create_test_courses(self):
        courses = []
        course_titles = [
            "Математические основы информатики",
            "Основы алгоритмизации",
            "Начала программирования",
            "Моделирование и формализация",
            "Обработка числовой информации",
            "Коммуникационные технологии",
            "Алгоритмы и структуры данных",
            "Django",
        ]

        for title in course_titles:
            course = Course.objects.create(title=title, description=f"Курс по теме: {title}.")
            courses.append(course)

        return courses

    def create_test_lessons(self, courses):
        lessons = []
        lesson_themes = [
            "Введение в тему",
            "Установка и настройка",
            "Основные концепции",
            "Практическое занятие",
            "Продвинутые техники",
            "Оптимизация",
            "Тестирование и отладка",
            "Финальный проект",
        ]

        for course in courses:
            num_lessons = random.randint(3, 5)
            chosen_themes = random.sample(lesson_themes, num_lessons)

            for i, theme in enumerate(chosen_themes, 1):
                lesson = Lesson.objects.create(
                    course=course,
                    title=f"{course.title} - {theme}",
                    description=f"Урок {i}: {theme}.",
                    video_url=f"https://example.com/video/{course.id}/{i}",
                )
                lessons.append(lesson)

        return lessons

    def get_random_payment(self, users, courses, lessons):
        user = random.choice(users)

        days = random.randint(0, 365)
        payment_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        amount = round(random.uniform(1000, 100000), 2)

        payment_method = random.choice(["transfer", "cash"])

        pay_for_course = random.random() < 0.6

        if pay_for_course and courses:
            course = random.choice(courses)
            return {
                "user": user,
                "payment_date": payment_date,
                "paid_course": course,
                "paid_lesson": None,
                "payment_amount": amount,
                "payment_method": payment_method,
            }
        elif lessons:
            lesson = random.choice(lessons)
            return {
                "user": user,
                "payment_date": payment_date,
                "paid_course": None,
                "paid_lesson": lesson,
                "payment_amount": amount,
                "payment_method": payment_method,
            }

        return None
