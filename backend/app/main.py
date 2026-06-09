"""Viz-AITraining — FastAPI entrypoint."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import classical, compare, demo, graphs, histograms, internal, metrics, profile, run_graphs, runs, ws, xai
from app.core.config import settings
from app.db.session import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    from app.services.metrics_hub import metrics_hub

    await metrics_hub.start()
    yield
    await metrics_hub.stop()


app = FastAPI(
    title=settings.app_name,
    description="ML/DL training visualization API",
    version="0.1.0",
    lifespan=lifespan,
)

_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(runs.router, prefix="/api/v1")
app.include_router(demo.router, prefix="/api/v1")
app.include_router(compare.router, prefix="/api/v1")
app.include_router(metrics.router, prefix="/api/v1")
app.include_router(histograms.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(classical.router, prefix="/api/v1")
app.include_router(internal.router, prefix="/api/v1")
app.include_router(xai.router, prefix="/api/v1")
app.include_router(graphs.router, prefix="/api/v1")
app.include_router(run_graphs.router, prefix="/api/v1")
app.include_router(ws.router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, str]:
    from app.services.metrics_hub import metrics_hub

    return {
        "status": "ok",
        "env": settings.env,
        "service": "viz-ai-training-api",
        "metrics_transport": "redis" if metrics_hub.uses_redis else "local",
    }
