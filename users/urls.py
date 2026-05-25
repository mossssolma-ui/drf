from django.urls import path

from users.apps import UsersConfig
from users.views import UserListCreateAPIView, UserRetrieveUpdateDestroyAPIView

app_name = UsersConfig.name

urlpatterns = [
    path("", UserListCreateAPIView.as_view(), name="user-list-create"),
    path("<int:pk>/", UserRetrieveUpdateDestroyAPIView.as_view(), name="user-detail"),
]
