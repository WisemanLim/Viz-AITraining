# impl/1st 시험 시나리오 — MVP Run API + Scalar Metrics (Epic E1/E2)

**PRD 근거**: §3.2 MVP P0 — REST API + SDK (log, list runs, get metrics), M1.1 Scalar Metrics, M6.3 API/SDK

## 케이스

| id | 목적 | 입력 | 기대결과 | 우선순위 |
|----|------|------|----------|----------|
| I1-01 | Run 생성 | POST `/api/v1/runs` `{name, params}` | 201, id·params 반환 | P0 |
| I1-02 | Run 목록 | GET `/api/v1/runs` | 200, total≥1 | P0 |
| I1-03 | Run 조회 | GET `/api/v1/runs/{id}` | 200 / 404 | P0 |
| I1-04 | Scalar ingest | POST `.../metrics/scalars` batch | 201, total=N | P0 |
| I1-05 | Scalar 조회 | GET `.../metrics/scalars?tag=loss` | 200, 필터링 | P0 |
| I1-06 | SDK 연동 | SummaryWriter.add_scalar + flush | API에 metric 저장 | P0 |
| I1-07 | edtech | PII 미수집 기본 | Run name만, 학습자 PII 없음 | P1 |

## edtech (COMPLIANCE.md)

- I1-07: MVP API는 학습자 PII 필드 없음 — name/params만 허용 (민감 데이터 업로드 금지 정책 준수)

## 실행

```bash
make test
cd backend && ENV=local uv run pytest -v
```

SDK 수동 검증 (API 실행 중):

```bash
make dev &
python -c "
from vizaitrain import SummaryWriter
with SummaryWriter(run_name='sdk-test') as w:
    w.add_scalar('loss', 0.1, 0)
    w.flush()
print('sdk ok')
"
```
