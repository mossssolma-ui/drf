from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Backend-сервер для платформы онлайн-обучения API",
        default_version="v1",
        description="API для платформы онлайн-обучения",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="mossssolma@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("lms.urls", namespace="lms")),
    path("users/", include("users.urls", namespace="users")),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
