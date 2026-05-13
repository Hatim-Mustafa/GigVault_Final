import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from models import Band, BookingContract, GigListing, Payment, PaymentStatus, User


def get_client_payment_summary(db: Session, client_id: int) -> dict:
    rows = (
        db.query(Payment.status, func.count(Payment.id), func.sum(Payment.amount))
        .filter(Payment.client_id == client_id)
        .group_by(Payment.status)
        .all()
    )
    summary: dict = {
        "pending_count": 0,
        "pending_amount": 0.0,
        "completed_count": 0,
        "completed_amount": 0.0,
        "failed_count": 0,
        "refunded_count": 0,
        "total_amount": 0.0,
    }
    for status, cnt, total in rows:
        status_val = status.value if hasattr(status, "value") else status
        s = status_val.lower()
        summary[f"{s}_count"] = cnt or 0
        summary[f"{s}_amount"] = float(total or 0)
        summary["total_amount"] += float(total or 0)
    return summary


def get_musician_payment_summary(db: Session, band_id: int) -> dict:
    rows = (
        db.query(Payment.status, func.count(Payment.id), func.sum(Payment.amount))
        .filter(Payment.musician_id == band_id)
        .group_by(Payment.status)
        .all()
    )
    summary: dict = {
        "pending_count": 0,
        "pending_amount": 0.0,
        "completed_count": 0,
        "completed_amount": 0.0,
        "total_earned": 0.0,
    }
    for status, cnt, total in rows:
        status_val = status.value if hasattr(status, "value") else status
        s = status_val.lower()
        summary[f"{s}_count"] = cnt or 0
        summary[f"{s}_amount"] = float(total or 0)
        if status_val == "Completed":
            summary["total_earned"] += float(total or 0)
    return summary


def get_client_payments_with_details(db: Session, client_id: int) -> list:
    return (
        db.query(Payment, Band, GigListing)
        .options(joinedload(Band.leader), joinedload(Payment.booking).joinedload(BookingContract.gig))
        .join(BookingContract, Payment.booking_id == BookingContract.id)
        .join(GigListing, BookingContract.gig_id == GigListing.id)
        .join(Band, Payment.musician_id == Band.id)
        .filter(Payment.client_id == client_id)
        .order_by(Payment.created_at.asc())
        .all()
    )


def get_musician_payments_with_details(db: Session, band_id: int) -> list:
    return (
        db.query(Payment, User, GigListing)
        .options(
            joinedload(Payment.booking).joinedload(BookingContract.gig),
            joinedload(User.client_profile),
        )
        .join(BookingContract, Payment.booking_id == BookingContract.id)
        .join(GigListing, BookingContract.gig_id == GigListing.id)
        .join(User, Payment.client_id == User.id)
        .filter(Payment.musician_id == band_id)
        .order_by(Payment.created_at.asc())
        .all()
    )
