import os
from dotenv import load_dotenv
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")


SUPABASE_DB_URL: str = os.getenv("SUPABASE_DB_URL", "")
DATABASE_URL: str = os.getenv("DATABASE_URL", "")
SECRET_KEY: str = os.getenv("SECRET_KEY", "gigvault-insecure-dev-key")
APP_ENV: str = os.getenv("APP_ENV", "development")
DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

PAYMENT_DUE_DAYS: int = 7

MUSIC_GENRES: list[str] = [
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

VENUE_TYPES: list[str] = [
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


def get_database_url() -> str:
    url = SUPABASE_DB_URL or DATABASE_URL
    if not url:
        sqlite_path = ROOT_DIR / "gigvault.db"
        return f"sqlite:///{sqlite_path.as_posix()}"
    return url


def is_postgresql() -> bool:
    url = get_database_url()
    return url.startswith("postgresql") or url.startswith("postgres")


def is_production() -> bool:
    return APP_ENV == "production"

MUSIC_GENRES_FILTER = MUSIC_GENRES
MUSIC_GENRES_SELECT = [genre for genre in MUSIC_GENRES if genre != "All"]
