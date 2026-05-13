import streamlit as st
from sqlalchemy.orm import joinedload

from database import get_db
from models import Band, BandMember, MusicianProfile, User


def get_musician_bands(user_id: int) -> list[Band]:
    with get_db() as db:
        return (
            db.query(Band)
            .options(joinedload(Band.leader))
            .join(BandMember, BandMember.band_id == Band.id)
            .filter(BandMember.user_id == user_id)
            .order_by(Band.created_at.desc(), Band.id.desc())
            .all()
        )


def get_band_by_id(band_id: int) -> Band | None:
    with get_db() as db:
        return (
            db.query(Band)
            .options(joinedload(Band.leader))
            .filter(Band.id == band_id)
            .first()
        )


def get_band_members(band_id: int) -> list[User]:
    with get_db() as db:
        return (
            db.query(User)
            .join(BandMember, BandMember.user_id == User.id)
            .filter(BandMember.band_id == band_id)
            .order_by(BandMember.joined_at.asc(), User.username.asc())
            .all()
        )


def get_band_member_count(band_id: int) -> int:
    with get_db() as db:
        return (
            db.query(BandMember)
            .filter(BandMember.band_id == band_id)
            .count()
        )


def get_active_band_id(user_id: int) -> int | None:
    selected_band_id = st.session_state.get("active_band_id")
    if selected_band_id:
        with get_db() as db:
            membership = (
                db.query(BandMember)
                .filter(
                    BandMember.user_id == user_id,
                    BandMember.band_id == selected_band_id,
                )
                .first()
            )
            if membership:
                return selected_band_id

    bands = get_musician_bands(user_id)
    if bands:
        st.session_state["active_band_id"] = bands[0].id
        return bands[0].id
    return None


def set_active_band_id(user_id: int, band_id: int) -> int:
    with get_db() as db:
        membership = (
            db.query(BandMember)
            .filter(
                BandMember.user_id == user_id,
                BandMember.band_id == band_id,
            )
            .first()
        )
        if not membership:
            raise ValueError("You are not a member of that band.")

    st.session_state["active_band_id"] = band_id
    return band_id


def create_band(user_id: int, name: str, genre: str = "", city: str = "", bio: str = "") -> Band:
    name = name.strip()
    if not name:
        raise ValueError("Band name is required.")

    with get_db() as db:
        band = Band(
            leader_id=user_id,
            name=name,
            genre=genre.strip() or None,
            city=city.strip() or None,
            bio=bio.strip() or None,
        )
        db.add(band)
        db.flush()
        db.add(BandMember(band_id=band.id, user_id=user_id, role_in_band="Leader"))
        db.commit()
        db.refresh(band)
        return band


def join_band(user_id: int, band_id: int) -> Band:
    with get_db() as db:
        band = db.query(Band).filter(Band.id == band_id).first()
        if not band:
            raise ValueError("Band not found.")

        musician_profile = (
            db.query(MusicianProfile)
            .filter(MusicianProfile.user_id == user_id)
            .first()
        )
        if not musician_profile or not musician_profile.instruments or not musician_profile.instruments.strip():
            raise ValueError("Set your instruments in your musician profile before joining a band.")

        instrument = musician_profile.instruments.split(",")[0].strip()
        if not instrument:
            raise ValueError("Set your instruments in your musician profile before joining a band.")

        existing = (
            db.query(BandMember)
            .filter(
                BandMember.band_id == band_id,
                BandMember.user_id == user_id,
            )
            .first()
        )
        if existing:
            return band

        db.add(BandMember(band_id=band_id, user_id=user_id, role_in_band=instrument))
        db.commit()
        db.refresh(band)
        return band
