from sqlalchemy.orm import Session

from models import BookingContract, BookingStatus, GigListing, User


def get_active_bookings_for_client(db: Session, client_id: int) -> list:
    return (
        db.query(BookingContract, GigListing, User)
        .join(GigListing, BookingContract.gig_id == GigListing.id)
        .join(User, BookingContract.musician_id == User.id)
        .filter(
            BookingContract.client_id == client_id,
            BookingContract.status == BookingStatus.ACTIVE,
        )
        .order_by(GigListing.performance_date.asc())
        .all()
    )


def get_all_bookings_for_client(db: Session, client_id: int) -> list:
    return (
        db.query(BookingContract, GigListing, User)
        .join(GigListing, BookingContract.gig_id == GigListing.id)
        .join(User, BookingContract.musician_id == User.id)
        .filter(BookingContract.client_id == client_id)
        .order_by(GigListing.performance_date.desc())
        .all()
    )


def get_all_bookings_for_musician(db: Session, musician_id: int) -> list:
    return (
        db.query(BookingContract, GigListing, User)
        .join(GigListing, BookingContract.gig_id == GigListing.id)
        .join(User, BookingContract.client_id == User.id)
        .filter(BookingContract.musician_id == musician_id)
        .order_by(GigListing.performance_date.desc())
        .all()
    )
