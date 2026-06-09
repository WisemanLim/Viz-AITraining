"""Classical ML chart ingest and query (M1.4)."""
import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_run_or_404
from app.db.session import get_db
from app.models.classical_chart import ClassicalChart
from app.schemas.classical import (
    ClassicalBatchCreate,
    ClassicalChartList,
    ClassicalChartRead,
    ChartType,
)

router = APIRouter(prefix="/runs/{run_id}/metrics/classical", tags=["classical"])


def _to_read(row: ClassicalChart) -> ClassicalChartRead:
    return ClassicalChartRead(
        id=row.id,
        run_id=row.run_id,
        chart_type=row.chart_type,  # type: ignore[arg-type]
        title=row.title,
        data=row.data,
        created_at=row.created_at,
    )


@router.post("", response_model=ClassicalChartList, status_code=201)
def ingest_classical_charts(
    run_id: str,
    body: ClassicalBatchCreate,
    db: Session = Depends(get_db),
) -> ClassicalChartList:
    get_run_or_404(run_id, db)
    created: list[ClassicalChart] = []
    for chart in body.charts:
        row = ClassicalChart(
            run_id=run_id,
            chart_type=chart.chart_type,
            title=chart.title,
            data_json=json.dumps(chart.data),
        )
        db.add(row)
        created.append(row)
    db.commit()
    for row in created:
        db.refresh(row)
    items = [_to_read(r) for r in created]
    return ClassicalChartList(items=items, total=len(items))


@router.get("", response_model=ClassicalChartList)
def list_classical_charts(
    run_id: str,
    chart_type: ChartType | None = Query(default=None),
    db: Session = Depends(get_db),
) -> ClassicalChartList:
    get_run_or_404(run_id, db)
    q = db.query(ClassicalChart).filter(ClassicalChart.run_id == run_id)
    if chart_type is not None:
        q = q.filter(ClassicalChart.chart_type == chart_type)
    rows = q.order_by(ClassicalChart.id).all()
    items = [_to_read(r) for r in rows]
    return ClassicalChartList(items=items, total=len(items))
