"""Shared API dependencies."""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.run import Run


def get_run_or_404(run_id: str, db: Session) -> Run:
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
