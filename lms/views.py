from rest_framework import generics, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from lms.models import Course, Lesson, Subscription
from lms.paginators import CustomPaginator
from lms.permissions import IsOwner
from lms.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsNotModerator


class CourseViewSet(viewsets.ModelViewSet):
    """CRUD для Course"""

    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    pagination_class = CustomPaginator

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="moderator").exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [IsNotModerator]
        elif self.action == "destroy":
            self.permission_classes = [IsOwner, IsNotModerator]
        elif self.action in ["update", "retrieve"]:
            self.permission_classes = [IsOwner | IsModerator]
        else:
            self.permission_classes = []

        return super().get_permissions()


class LessonCreateAPIView(generics.CreateAPIView):
    """Создание лекции"""

    serializer_class = LessonSerializer
    permission_classes = [IsNotModerator]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    """Список лекций"""

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    pagination_class = CustomPaginator

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="moderator").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """Просмотр 1 лекции"""

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsOwner | IsModerator]


class LessonUpdateAPIView(generics.UpdateAPIView):
    """Изменение лекции"""

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsOwner | IsModerator]


class LessonDestroyAPIView(generics.DestroyAPIView):
    """Удаление лекции"""

    queryset = Lesson.objects.all()
    permission_classes = [IsOwner, IsNotModerator]


class SubscriptionAPIView(generics.GenericAPIView):

    def post(self, *args, **kwargs):
        user = self.request.user
        course_id = self.request.data.get("course_id")

        if not course_id:
            return Response(
                {"error": "Не указан course_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        course_item = get_object_or_404(Course, pk=course_id)

        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists():
            subs_item.delete()
            message = "подписка удалена"
            is_subscribed = False
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = "подписка добавлена"
            is_subscribed = True

        return Response(
            {
                "message": message,
                "is_subscribed": is_subscribed,
                "course_id": course_id,
                "course_title": course_item.title,
            },
            status=status.HTTP_200_OK,
        )
