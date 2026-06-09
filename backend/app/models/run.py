"""Training run metadata."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="running")
    params_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    scalar_metrics = relationship(
        "ScalarMetric", back_populates="run", cascade="all, delete-orphan"
    )
    histogram_metrics = relationship(
        "HistogramMetric", back_populates="run", cascade="all, delete-orphan"
    )
    model_graphs = relationship(
        "ModelGraph", back_populates="run", cascade="all, delete-orphan"
    )
    profile_events = relationship(
        "ProfileEvent", back_populates="run", cascade="all, delete-orphan"
    )
    classical_charts = relationship(
        "ClassicalChart", back_populates="run", cascade="all, delete-orphan"
    )
    internal_metrics = relationship(
        "InternalMetric", back_populates="run", cascade="all, delete-orphan"
    )
    xai_attributions = relationship(
        "XaiAttribution", back_populates="run", cascade="all, delete-orphan"
    )
