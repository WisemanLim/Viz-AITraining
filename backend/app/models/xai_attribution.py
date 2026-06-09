"""Explainability attributions — SHAP/LIME (M4)."""
import json
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

METHODS = frozenset({"shap", "lime"})
SCOPES = frozenset({"local", "global", "temporal"})


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class XaiAttribution(Base):
    __tablename__ = "xai_attributions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("runs.id", ondelete="CASCADE"), index=True
    )
    method: Mapped[str] = mapped_column(String(16), index=True)
    scope: Mapped[str] = mapped_column(String(16), index=True)
    step: Mapped[int | None] = mapped_column(Integer, nullable=True)
    epoch: Mapped[int | None] = mapped_column(Integer, nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    data_json: Mapped[str] = mapped_column(Text, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    run = relationship("Run", back_populates="xai_attributions")

    @property
    def data(self) -> dict:
        return json.loads(self.data_json)
