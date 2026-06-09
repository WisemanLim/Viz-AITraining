# One-Page PRD: Visualization of AI Training (ML, DL, Neural Network, etc.)

## 1. 개요

| 항목 | 내용 |
|------|------|
| **한 줄 요약** | ML/DL/NN 학습 과정(Training Dynamics)을 실시간·인터랙티브하게 시각화하는 통합 오픈소스 플랫폼 |
| **배경 / 왜 지금 하는가** | 기존 30+ 도구 조사 결과, **학습 시간축 모니터링·내부 상태(activation/gradient)·아키텍처 시각화·교육용 인터랙션**을 하나의 워크플로로 제공하는 솔루션이 부재함. TensorBoard/MLflow는 메트릭 중심, Netron/Visualkeras는 정적 구조 중심, GAN Lab/TensorFlow Playground는 교육 데모에 한정됨 |
| **작성자** | 가정: 프로젝트 오너(연구·엔터프라이즈 ML 엔지니어) |
| **날짜 / 버전** | 2026-06-07 / v0.1 (초안) |
| **근거 문서** | [.doc/Perplexity-ML, DL, NLP 등의 시각화.md](./Perplexity-ML,%20DL,%20NLP%20등의%20시각화.md) |

---

## 2. 문제와 대상 (Why & Who)

### 2.1 해결하려는 핵심 문제

- **문제**: 딥러닝 학습 중 loss/metric만으로는 **가중치 분포 변화, activation 패턴, gradient vanishing/exploding, latent space 변화**를 직관적으로 파악하기 어렵다.
- **영향**: 디버깅 시간 증가, 하이퍼파라미터 튜닝 비효율, 교육·발표용 자료 제작에 별도 도구를 혼용해야 한다.
- **근거**: Perplexity 조사([Visual Analytics in Deep Learning](https://www.sciencedirect.com/science/article/pii/S2468502X1830038X), [30+ 도구 비교](./Perplexity-ML,%20DL,%20NLP%20등의%20시각화.md)) — 단일 도구가 “학습 시간축 + 내부 상태 + 아키텍처 + 교육 UX”를 모두 충족하지 못함.

### 2.2 비즈니스·연구 관점 중요성

- 연구·프로토타입 환경에서 실험 재현성과 디버깅 속도 향상
- 엔터프라이즈 ML 파이프라인(K8s, MLflow 등)과 연동 가능한 **관측성(Observability)** 계층 제공
- 교육·온보딩에서 “블랙박스”인 NN 학습 과정을 **설명 가능한 시각 경험**으로 전환

### 2.3 타깃 사용자 / 페르소나

| 페르소나 | 역할 | 대표 사용 상황 |
|----------|------|----------------|
| **ML Researcher** | PyTorch/TF 실험 설계·디버깅 | epoch/step별 activation·gradient 이상 탐지 |
| **ML Engineer (Enterprise)** | K8s 기반 학습 Job 운영 | 다중 실험 비교, MLflow/TensorBoard 대체·보완 |
| **Educator / Technical Writer** | 강의·튜토리얼·논문 | GAN Lab/Playground 수준의 인터랙티브 데모 제작 |
| **Data Scientist (Classical ML)** | scikit-learn 파이프라인 | 학습 곡선·ROC·feature importance 시각화 |

### 2.4 벤치마크·참고 오픈소스 (조사 근거)

| 유형 | 대표 도구 | URL/출처 |
|------|-----------|----------|
| 프레임워크 통합형 | TensorBoard, MLflow, Yellowbrick | [TensorBoard](https://goatlab.tistory.com/entry/딥러닝-프레임워크-비교), [MLflow](https://velog.io/@shinichi77/2025-top-10-dev-tools) |
| 아키텍처 시각화 | Netron, TensorSpace, Visualkeras | [GitHub NN Viz Tools](https://github.com/ashishpatel26/Tools-to-Design-or-Visualize-Architecture-of-Neural-Network) |
| 학습 동작·XAI | ActiVis, LSTMVis, RNNbow, SHAP/LIME | [Visual Analytics Survey](https://www.sciencedirect.com/science/article/pii/S2468502X1830038X) |
| 교육·데모 | TensorFlow Playground, GAN Lab, Conx | [DL Visualization Survey](https://subinium.github.io/LR014/) |

---

## 3. 범위 (What — In / Out)

### 3.1 기능 요구사항 — 계층형 기능 표 (Major → Medium → Minor)

| 대분류 (Major) | 중분류 (Medium) | 소분류 (Minor) | 설명 | 우선순위 | 수용 기준 (Given-When-Then) |
|----------------|-----------------|----------------|------|----------|----------------------------|
| **M1. 학습 모니터링** | M1.1 Scalar Metrics | Loss / Accuracy / LR 곡선 | epoch·step 단위 실시간 차트 | P0 | Given 학습 Job 실행 When step 진행 Then 5초 이내 차트 갱신 |
| | M1.2 Experiment Tracking | Run 비교·하이퍼파라미터 | MLflow 스타일 실험 메타데이터 | P0 | Given 2개 이상 run When 비교 뷰 선택 Then metric·param diff 표시 |
| | M1.3 Profiling | GPU/CPU·throughput | 학습 병목 프로파일 | P1 | Given profile 활성 When 1 epoch 완료 Then timeline 리포트 생성 |
| | M1.4 Classical ML | 학습 곡선·ROC·Confusion Matrix | scikit-learn 연동 (Yellowbrick 유사) | P2 | Given sklearn estimator When fit 완료 Then 진단 차트 export |
| **M2. 모델 구조 시각화** | M2.1 Graph View | 연산 그래프·레이어 트리 | Netron/TensorBoard Graph 유사 | P0 | Given ONNX/PT/TF 모델 When import Then 레이어·shape·연결 표시 |
| | M2.2 2D Architecture Diagram | 논문·발표용 구조도 | Visualkeras/PlotNeuralNet 스타일 export | P1 | Given Keras/PyTorch model When export Then PNG/SVG/PDF 생성 |
| | M2.3 3D Interactive View | 브라우저 3D NN | TensorSpace 유사 WebGL | P2 | Given 사전학습 모델 When 3D 뷰 Then 레이어별 zoom·rotate |
| **M3. 학습 내부 상태** | M3.1 Weight Histogram | epoch별 가중치 분포 | TensorBoard histogram 유사 | P0 | Given checkpoint When epoch 선택 Then layer별 histogram |
| | M3.2 Activation Map | CNN filter·feature map | Deep Visualization Toolbox 유사 | P1 | Given CNN When forward pass Then activation heatmap |
| | M3.3 Gradient Flow | BPTT gradient 크기 | RNNbow 유사 | P1 | Given RNN 학습 When backward Then timestep별 gradient 시각화 |
| | M3.4 Embedding / Latent Space | t-SNE/UMAP projector | embedding projector | P1 | Given embedding log When projector 실행 Then 2D/3D scatter |
| | M3.5 Hidden State (RNN) | LSTM state dynamics | LSTMVis 유사 | P2 | Given 시퀀스 입력 When LSTM run Then state trajectory |
| **M4. 설명가능성 (XAI)** | M4.1 Feature Attribution | SHAP/LIME 연동 | checkpoint별 importance | P1 | Given tabular/image model When XAI 요청 Then local/global plot |
| | M4.2 Temporal XAI | 학습 진행에 따른 importance 변화 | checkpoint 시계열 비교 | P2 | Given N checkpoints When SHAP batch Then time-series dashboard |
| **M5. 교육·데모** | M5.1 Playground | 브라우저 실시간 NN 학습 | TF Playground 유사 | P1 | Given 2D dataset When 학습 시작 Then decision boundary 애니메이션 |
| | M5.2 GAN Simulator | GAN Lab 유사 adversarial viz | generator/discriminator 분포 | P2 | Given GAN demo When train Then boundary·loss 동시 표시 |
| | M5.3 Step-by-step Forward | 데이터 흐름 안내 | Conx/nn_vis 유사 | P1 | Given small NN When step 클릭 Then layer별 activation 강조 |
| **M6. 플랫폼·연동** | M6.1 Framework Adapter | PyTorch, TensorFlow/Keras, ONNX | SummaryWriter/callback hook | P0 | Given PyTorch When callback 등록 Then 자동 로그 수집 |
| | M6.2 Storage Backend | 로컬·S3·MinIO | artifact·metric 저장 | P0 | Given S3 config When run 종료 Then artifact 업로드·재조회 |
| | M6.3 API / SDK | REST + Python SDK | 외부 대시보드·CI 연동 | P0 | Given API key When GET /runs/{id}/metrics Then JSON 반환 |
| | M6.4 K8s Integration | Sidecar/collector 패턴 | 분산 학습 Job 관측 | P1 | Given K8s Job When sidecar 배포 Then pod별 metric 집계 |
| | M6.5 Auth & Multi-tenant | RBAC, workspace | 엔터프라이즈 공유 | P2 | Given tenant A When tenant B run 조회 Then 403 |

### 3.2 MVP (Phase 1) — P0 기능만

1. PyTorch SummaryWriter 호환 로그 수집 (scalar, histogram)
2. Web 대시보드: run 목록, loss/metric 실시간 차트
3. 모델 구조 import (ONNX 우선) 및 그래프 뷰
4. 로컬 + S3-compatible artifact 저장
5. REST API + Python SDK (최소: log, list runs, get metrics)

### 3.3 하지 않을 것 (Out of Scope — MVP)

| 항목 | 사유 |
|------|------|
| 자체 DL 프레임워크 구현 | 기존 PyTorch/TF 위 관측 레이어로 한정 |
| 모델 학습 실행·하이퍼파라미터 자동 탐색 | MLflow/Kubeflow 등과 연동으로 대체 |
| 상용 BI 전체 대체 (Superset/Tableau) | ML 특화 metric·activation에 집중 |
| NVIDIA DIGITS급 end-to-end MLOps | Phase 2 이후 검토 |
| 모바일 네이티브 앱 | Web-first (반응형) |
| LLM/RAG 파이프라인 전용 UI | Phase 3 로드맵 (token-level attention viz) |

---

## 4. 사용자 경험 (How — User Flow)

### 4.1 시나리오 1: 연구자 — PyTorch 학습 디버깅

```
[연구자] → Python SDK로 VizCallback 등록
         → torch train loop 실행
         → Web UI (localhost:8080) 자동 오픈
         → Run 대시보드에서 loss curve 실시간 확인
         → 이상 epoch 클릭 → weight histogram + activation map drill-down
         → gradient flow 탭에서 vanishing 구간 식별
         → MLflow run ID와 링크 공유
```

### 4.2 시나리오 2: 교육자 — 인터랙티브 데모 제작

```
[교육자] → Playground 템플릿 선택 (2D classification)
         → hidden layer·activation·learning rate UI 조절
         → 학습 애니메이션 녹화 / embed URL 생성
         → 강의 슬라이드·Jupyter Notebook에 iframe 삽입
```

### 4.3 시나리오 3: ML Engineer — K8s 분산 학습 관측

```
[MLE] → Helm chart로 collector sidecar 배포
      → 다중 GPU Job metric 중앙 집계
      → Grafana/OpenTelemetry export (선택)
      → 실험 비교 뷰에서 best run 선정 → artifact download
```

---

## 5. 성공 지표 (Success)

| KPI | Baseline (현재) | Target (MVP 6개월) | 측정 방법 |
|-----|-----------------|---------------------|-----------|
| **Time-to-first-viz** | 가정: TensorBoard 셋업 30분+ | **≤ 5분** (pip install + 10줄 코드) | onboarding 타이머 이벤트 |
| **실시간 metric 지연** | TensorBoard refresh ~10–30s | **≤ 5초** (p95) | OTel span latency |
| **지원 프레임워크** | 0 (신규) | **PyTorch + ONNX** (MVP) | adapter 테스트 통과율 |
| **주간 활성 사용자 (WAU)** | 0 | 가정: **50+** (내부·오픈소스 early adopters) | anonymous telemetry opt-in |
| **GitHub Stars** | 0 | 가정: **500+** (6개월) | GitHub API |
| **교육 데모 완료율** | N/A | **≥ 70%** Playground 튜토리얼 완료 | funnel analytics |

### 5.1 ICT/SaaS 도메인 NFR 후보 (domains/ict-saas.yaml 근거)

| NFR | 요구 | 출처 |
|-----|------|------|
| 관측성 | OpenTelemetry trace/log/metric, 티어드 보관 | ict-saas `observability` |
| API-first | OpenAPI 3.x 계약, contract test | ict-saas `stack_overrides.backend` |
| 멀티테넌트 | workspace 격리 (Phase 2), RLS | ict-saas `tenancy` |
| 보안 | PIPA/GDPR — 학습 데이터·PII 업로드 금지 기본 정책 | ict-saas `korea_regulations`, `data_classes` |
| CI/CD | lint/type/test/build/deploy 파이프라인 | ict-saas `dev_env_special` |

---

## 6. 리스크 및 메모

| 구분 | 내용 |
|------|------|
| **주요 리스크** | (1) TensorBoard/MLflow 생태계 lock-in — 차별화는 activation·교육 UX (2) 대규모 activation 로그 storage 비용 (3) 프레임워크별 hook API 파편화 |
| **의존성** | PyTorch, ONNX Runtime, WebGL(Three.js), object storage(S3/MinIO), 선택: MLflow export |
| **미결정 (Open Questions)** | (1) Phase 1 frontend: React vs Next.js (2) 실시간 transport: WebSocket vs SSE (3) LLM attention viz 우선순위 (4) 상용 라이선스 vs Apache-2.0 |
| **경쟁·차별화** | TensorBoard(메트릭 표준) + Netron(구조) + GAN Lab(교육) **통합** + K8s-native + framework-agnostic adapter |

---

## 7. 기술 메모 (Technical Notes) — `--full` 확장

> 아래는 **예시/초안**이며, `/wise-dev-standard:recommend` 로 스택 확정 후 갱신한다.

### 7.1 권장 아키텍처 (조사 기반)

```
┌─────────────────────────────────────────────────────────────┐
│  Client (Web)                                               │
│  - Dashboard (metrics, histogram, graph, playground)        │
│  - Three.js 3D view (Phase 2)                               │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST / WebSocket
┌──────────────────────────▼──────────────────────────────────┐
│  Backend API (FastAPI or NestJS)                            │
│  - Run/Experiment CRUD                                      │
│  - Metric query (time-series)                               │
│  - Model artifact parse (ONNX → graph JSON)                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│  Collector / SDK (Python)                                   │
│  - PyTorch callback (SummaryWriter-compatible API)          │
│  - TensorFlow/Keras callback (Phase 2)                      │
│  - Batch export to MLflow format (optional)                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│  Storage                                                    │
│  - PostgreSQL (metadata, runs, params)                      │
│  - TimescaleDB or ClickHouse (metrics TS) — 가정            │
│  - S3/MinIO (checkpoints, activation tensors, images)       │
│  - Redis (pub/sub for live updates)                         │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 디렉터리 구조 (구현 예시 — frontend/backend/db/ops)

```
Viz-AITraining/
├── frontend/          # Next.js dashboard + playground
├── backend/           # FastAPI/NestJS API + collector ingest
├── db/                # migrations, schema (PostgreSQL + TS store)
├── ops/               # docker-compose, K8s manifests, scripts
├── sdk/               # Python vizaitrain SDK
└── test/              # 시험 시나리오·결과
```

### 7.3 비기능 요구사항

| 항목 | MVP 목표 | Phase 2 |
|------|----------|---------|
| Metric ingest throughput | ≥ 1,000 points/s (single node) | ≥ 10,000 points/s |
| Dashboard p95 latency | ≤ 500ms (cached queries) | ≤ 200ms |
| Availability | 99.5% (self-hosted) | 99.9% |
| Max run retention | 가정: 90일 (configurable) | tiered (hot/warm/cold) |
| Security | API key auth, HTTPS, no PII in logs by default | RBAC, SSO, audit log |

### 7.4 데이터 / 로깅 요구사항

- **Metric schema**: `{run_id, step, epoch, key, value, timestamp}`
- **Histogram schema**: `{run_id, step, layer, bin_edges, counts}`
- **Artifact**: ONNX, PNG (activation), JSON (graph)
- **Observability**: OTel exporter → platform self-monitoring

### 7.5 외부 연동

| 시스템 | 방향 | 용도 |
|--------|------|------|
| MLflow | Export/Import | 실험 메타데이터 호환 |
| TensorBoard | Import event files | 기존 로그 마이그레이션 |
| ONNX | Import | 구조 시각화 |
| Prometheus/Grafana | Export metrics | infra 모니터링 |
| K8s | Sidecar deploy | 분산 학습 |

### 7.6 오픈소스 벤치마크 — 차별화 매트릭스

| 기능 축 | TensorBoard | MLflow | Netron | GAN Lab | **본 프로젝트 (목표)** |
|---------|-------------|--------|--------|---------|------------------------|
| 학습 시간축 | ◎ | ◎ | ✗ | ○ | ◎ |
| Weight/Activation | ○ | ✗ | △ | ○ | ◎ |
| 아키텍처 viz | ○ | ✗ | ◎ | △ | ○→◎ |
| 교육 Playground | ✗ | ✗ | ✗ | ◎ | ○ |
| Framework agnostic | △ | ◎ | ◎ | ✗ | ◎ |
| K8s-native | △ | ○ | ✗ | ✗ | ○ |

(◎=강점, ○=부분, △=제한, ✗=없음 — [조사 문서 §3 비교표](./Perplexity-ML,%20DL,%20NLP%20등의%20시각화.md) 기반)

---

## 8. 실행 연결 (Epic / Story 힌트)

| Epic | 설명 | Phase |
|------|------|-------|
| **E1. Python SDK & Collector** | PyTorch callback, scalar/histogram log, local buffer | MVP |
| **E2. Storage & API** | PostgreSQL schema, S3 artifact, REST CRUD | MVP |
| **E3. Web Dashboard Core** | Run list, live metric charts, WebSocket | MVP |
| **E4. Model Graph Viewer** | ONNX import, interactive graph UI | MVP |
| **E5. Weight & Activation Viz** | Histogram drill-down, CNN activation heatmap | Phase 1.5 |
| **E6. Playground Module** | 2D NN browser trainer | Phase 2 |
| **E7. K8s & OTel** | Helm chart, sidecar, export | Phase 2 |
| **E8. XAI Integration** | SHAP/LIME adapter, temporal dashboard | Phase 2 |
| **E9. 3D & Advanced** | TensorSpace-style 3D, LSTMVis, GAN Lab | Phase 3 |

---

## 9. 리뷰 체크리스트 (Definition of Ready)

| 항목 | 상태 |
|------|------|
| 문제 정의가 실제 사용자 문제를 설명하는가? | ✅ 30+ 도구 gap 분석 근거 |
| MVP 범위(In)와 비범위(Out)가 명확한가? | ✅ P0 5항 + Out 6항 |
| 성공 지표가 측정 가능하고 기준선이 있는가? | ✅ KPI 6개 (`가정:` 포함) |
| 수용 기준이 Given-When-Then인가? | ✅ 기능 표에 포함 |
| 의존성·리스크가 명시되었는가? | ✅ §6, §7 |
| 업종(ict-saas) NFR이 반영되었는가? | ✅ §5.1 |

---

## 10. 다음 단계

1. **검토·수정**: Open Questions(§6) 확정 — 특히 frontend 스택, 라이선스
2. **스택 추천**: `/wise-dev-standard:recommend python ict-saas` 실행
3. **스캐폴딩**: `/wise-dev-standard:scaffold` 로 frontend/backend/db/ops 구조 생성
4. **구현**: Epic E1→E4 순 MVP 개발

---

## 참고 출처 (Original Sources)

- [Perplexity 조사 — ML/DL/NLP 시각화 30+ 도구](./Perplexity-ML,%20DL,%20NLP%20등의%20시각화.md)
- [Visual Analytics in Deep Learning (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S2468502X1830038X)
- [Tools to Visualize NN Architecture (GitHub)](https://github.com/ashishpatel26/Tools-to-Design-or-Visualize-Architecture-of-Neural-Network)
- [5 Tools for Visualizing ML Models (Machine Learning Mastery)](https://machinelearningmastery.com/5-tools-visualizing-machine-learning-models/)
- [DL Visualization Survey (subinium)](https://subinium.github.io/LR014/)
- [Polo Club Visualization Tools](https://poloclub.github.io)
- [ict-saas domain baseline](/Users/wise/.claude/plugins/cache/wise-dev-standard/wise-dev-standard/0.8.0/domains/ict-saas.yaml)
