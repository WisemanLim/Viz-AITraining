# impl/5th 시험 시나리오 — Live Metrics, Compare, Artifacts, Neural Viz

**PRD 근거**: M1.1 WebSocket live metrics, M1.2 Multi-run compare, M6.2 MinIO artifacts, §3.2 neural network visualization

## 케이스

| id | 목적 | 입력 | 기대결과 | 우선순위 |
|----|------|------|----------|----------|
| I5-01 | WebSocket 연결 | WS `/api/v1/ws/runs/{id}/metrics` | `connected` 메시지 | P0 |
| I5-02 | WS scalar push | POST scalars while WS open | `scalars` broadcast 수신 | P0 |
| I5-03 | Multi-run compare | POST/GET `/api/v1/compare` | runs, param_diffs, tags overlay | P0 |
| I5-04 | Artifact 저장 | POST `/api/v1/graphs` ONNX | artifact_key, local/MinIO backend | P0 |
| I5-05 | Artifact 다운로드 | GET `/api/v1/graphs/{id}/artifact` | ONNX bytes | P0 |
| I5-06 | Architecture view | GET `/api/v1/graphs/{id}/architecture` | layers, edges, formulas | P0 |
| I5-07 | Neural Network UI | `/graphs/[id]` Neural tab | glowing nodes, weight labels | P0 |
| I5-08 | Compare UI | `/compare` | run 선택, overlay charts | P0 |
| I5-09 | Run live WS | `/runs/[id]` | WebSocket primary, polling fallback | P0 |
| I5-10 | 회귀 | pytest + frontend build | 19 + build PASS | P0 |

## edtech (COMPLIANCE.md)

- Artifact는 ONNX 모델만 — PII 미포함; 50MB 제한 유지
- Compare는 동일 프로젝트 내 Run 메타·metric만 — 학습자 식별 정보 없음

## 실행

```bash
make sync
make test       # 19 passed
make test-web   # lint + build PASS
```

수동 검증:

```bash
make dev        # :8000
make dev-web    # :3000
# http://localhost:3000/compare
# http://localhost:3000/graphs/{id} → Neural Network tab
# Run detail → Live · WebSocket indicator
```

MinIO (dev):

```bash
ENV=dev make up   # minio :9000 / console :9001
# .env.dev MINIO_* 설정 후 API 재기동 → artifact_backend=minio
```

WebSocket curl/wscat:

```bash
# wscat -c ws://localhost:8000/api/v1/ws/runs/{RUN_ID}/metrics
```
