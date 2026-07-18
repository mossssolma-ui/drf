from django.contrib import admin

from users.models import CustomUser, Payment


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    def get_groups(self, obj):
        names = [group.name for group in obj.groups.all()]
        return ", ".join(names)

    list_display = ("id", "email", "is_staff", "is_active", "is_superuser", "get_groups")
    list_filter = ("is_staff", "is_active", "is_superuser")
    exclude = ("password",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "payment_date", "payment_amount", "payment_method", "paid_course", "paid_lesson"]
    list_filter = ["payment_method", "payment_date"]
    search_fields = ["user__email", "paid_course__title", "paid_lesson__title"]
    readonly_fields = [
        "payment_date",
        "stripe_session_id",
        "stripe_product_id",
        "stripe_price_id",
        "stripe_payment_link",
        "paid_at",
    ]
    fields = ["user", "payment_date", "paid_course", "paid_lesson", "payment_amount", "payment_method"]
