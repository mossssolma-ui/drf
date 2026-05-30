from django.contrib import admin

from users.models import CustomUser, Payment


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    exclude = ("password",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "payment_date", "payment_amount", "payment_method", "paid_course", "paid_lesson"]
    list_filter = ["payment_method", "payment_date"]
    search_fields = ["user__email", "paid_course__title", "paid_lesson__title"]
    fields = ["user", "payment_date", "paid_course", "paid_lesson", "payment_amount", "payment_method"]
