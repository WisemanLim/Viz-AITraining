"""SQLAlchemy engine and session factory."""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def _engine_kwargs() -> dict:
    url = settings.database_url
    if url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {}


engine = create_engine(settings.database_url, **_engine_kwargs())
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db() -> None:
    from app.models import (  # noqa: F401
        classical_chart,
        histogram_metric,
        internal_metric,
        model_graph,
        profile_event,
        run,
        scalar_metric,
        xai_attribution,
    )

    Base.metadata.create_all(bind=engine)
    from app.db.migrate import apply_sqlite_migrations

    apply_sqlite_migrations(engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
