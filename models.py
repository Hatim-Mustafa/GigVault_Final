import enum
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey,
    Index, Integer, Numeric, String, Text, Time, UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class UserRole(str, enum.Enum):
    CLIENT = "Venue_Owner"
    MUSICIAN = "Musician"


class GigStatus(str, enum.Enum):
    OPEN = "Open"
    BOOKED = "Filled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class ApplicationStatus(str, enum.Enum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"


class BookingStatus(str, enum.Enum):
    ACTIVE = "Active"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class PaymentStatus(str, enum.Enum):
    PENDING = "Pending"
    PAID = "Completed"
    FAILED = "Failed"
    REFUNDED = "Refunded"


class User(Base):
    __tablename__ = "users"

    id = Column("user_id", Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False, default="")
    last_name = Column(String(100), nullable=False, default="")
    phone_number = Column(String(15))
    role = Column(String(20), nullable=False)
    profile_picture_url = Column(Text)
    bio = Column(Text)
    city = Column(String(100))
    zip_code = Column(String(10))
    created_at = Column("account_created_at", DateTime, server_default=func.now())
    updated_at = Column("last_updated", DateTime, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True, nullable=False)

    client_profile    = relationship("ClientProfile",   back_populates="user", uselist=False, cascade="all, delete-orphan")
    musician_profile  = relationship("MusicianProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    gig_listings      = relationship("GigListing",      foreign_keys="GigListing.client_id",       back_populates="client",   cascade="all, delete-orphan")
    client_bookings   = relationship("BookingContract", foreign_keys="BookingContract.client_id",  back_populates="client")
    availability_slots= relationship("AvailabilityCalendar", back_populates="musician", cascade="all, delete-orphan")
    client_payments   = relationship("Payment", foreign_keys="Payment.client_id",   back_populates="client")
    bands_led         = relationship("Band",    foreign_keys="Band.leader_id",       back_populates="leader")
    band_memberships  = relationship("BandMember", foreign_keys="BandMember.user_id",back_populates="user", cascade="all, delete-orphan")
    setlists          = relationship("Setlist", back_populates="musician", cascade="all, delete-orphan")


class ClientProfile(Base):
    __tablename__ = "client_profiles"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    venue_name  = Column(String(200), nullable=False, default="")
    venue_type  = Column(String(100), default="Bar")
    genre_specialization = Column(String(300), default="")
    city        = Column(String(100), nullable=False, default="")
    address     = Column(String(300))
    capacity    = Column(Integer)
    description = Column(Text)
    website     = Column(String(300))
    created_at  = Column(DateTime, server_default=func.now())
    updated_at  = Column(DateTime, onupdate=func.now())
    user = relationship("User", back_populates="client_profile")


class MusicianProfile(Base):
    __tablename__ = "musician_profiles"
    id               = Column(Integer, primary_key=True, autoincrement=True)
    user_id          = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    stage_name       = Column(String(200), default="")
    genres           = Column(String(300), default="")
    instruments      = Column(String(300), default="")
    hourly_rate      = Column(Numeric(10, 2), default=0)
    years_experience = Column(Integer, default=0)
    soundcloud_url   = Column(String(300))
    spotify_url      = Column(String(300))
    created_at       = Column(DateTime, server_default=func.now())
    updated_at       = Column(DateTime, onupdate=func.now())
    user = relationship("User", back_populates="musician_profile")


class Band(Base):
    __tablename__ = "bands"
    id         = Column("band_id", Integer, primary_key=True, autoincrement=True)
    leader_id  = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    name       = Column("band_name", String(150), nullable=False)
    genre      = Column(String(100))
    bio        = Column(Text)
    city       = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
    leader  = relationship("User",       foreign_keys=[leader_id], back_populates="bands_led")
    members = relationship("BandMember", back_populates="band", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="band", cascade="all, delete-orphan")
    bookings = relationship("BookingContract", back_populates="band", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="band", cascade="all, delete-orphan")


class BandMember(Base):
    __tablename__ = "band_members"
    id           = Column("member_id", Integer, primary_key=True, autoincrement=True)
    band_id      = Column(Integer, ForeignKey("bands.band_id",  ondelete="CASCADE"), nullable=False)
    user_id      = Column(Integer, ForeignKey("users.user_id",  ondelete="CASCADE"), nullable=False)
    role_in_band = Column(String(50))
    instrument = Column(String(50))
    joined_at    = Column("joined_date", DateTime, server_default=func.now())
    __table_args__ = (UniqueConstraint("band_id", "user_id", name="uq_band_member"),)
    band = relationship("Band", back_populates="members")
    user = relationship("User", back_populates="band_memberships")


class GigListing(Base):
    __tablename__ = "gig_listings"
    id               = Column("gig_id",         Integer, primary_key=True, autoincrement=True)
    client_id        = Column("venue_owner_id",  Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    title            = Column("gig_title",       String(200), nullable=False)
    description      = Column(Text)
    genre            = Column("genre_required",  String(100), nullable=False)
    city             = Column("location_city",   String(100), nullable=False)
    performance_date = Column(Date, nullable=False)
    start_time = Column("performance_time", Time, nullable=False)
    venue_name = Column(String(150), nullable=False, default="")
    location_zip_code = Column(String(10))
    duration_hours = Column(Numeric(3, 1))
    budget = Column("offered_pay", Numeric(10, 2), nullable=False)
    payment_status = Column(String(20), default="Pending")
    status = Column("gig_status", String(20), default=GigStatus.OPEN.value, nullable=False)
    created_at       = Column(DateTime, server_default=func.now())
    updated_at       = Column("last_updated", DateTime, server_default=func.now(), onupdate=func.now())
    __table_args__ = (
        Index("ix_gig_client_date",      "venue_owner_id", "performance_date"),
        Index("ix_gig_city_genre_date",  "location_city",  "genre_required", "performance_date"),
        Index("ix_gig_status",           "gig_status"),
        Index("ix_gig_performance_date", "performance_date"),
    )
    client       = relationship("User",            foreign_keys=[client_id], back_populates="gig_listings")
    applications = relationship("Application",     back_populates="gig", cascade="all, delete-orphan")
    booking      = relationship("BookingContract", back_populates="gig", uselist=False)


class Application(Base):
    __tablename__ = "applications"
    id        = Column("application_id",   Integer, primary_key=True, autoincrement=True)
    gig_id    = Column(Integer, ForeignKey("gig_listings.gig_id", ondelete="CASCADE"), nullable=False)
    band_id   = Column(Integer, ForeignKey("bands.band_id", ondelete="CASCADE"), nullable=False)
    message   = Column("cover_letter", Text)
    status    = Column("application_status", String(20), default=ApplicationStatus.PENDING.value, nullable=False)
    applied_at    = Column("application_date",   DateTime, server_default=func.now())
    updated_at    = Column("last_updated",        DateTime, server_default=func.now(), onupdate=func.now())
    __table_args__ = (
        UniqueConstraint("gig_id", "band_id", name="uq_application_gig_musician"),
        Index("ix_application_musician_status", "band_id",  "application_status"),
        Index("ix_application_gig_status",      "gig_id",   "application_status"),
    )
    gig      = relationship("GigListing", back_populates="applications")
    band     = relationship("Band", foreign_keys=[band_id], back_populates="applications")


class BookingContract(Base):
    __tablename__ = "bookings_contracts"
    id            = Column("booking_id",     Integer, primary_key=True, autoincrement=True)
    gig_id        = Column(Integer, ForeignKey("gig_listings.gig_id",  ondelete="CASCADE"), unique=True, nullable=False)
    client_id     = Column("venue_owner_id", Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    musician_id   = Column("band_id",        Integer, ForeignKey("bands.band_id", ondelete="CASCADE"), nullable=False)
    performance_date = Column(Date, nullable=False)
    performance_time = Column(Time, nullable=False)
    agreed_amount = Column("agreed_fee",     Numeric(10, 2), nullable=False)
    status        = Column("contract_status",String(20), default=BookingStatus.ACTIVE.value, nullable=False)
    booked_at     = Column("contract_date",  DateTime, server_default=func.now())
    notes         = Column("contract_terms", Text)
    __table_args__ = (
        Index("ix_booking_client",  "venue_owner_id"),
        Index("ix_booking_musician","band_id"),
        Index("ix_booking_status",  "contract_status"),
    )
    gig      = relationship("GigListing", back_populates="booking")
    client   = relationship("User", foreign_keys=[client_id],   back_populates="client_bookings")
    band     = relationship("Band", foreign_keys=[musician_id], back_populates="bookings")
    payment  = relationship("Payment", back_populates="booking", uselist=False, cascade="all, delete-orphan")


class AvailabilityCalendar(Base):
    __tablename__ = "availability_calendar"
    id          = Column("availability_id", Integer, primary_key=True, autoincrement=True)
    musician_id = Column("user_id", Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    date        = Column("busy_date", Date, nullable=False)
    __table_args__ = (
        UniqueConstraint("user_id", "busy_date", name="uq_availability_musician_date"),
        Index("ix_availability_musician_date", "user_id", "busy_date"),
    )
    musician = relationship("User", back_populates="availability_slots")


class Payment(Base):
    __tablename__ = "payments"
    id           = Column("payment_id",    Integer, primary_key=True, autoincrement=True)
    booking_id   = Column(Integer, ForeignKey("bookings_contracts.booking_id", ondelete="CASCADE"), nullable=False)
    client_id    = Column("venue_owner_id",Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    musician_id  = Column("band_id",       Integer, ForeignKey("bands.band_id", ondelete="CASCADE"), nullable=False)
    amount       = Column(Numeric(10, 2),  nullable=False)
    payment_type = Column(String(20), nullable=False, default="Final")
    status       = Column("payment_status",String(20), default=PaymentStatus.PENDING.value, nullable=False)
    paid_at      = Column("payment_date",  DateTime, nullable=True)
    notes        = Column(Text)
    created_at   = Column(DateTime, server_default=func.now())
    __table_args__ = (
        Index("ix_payment_client_status",   "venue_owner_id", "payment_status"),
        Index("ix_payment_musician_status", "band_id",         "payment_status"),
    )
    booking  = relationship("BookingContract", back_populates="payment")
    client   = relationship("User", foreign_keys=[client_id],   back_populates="client_payments")
    band     = relationship("Band", foreign_keys=[musician_id], back_populates="payments")


class ReviewDispute(Base):
    __tablename__ = "reviews_disputes"
    id          = Column("review_id",   Integer, primary_key=True, autoincrement=True)
    booking_id  = Column(Integer, ForeignKey("bookings_contracts.booking_id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    reviewee_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    rating      = Column(Integer)
    comment     = Column("review_text", Text)
    is_dispute  = Column(Boolean, default=False)
    created_at  = Column(DateTime, server_default=func.now())
    __table_args__ = (UniqueConstraint("booking_id", "reviewer_id", name="uq_review_booking_reviewer"),)


class Setlist(Base):
    __tablename__ = "setlists"
    id          = Column("setlist_id", Integer, primary_key=True, autoincrement=True)
    musician_id = Column("band_id",    Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    name        = Column("setlist_name", String(200), nullable=False)
    created_at  = Column(DateTime, server_default=func.now())
    musician = relationship("User",        back_populates="setlists")
    songs    = relationship("SetlistSong", back_populates="setlist", cascade="all, delete-orphan")


class SetlistSong(Base):
    __tablename__ = "setlist_songs"
    id               = Column("song_id",    Integer, primary_key=True, autoincrement=True)
    setlist_id       = Column(Integer, ForeignKey("setlists.setlist_id", ondelete="CASCADE"), nullable=False)
    title            = Column("song_title", String(200), nullable=False)
    artist           = Column("artist_name",String(150))
    duration_minutes = Column(Integer)
    order_index      = Column("song_order", Integer, default=0)
    setlist = relationship("Setlist", back_populates="songs")


class RecruitmentAd(Base):
    __tablename__ = "recruitment_ads"
    id                 = Column("recruitment_id",    Integer, primary_key=True, autoincrement=True)
    poster_id          = Column("posted_by_user_id", Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    title              = Column(String(200), nullable=False)
    description        = Column(Text)
    genre              = Column(String(100))
    city               = Column(String(100))
    instruments_needed = Column(String(255))
    is_active          = Column(Boolean, default=True)
    created_at         = Column(DateTime, server_default=func.now())
