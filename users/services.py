from decimal import Decimal

import stripe
from django.conf import settings
from django.utils import timezone
from stripe import StripeClient

from lms.models import Course, Subscription
from users.exceptions import FailedToCreatePrice, FailedToCreateProduct, FailedToCreateSessions, FailedToGetStatus
from users.models import CustomUser, Payment

stripe_client = StripeClient(settings.STRIPE_API_KEY)


def create_stripe_product(name: str, description: str | None = None) -> dict:
    """Создает продукт в страйпе"""

    product_data = {
        "name": name,
    }
    try:
        if description:
            product_data["description"] = description

        product = stripe_client.v1.products.create(product_data)
    except stripe.error.StripeError as e:
        raise FailedToCreateProduct(f"Ошибка создания продукта: {e}") from e

    return {
        "id": product["id"],
        "name": product["name"],
        "description": product["description"] if "description" in product else None,
    }


def create_stripe_price(amount: Decimal, product_id: str, currency: str = "rub") -> dict:
    """Создает цену для продукта в страйпе"""

    amount_in_cents = int(amount * Decimal(100))

    price_data = {
        "currency": currency,
        "unit_amount": amount_in_cents,
        "product": product_id,
    }

    try:
        price = stripe_client.v1.prices.create(price_data)
    except stripe.error.StripeError as e:
        raise FailedToCreatePrice(f"Ошибка создания цены: {e}") from e

    return {
        "id": price["id"],
        "amount": amount,
        "amount_in_cents": amount_in_cents,
        "currency": currency,
        "product_id": product_id,
    }


def create_stripe_session(price_id: str, success_url: str, cancel_url: str) -> dict:
    """Создает сессию на оплату в страйпе"""

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
    try:
        session = stripe_client.v1.checkout.sessions.create(session_data)
    except stripe.error.StripeError as e:
        raise FailedToCreateSessions(f"Ошибка создания сессии оплаты: {e}") from e

    return {
        "id": session["id"],
        "url": session["url"],
        "payment_status": session["payment_status"],
        "status": session["status"],
    }


def get_payment_status(stripe_session_id: str) -> dict:
    """Получает статус платежа из страйпа"""
    try:
        session = stripe_client.v1.checkout.sessions.retrieve(stripe_session_id)
    except stripe.error.StripeError as e:
        raise FailedToGetStatus(f"Ошибка получения статуса платежа: {e}") from e

    return {
        "id": session["id"],
        "payment_status": session["payment_status"],
        "status": session["status"],
    }


def process_course_payment(user: CustomUser, course: Course, success_url: str, cancel_url: str) -> Payment:
    """Платеж для курса"""

    product = create_stripe_product(name=course.title, description=course.description)

    price = create_stripe_price(amount=course.price, product_id=product["id"])

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


def update_payment_status(payment: Payment) -> bool:
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
