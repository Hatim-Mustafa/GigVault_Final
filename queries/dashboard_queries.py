import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import (
    Application,
    ApplicationStatus,
    BookingContract,
    BookingStatus,
    GigListing,
    GigStatus,
    Payment,
    PaymentStatus,
)


def get_client_dashboard_stats(db: Session, client_id: int) -> dict:
    gig_stats = (
        db.query(GigListing.status, func.count(GigListing.id))
        .filter(GigListing.client_id == client_id)
        .group_by(GigListing.status)
        .all()
    )
    gig_map = {}
    for status, cnt in gig_stats:
        gig_map[status.value if hasattr(status, "value") else status] = cnt

    pending_apps = (
        db.query(func.count(Application.id))
        .join(Application.gig)
        .filter(
            GigListing.client_id == client_id,
            Application.status == ApplicationStatus.PENDING,
        )
        .scalar()
        or 0
    )

    total_committed = (
        db.query(func.sum(BookingContract.agreed_amount))
        .filter(
            BookingContract.client_id == client_id,
            BookingContract.status.in_([BookingStatus.ACTIVE, BookingStatus.COMPLETED]),
        )
        .scalar()
        or 0.0
    )

    overdue_count = 0

    upcoming = (
        db.query(func.count(GigListing.id))
        .filter(
            GigListing.client_id == client_id,
            GigListing.status == GigStatus.BOOKED,
            GigListing.performance_date >= datetime.date.today(),
        )
        .scalar()
        or 0
    )

    return {
        "total_gigs": sum(gig_map.values()),
        "open_gigs": gig_map.get("Open", 0),
        "booked_gigs": gig_map.get("Filled", 0),
        "completed_gigs": gig_map.get("Completed", 0),
        "cancelled_gigs": gig_map.get("Cancelled", 0),
        "pending_applications": pending_apps,
        "total_committed": float(total_committed),
        "overdue_payments": overdue_count,
        "upcoming_performances": upcoming,
    }


def get_musician_dashboard_stats(db: Session, band_id: int | None) -> dict:
    if band_id is None:
        app_stats = []
    else:
        app_stats = (
            db.query(Application.status, func.count(Application.id))
            .filter(Application.band_id == band_id)
            .group_by(Application.status)
            .all()
        )
    app_map = {}
    for status, cnt in app_stats:
        app_map[status.value if hasattr(status, "value") else status] = cnt

    total_earned = (
        db.query(func.sum(Payment.amount))
        .filter(
            Payment.musician_id == band_id,
            Payment.status == PaymentStatus.PAID,
        )
        .scalar()
        or 0.0
    )

    pending_pay = (
        db.query(func.sum(Payment.amount))
        .filter(
            Payment.musician_id == band_id,
            Payment.status == PaymentStatus.PENDING,
        )
        .scalar()
        or 0.0
    )

    upcoming = (
        db.query(func.count(BookingContract.id))
        .join(BookingContract.gig)
        .filter(
            BookingContract.musician_id == band_id,
            BookingContract.status == BookingStatus.ACTIVE,
            GigListing.performance_date >= datetime.date.today(),
        )
        .scalar()
        or 0
    )

    overdue_count = 0

    return {
        "total_applications": sum(app_map.values()),
        "pending_applications": app_map.get("Pending", 0),
        "accepted_applications": app_map.get("Accepted", 0),
        "rejected_applications": app_map.get("Rejected", 0),
        "upcoming_gigs": upcoming,
        "total_earned": float(total_earned),
        "pending_payment": float(pending_pay),
        "overdue_payments": overdue_count,
    }
