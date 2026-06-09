"""Demo data seeding for local onboarding."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.demo_seed import seed_demo_run

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/seed")
def create_demo_seed(db: Session = Depends(get_db)) -> dict:
    """Create a sample experiment with metrics (local/dev onboarding)."""
    return seed_demo_run(db)
