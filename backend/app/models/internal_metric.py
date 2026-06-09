"""Training internal state — activation, gradient, embedding, hidden state (M3.2–M3.5)."""
import json
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

KINDS = frozenset({"activation_map", "gradient_flow", "embedding", "hidden_state"})


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class InternalMetric(Base):
    __tablename__ = "internal_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("runs.id", ondelete="CASCADE"), index=True
    )
    kind: Mapped[str] = mapped_column(String(32), index=True)
    layer: Mapped[str | None] = mapped_column(String(128), nullable=True)
    step: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    epoch: Mapped[int | None] = mapped_column(Integer, nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    data_json: Mapped[str] = mapped_column(Text, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    run = relationship("Run", back_populates="internal_metrics")

    @property
    def data(self) -> dict:
        return json.loads(self.data_json)
