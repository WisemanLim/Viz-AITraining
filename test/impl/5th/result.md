# impl/5th 시험 결과 — Live Metrics, Compare, Artifacts, Neural Viz

**일시**: 2026-06-07  
**판정**: **PASS**

## 요약

| 항목 | 결과 |
|------|------|
| WebSocket metrics hub (M1.1) | scalar ingest → broadcast |
| Multi-run compare API (M1.2) | param diff + tag overlay |
| Artifact storage (M6.2) | local default, MinIO when configured |
| ONNX architecture parser | MLP-style layers + weight samples |
| Neural Network SVG viewer | reference-image style UI |
| pytest | **19 passed** (+4 impl5) |
| frontend build | PASS |

## 케이스 결과

| id | 결과 | 비고 |
|----|------|------|
| I5-01 | PASS | `test_metrics_websocket` connected |
| I5-02 | PASS | broadcast after scalar POST |
| I5-03 | PASS | `test_compare_runs` |
| I5-04 | PASS | `test_graph_artifact_and_architecture` |
| I5-05 | PASS | GET artifact bytes |
| I5-06 | PASS | architecture JSON |
| I5-07 | PASS | `/graphs/[id]` build |
| I5-08 | PASS | `/compare` build |
| I5-09 | PASS | WS hook + polling fallback |
| I5-10 | PASS | full regression |

## 구현 파일

**Backend**
- `backend/app/services/artifact_storage.py`
- `backend/app/services/metrics_hub.py`
- `backend/app/services/onnx_architecture.py`
- `backend/app/api/compare.py`, `ws.py`
- `backend/app/api/metrics.py` (async + broadcast)
- `backend/app/api/graphs.py` (artifact + architecture)
- `backend/tests/test_impl5.py`

**Frontend**
- `frontend/src/components/NeuralArchitectureViewer.tsx`
- `frontend/src/components/CompareChartPanel.tsx`
- `frontend/src/hooks/useMetricsWebSocket.ts`
- `frontend/src/app/compare/page.tsx`
- `frontend/src/app/graphs/[id]/page.tsx` (Neural / ONNX tabs)
- `frontend/src/app/runs/[id]/page.tsx` (WebSocket live)

## PRD MVP P0 상태

| # | 항목 | 상태 |
|---|------|------|
| 1 | SDK scalar + histogram | ✅ |
| 2 | Web dashboard + WS live | ✅ |
| 3 | ONNX graph + neural layer viz | ✅ |
| 4 | S3/MinIO artifacts | ✅ (local fallback) |
| 5 | REST API + SDK | ✅ |
| 6 | Multi-run compare | ✅ |

## 알려진 제한

- impl/5th 이전 import graph는 `artifact_key` 없음 → architecture 404 (재-import 필요)
- Architecture view는 edge weight **sample** 표시 (전체 행렬 아님)
- WebSocket hub는 in-process (Redis pub/sub 미구현)
- MinIO는 `MINIO_ENDPOINT` 등 env 설정 시에만 활성

## 잔여 (impl/6th 후보)

- Redis pub/sub for horizontal WS scale
- Full weight matrix heatmap on edges
- Run export / share links
