from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from lms.models import Course
from lms.permissions import IsOwner
from users.models import CustomUser, Payment
from users.permissions import IsPaymentOwner
from users.serializers import CustomUserSerializer, PaymentCreateSerializer, PaymentSerializer
from users.services import get_payment_status, process_course_payment, update_payment_status


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            return Response({"message": "Пользователь существует"}, status=status.HTTP_409_CONFLICT)
        return super().create(request, *args, **kwargs)


class UserListAPIView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()


class PaymentListAPIView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = (
        "paid_course",
        "paid_lesson",
        "payment_method",
    )

    ordering_fields = ("payment_date",)


class PaymentCreateAPIView(generics.CreateAPIView):
    """Создает платеж"""

    serializer_class = PaymentCreateSerializer

    @swagger_auto_schema(
        operation_description="Создает новый платеж через Stripe и возвращает ссылку на оплату.",
        request_body=serializer_class,
        responses={
            201: openapi.Response(
                description="Платеж успешно создан.",
                examples={
                    "application/json": {
                        "payment_id": 1,
                        "payment_link": "https://checkout.stripe.com/pay/...",
                        "amount": "5000.00",
                        "status": "pending",
                    }
                },
            ),
            400: openapi.Response(
                description="Ошибка валидации или курс бесплатный.",
                examples={"application/json": {"error": "Курс бесплатный"}},
            ),
            401: "Не авторизован",
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        course = get_object_or_404(Course, pk=data["course_id"])

        if course.price <= 0:
            return Response({"error": "Курс бесплатный"}, status=status.HTTP_400_BAD_REQUEST)

        payment = process_course_payment(
            user=request.user, course=course, success_url=data["success_url"], cancel_url=data["cancel_url"]
        )

        return Response(
            {
                "payment_id": payment.id,
                "payment_link": payment.stripe_payment_link,
                "amount": payment.payment_amount,
                "status": payment.status,
            },
            status=status.HTTP_201_CREATED,
        )


class PaymentStatusAPIView(generics.RetrieveAPIView):
    """Проверяет статус"""

    queryset = Payment.objects.all()
    permission_classes = [IsPaymentOwner]

    @swagger_auto_schema(
        operation_description="Проверяет статус платежа в Stripe и обновляет его в БД.",
        responses={
            200: openapi.Response(
                description="Статус платежа получен.",
                examples={
                    "application/json": {"payment_id": 1, "status": "paid", "stripe_status": "paid", "updated": True}
                },
            ),
            403: openapi.Response(
                description="Нет доступа к этому платежу.", examples={"application/json": {"error": "Нет доступа"}}
            ),
            404: "Платеж не найден",
        },
    )
    def get(self, request, *args, **kwargs):
        payment = self.get_object()

        # if payment.user != request.user:
        #     return Response({"error": "Нет доступа"}, status=status.HTTP_403_FORBIDDEN)

        stripe_status = get_payment_status(payment.stripe_session_id)
        updated = update_payment_status(payment)

        return Response(
            {
                "payment_id": payment.id,
                "status": payment.status,
                "stripe_status": stripe_status["payment_status"],
                "updated": updated,
            }
        )
