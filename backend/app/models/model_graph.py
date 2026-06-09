"""Imported ONNX model graph metadata."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ModelGraph(Base):
    __tablename__ = "model_graphs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    run_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("runs.id", ondelete="SET NULL"), index=True, nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    graph_json: Mapped[str] = mapped_column(Text, nullable=False)
    opset_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    artifact_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    artifact_backend: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    run = relationship("Run", back_populates="model_graphs")
