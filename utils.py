import datetime
from typing import Any, Optional


MUSIC_GENRES_FILTER = [
    "All",
    "Rock",
    "Jazz",
    "Pop",
    "Classical",
    "Hip-Hop",
    "R&B",
    "Electronic",
    "Country",
    "Folk",
    "Blues",
    "Metal",
    "Indie",
    "Soul",
    "Reggae",
    "Latin",
    "World",
    "Gospel",
    "Alternative",
    "Other",
]

MUSIC_GENRES_SELECT = [g for g in MUSIC_GENRES_FILTER if g != "All"]

VENUE_TYPES = [
    "Bar",
    "Club",
    "Concert Hall",
    "Outdoor Festival",
    "Restaurant",
    "Hotel",
    "Theater",
    "Private Event",
    "Corporate",
    "Other",
]

STATUS_COLORS = {
    "Open": "#16a34a",
    "Booked": "#2563eb",
    "Completed": "#6b7280",
    "Cancelled": "#dc2626",
    "Pending": "#d97706",
    "Paid": "#16a34a",
    "Overdue": "#dc2626",
    "Active": "#7c3aed",
    "Accepted": "#16a34a",
    "Rejected": "#dc2626",
    "Withdrawn": "#6b7280",
}


def format_currency(amount: Any) -> str:
    if amount is None:
        return "$0.00"
    try:
        return f"${float(amount):,.2f}"
    except (TypeError, ValueError):
        return "$0.00"


def format_date(date_obj: Any) -> str:
    if date_obj is None:
        return "N/A"
    if isinstance(date_obj, datetime.datetime):
        return date_obj.strftime("%b %d, %Y")
    if isinstance(date_obj, datetime.date):
        return date_obj.strftime("%b %d, %Y")
    return str(date_obj)


def format_datetime(dt_obj: Any) -> str:
    if dt_obj is None:
        return "N/A"
    if isinstance(dt_obj, datetime.datetime):
        return dt_obj.strftime("%b %d, %Y %I:%M %p")
    return str(dt_obj)


def format_time(t: Any) -> str:
    if t is None:
        return ""
    if isinstance(t, datetime.time):
        return t.strftime("%I:%M %p")
    return str(t)


def days_until(date_obj: Any) -> Optional[int]:
    if date_obj is None:
        return None
    today = datetime.date.today()
    if isinstance(date_obj, datetime.datetime):
        date_obj = date_obj.date()
    return (date_obj - today).days


def is_past(date_obj: Any) -> bool:
    if date_obj is None:
        return False
    today = datetime.date.today()
    if isinstance(date_obj, datetime.datetime):
        date_obj = date_obj.date()
    return date_obj < today


def truncate_text(text: str, max_len: int = 120) -> str:
    if not text:
        return ""
    return text if len(text) <= max_len else text[:max_len] + "..."


def status_badge_html(status: str) -> str:
    color = STATUS_COLORS.get(status, "#6b7280")
    return (
        f'<span style="background:{color};color:white;padding:3px 12px;'
        f'border-radius:20px;font-size:12px;font-weight:600;">{status}</span>'
    )


def role_badge_html(role: str) -> str:
    color = "#7c3aed" if role == "Musician" else "#0891b2"
    label = "🎵 Musician" if role == "Musician" else "🏛 Venue Owner"
    return (
        f'<span style="background:{color};color:white;padding:3px 14px;'
        f'border-radius:20px;font-size:13px;font-weight:700;">{label}</span>'
    )


def empty_state(message: str, icon: str = "🎵") -> str:
    return f"""
    <div style="text-align:center;padding:3rem 1rem;color:#9ca3af;">
        <div style="font-size:3rem;margin-bottom:0.5rem;">{icon}</div>
        <p style="font-size:1rem;">{message}</p>
    </div>
    """
