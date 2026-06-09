# Viz-AITraining

**AI 학습 과정 시각화 (ML · DL · Neural Network 등)**

ML/DL/NN 학습 동역학을 실시간·인터랙티브하게 시각화하는 오픈소스 플랫폼.

English: [README.en.md](README.en.md)

| 항목 | 값 |
|------|-----|
| **Profile** | `python-fastapi` |
| **Domain** | `edtech` (KSIC P) |
| **PRD** | [.doc/PRD.md](.doc/PRD.md) |
| **Compliance** | [COMPLIANCE.md](COMPLIANCE.md) |

---

## 1. 개요

MVP 1~**10차** 반복으로 **Run 추적**, **scalar/histogram/profile/classical/internal/XAI REST API**, **Redis pub/sub 기반 WebSocket 실시간 메트릭**, **다중 Run 비교**, **Python SDK + PyTorch VizCallback + sklearn/SHAP XAI 어댑터**, **Next.js 대시보드**, **ONNX + 뉴럴 레이어 뷰어 + 3D WebGL(가중치 애니메이션)**, **MinIO/로컬 아티팩트 저장 + 백필**, **프로파일링 타임라인(M1.3)**, **아키텍처 SVG/PNG/PDF export(M2.2)**, **NN Playground(M5.1)**, **GAN Lab(M5.2)**, **internal state / temporal XAI 대시보드(M3·M4)**, **단계별 forward pass(M5.3)** 를 제공한다.

## 2. 아키텍처 / 구조

```
Viz-AITraining/
├── backend/           FastAPI API (:8000)
│   └── app/
│       ├── api/       runs, metrics, histograms, profile, graphs, compare, ws
│       ├── models/    Run, ScalarMetric, HistogramMetric, ProfileEvent, ModelGraph
│       └── services/  onnx_graph, onnx_architecture, architecture_svg, profile_timeline, artifact_storage, metrics_hub
├── sdk/               vizaitrain (SummaryWriter)
├── frontend/          Next.js 대시보드 (:3000)
│   └── src/app/       runs, /compare, /graphs, /playground
├── ops/               docker-compose (postgres, redis, minio)
├── scripts/           publish-pages.sh (GitHub Pages 배포)
└── test/              dev-env + impl/<Nth>
```

| 서비스 | 포트 | compose profile | 비고 |
|--------|------|-----------------|------|
| **Dashboard** | 3000 | — | `make dev-web` |
| API (host) | 8000 | — | `make dev` |
| API (container) | 8000 | `app` | `ENV=dev make build` |
| PostgreSQL | 5432 | default | `ENV=dev make up` |
| Redis | 6379 | default | dev+ |
| MinIO | 9000/9001 | default | artifacts (M6.2, `ENV=dev`) |

## 3. 사전 요구사항

- Python **3.12+** (검증: 3.13.12)
- Node.js **20+** (대시보드, 검증: Next.js 15)
- [uv](https://docs.astral.sh/uv/)
- Docker Compose (`ENV=dev` 이상)

## 4. 환경

| ENV | DB | compose | 파일 |
|-----|-----|---------|------|
| **local** (기본) | SQLite `backend/local.db` | 불필요 | `.env.local` |
| dev | PostgreSQL + Redis + MinIO | 필요 | `.env.dev` |
| staging | PostgreSQL | 필요 | `.env.staging` |
| prod | Secret 주입 | K8s | `.env.prod` (키만) |

```bash
cp .env.example .env.local   # 최초 1회
```

`.env.local` 등 실제 env 파일에 실값 시크릿을 커밋하지 말 것.

## 5. 실행 방법

### A) 호스트 직접 (local — 권장)

```bash
make sync
make sync-web    # frontend npm (최초 1회)
make dev         # API :8000
make dev-web     # Dashboard :3000 (별도 터미널)
```

### B) Docker Compose (dev+)

```bash
ENV=dev make up              # postgres + redis + minio
ENV=dev make dev             # API 는 호스트, postgres 연동
ENV=dev make down
```

`make up` 은 **`ENV=local` 이면 compose 를 건너뛴다** (SQLite 모드).

## 6. 엔드포인트 / API

| URL | 설명 |
|-----|------|
| http://localhost:3000 | **웹 대시보드** (runs, charts, compare, ONNX/neural graphs) |
| http://localhost:3000/compare | 다중 Run 메트릭·파라미터 비교 |
| http://localhost:3000/graphs | ONNX · Neural / **3D** / **Step Forward** / Operations 뷰 |
| http://localhost:3000/playground | **NN Playground** — 2D 분류 데모 (M5.1) |
| http://localhost:3000/gan-lab | **GAN Lab** — 적대적 2D 시각화 (M5.2) |
| http://localhost:8000/health | 헬스 체크 |
| http://localhost:8000/docs | Swagger UI (OpenAPI) |
| http://localhost:8000/redoc | ReDoc |

구현된 API 전체 목록과 curl/SDK 예시는 [README.en.md](README.en.md#6-endpoints--api) 참고.

```python
from vizaitrain import SummaryWriter, VizCallback

with SummaryWriter(run_name="my-experiment", params={"lr": 1e-3}) as writer:
    writer.add_scalar("loss", 0.9, global_step=0)
    writer.add_scalar("loss", 0.4, global_step=1)
    writer.flush()

# PyTorch 학습 루프 (M6.1)
with VizCallback(run_name="pt-exp", params={"lr": 1e-3}) as cb:
    cb.on_train_batch_end(loss=0.42, metrics={"accuracy": 0.88}, step=1)
```

## 7. 시험

```bash
make test        # pytest 33 cases
cd sdk && uv run pytest -v   # 10 cases
make test-web    # frontend lint + build
make env-check
```

결과: [test/dev-env/result.md](test/dev-env/result.md), [test/impl/1st](test/impl/1st/result.md)~[10th](test/impl/10th/result.md) — 전체 PASS.

## 8. Make 타깃

```bash
make help        # ENV + 명령 목록
make env-check   # .env.{ENV} 확인
make sync        # uv sync (backend + sdk)
make sync-web    # npm install (frontend)
make dev         # API (local 기본)
make dev-web     # Next.js 대시보드
make test        # pytest
make test-web    # frontend lint + build
make up          # compose (local 은 스킵)
make down
make build       # dev+ 전용
make publish     # 정적 export → GitHub Pages 저장소로 배포
make publish-build  # 배포 없이 정적 export 만 (frontend/out)
```

### GitHub Pages 배포 (`make publish`)

`make publish` 는 **frontend** 를 정적 export(`next build`, `output: 'export'`)로 빌드해
`frontend/out/` 을 별도 GitHub Pages 저장소로 push 한다
([scripts/publish-pages.sh](scripts/publish-pages.sh)). Atomica 의 `publish-pages.sh` 로직을
단일 npm 앱 구조에 맞게 이식.

`.env` / `.env.local` 에 설정 (또는 인라인 전달):

| 변수 | 의미 | 예시 |
|------|------|------|
| `DEPLOY_ACCOUNT` | GitHub Pages 소유 계정 | `WisemanLim` |
| `DEPLOY_REPO` | Pages 저장소명 → `basePath=/<repo>` | `Viz-AITraining` |
| `DEPLOY_BRANCH` | 배포 브랜치 (기본 `main`) | `main` |
| `GIT_USER_NAME` / `GIT_USER_EMAIL` | 커밋 작성자 (선택) | — |

```bash
make publish-build                       # 빌드만, frontend/out 확인
make publish                             # 빌드 + push (gh CLI 토큰 사용)
DEPLOY_REPO=my-pages make publish        # 저장소 인라인 오버라이드
```

동작 메모:
- 정적 export 는 `NEXT_PUBLIC_STATIC_EXPORT=true` 일 때만 `output:'export'` + `basePath` 적용
  (publish 스크립트가 자동 설정). 일반 `make dev-web` 은 API rewrites 유지.
- **백엔드 불필요** — 정적 모드에서는 `/api` 호출 대신 번들된 데모 데이터
  [frontend/public/demo/data.json](frontend/public/demo/data.json) 를 로드한다.
  [lib/api.ts](frontend/src/lib/api.ts) 가 모든 조회를 이 번들로 라우팅(`IS_STATIC_DEMO`),
  WebSocket 비활성, 쓰기(ONNX 업로드·seed)는 "데모 모드" 안내.
- 동적 라우트 `/runs/[id]` · `/graphs/[id]` 는 데모 id(`demo`·`demo-baseline`·`demo-graph`)
  셸을 미리 생성하고 실제 id 는 클라이언트 SPA 네비게이션으로 해석. Pages 배포는
  **대시보드 쇼케이스** 이며 실데이터는 FastAPI 백엔드가 필요.
- 데모 데이터 재생성: API 기동(`make dev`) → `make seed-demo` → 샘플 ONNX 업로드
  (`.doc/onnx-samples/02_tiny_mlp.onnx`) → GET 엔드포인트 스냅샷을 `frontend/public/demo/data.json`
  에 저장(id 를 `demo`/`demo-baseline`/`demo-graph` 로 치환).
- 최초 배포: GitHub → Settings → Pages → Source `Deploy from a branch`, Branch `<DEPLOY_BRANCH>` /(root).

## 9. 트러블슈팅

| 증상 | 해결 |
|------|------|
| `.env.local` 없음 | `cp .env.example .env.local` |
| local 에서 `make up` 실패 | 정상 — `ENV=dev make up` 사용 |
| pytest `no such table` | `backend/tests/conftest.py` 의 `StaticPool` 확인 |
| SDK connection refused | 먼저 `make dev` 로 API 기동 |
| Dashboard CORS 오류 | `.env.local` 에 `CORS_ORIGINS=http://localhost:3000` |
| Dashboard API 연결 불가 | `frontend/.env.local` 의 `NEXT_PUBLIC_API_URL` 확인 |
| `make publish` 토큰 실패 | `DEPLOY_ACCOUNT` 로 `gh auth login`, 또는 `GH_TOKEN`/`GITHUB_TOKEN` 해제 |
| `generateStaticParams` 누락 | 동적 라우트에 서버 셸 필요 — [next.config.ts](frontend/next.config.ts) export 모드 참고 |
| Pages 에셋 404 | `basePath` = `/<DEPLOY_REPO>` 일치 확인, `_next/` 용 `.nojekyll` 자동 추가됨 |

## 10. 다음 단계 (PRD Phase 5+)

- [x] Temporal XAI 대시보드 (M4.2)
- [x] sklearn/SHAP 자동 어댑터 (`vizaitrain.xai_adapter`)
- [x] 3D 엣지 가중치 애니메이션
- [ ] TensorFlow/Keras 콜백
- [ ] MLflow export/import
- [ ] LIME 어댑터 (선택)
