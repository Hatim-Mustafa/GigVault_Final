import datetime
from typing import Optional

from sqlalchemy.orm import Session
from models import GigListing, GigStatus


def get_open_gigs_filtered(
    db: Session,
    genre: Optional[str] = None,
    city: Optional[str] = None,
    date: Optional[datetime.date] = None,
    min_budget: Optional[float] = None,
    max_budget: Optional[float] = None,
    musician_id: Optional[int] = None,
) -> list[GigListing]:
    q = (
        db.query(GigListing)
        .filter(
            GigListing.status == GigStatus.OPEN.value,
            GigListing.performance_date >= datetime.date.today(),
        )
    )

    if genre and genre != "All":
        q = q.filter(GigListing.genre.ilike(f"%{genre}%"))
    if city and city.strip():
        q = q.filter(GigListing.city.ilike(f"%{city.strip()}%"))
    if date:
        q = q.filter(GigListing.performance_date == date)
    if min_budget is not None and min_budget > 0:
        q = q.filter(GigListing.budget >= min_budget)
    if max_budget is not None and max_budget > 0:
        q = q.filter(GigListing.budget <= max_budget)

    return q.order_by(GigListing.performance_date.asc()).all()


def get_client_gig_stats(db: Session, client_id: int) -> dict:
    from sqlalchemy import func
    from models import Application

    gigs = (
        db.query(GigListing.status, func.count(GigListing.id).label("cnt"))
        .filter(GigListing.client_id == client_id)
        .group_by(GigListing.status)
        .all()
    )
    stats = {row.status: row.cnt for row in gigs}

    pending_apps = (
        db.query(func.count(Application.id))
        .join(Application.gig)
        .filter(
            GigListing.client_id == client_id,
            Application.status == "Pending",
        )
        .scalar()
        or 0
    )

    return {
        "open": stats.get("Open", stats.get(GigStatus.OPEN, 0)),
        "booked": stats.get("Filled", stats.get(GigStatus.BOOKED, 0)),
        "completed": stats.get("Completed", stats.get(GigStatus.COMPLETED, 0)),
        "cancelled": stats.get("Cancelled", stats.get(GigStatus.CANCELLED, 0)),
        "total": sum(stats.values()),
        "pending_applications": pending_apps,
    }
