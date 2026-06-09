"""ONNX model graph import and query."""
import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_run_or_404
from app.db.session import get_db
from app.models.model_graph import ModelGraph
from app.schemas.architecture import ArchitectureView
from app.schemas.graph import (
    GraphList,
    GraphRead,
    graph_from_row,
    loads_graph_json,
    summary_from_row,
)
from app.services.architecture_3d import architecture_to_3d
from app.services.architecture_svg import architecture_to_svg, svg_to_pdf, svg_to_png
from app.services.artifact_storage import get_artifact_storage, new_artifact_key
from app.services.onnx_architecture import (
    parse_architecture_from_bytes,
    parse_architecture_from_graph_json,
)
from app.services.onnx_graph import parse_onnx_bytes, validate_onnx_bytes

router = APIRouter(prefix="/graphs", tags=["graphs"])

MAX_ONNX_BYTES = 50 * 1024 * 1024  # 50 MB


def _load_artifact_bytes(row: ModelGraph) -> bytes | None:
    if not row.artifact_key:
        return None
    storage = get_artifact_storage()
    try:
        return storage.get(row.artifact_key)
    except Exception:
        return None


def _store_artifact(data: bytes, filename: str) -> tuple[str, str]:
    storage = get_artifact_storage()
    artifact_key = new_artifact_key(filename)
    storage.put(artifact_key, data, "application/octet-stream")
    return artifact_key, storage.backend_name()


@router.post("", response_model=GraphRead, status_code=201)
async def import_onnx_graph(
    file: UploadFile = File(...),
    run_id: str | None = Form(default=None),
    db: Session = Depends(get_db),
) -> GraphRead:
    if run_id:
        get_run_or_404(run_id, db)

    if not file.filename or not file.filename.lower().endswith(".onnx"):
        raise HTTPException(status_code=400, detail="File must be a .onnx model")

    data = await file.read()
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(data) > MAX_ONNX_BYTES:
        raise HTTPException(status_code=413, detail="ONNX file too large (max 50MB)")

    try:
        validate_onnx_bytes(data)
        parsed = parse_onnx_bytes(data)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Invalid ONNX model: {exc}") from exc

    artifact_key, backend = _store_artifact(data, file.filename)

    meta = parsed.get("metadata", {})
    row = ModelGraph(
        run_id=run_id,
        name=file.filename,
        graph_json=json.dumps(parsed),
        opset_version=meta.get("opset_version"),
        artifact_key=artifact_key,
        artifact_backend=backend,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return graph_from_row(row, parsed)


@router.post("/{graph_id}/artifact", response_model=GraphRead)
async def backfill_graph_artifact(
    graph_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> GraphRead:
    """Upload ONNX bytes for legacy graphs missing artifact storage."""
    row = db.get(ModelGraph, graph_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Graph not found")

    if not file.filename or not file.filename.lower().endswith(".onnx"):
        raise HTTPException(status_code=400, detail="File must be a .onnx model")

    data = await file.read()
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(data) > MAX_ONNX_BYTES:
        raise HTTPException(status_code=413, detail="ONNX file too large (max 50MB)")

    try:
        validate_onnx_bytes(data)
        parsed = parse_onnx_bytes(data)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Invalid ONNX model: {exc}") from exc

    artifact_key, backend = _store_artifact(data, file.filename or row.name)
    row.artifact_key = artifact_key
    row.artifact_backend = backend
    row.graph_json = json.dumps(parsed)
    meta = parsed.get("metadata", {})
    row.opset_version = meta.get("opset_version")
    db.commit()
    db.refresh(row)
    return graph_from_row(row, parsed)


@router.get("", response_model=GraphList)
def list_graphs(db: Session = Depends(get_db)) -> GraphList:
    rows = db.query(ModelGraph).order_by(ModelGraph.created_at.desc()).all()
    items = [summary_from_row(r, loads_graph_json(r.graph_json)) for r in rows]
    return GraphList(items=items, total=len(items))


@router.get("/{graph_id}", response_model=GraphRead)
def get_graph(graph_id: str, db: Session = Depends(get_db)) -> GraphRead:
    row = db.get(ModelGraph, graph_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Graph not found")
    parsed = loads_graph_json(row.graph_json)
    return graph_from_row(row, parsed)


def _architecture_payload(row: ModelGraph) -> tuple[dict, str, bool]:
    parsed = loads_graph_json(row.graph_json)
    raw = _load_artifact_bytes(row)
    if raw is not None:
        return parse_architecture_from_bytes(raw), "artifact", False
    return parse_architecture_from_graph_json(parsed), "graph_json", True


@router.get("/{graph_id}/architecture/3d")
def get_graph_architecture_3d(graph_id: str, db: Session = Depends(get_db)) -> dict:
    """3D layout JSON for WebGL viewer (M2.3)."""
    row = db.get(ModelGraph, graph_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Graph not found")
    arch, _, _ = _architecture_payload(row)
    layout = architecture_to_3d(arch)
    return {"graph_id": graph_id, **layout}


@router.get("/{graph_id}/architecture/export")
def export_graph_architecture(
    graph_id: str,
    format: str = Query(default="svg", pattern="^(svg|png|pdf)$"),
    db: Session = Depends(get_db),
) -> Response:
    """Export MLP architecture diagram as SVG, PNG, or PDF (M2.2)."""
    row = db.get(ModelGraph, graph_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Graph not found")

    arch, _, _ = _architecture_payload(row)
    svg = architecture_to_svg(arch)
    stem = row.name.rsplit(".", 1)[0]

    if format == "svg":
        return Response(
            content=svg,
            media_type="image/svg+xml",
            headers={
                "Content-Disposition": f'attachment; filename="{stem}-architecture.svg"'
            },
        )

    if format == "pdf":
        try:
            pdf_bytes = svg_to_pdf(svg)
        except RuntimeError as exc:
            raise HTTPException(status_code=501, detail=str(exc)) from exc
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{stem}-architecture.pdf"'
            },
        )

    try:
        png_bytes = svg_to_png(svg)
    except RuntimeError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc

    return Response(
        content=png_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": f'attachment; filename="{stem}-architecture.png"'
        },
    )


@router.get("/{graph_id}/architecture", response_model=ArchitectureView)
def get_graph_architecture(graph_id: str, db: Session = Depends(get_db)) -> ArchitectureView:
    row = db.get(ModelGraph, graph_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Graph not found")

    arch, source, artifact_missing = _architecture_payload(row)

    return ArchitectureView(
        graph_id=graph_id,
        source=source,
        artifact_missing=artifact_missing,
        **arch,
    )


@router.get("/{graph_id}/artifact")
def download_graph_artifact(graph_id: str, db: Session = Depends(get_db)) -> Response:
    row = db.get(ModelGraph, graph_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Graph not found")
    raw = _load_artifact_bytes(row)
    if raw is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return Response(
        content=raw,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{row.name}"'},
    )
