"""Pytest fixtures — in-memory SQLite for API tests."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app
from app.models import classical_chart as classical_chart_model  # noqa: F401
from app.models import internal_metric as internal_metric_model  # noqa: F401
from app.models import xai_attribution as xai_attribution_model  # noqa: F401
from app.models import histogram_metric as histogram_metric_model  # noqa: F401
from app.models import model_graph as model_graph_model  # noqa: F401
from app.models import profile_event as profile_event_model  # noqa: F401
from app.models import run as run_model  # noqa: F401
from app.models import scalar_metric as scalar_metric_model  # noqa: F401

pytest_plugins = ["tests.fixtures_onnx"]


@pytest.fixture
def client(monkeypatch) -> TestClient:
    monkeypatch.setattr("app.db.session.init_db", lambda: None)
    monkeypatch.setattr("app.core.config.settings.redis_url", "")

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
