import datetime

from config import PAYMENT_DUE_DAYS
from database import get_db
from sqlalchemy.orm import joinedload
from models import (
    Application,
    ApplicationStatus,
    AvailabilityCalendar,
    BandMember,
    BookingContract,
    BookingStatus,
    GigListing,
    GigStatus,
    Payment,
    PaymentStatus,
    Band,
)


def accept_application(application_id: int, client_id: int) -> BookingContract:
    with get_db() as db:
        app = (
            db.query(Application)
            .join(Application.gig)
            .filter(
                Application.id == application_id,
                Application.status == ApplicationStatus.PENDING,
                GigListing.client_id == client_id,
                GigListing.status == GigStatus.OPEN,
            )
            .first()
        )
        if not app:
            raise ValueError(
                "Application not found, already processed, or gig is no longer open."
            )

        gig = app.gig

        # Check if any band member is busy on that date (presence of a row means busy)
        band_member_ids = [row[0] for row in db.query(BandMember.user_id).filter(BandMember.band_id == app.band_id).all()]
        busy = (
            db.query(AvailabilityCalendar)
            .filter(
                AvailabilityCalendar.musician_id.in_(band_member_ids),
                AvailabilityCalendar.date == gig.performance_date,
            )
            .first()
        )
        if busy:
            raise ValueError(
                "Someone in this band is no longer available on the performance date."
            )

        app.status = ApplicationStatus.ACCEPTED

        db.query(Application).filter(
            Application.gig_id == gig.id,
            Application.id != application_id,
            Application.status == ApplicationStatus.PENDING,
        ).update({"status": ApplicationStatus.REJECTED.value}, synchronize_session=False)

        gig.status = GigStatus.BOOKED

        agreed = float(gig.budget)
        booking = BookingContract(
            gig_id=gig.id,
            client_id=client_id,
            musician_id=app.band_id,
            agreed_amount=agreed,
            status=BookingStatus.ACTIVE,
        )
        db.add(booking)
        db.flush()

        # Mark all band members as busy by inserting rows (presence = busy)
        for member_id in band_member_ids:
            db.add(
                AvailabilityCalendar(
                    musician_id=member_id,
                    date=gig.performance_date,
                )
            )

        payment = Payment(
            booking_id=booking.id,
            client_id=client_id,
            musician_id=app.band_id,
            amount=agreed,
            payment_type="Final",
            status=PaymentStatus.PENDING,
        )
        db.add(payment)
        db.commit()
        db.refresh(booking)
        return booking


def reject_application(application_id: int, client_id: int) -> Application:
    with get_db() as db:
        app = (
            db.query(Application)
            .join(Application.gig)
            .filter(
                Application.id == application_id,
                Application.status == ApplicationStatus.PENDING,
                GigListing.client_id == client_id,
            )
            .first()
        )
        if not app:
            raise ValueError("Application not found.")
        app.status = ApplicationStatus.REJECTED
        db.commit()
        db.refresh(app)
        return app


def cancel_booking(booking_id: int, client_id: int) -> BookingContract:
    with get_db() as db:
        booking = (
            db.query(BookingContract)
            .filter(
                BookingContract.id == booking_id,
                BookingContract.client_id == client_id,
                BookingContract.status == BookingStatus.ACTIVE,
            )
            .first()
        )
        if not booking:
            raise ValueError("Booking not found or already finalised.")

        booking.status = BookingStatus.CANCELLED
        booking.gig.status = GigStatus.CANCELLED

        # Remove the busy date record so the band is free again
        band_member_ids = [row[0] for row in db.query(BandMember.user_id).filter(BandMember.band_id == booking.musician_id).all()]
        avail_rows = (
            db.query(AvailabilityCalendar)
            .filter(
                AvailabilityCalendar.musician_id.in_(band_member_ids),
                AvailabilityCalendar.date == booking.gig.performance_date,
            )
            .all()
        )
        for avail in avail_rows:
            db.delete(avail)

        db.commit()
        db.refresh(booking)
        return booking


def complete_booking(booking_id: int, client_id: int) -> BookingContract:
    with get_db() as db:
        booking = (
            db.query(BookingContract)
            .filter(
                BookingContract.id == booking_id,
                BookingContract.client_id == client_id,
                BookingContract.status == BookingStatus.ACTIVE,
            )
            .first()
        )
        if not booking:
            raise ValueError("Booking not found.")
        booking.status = BookingStatus.COMPLETED
        booking.gig.status = GigStatus.COMPLETED
        db.commit()
        db.refresh(booking)
        return booking


def get_client_bookings(client_id: int) -> list[BookingContract]:
    with get_db() as db:
        return (
            db.query(BookingContract)
            .options(joinedload(BookingContract.band).joinedload(Band.leader))
            .join(BookingContract.gig)
            .filter(BookingContract.client_id == client_id)
            .order_by(GigListing.performance_date.desc())
            .all()
        )


def get_musician_bookings(band_id: int) -> list[BookingContract]:
    with get_db() as db:
        return (
            db.query(BookingContract)
            .options(joinedload(BookingContract.band).joinedload(Band.leader))
            .join(BookingContract.gig)
            .filter(BookingContract.musician_id == band_id)
            .order_by(GigListing.performance_date.desc())
            .all()
        )
