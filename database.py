import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)

_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        init_db()
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        init_db()
    return _SessionLocal


def init_db():
    global _engine, _SessionLocal
    from config import get_database_url, is_postgresql
    from models import Base

    url = get_database_url()

    if is_postgresql():
        _engine = create_engine(
            url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False,
        )
    else:
        _engine = create_engine(
            url,
            connect_args={"check_same_thread": False},
            echo=False,
        )

        @event.listens_for(_engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    _SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        bind=_engine,
    )

    Base.metadata.create_all(bind=_engine)

    if is_postgresql():
        _create_postgresql_partial_index(_engine)

    logger.info("Database initialized with URL: %s", url[:60])
    return _engine


def _create_postgresql_partial_index(engine):
    ddl = text(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ix_uq_client_date_active
        ON gig_listings (client_id, performance_date)
        WHERE status != 'Cancelled'
        """
    )
    with engine.connect() as conn:
        try:
            conn.execute(ddl)
            conn.commit()
        except Exception:
            conn.rollback()


@contextmanager
def get_db() -> Generator[Session, None, None]:
    factory = get_session_factory()
    db: Session = factory()
    try:
        yield db
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error("DB transaction rolled back: %s", exc)
        raise
    finally:
        db.close()
