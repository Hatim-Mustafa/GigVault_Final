import datetime

from database import get_db
from models import Payment, PaymentStatus


def mark_payment_paid(payment_id: int, client_id: int, notes: str = "") -> Payment:
    with get_db() as db:
        payment = (
            db.query(Payment)
            .filter(
                Payment.id == payment_id,
                Payment.client_id == client_id,
                Payment.status == PaymentStatus.PENDING,
            )
            .first()
        )
        if not payment:
            raise ValueError("Payment not found or already paid/cancelled.")
        payment.status = PaymentStatus.PAID
        payment.paid_at = datetime.datetime.utcnow()
        if notes:
            payment.notes = notes
        db.commit()
        db.refresh(payment)
        return payment


def get_client_payments(client_id: int) -> list[Payment]:
    with get_db() as db:
        return (
            db.query(Payment)
            .filter(Payment.client_id == client_id)
            .order_by(Payment.created_at.asc())
            .all()
        )


def get_musician_payments(band_id: int) -> list[Payment]:
    with get_db() as db:
        return (
            db.query(Payment)
            .filter(Payment.musician_id == band_id)
            .order_by(Payment.created_at.asc())
            .all()
        )
