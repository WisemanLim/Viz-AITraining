"""Multi-run experiment comparison."""
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.run import Run
from app.models.scalar_metric import ScalarMetric
from app.schemas.compare import CompareRequest, CompareResult, ParamDiff, SeriesByRun, TagSeries
from app.schemas.metric import ScalarPointRead
from app.schemas.run import RunRead

router = APIRouter(prefix="/compare", tags=["compare"])


def _to_run_read(run: Run) -> RunRead:
    params = json.loads(run.params_json) if run.params_json else None
    return RunRead(
        id=run.id,
        name=run.name,
        status=run.status,
        params=params,
        created_at=run.created_at,
    )


def _build_compare(run_ids: list[str], db: Session) -> CompareResult:
    runs: list[RunRead] = []
    all_params: dict[str, dict[str, object]] = {}

    for rid in run_ids:
        run = db.get(Run, rid)
        if run is None:
            raise HTTPException(status_code=404, detail=f"Run not found: {rid}")
        rr = _to_run_read(run)
        runs.append(rr)
        all_params[rid] = rr.params or {}

    param_keys: set[str] = set()
    for p in all_params.values():
        param_keys.update(p.keys())

    param_diffs = [
        ParamDiff(key=k, values={rid: all_params[rid].get(k) for rid in run_ids})
        for k in sorted(param_keys)
    ]

    tag_map: dict[str, list[SeriesByRun]] = {}
    for rid in run_ids:
        run = db.get(Run, rid)
        assert run is not None
        rows = (
            db.query(ScalarMetric)
            .filter(ScalarMetric.run_id == rid)
            .order_by(ScalarMetric.step.nulls_last(), ScalarMetric.id)
            .all()
        )
        by_tag: dict[str, list[ScalarPointRead]] = {}
        for row in rows:
            pt = ScalarPointRead.model_validate(row)
            by_tag.setdefault(row.tag, []).append(pt)
        for tag, points in by_tag.items():
            tag_map.setdefault(tag, []).append(
                SeriesByRun(run_id=rid, run_name=run.name, points=points)
            )

    tags = [TagSeries(tag=t, series=s) for t, s in sorted(tag_map.items())]
    return CompareResult(runs=runs, param_diffs=param_diffs, tags=tags)


@router.post("", response_model=CompareResult)
def compare_runs_post(body: CompareRequest, db: Session = Depends(get_db)) -> CompareResult:
    return _build_compare(body.run_ids, db)


@router.get("", response_model=CompareResult)
def compare_runs_get(
    ids: str = Query(..., description="Comma-separated run IDs"),
    db: Session = Depends(get_db),
) -> CompareResult:
    run_ids = [x.strip() for x in ids.split(",") if x.strip()]
    if len(run_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 run IDs required")
    return _build_compare(run_ids, db)
