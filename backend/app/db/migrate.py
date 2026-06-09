"""Lightweight SQLite schema upgrades for local dev (create_all does not ALTER)."""
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from app.core.config import settings


def apply_sqlite_migrations(engine: Engine) -> None:
    if not settings.database_url.startswith("sqlite"):
        return

    insp = inspect(engine)
    if "model_graphs" not in insp.get_table_names():
        return

    cols = {c["name"] for c in insp.get_columns("model_graphs")}
    statements: list[str] = []
    if "artifact_key" not in cols:
        statements.append(
            "ALTER TABLE model_graphs ADD COLUMN artifact_key VARCHAR(512)"
        )
    if "artifact_backend" not in cols:
        statements.append(
            "ALTER TABLE model_graphs ADD COLUMN artifact_backend VARCHAR(32)"
        )

    if not statements:
        return

    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
