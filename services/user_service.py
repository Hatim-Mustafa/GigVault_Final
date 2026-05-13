from database import get_db
from models import ClientProfile, MusicianProfile, User


def get_user_by_id(user_id: int) -> User | None:
    with get_db() as db:
        return (
            db.query(User)
            .filter(User.id == user_id, User.is_active == True)
            .first()
        )


def get_client_profile(user_id: int) -> ClientProfile | None:
    with get_db() as db:
        return (
            db.query(ClientProfile)
            .filter(ClientProfile.user_id == user_id)
            .first()
        )


def get_musician_profile(user_id: int) -> MusicianProfile | None:
    with get_db() as db:
        return (
            db.query(MusicianProfile)
            .filter(MusicianProfile.user_id == user_id)
            .first()
        )


def update_client_profile(
    user_id: int,
    venue_name: str,
    venue_type: str,
    genre_specialization: str,
    city: str,
    address: str,
    capacity: int | None,
    description: str,
    website: str,
) -> ClientProfile:
    with get_db() as db:
        profile = db.query(ClientProfile).filter(ClientProfile.user_id == user_id).first()
        if not profile:
            profile = ClientProfile(user_id=user_id)
            db.add(profile)

        profile.venue_name = venue_name
        profile.venue_type = venue_type
        profile.genre_specialization = genre_specialization
        profile.city = city
        profile.address = address
        profile.capacity = capacity
        profile.description = description
        profile.website = website

        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.city = city

        db.commit()
        db.refresh(profile)
        return profile


def update_musician_profile(
    user_id: int,
    stage_name: str,
    genres: str,
    instruments: str,
    hourly_rate: float,
    years_experience: int,
    bio: str,
    soundcloud_url: str,
    spotify_url: str,
) -> MusicianProfile:
    with get_db() as db:
        profile = db.query(MusicianProfile).filter(MusicianProfile.user_id == user_id).first()
        if not profile:
            profile = MusicianProfile(user_id=user_id)
            db.add(profile)

        profile.stage_name = stage_name
        profile.genres = genres
        profile.instruments = instruments
        profile.hourly_rate = hourly_rate
        profile.years_experience = years_experience
        profile.soundcloud_url = soundcloud_url
        profile.spotify_url = spotify_url

        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.bio = bio

        db.commit()
        db.refresh(profile)
        return profile


def update_user_bio(user_id: int, bio: str) -> None:
    with get_db() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.bio = bio
            db.commit()
