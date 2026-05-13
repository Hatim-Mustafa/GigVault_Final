import datetime
from typing import Optional

from database import get_db
from models import GigListing, GigStatus


def create_gig(
    client_id: int,
    title: str,
    description: str,
    genre: str,
    city: str,
    performance_date: datetime.date,
    start_time: Optional[datetime.time],
    end_time: Optional[datetime.time],
    budget: float,
    requirements: str,
    duration_hours: Optional[float] = None,
) -> GigListing:
    with get_db() as db:
        existing = (
            db.query(GigListing)
            .filter(
                GigListing.client_id == client_id,
                GigListing.performance_date == performance_date,
                GigListing.status != GigStatus.CANCELLED,
            )
            .first()
        )
        if existing:
            raise ValueError(
                f"You already have an active gig on {performance_date.strftime('%b %d, %Y')}. "
                f"Cancel it first, or choose a different date."
            )

        if performance_date < datetime.date.today():
            raise ValueError("Performance date cannot be in the past.")

        if budget <= 0:
            raise ValueError("Budget must be greater than zero.")

        gig = GigListing(
            client_id=client_id,
            title=title.strip(),
            description=description.strip() if description else None,
            genre=genre,
            city=city.strip(),
            performance_date=performance_date,
            start_time=start_time,
            venue_name=title.strip(),
            budget=budget,
            duration_hours=duration_hours,
            status=GigStatus.OPEN,
        )
        db.add(gig)
        db.commit()
        db.refresh(gig)
        return gig


def update_gig(
    gig_id: int,
    client_id: int,
    title: str,
    description: str,
    genre: str,
    city: str,
    start_time: Optional[datetime.time],
    end_time: Optional[datetime.time],
    budget: float,
    requirements: str,
    duration_hours: Optional[float],
) -> GigListing:
    with get_db() as db:
        gig = (
            db.query(GigListing)
            .filter(
                GigListing.id == gig_id,
                GigListing.client_id == client_id,
                GigListing.status == GigStatus.OPEN,
            )
            .first()
        )
        if not gig:
            raise ValueError("Gig not found or cannot be edited in its current state.")
        if budget <= 0:
            raise ValueError("Budget must be greater than zero.")

        gig.title = title.strip()
        gig.description = description.strip() if description else None
        gig.genre = genre
        gig.city = city.strip()
        gig.start_time = start_time
        gig.end_time = end_time
        gig.budget = budget
        gig.requirements = requirements.strip() if requirements else None
        gig.duration_hours = duration_hours

        db.commit()
        db.refresh(gig)
        return gig


def cancel_gig(gig_id: int, client_id: int) -> GigListing:
    with get_db() as db:
        gig = (
            db.query(GigListing)
            .filter(
                GigListing.id == gig_id,
                GigListing.client_id == client_id,
                GigListing.status.in_([GigStatus.OPEN]),
            )
            .first()
        )
        if not gig:
            raise ValueError(
                "Gig not found, already booked, or cannot be cancelled."
            )
        gig.status = GigStatus.CANCELLED
        db.commit()
        db.refresh(gig)
        return gig


def complete_gig(gig_id: int, client_id: int) -> GigListing:
    with get_db() as db:
        gig = (
            db.query(GigListing)
            .filter(
                GigListing.id == gig_id,
                GigListing.client_id == client_id,
                GigListing.status == GigStatus.BOOKED,
            )
            .first()
        )
        if not gig:
            raise ValueError("Gig not found or not in a Booked state.")

        gig.status = GigStatus.COMPLETED

        if gig.booking:
            from models import BookingStatus
            gig.booking.status = BookingStatus.COMPLETED

        db.commit()
        db.refresh(gig)
        return gig


def get_client_gigs(client_id: int) -> list[GigListing]:
    with get_db() as db:
        return (
            db.query(GigListing)
            .filter(GigListing.client_id == client_id)
            .order_by(GigListing.performance_date.desc())
            .all()
        )


def get_gig_by_id(gig_id: int) -> GigListing | None:
    with get_db() as db:
        return db.query(GigListing).filter(GigListing.id == gig_id).first()
