from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from users.apps import UsersConfig
from users.views import (
    PaymentCreateAPIView,
    PaymentListAPIView,
    PaymentStatusAPIView,
    UserCreateAPIView,
    UserListAPIView,
    UserRetrieveUpdateDestroyAPIView,
)

app_name = UsersConfig.name

urlpatterns = [
    path("", UserListAPIView.as_view(), name="user-list-create"),
    path("<int:pk>/", UserRetrieveUpdateDestroyAPIView.as_view(), name="user-detail"),
    path("register/", UserCreateAPIView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("payments/", PaymentListAPIView.as_view(), name="user-payments-list"),
    path("payments/create/", PaymentCreateAPIView.as_view(), name="payment-create"),
    path("payments/check_status/<int:pk>/", PaymentStatusAPIView.as_view(), name="payment-status"),
]
