# impl/3rd 시험 시나리오 — Web Dashboard Core (Epic E3)

**PRD 근거**: §3.2 MVP P0 #2 — Web 대시보드 run 목록, loss/metric 실시간 차트; Epic E3 Run list, live metric charts

## 케이스

| id | 목적 | 입력 | 기대결과 | 우선순위 |
|----|------|------|----------|----------|
| I3-01 | Run 목록 UI | GET `/api/v1/runs` (4s polling) | 테이블에 run 표시 | P0 |
| I3-02 | Run 상세 | `/runs/{id}` | name, params, 링크 | P0 |
| I3-03 | Scalar 차트 | GET scalars | tag별 LineChart | P0 |
| I3-04 | Histogram 차트 | GET histograms | tag별 BarChart (latest step) | P0 |
| I3-05 | Live refresh | 4s interval | PRD M1.1 ≤5s 목표 충족 | P0 |
| I3-06 | CORS | Origin localhost:3000 | preflight 200 | P0 |
| I3-07 | Frontend build | `npm run lint && npm run build` | PASS | P0 |
| I3-08 | Backend 회귀 | pytest | 9 passed | P0 |

## edtech (COMPLIANCE.md)

- 대시보드는 run name·집계 metric만 표시 — 학습자 PII 필드 없음

## 실행

```bash
# 터미널 1
make dev

# 터미널 2
make dev-web

# 자동 시험
make test       # 9 passed
make test-web   # lint + build PASS
```

브라우저: http://localhost:3000

SDK로 데이터 생성 후 대시보드에서 확인:

```bash
python -c "
from vizaitrain import SummaryWriter
with SummaryWriter(run_name='dashboard-demo', params={'lr':0.001}) as w:
    for i in range(5):
        w.add_scalar('loss', 1.0/(i+1), global_step=i)
        w.add_scalar('accuracy', 0.5+i*0.1, global_step=i)
    w.add_histogram_from_values('layer/w', [0.1,0.3,0.7,0.9], bins=4, global_step=0)
"
```
