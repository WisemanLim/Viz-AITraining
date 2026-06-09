# impl/8th 시험 시나리오 — Phase 2+ (M1.4, M2.2 PDF, M5.2)

## 범위

| PRD | 기능 |
|-----|------|
| M1.4 | Classical ML charts (learning curve, ROC, confusion matrix, feature importance) |
| M2.2 | Architecture PDF export |
| M5.2 | GAN Lab browser simulator |

## 시나리오

### S1 — Classical ML API

1. Run 생성
2. `POST /api/v1/runs/{id}/metrics/classical` — 4종 차트 batch ingest
3. `GET .../classical` — 전체 조회
4. `GET .../classical?chart_type=roc` — 필터 조회
5. 잘못된 ROC payload → 422

### S2 — PDF export

1. ONNX graph import
2. `GET /api/v1/graphs/{id}/architecture/export?format=pdf`
3. cairosvg 미설치 시 501, 설치 시 `%PDF` magic bytes

### S3 — SDK classical logging

1. `writer.add_learning_curve`, `add_roc_curve` 후 `flush()`
2. classical endpoint 호출 확인

### S4 — Dashboard

1. Run 상세 **Classical ML** 탭 — 차트 렌더
2. Graph 상세 **Export PDF** 링크
3. `/gan-lab` — Train → fake points 수렴·D/G loss 표시

## 자동 시험

```bash
make test        # pytest 29
cd sdk && uv run pytest -v   # 4
make test-web
```
