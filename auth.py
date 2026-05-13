import logging
import streamlit as st
from passlib.context import CryptContext
from database import get_db
from models import ClientProfile, MusicianProfile, User, UserRole

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain[:72], hashed)
    except Exception:
        return False


def login(username: str, password: str) -> dict | None:
    if not username or not password:
        return None
    with get_db() as db:
        user = db.query(User).filter(User.username == username.strip(), User.is_active == True).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return {"user_id": user.id, "username": user.username, "email": user.email, "role": user.role}


def register(username: str, email: str, password: str, role: str, city: str = "") -> dict | None:
    username = username.strip()
    email = email.strip().lower()
    if not username or not email or not password or not role:
        return None

    # Map UI values ("client"/"musician") to Supabase CHECK constraint values
    db_role = UserRole.CLIENT.value if role == "client" else UserRole.MUSICIAN.value

    with get_db() as db:
        if db.query(User).filter((User.username == username) | (User.email == email)).first():
            return None

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role=db_role,
            first_name=username,
            last_name="",
            city=city,
            is_active=True,
        )
        db.add(user)
        db.flush()

        if role == "client":
            db.add(ClientProfile(user_id=user.id, venue_name=f"{username}'s Venue", city=city or "Unknown", genre_specialization=""))
        else:
            db.add(MusicianProfile(user_id=user.id, stage_name=username, genres="", instruments=""))

        db.commit()
        db.refresh(user)
        return {"user_id": user.id, "username": user.username, "email": user.email, "role": user.role}


def set_session(user_data: dict) -> None:
    st.session_state["authenticated"] = True
    st.session_state["user_id"]   = user_data["user_id"]
    st.session_state["username"]  = user_data["username"]
    st.session_state["email"]     = user_data["email"]
    st.session_state["role"]      = user_data["role"]
    if user_data["role"] == UserRole.MUSICIAN.value:
        st.session_state["active_band_id"] = _get_default_band_id(user_data["user_id"])


def clear_session() -> None:
    for key in ["authenticated", "user_id", "username", "email", "role", "active_band_id"]:
        st.session_state.pop(key, None)


def is_authenticated() -> bool:
    return bool(st.session_state.get("authenticated", False))

def get_current_user_id() -> int | None:
    return st.session_state.get("user_id")

def get_current_role() -> str | None:
    return st.session_state.get("role")

def get_current_username() -> str | None:
    return st.session_state.get("username")


def _get_default_band_id(user_id: int) -> int | None:
    from models import BandMember

    with get_db() as db:
        membership = (
            db.query(BandMember)
            .filter(BandMember.user_id == user_id)
            .order_by(BandMember.joined_at.asc(), BandMember.id.asc())
            .first()
        )
        return membership.band_id if membership else None
