"""Graphs linked to a training run."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_run_or_404
from app.db.session import get_db
from app.models.model_graph import ModelGraph
from app.schemas.graph import GraphList, loads_graph_json, summary_from_row

router = APIRouter(prefix="/runs/{run_id}/graphs", tags=["graphs"])


@router.get("", response_model=GraphList)
def list_run_graphs(run_id: str, db: Session = Depends(get_db)) -> GraphList:
    get_run_or_404(run_id, db)
    rows = (
        db.query(ModelGraph)
        .filter(ModelGraph.run_id == run_id)
        .order_by(ModelGraph.created_at.desc())
        .all()
    )
    items = [
        summary_from_row(r, loads_graph_json(r.graph_json)) for r in rows
    ]
    return GraphList(items=items, total=len(items))
