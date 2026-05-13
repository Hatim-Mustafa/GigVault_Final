from database import get_db
from queries.dashboard_queries import (
    get_client_dashboard_stats,
    get_musician_dashboard_stats,
)


def get_client_analytics(client_id: int) -> dict:
    with get_db() as db:
        return get_client_dashboard_stats(db, client_id)


def get_musician_analytics(band_id: int | None) -> dict:
    with get_db() as db:
        return get_musician_dashboard_stats(db, band_id)
