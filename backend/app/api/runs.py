"""Run CRUD endpoints."""
import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.run import Run
from app.schemas.run import RunCreate, RunList, RunRead

router = APIRouter(prefix="/runs", tags=["runs"])


def _to_read(run: Run) -> RunRead:
    params = json.loads(run.params_json) if run.params_json else None
    return RunRead(
        id=run.id,
        name=run.name,
        status=run.status,
        params=params,
        created_at=run.created_at,
    )


@router.post("", response_model=RunRead, status_code=status.HTTP_201_CREATED)
def create_run(body: RunCreate, db: Session = Depends(get_db)) -> RunRead:
    run = Run(
        name=body.name,
        params_json=json.dumps(body.params) if body.params else None,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return _to_read(run)


@router.get("", response_model=RunList)
def list_runs(db: Session = Depends(get_db)) -> RunList:
    rows = db.query(Run).order_by(Run.created_at.desc()).all()
    items = [_to_read(r) for r in rows]
    return RunList(items=items, total=len(items))


@router.get("/{run_id}", response_model=RunRead)
def get_run(run_id: str, db: Session = Depends(get_db)) -> RunRead:
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return _to_read(run)
