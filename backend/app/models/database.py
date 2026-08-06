"""SQLAlchemy engine/session setup. SQLite for the hackathon build — the
ORM layer above this (models/schemas/services) is unchanged if this is
later pointed at Postgres via DATABASE_URL; that's the whole point of
using SQLAlchemy instead of raw sqlite3 calls."""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables if they don't exist. Fine for a hackathon build;
    swap for Alembic migrations before any real production use."""
    from app.models import models  # noqa: F401 ensure models are registered

    Base.metadata.create_all(bind=engine)
