"""Training profile ingest and timeline (M1.3)."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_run_or_404
from app.db.session import get_db
from app.models.profile_event import ProfileEvent
from app.schemas.profile import (
    ProfileBatchCreate,
    ProfileList,
    ProfilePointRead,
    ProfileTimelineReport,
)
from app.services.profile_timeline import build_timeline_report

router = APIRouter(prefix="/runs/{run_id}/metrics/profile", tags=["profile"])


@router.post("", response_model=ProfileList, status_code=201)
def ingest_profile_events(
    run_id: str,
    body: ProfileBatchCreate,
    db: Session = Depends(get_db),
) -> ProfileList:
    get_run_or_404(run_id, db)
    created: list[ProfileEvent] = []
    for point in body.events:
        row = ProfileEvent(
            run_id=run_id,
            epoch=point.epoch,
            phase=point.phase,
            step=point.step,
            cpu_percent=point.cpu_percent,
            gpu_percent=point.gpu_percent,
            memory_mb=point.memory_mb,
            throughput=point.throughput,
            duration_ms=point.duration_ms,
        )
        db.add(row)
        created.append(row)
    db.commit()
    for row in created:
        db.refresh(row)
    items = [ProfilePointRead.model_validate(r) for r in created]
    return ProfileList(items=items, total=len(items))


@router.get("", response_model=ProfileList)
def list_profile_events(
    run_id: str,
    epoch: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> ProfileList:
    get_run_or_404(run_id, db)
    q = db.query(ProfileEvent).filter(ProfileEvent.run_id == run_id)
    if epoch is not None:
        q = q.filter(ProfileEvent.epoch == epoch)
    rows = q.order_by(ProfileEvent.epoch, ProfileEvent.id).all()
    items = [ProfilePointRead.model_validate(r) for r in rows]
    return ProfileList(items=items, total=len(items))


@router.get("/timeline", response_model=ProfileTimelineReport)
def get_profile_timeline(
    run_id: str,
    db: Session = Depends(get_db),
) -> ProfileTimelineReport:
    get_run_or_404(run_id, db)
    rows = (
        db.query(ProfileEvent)
        .filter(ProfileEvent.run_id == run_id)
        .order_by(ProfileEvent.epoch, ProfileEvent.id)
        .all()
    )
    report = build_timeline_report(run_id, rows)
    return ProfileTimelineReport(**report)
