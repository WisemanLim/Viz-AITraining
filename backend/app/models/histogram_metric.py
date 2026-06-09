"""Weight histogram snapshots (TensorBoard-compatible subset)."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class HistogramMetric(Base):
    __tablename__ = "histogram_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("runs.id", ondelete="CASCADE"), index=True
    )
    tag: Mapped[str] = mapped_column(String(255), index=True)
    step: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bin_edges_json: Mapped[str] = mapped_column(Text)
    counts_json: Mapped[str] = mapped_column(Text)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    run = relationship("Run", back_populates="histogram_metrics")
