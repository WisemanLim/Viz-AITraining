"""Classical ML diagnostic charts — learning curve, ROC, etc. (M1.4)."""
import json
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

CHART_TYPES = frozenset(
    {"learning_curve", "roc", "confusion_matrix", "feature_importance"}
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ClassicalChart(Base):
    __tablename__ = "classical_charts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("runs.id", ondelete="CASCADE"), index=True
    )
    chart_type: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    data_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    run = relationship("Run", back_populates="classical_charts")

    @property
    def data(self) -> dict:
        return json.loads(self.data_json)
