# impl/9th 시험 시나리오 — Phase 3+ (M2.3, M3.2–M3.5, M4, M5.3)

## 범위

| PRD | 기능 |
|-----|------|
| M2.3 | 3D Interactive Architecture View (Three.js) |
| M3.2 | Activation maps ingest + heatmap panel |
| M3.3 | Gradient flow ingest + layer×step chart |
| M3.4 | Embedding scatter (t-SNE/UMAP payload) |
| M3.5 | Hidden state time series |
| M4 | XAI SHAP/LIME local·global·temporal |
| M5.3 | Step-by-step forward pass (graph tab) |

## 시나리오

### S1 — Internal metrics API

1. Run 생성
2. `POST /api/v1/runs/{id}/metrics/internal` — activation_map, gradient_flow, embedding, hidden_state batch ingest
3. `GET .../internal` — 전체 조회
4. `GET .../internal?kind=embedding` — 필터 조회
5. 잘못된 activation_map payload → 422

### S2 — XAI API

1. `POST /api/v1/runs/{id}/metrics/xai` — shap local, lime local, temporal batch ingest
2. `GET .../xai?method=shap&scope=local` — 필터 조회

### S3 — 3D architecture

1. ONNX graph import
2. `GET /api/v1/graphs/{id}/architecture/3d` — layers/nodes/edges 3D layout JSON

### S4 — SDK flush

1. `writer.add_activation_map`, `add_gradient_flow`, `add_embedding`, `add_hidden_state`
2. `writer.add_shap_local`, `add_lime_local` 후 `flush()`
3. internal + xai endpoint 호출 확인

### S5 — Dashboard

1. Graph 상세 **3D View** — OrbitControls WebGL 렌더
2. Graph 상세 **Step Forward** — 레이어별 activation 하이라이트
3. Run 상세 **Internal state** — heatmap / gradient / embedding / hidden charts
4. Run 상세 **XAI** — SHAP/LIME bar + temporal line

## 자동 시험

```bash
make test        # pytest 33
cd sdk && uv run pytest -v   # 5
make test-web
```
