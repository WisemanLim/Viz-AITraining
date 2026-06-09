# Viz-AITraining

**Visualization of AI Training (ML, DL, Neural Network, etc.)**

An open-source platform for real-time, interactive visualization of ML/DL/NN training dynamics.

Korean: [README.md](README.md)

| Item | Value |
|------|-------|
| **Profile** | `python-fastapi` |
| **Domain** | `edtech` (KSIC P) |
| **PRD** | [.doc/PRD.md](.doc/PRD.md) |
| **Compliance** | [COMPLIANCE.md](COMPLIANCE.md) |

---

## 1. Overview

MVP iterations 1–**10** deliver **Run tracking**, **scalar/histogram/profile/classical/internal/XAI REST API**, **WebSocket live metrics with Redis pub/sub**, **multi-run compare**, **Python SDK + PyTorch VizCallback + sklearn/SHAP XAI adapter**, **Next.js dashboard**, **ONNX + neural layer viewer + 3D WebGL (weight animation)**, **MinIO/local artifact storage with backfill**, **profiling timeline (M1.3)**, **architecture SVG/PNG/PDF export (M2.2)**, **NN Playground (M5.1)**, **GAN Lab (M5.2)**, **internal state / temporal XAI dashboard (M3·M4)**, and **step-by-step forward pass (M5.3)**.

## 2. Architecture / layout

```
Viz-AITraining/
├── backend/           FastAPI API (:8000)
│   └── app/
│       ├── api/       runs, metrics, histograms, profile, graphs, compare, ws
│       ├── models/    Run, ScalarMetric, HistogramMetric, ProfileEvent, ModelGraph
│       └── services/  onnx_graph, onnx_architecture, architecture_svg, profile_timeline, artifact_storage, metrics_hub
├── sdk/               vizaitrain (SummaryWriter)
├── frontend/          Next.js dashboard (:3000)
│   └── src/app/       runs, /compare, /graphs, /playground
├── ops/               docker-compose (postgres, redis, minio)
└── test/              dev-env + impl/<Nth>
```

| Service | Port | compose profile | Notes |
|---------|------|-----------------|-------|
| **Dashboard** | 3000 | — | `make dev-web` |
| API (host) | 8000 | — | `make dev` |
| API (container) | 8000 | `app` | `ENV=dev make build` |
| PostgreSQL | 5432 | default | `ENV=dev make up` |
| Redis | 6379 | default | dev+ |
| MinIO | 9000/9001 | default | artifacts (M6.2, `ENV=dev`) |

## 3. Prerequisites

- Python **3.12+** (verified: 3.13.12)
- Node.js **20+** (dashboard, verified: Next.js 15)
- [uv](https://docs.astral.sh/uv/)
- Docker Compose (for `ENV=dev` and above)

## 4. Environment

| ENV | DB | compose | File |
|-----|-----|---------|------|
| **local** (default) | SQLite `backend/local.db` | not required | `.env.local` |
| dev | PostgreSQL + Redis + MinIO | required | `.env.dev` |
| staging | PostgreSQL | required | `.env.staging` |
| prod | Secret injection | K8s | `.env.prod` (keys only) |

```bash
cp .env.example .env.local   # first time
```

Never commit real secrets in `.env.local` or other env files.

## 5. How to run

### A) Host direct (local — recommended)

```bash
make sync
make sync-web    # frontend npm (first time)
make dev         # API :8000
make dev-web     # Dashboard :3000 (separate terminal)
```

### B) Docker Compose (dev+)

```bash
ENV=dev make up              # postgres + redis + minio
ENV=dev make dev             # API on host, postgres connected
ENV=dev make down
```

`make up` **skips compose when `ENV=local`** (SQLite mode).

## 6. Endpoints / API

| URL | Description |
|-----|-------------|
| http://localhost:3000 | **Web dashboard** (runs, charts, compare, ONNX/neural graphs) |
| http://localhost:3000/compare | Multi-run metric & param compare |
| http://localhost:3000/graphs | ONNX · Neural / **3D** / **Step Forward** / Operations view |
| http://localhost:3000/playground | **NN Playground** — 2D classification demo (M5.1) |
| http://localhost:3000/gan-lab | **GAN Lab** — adversarial 2D viz (M5.2) |
| http://localhost:8000/health | Health check |
| http://localhost:8000/docs | Swagger UI (OpenAPI) |
| http://localhost:8000/redoc | ReDoc |

### Implemented API (v1)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/runs` | Create run |
| GET | `/api/v1/runs` | List runs |
| GET | `/api/v1/runs/{id}` | Get run |
| POST | `/api/v1/runs/{id}/metrics/scalars` | Batch scalar ingest |
| GET | `/api/v1/runs/{id}/metrics/scalars` | List scalars (`?tag=`) |
| POST | `/api/v1/runs/{id}/metrics/histograms` | Batch histogram ingest |
| GET | `/api/v1/runs/{id}/metrics/histograms` | List histograms (`?tag=`) |
| POST | `/api/v1/graphs` | ONNX upload (multipart) |
| GET | `/api/v1/graphs` | List graphs |
| GET | `/api/v1/graphs/{id}` | Graph JSON (nodes/edges) |
| GET | `/api/v1/runs/{id}/graphs` | Graphs linked to run |
| WS | `/api/v1/ws/runs/{id}/metrics` | Live scalar push (M1.1) |
| POST | `/api/v1/compare` | Multi-run compare `{run_ids:[...]}` |
| GET | `/api/v1/compare?ids=a,b` | Multi-run compare (M1.2) |
| POST | `/api/v1/graphs/{id}/artifact` | Legacy graph ONNX backfill (M6.2) |
| GET | `/api/v1/graphs/{id}/artifact` | Download ONNX artifact |
| GET | `/api/v1/graphs/{id}/architecture` | MLP-style layer visualization + full weight matrices |
| GET | `/api/v1/runs/{id}/metrics/profile` | List profile events |
| POST | `/api/v1/runs/{id}/metrics/profile` | Profile batch ingest (M1.3) |
| GET | `/api/v1/runs/{id}/metrics/profile/timeline` | Epoch timeline + bottleneck report |
| GET | `/api/v1/runs/{id}/metrics/classical` | List classical ML charts (M1.4) |
| POST | `/api/v1/runs/{id}/metrics/classical` | Classical ML charts batch ingest |
| GET | `/api/v1/graphs/{id}/architecture/export?format=svg\|png\|pdf` | Diagram export (M2.2) |
| GET | `/api/v1/graphs/{id}/architecture/3d` | 3D WebGL layout JSON (M2.3) |
| GET | `/api/v1/runs/{id}/metrics/internal` | List internal state metrics (M3) |
| POST | `/api/v1/runs/{id}/metrics/internal` | Internal state batch ingest |
| GET | `/api/v1/runs/{id}/metrics/xai` | List XAI attributions (M4) |
| POST | `/api/v1/runs/{id}/metrics/xai` | XAI attribution batch ingest |

### curl examples

```bash
curl -s -X POST http://localhost:8000/api/v1/runs \
  -H 'Content-Type: application/json' \
  -d '{"name":"exp-001","params":{"lr":0.001}}'

curl -s -X POST http://localhost:8000/api/v1/runs/{RUN_ID}/metrics/scalars \
  -H 'Content-Type: application/json' \
  -d '{"metrics":[{"tag":"loss","value":0.42,"step":1}]}'

curl -s "http://localhost:8000/api/v1/runs/{RUN_ID}/metrics/scalars?tag=loss"

curl -s -X POST http://localhost:8000/api/v1/runs/{RUN_ID}/metrics/histograms \
  -H 'Content-Type: application/json' \
  -d '{"histograms":[{"tag":"layer/w","bin_edges":[0,0.5,1],"counts":[3,7],"step":0}]}'

curl -s -X POST http://localhost:8000/api/v1/graphs \
  -F "file=@model.onnx" \
  -F "run_id={RUN_ID}"

curl -s http://localhost:8000/api/v1/graphs/{GRAPH_ID}/architecture

curl -s -X POST http://localhost:8000/api/v1/compare \
  -H 'Content-Type: application/json' \
  -d '{"run_ids":["run-a","run-b"]}'
```

**Artifact backend**: `ENV=local` uses `backend/artifacts/`. Set `MINIO_*` env vars for MinIO (`ENV=dev make up`).

### SDK example

```python
from vizaitrain import SummaryWriter, VizCallback

with SummaryWriter(run_name="my-experiment", params={"lr": 1e-3}) as writer:
    writer.add_scalar("loss", 0.9, global_step=0)
    writer.add_scalar("loss", 0.4, global_step=1)
    writer.add_histogram_from_values("layer/weights", [0.1, 0.5, 0.9], bins=10, global_step=0)
    writer.add_profile("train", 0, gpu_percent=0.82, step=1)
    writer.add_learning_curve([10, 50], [0.7, 0.9], [0.65, 0.85])
    writer.flush()

# PyTorch training loop (M6.1)
with VizCallback(run_name="pt-exp", params={"lr": 1e-3}) as cb:
    cb.on_train_batch_end(loss=0.42, metrics={"accuracy": 0.88}, step=1)
```

## 7. Tests

```bash
make test        # pytest 33 cases
cd sdk && uv run pytest -v   # 10 cases
make test-web    # frontend lint + build
make env-check
```

Results:

- [test/dev-env/result.md](test/dev-env/result.md) — PASS
- [test/impl/1st/result.md](test/impl/1st/result.md) — PASS
- [test/impl/2nd/result.md](test/impl/2nd/result.md) — PASS
- [test/impl/3rd/result.md](test/impl/3rd/result.md) — PASS
- [test/impl/4th/result.md](test/impl/4th/result.md) — PASS
- [test/impl/5th/result.md](test/impl/5th/result.md) — PASS
- [test/impl/6th/result.md](test/impl/6th/result.md) — PASS
- [test/impl/7th/result.md](test/impl/7th/result.md) — PASS
- [test/impl/8th/result.md](test/impl/8th/result.md) — PASS
- [test/impl/9th/result.md](test/impl/9th/result.md) — PASS
- [test/impl/10th/result.md](test/impl/10th/result.md) — PASS

## 8. Make targets

```bash
make help        # ENV + command list
make env-check   # verify .env.{ENV}
make sync        # uv sync (backend + sdk)
make sync-web    # npm install (frontend)
make dev         # API (local default)
make dev-web     # Next.js dashboard
make test        # pytest
make test-web    # frontend lint + build
make up          # compose (skipped for local)
make down
make build       # dev+ only
make publish     # static export → push to GitHub Pages repo
make publish-build  # static export only (no push) → frontend/out
```

### GitHub Pages publish

`make publish` builds the **frontend** as a static export (`next build`, `output: 'export'`)
and pushes `frontend/out/` to a separate GitHub Pages repository
([scripts/publish-pages.sh](scripts/publish-pages.sh)).

Configure in `.env` / `.env.local` (or pass inline):

| Var | Meaning | Example |
|-----|---------|---------|
| `DEPLOY_ACCOUNT` | GitHub Pages owner account | `WisemanLim` |
| `DEPLOY_REPO` | Pages repo name → `basePath=/<repo>` | `Viz-AITraining` |
| `DEPLOY_BRANCH` | deploy branch (default `main`) | `main` |
| `GIT_USER_NAME` / `GIT_USER_EMAIL` | commit author (optional) | — |

```bash
make publish-build                       # build only, inspect frontend/out
make publish                             # build + push (uses gh CLI token)
DEPLOY_REPO=my-pages make publish        # override repo inline
```

Notes:
- Static export sets `output:'export'` + `basePath` only when `NEXT_PUBLIC_STATIC_EXPORT=true`
  (the publish script sets it); normal `make dev-web` keeps API rewrites.
- **No backend needed** — in static mode the dashboard loads bundled demo data from
  [frontend/public/demo/data.json](frontend/public/demo/data.json) instead of calling `/api`.
  [lib/api.ts](frontend/src/lib/api.ts) routes every read to that bundle (`IS_STATIC_DEMO`),
  WebSocket is disabled, and writes (ONNX upload, seed) report "demo mode".
- Dynamic routes `/runs/[id]` · `/graphs/[id]` pre-build shells for the demo ids
  (`demo`, `demo-baseline`, `demo-graph`); real ids resolve via client-side SPA navigation.
  A Pages deployment is a **dashboard showcase** — live data still needs the FastAPI backend.
- Regenerate demo data: run the API (`make dev`), `make seed-demo`, upload a sample ONNX
  (`.doc/onnx-samples/02_tiny_mlp.onnx`), then snapshot the GET endpoints into
  `frontend/public/demo/data.json` (ids remapped to `demo`/`demo-baseline`/`demo-graph`).
- First deploy: GitHub → Settings → Pages → Source `Deploy from a branch`, Branch `<DEPLOY_BRANCH>` /(root).

## 9. Troubleshooting

| Symptom | Fix |
|---------|-----|
| missing `.env.local` | `cp .env.example .env.local` |
| `make up` fails on local | expected — use `ENV=dev make up` |
| pytest `no such table` | check `StaticPool` in `backend/tests/conftest.py` |
| SDK connection refused | start API with `make dev` first |
| Dashboard CORS error | set `CORS_ORIGINS=http://localhost:3000` in `.env.local` |
| Dashboard API unreachable | check `NEXT_PUBLIC_API_URL` in `frontend/.env.local` |
| `make publish` token fail | run `gh auth login` for `DEPLOY_ACCOUNT`, or unset `GH_TOKEN`/`GITHUB_TOKEN` |
| publish missing `generateStaticParams` | dynamic route lacks a server shell — see [next.config.ts](frontend/next.config.ts) export mode |
| Pages assets 404 | `basePath` must equal `/<DEPLOY_REPO>`; `.nojekyll` is auto-added for `_next/` |

## 10. Next steps (PRD Phase 5+)

- [x] Temporal XAI dashboard (M4.2)
- [x] sklearn/SHAP auto adapter (`vizaitrain.xai_adapter`)
- [x] 3D edge weight animation
- [ ] TensorFlow/Keras callback
- [ ] MLflow export/import
- [ ] Optional LIME adapter
