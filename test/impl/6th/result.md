# impl/6th 시험 결과 — 제한 해소 + PRD 재점검

**일시**: 2026-06-07  
**판정**: **PASS**

## 요약

| 항목 | 결과 |
|------|------|
| Legacy graph architecture fallback | graph_json 추정, 404 제거 |
| Artifact backfill API | POST `/graphs/{id}/artifact` |
| Full weight matrix | connections[].matrix [out×in] |
| Redis metrics pub/sub | `viz:metrics:live` channel |
| PyTorch VizCallback (M6.1) | sdk/vizaitrain/callbacks/pytorch.py |
| pytest | **23 passed** |
| sdk pytest | **2 passed** |
| frontend build | PASS |

## 케이스 결과

| id | 결과 |
|----|------|
| I6-01 | PASS `test_legacy_graph_architecture_fallback` |
| I6-02 | PASS `test_artifact_backfill` |
| I6-03 | PASS `test_full_weight_matrix_in_architecture` |
| I6-04 | PASS `test_redis_hub_publish` |
| I6-05 | PASS `test_health` metrics_transport |
| I6-06 | PASS sdk callback tests |
| I6-07 | PASS build |
| I6-08 | PASS build + backfill UI |
| I6-09 | PASS full regression |

## PRD MVP P0 — 완료

MVP §3.2 5항목 모두 충족. Phase 1.5+ (M1.3 profiling, M2.2 export PNG, M5 playground)은 잔여.

## 잔여 (Phase 1.5+)

- M1.3 GPU profiling timeline
- M2.2 architecture PNG/SVG export
- M6.1 `.pt` → ONNX export helper
- API key auth (M6.5 Phase 2)
