# impl/2nd 시험 시나리오 — Histogram Metrics (M3.1, Epic E2 확장)

**PRD 근거**: §3.2 MVP P0 — PyTorch SummaryWriter 호환 (scalar + histogram), M3.1 Histogram ingest

## 케이스

| id | 목적 | 입력 | 기대결과 | 우선순위 |
|----|------|------|----------|----------|
| I2-01 | Histogram ingest | POST `.../metrics/histograms` batch | 201, bin_edges/counts 반환 | P0 |
| I2-02 | Histogram 조회 | GET `.../metrics/histograms?tag=` | 200, 필터링 | P0 |
| I2-03 | 스키마 검증 | counts 길이 ≠ bin_edges-1 | 422 | P0 |
| I2-04 | Run 없음 | POST missing run_id | 404 | P0 |
| I2-05 | SDK histogram | add_histogram + add_histogram_from_values + flush | API 저장 | P0 |
| I2-06 | 회귀 | 기존 scalar API | 8 pytest PASS | P0 |

## edtech (COMPLIANCE.md)

- Histogram은 가중치 분포 등 **집계 통계**만 저장 — 원시 학습자 데이터·PII 미포함

## 실행

```bash
make test   # 8 passed
```

SDK 수동 검증 (API 실행 중):

```bash
make dev &
python -c "
from vizaitrain import SummaryWriter
with SummaryWriter(run_name='hist-sdk') as w:
    w.add_histogram_from_values('layer/w', [0.1, 0.2, 0.9, 0.8], bins=4, global_step=0)
    w.flush()
print('histogram sdk ok')
"
