"""XAI attribution ingest and query (M4)."""
import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_run_or_404
from app.db.session import get_db
from app.models.xai_attribution import XaiAttribution
from app.schemas.xai import (
    XaiAttributionList,
    XaiAttributionRead,
    XaiBatchCreate,
    XaiMethod,
    XaiScope,
)

router = APIRouter(prefix="/runs/{run_id}/metrics/xai", tags=["xai"])


def _to_read(row: XaiAttribution) -> XaiAttributionRead:
    return XaiAttributionRead(
        id=row.id,
        run_id=row.run_id,
        method=row.method,  # type: ignore[arg-type]
        scope=row.scope,  # type: ignore[arg-type]
        step=row.step,
        epoch=row.epoch,
        title=row.title,
        data=row.data,
        recorded_at=row.recorded_at,
    )


@router.post("", response_model=XaiAttributionList, status_code=201)
def ingest_xai_attributions(
    run_id: str,
    body: XaiBatchCreate,
    db: Session = Depends(get_db),
) -> XaiAttributionList:
    get_run_or_404(run_id, db)
    created: list[XaiAttribution] = []
    for item in body.attributions:
        row = XaiAttribution(
            run_id=run_id,
            method=item.method,
            scope=item.scope,
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
    return XaiAttributionList(items=[_to_read(r) for r in created], total=len(created))


@router.get("", response_model=XaiAttributionList)
def list_xai_attributions(
    run_id: str,
    method: XaiMethod | None = Query(default=None),
    scope: XaiScope | None = Query(default=None),
    db: Session = Depends(get_db),
) -> XaiAttributionList:
    get_run_or_404(run_id, db)
    q = db.query(XaiAttribution).filter(XaiAttribution.run_id == run_id)
    if method is not None:
        q = q.filter(XaiAttribution.method == method)
    if scope is not None:
        q = q.filter(XaiAttribution.scope == scope)
    rows = q.order_by(XaiAttribution.id).all()
    return XaiAttributionList(items=[_to_read(r) for r in rows], total=len(rows))
