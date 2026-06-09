"""Internal training state ingest and query (M3.2–M3.5)."""
import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_run_or_404
from app.db.session import get_db
from app.models.internal_metric import InternalMetric
from app.schemas.internal import (
    InternalBatchCreate,
    InternalKind,
    InternalMetricList,
    InternalMetricRead,
)

router = APIRouter(prefix="/runs/{run_id}/metrics/internal", tags=["internal"])


def _to_read(row: InternalMetric) -> InternalMetricRead:
    return InternalMetricRead(
        id=row.id,
        run_id=row.run_id,
        kind=row.kind,  # type: ignore[arg-type]
        layer=row.layer,
        step=row.step,
        epoch=row.epoch,
        title=row.title,
        data=row.data,
        recorded_at=row.recorded_at,
    )


@router.post("", response_model=InternalMetricList, status_code=201)
def ingest_internal_metrics(
    run_id: str,
    body: InternalBatchCreate,
    db: Session = Depends(get_db),
) -> InternalMetricList:
    get_run_or_404(run_id, db)
    created: list[InternalMetric] = []
    for item in body.metrics:
        row = InternalMetric(
            run_id=run_id,
            kind=item.kind,
            layer=item.layer,
            step=item.step,
            epoch=item.epoch,
            title=item.title,
            data_json=json.dumps(item.data),
        )
        db.add(row)
        created.append(row)
    db.commit()
    for row in created:
        db.refresh(row)
    return InternalMetricList(items=[_to_read(r) for r in created], total=len(created))


@router.get("", response_model=InternalMetricList)
def list_internal_metrics(
    run_id: str,
    kind: InternalKind | None = Query(default=None),
    db: Session = Depends(get_db),
) -> InternalMetricList:
    get_run_or_404(run_id, db)
    q = db.query(InternalMetric).filter(InternalMetric.run_id == run_id)
    if kind is not None:
        q = q.filter(InternalMetric.kind == kind)
    rows = q.order_by(InternalMetric.id).all()
    return InternalMetricList(items=[_to_read(r) for r in rows], total=len(rows))
