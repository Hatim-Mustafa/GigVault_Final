import datetime

from database import get_db
from models import Application, ApplicationStatus, AvailabilityCalendar, GigListing, GigStatus


def apply_to_gig(
    musician_id: int,
    gig_id: int,
    message: str,
) -> Application:
    with get_db() as db:
        gig = (
            db.query(GigListing)
            .filter(
                GigListing.id == gig_id,
                GigListing.status == GigStatus.OPEN,
            )
            .first()
        )
        if not gig:
            raise ValueError("This gig is no longer available.")

        if gig.performance_date < datetime.date.today():
            raise ValueError("Cannot apply to a gig with a past performance date.")

        duplicate = (
            db.query(Application)
            .filter(
                Application.gig_id == gig_id,
                Application.band_id == musician_id,
                Application.status != ApplicationStatus.WITHDRAWN,
            )
            .first()
        )
        if duplicate:
            raise ValueError("You have already applied to this gig.")

        busy = (
            db.query(AvailabilityCalendar)
            .filter(
                AvailabilityCalendar.musician_id == musician_id,
                AvailabilityCalendar.date == gig.performance_date,
            )
            .first()
        )
        if busy:
            raise ValueError(
                f"You already have a confirmed booking on {gig.performance_date.strftime('%b %d, %Y')}."
            )

        app = Application(
            gig_id=gig_id,
            band_id=musician_id,
            message=message.strip() if message else None,
            status=ApplicationStatus.PENDING,
        )
        db.add(app)
        db.commit()
        db.refresh(app)
        return app


def withdraw_application(application_id: int, musician_id: int) -> Application:
    with get_db() as db:
        app = (
            db.query(Application)
            .filter(
                Application.id == application_id,
                Application.band_id == musician_id,
                Application.status == ApplicationStatus.PENDING,
            )
            .first()
        )
        if not app:
            raise ValueError("Application not found or cannot be withdrawn.")
        app.status = ApplicationStatus.WITHDRAWN
        db.commit()
        db.refresh(app)
        return app


def get_musician_applications(musician_id: int) -> list[Application]:
    with get_db() as db:
        return (
            db.query(Application)
            .join(Application.gig)
            .filter(Application.band_id == musician_id)
            .order_by(Application.applied_at.desc())
            .all()
        )


def get_gig_applications(gig_id: int, client_id: int) -> list[Application]:
    with get_db() as db:
        return (
            db.query(Application)
            .join(Application.gig)
            .filter(
                Application.gig_id == gig_id,
                GigListing.client_id == client_id,
                Application.status == ApplicationStatus.PENDING,
            )
            .order_by(Application.applied_at.asc())
            .all()
        )


def get_all_client_pending_applications(client_id: int) -> list[Application]:
    with get_db() as db:
        return (
            db.query(Application)
            .join(Application.gig)
            .filter(
                GigListing.client_id == client_id,
                Application.status == ApplicationStatus.PENDING,
            )
            .order_by(Application.applied_at.asc())
            .all()
        )
