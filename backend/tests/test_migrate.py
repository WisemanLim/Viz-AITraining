from sqlalchemy import inspect, text

from app.db.migrate import apply_sqlite_migrations
from app.db.session import Base, engine


def test_sqlite_adds_model_graph_artifact_columns() -> None:
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS model_graphs"))
        conn.execute(
            text(
                """
                CREATE TABLE model_graphs (
                    id VARCHAR(36) NOT NULL PRIMARY KEY,
                    run_id VARCHAR(36),
                    name VARCHAR(255) NOT NULL,
                    graph_json TEXT NOT NULL,
                    opset_version INTEGER,
                    created_at DATETIME NOT NULL
                )
                """
            )
        )

    apply_sqlite_migrations(engine)

    cols = {c["name"] for c in inspect(engine).get_columns("model_graphs")}
    assert "artifact_key" in cols
    assert "artifact_backend" in cols
