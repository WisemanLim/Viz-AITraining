"""Scalar metric ingest and query."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_run_or_404
from app.db.session import get_db
from app.models.scalar_metric import ScalarMetric
from app.schemas.metric import ScalarBatchCreate, ScalarList, ScalarPointRead
from app.services.metrics_hub import metrics_hub

router = APIRouter(prefix="/runs/{run_id}/metrics/scalars", tags=["metrics"])


@router.post("", response_model=ScalarList, status_code=201)
async def ingest_scalars(
    run_id: str,
    body: ScalarBatchCreate,
    db: Session = Depends(get_db),
) -> ScalarList:
    get_run_or_404(run_id, db)
    created: list[ScalarMetric] = []
    for point in body.metrics:
        row = ScalarMetric(
            run_id=run_id,
            tag=point.tag,
            value=point.value,
            step=point.step,
        )
        db.add(row)
        created.append(row)
    db.commit()
    for row in created:
        db.refresh(row)
    items = [ScalarPointRead.model_validate(r) for r in created]
    await metrics_hub.broadcast(
        run_id,
        {
            "type": "scalars",
            "run_id": run_id,
            "metrics": [i.model_dump(mode="json") for i in items],
        },
    )
    return ScalarList(items=items, total=len(items))


@router.get("", response_model=ScalarList)
def list_scalars(
    run_id: str,
    tag: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> ScalarList:
    get_run_or_404(run_id, db)
    q = db.query(ScalarMetric).filter(ScalarMetric.run_id == run_id)
    if tag:
        q = q.filter(ScalarMetric.tag == tag)
    rows = q.order_by(ScalarMetric.step.nulls_last(), ScalarMetric.id).all()
    items = [ScalarPointRead.model_validate(r) for r in rows]
    return ScalarList(items=items, total=len(items))
