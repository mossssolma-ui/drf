from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from stripe import StripeClient

from lms.models import Subscription
from users.models import Payment

stripe_client = StripeClient(settings.STRIPE_API_KEY)


def create_stripe_product(name, description=None):
    """Создает продукт в страйпе"""
    try:
        product_data = {
            "name": name,
        }
        if description:
            product_data["description"] = description

        product = stripe_client.v1.products.create(product_data)

        return {
            "id": product["id"],
            "name": product["name"],
            "description": product["description"] if "description" in product else None,
        }
    except Exception as e:
        raise serializers.ValidationError(f"Ошибка создания продукта: {e}")


# def create_stripe_product(name, description=None):
#     """Создает продукт в страйпе"""
#     try:
#         print(f"DEBUG: Creating product with name={name}, description={description}")  # ← добавить
#
#         product_data = {
#             "name": name,
#         }
#         if description:
#             product_data["description"] = description
#
#         print(f"DEBUG: product_data={product_data}")  # ← добавить
#
#         product = stripe_client.v1.products.create(product_data)
#
#         print(f"DEBUG: product type={type(product)}")  # ← добавить
#         print(f"DEBUG: product={product}")  # ← добавить
#
#         return {
#             "id": product["id"],
#             "name": product["name"],
#             "description": product["description"] if "description" in product else None
#         }
#     except Exception as e:
#         print(f"DEBUG: Exception = {e}")  # ← добавить
#         raise serializers.ValidationError(f"Ошибка создания продукта: {e}")


def create_stripe_price(amount, product_id, currency="rub"):
    """Создает цену для продукта в страйпе"""
    try:
        amount_in_cents = int(amount * 100)

        price_data = {
            "currency": currency,
            "unit_amount": amount_in_cents,
            "product": product_id,
        }

        price = stripe_client.v1.prices.create(price_data)

        return {
            "id": price["id"],
            "amount": amount,
            "amount_in_cents": amount_in_cents,
            "currency": currency,
            "product_id": product_id,
        }
    except Exception as e:
        raise serializers.ValidationError(f"Ошибка создания цены: {e}")


def create_stripe_session(price_id, success_url, cancel_url):
    """Создает сессию на оплату в страйпе"""
    try:
        session_data = {
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": [
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            "mode": "payment",
        }

        session = stripe_client.v1.checkout.sessions.create(session_data)

        return {
            "id": session["id"],
            "url": session["url"],
            "payment_status": session["payment_status"],
            "status": session["status"],
        }
    except Exception as e:
        raise serializers.ValidationError(f"Ошибка создания сессии оплаты: {e}")


def get_payment_status(stripe_session_id):
    """Получает статус платежа из страйпа"""
    try:
        session = stripe_client.v1.checkout.sessions.retrieve(stripe_session_id)

        return {
            "id": session["id"],
            "payment_status": session["payment_status"],
            "status": session["status"],
        }
    except Exception as e:
        raise serializers.ValidationError(f"Ошибка получения статуса платежа: {e}")


def process_course_payment(user, course, success_url, cancel_url):
    """Платеж для курса"""

    product = create_stripe_product(name=course.title, description=course.description)

    price = create_stripe_price(amount=float(course.price), product_id=product["id"])

    session = create_stripe_session(price_id=price["id"], success_url=success_url, cancel_url=cancel_url)

    payment = Payment.objects.create(
        user=user,
        paid_course=course,
        payment_amount=course.price,
        payment_method=Payment.PayMethod.STRIPE,
        status=Payment.StatusChoices.PENDING,
        stripe_session_id=session["id"],
        stripe_product_id=product["id"],
        stripe_price_id=price["id"],
        stripe_payment_link=session["url"],
        paid_at=None,
    )

    return payment


def update_payment_status(payment):
    """Обновление статуса платежа и добавление автоматической подписки"""

    if not payment.stripe_session_id:
        return False

    stripe_data = get_payment_status(payment.stripe_session_id)
    updated = False

    if stripe_data["payment_status"] == "paid" and payment.status != Payment.StatusChoices.PAID:
        payment.status = Payment.StatusChoices.PAID
        payment.paid_at = timezone.now()
        payment.save()
        updated = True

        if payment.paid_course:
            Subscription.objects.get_or_create(
                user=payment.user,
                course=payment.paid_course,
            )

    return updated
