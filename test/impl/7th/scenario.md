# impl/7th 시험 시나리오 — Phase 1.5+ (M1.3, M2.2, M5.1)

**PRD 근거**: M1.3 profiling timeline, M2.2 PNG/SVG export, M5.1 Playground

## 케이스

| id | 목적 | 기대결과 | P |
|----|------|----------|---|
| I7-01 | Profile ingest | POST profile events 201 | P0 |
| I7-02 | Timeline report | bottleneck phase per epoch | P0 |
| I7-03 | SVG export | GET export?format=svg | P0 |
| I7-04 | PNG export | svg or 501 without cairosvg | P0 |
| I7-05 | SDK add_profile | flush to API | P0 |
| I7-06 | Playground UI | /playground build | P0 |
| I7-07 | Run profiling tab | ProfileTimelinePanel | P0 |
| I7-08 | 회귀 | pytest 26+ build PASS | P0 |

## 실행

```bash
make test
cd sdk && uv run pytest
make test-web
# http://localhost:3000/playground
```
