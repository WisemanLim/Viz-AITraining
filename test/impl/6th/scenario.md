# impl/6th 시험 시나리오 — 제한 해소 + PRD 재점검

**PRD 근거**: M1.1 Redis pub/sub, M2.1 full weight matrix, M6.1 PyTorch callback, M6.2 artifact backfill

## 케이스

| id | 목적 | 입력 | 기대결과 | 우선순위 |
|----|------|------|----------|----------|
| I6-01 | Legacy architecture | graph without artifact_key | 200, source=graph_json | P0 |
| I6-02 | Artifact backfill | POST `/graphs/{id}/artifact` | artifact 저장, source=artifact | P0 |
| I6-03 | Full weight matrix | GET architecture | connections[].matrix shape 일치 | P0 |
| I6-04 | Redis pub/sub | REDIS_URL + broadcast | publish envelope | P0 |
| I6-05 | Health transport | GET /health | metrics_transport 필드 | P0 |
| I6-06 | PyTorch callback | VizCallback unit test | scalar flush | P0 |
| I6-07 | UI weight heatmap | Neural tab | matrix panel render | P0 |
| I6-08 | UI backfill | artifact_missing graph | upload ONNX | P0 |
| I6-09 | 회귀 | pytest 23 + sdk 2 + build | PASS | P0 |

## PRD MVP P0 재점검

| PRD 항목 | impl/6th 상태 |
|----------|---------------|
| M1.1 WS live (≤5s) | ✅ + Redis scale-out |
| M1.2 compare | ✅ (impl/5th) |
| M2.1 graph + weights | ✅ full matrix |
| M3.1 histogram | ✅ |
| M6.1 PyTorch adapter | ✅ VizCallback |
| M6.2 S3/MinIO + local | ✅ + backfill |
| M6.3 REST + SDK | ✅ |

## 실행

```bash
make test          # 23 passed
cd sdk && uv run pytest
make test-web
```
