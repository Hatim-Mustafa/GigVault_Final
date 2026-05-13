from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from models import Band, BookingContract, BookingStatus, GigListing, User


def get_active_bookings_for_client(db: Session, client_id: int) -> list:
    return (
        db.query(BookingContract, GigListing, Band)
        .options(joinedload(Band.leader))
        .join(GigListing, BookingContract.gig_id == GigListing.id)
        .join(Band, BookingContract.musician_id == Band.id)
        .filter(
            BookingContract.client_id == client_id,
            BookingContract.status == BookingStatus.ACTIVE,
        )
        .order_by(GigListing.performance_date.asc())
        .all()
    )


def get_all_bookings_for_client(db: Session, client_id: int) -> list:
    return (
        db.query(BookingContract, GigListing, Band)
        .options(joinedload(Band.leader))
        .join(GigListing, BookingContract.gig_id == GigListing.id)
        .join(Band, BookingContract.musician_id == Band.id)
        .filter(BookingContract.client_id == client_id)
        .order_by(GigListing.performance_date.desc())
        .all()
    )


def get_all_bookings_for_musician(db: Session, band_id: int) -> list:
    return (
        db.query(BookingContract, GigListing, User)
        .options(joinedload(BookingContract.band).joinedload(Band.leader))
        .join(GigListing, BookingContract.gig_id == GigListing.id)
        .join(User, BookingContract.client_id == User.id)
        .filter(BookingContract.musician_id == band_id)
        .order_by(GigListing.performance_date.desc())
        .all()
    )
