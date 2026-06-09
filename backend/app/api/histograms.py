"""Histogram metric ingest and query."""
import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_run_or_404
from app.db.session import get_db
from app.models.histogram_metric import HistogramMetric
from app.schemas.histogram import (
    HistogramBatchCreate,
    HistogramList,
    HistogramPointRead,
)

router = APIRouter(prefix="/runs/{run_id}/metrics/histograms", tags=["metrics"])


@router.post("", response_model=HistogramList, status_code=201)
def ingest_histograms(
    run_id: str,
    body: HistogramBatchCreate,
    db: Session = Depends(get_db),
) -> HistogramList:
    get_run_or_404(run_id, db)
    created: list[HistogramMetric] = []
    for point in body.histograms:
        row = HistogramMetric(
            run_id=run_id,
            tag=point.tag,
            step=point.step,
            bin_edges_json=json.dumps(point.bin_edges),
            counts_json=json.dumps(point.counts),
        )
        db.add(row)
        created.append(row)
    db.commit()
    for row in created:
        db.refresh(row)
    items = [HistogramPointRead.from_orm_row(r) for r in created]
    return HistogramList(items=items, total=len(items))


@router.get("", response_model=HistogramList)
def list_histograms(
    run_id: str,
    tag: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> HistogramList:
    get_run_or_404(run_id, db)
    q = db.query(HistogramMetric).filter(HistogramMetric.run_id == run_id)
    if tag:
        q = q.filter(HistogramMetric.tag == tag)
    rows = q.order_by(
        HistogramMetric.step.nulls_last(), HistogramMetric.id
    ).all()
    items = [HistogramPointRead.from_orm_row(r) for r in rows]
    return HistogramList(items=items, total=len(items))
