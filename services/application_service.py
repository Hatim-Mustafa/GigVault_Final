import datetime

from sqlalchemy.orm import joinedload

from database import get_db
from models import Application, ApplicationStatus, AvailabilityCalendar, Band, BandMember, GigListing, GigStatus, User


def apply_to_gig(
    user_id: int,
    band_id: int,
    gig_id: int,
    message: str,
) -> Application:
    with get_db() as db:
        band_membership = (
            db.query(BandMember)
            .join(Band, BandMember.band_id == Band.id)
            .filter(
                BandMember.user_id == user_id,
                BandMember.band_id == band_id,
            )
            .first()
        )
        if not band_membership:
            raise ValueError("You can only apply with a band you belong to.")

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

        member_ids = [row[0] for row in db.query(BandMember.user_id).filter(BandMember.band_id == band_id).all()]
        if not member_ids:
            raise ValueError("This band has no members yet.")

        busy = (
            db.query(AvailabilityCalendar)
            .filter(
                AvailabilityCalendar.musician_id.in_(member_ids),
                AvailabilityCalendar.date == gig.performance_date,
            )
            .first()
        )
        if busy:
            raise ValueError(
                f"Someone in this band is already booked on {gig.performance_date.strftime('%b %d, %Y')}."
            )

        duplicate = (
            db.query(Application)
            .filter(
                Application.gig_id == gig_id,
                Application.band_id == band_id,
                Application.status != ApplicationStatus.WITHDRAWN,
            )
            .first()
        )
        if duplicate:
            raise ValueError("You have already applied to this gig.")

        app = Application(
            gig_id=gig_id,
            band_id=band_id,
            message=message.strip() if message else None,
            status=ApplicationStatus.PENDING,
        )
        db.add(app)
        db.commit()
        db.refresh(app)
        return app


def withdraw_application(application_id: int, user_id: int, band_id: int) -> Application:
    with get_db() as db:
        app = (
            db.query(Application)
            .filter(
                Application.id == application_id,
                Application.band_id == band_id,
                Application.status == ApplicationStatus.PENDING,
            )
            .first()
        )
        if not app:
            raise ValueError("Application not found or cannot be withdrawn.")

        membership = (
            db.query(BandMember)
            .filter(
                BandMember.user_id == user_id,
                BandMember.band_id == band_id,
            )
            .first()
        )
        if not membership:
            raise ValueError("You can only withdraw applications from your own band.")

        app.status = ApplicationStatus.WITHDRAWN
        db.commit()
        db.refresh(app)
        return app


def get_musician_applications(band_id: int) -> list[Application]:
    with get_db() as db:
        return (
            db.query(Application)
            .options(
                joinedload(Application.gig).joinedload(GigListing.booking),
                joinedload(Application.band).joinedload(Band.leader),
            )
            .join(Application.gig)
            .filter(Application.band_id == band_id)
            .order_by(Application.applied_at.desc())
            .all()
        )


def get_gig_applications(gig_id: int, client_id: int) -> list[Application]:
    with get_db() as db:
        return (
            db.query(Application)
            .options(
                joinedload(Application.gig).joinedload(GigListing.booking),
                joinedload(Application.band).joinedload(Band.leader),
            )
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
            .options(
                joinedload(Application.gig).joinedload(GigListing.booking),
                joinedload(Application.band).joinedload(Band.leader).joinedload(User.musician_profile),
            )
            .join(Application.gig)
            .filter(
                GigListing.client_id == client_id,
                Application.status == ApplicationStatus.PENDING,
            )
            .order_by(Application.applied_at.asc())
            .all()
        )
