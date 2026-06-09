# impl/4th 시험 시나리오 — ONNX Graph Viewer (Epic E4, M2.1)

**PRD 근거**: §3.2 MVP P0 #3 — ONNX import 및 그래프 뷰; Epic E4 Model Graph Viewer

## 케이스

| id | 목적 | 입력 | 기대결과 | 우선순위 |
|----|------|------|----------|----------|
| I4-01 | ONNX import | POST `/api/v1/graphs` multipart `.onnx` | 201, nodes/edges JSON | P0 |
| I4-02 | Graph 조회 | GET `/api/v1/graphs/{id}` | 200, op_type·shape | P0 |
| I4-03 | Graph 목록 | GET `/api/v1/graphs` | 200, total≥1 | P0 |
| I4-04 | Run 연동 | POST with run_id + GET `.../runs/{id}/graphs` | linked list | P0 |
| I4-05 | 검증 | invalid bytes | 422 | P0 |
| I4-06 | 확장자 | non-.onnx | 400 | P0 |
| I4-07 | Parser | Identity chain ONNX | Input→Identity edges | P0 |
| I4-08 | UI | `/graphs`, `/graphs/[id]` | React Flow viewer | P0 |
| I4-09 | 회귀 | pytest + frontend build | 15 + build PASS | P0 |

## edtech (COMPLIANCE.md)

- ONNX 모델만 업로드 — 학습자 PII 미포함; 50MB 크기 제한

## 실행

```bash
make test       # 15 passed
make test-web   # lint + build PASS
```

수동 검증:

```bash
make dev        # :8000
make dev-web    # :3000
# http://localhost:3000/graphs → .onnx 업로드
```

curl import:

```bash
curl -s -X POST http://localhost:8000/api/v1/graphs \
  -F "file=@model.onnx"
```
