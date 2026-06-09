# impl/10th 시험 시나리오 — Phase 4+ (선택)

## 범위

| PRD | 기능 |
|-----|------|
| M4.2 | Temporal XAI 대시보드 고도화 (heatmap, scrubber, playback, rank delta) |
| — | sklearn/SHAP 자동 어댑터 (`vizaitrain.xai_adapter`) |
| M2.3+ | 3D edge weight pulse / flow particle 애니메이션 |

## 시나리오

### S1 — Temporal XAI dashboard

1. Run에 `scope=temporal` XAI attribution ingest (≥2 checkpoints)
2. Run 상세 **XAI** 탭 — Temporal dashboard 섹션 표시
3. Step slider / Play / ← → 로 snapshot bar chart 갱신
4. Feature×step heatmap, rank change (first→last) 표시

### S2 — SDK xai_adapter

1. `from_shap_values`, `from_shap_temporal_checkpoints` payload 단위 테스트
2. `writer.add_shap_temporal`, `add_shap_global` flush
3. (선택) `uv sync --group xai` 후 `explain_shap_local(model, X)` 수동 검증

### S3 — 3D weight animation

1. Graph **3D View** — edge opacity/color pulse
2. **Animate weights** 토글 on/off

## 자동 시험

```bash
make test        # pytest 33
cd sdk && uv run pytest -v   # 10
make test-web
```
