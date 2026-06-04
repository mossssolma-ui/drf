from rest_framework import serializers

from users.models import CustomUser, Payment


class PaymentSerializer(serializers.ModelSerializer):
    paid_item = serializers.SerializerMethodField()

    def get_paid_item(self, obj):
        if obj.paid_course:
            return f"Курс: {obj.paid_course.title}"
        elif obj.paid_lesson:
            return f"Урок: {obj.paid_lesson.title}"
        return "Нет данных"

    class Meta:
        model = Payment
        fields = "__all__"


class CustomUserSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ("id", "email", "phone_number", "city", "avatar", "payments", "password")
        extra_kwargs = {"password": {"write_only": True}}
