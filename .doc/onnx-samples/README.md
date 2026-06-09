# ONNX Import 시험용 샘플

대시보드 **Import ONNX model** (`/runs/{id}` 하단 또는 `/graphs`) 수동 시험용 ONNX 파일입니다.

| 파일 | 설명 | 노드(대략) | 용도 |
|------|------|------------|------|
| `01_minimal_identity.onnx` | Input → Identity → Output | Input, Identity, Output | 업로드·파싱 smoke test |
| `02_tiny_mlp.onnx` | Gemm → Relu → Gemm (4→8→2) | Input, Gemm×2, Relu | **Architecture / 3D / Step Forward** 레이어 시각화 |
| `03_tiny_cnn.onnx` | Conv → Relu → GAP → Flatten → Gemm | Conv, Relu, Pool, Flatten, Gemm | CNN 스타일 그래프·가중치 뷰 |
| `99_invalid_not_onnx.bin` | ONNX 아님 | — | **422** 오류 확인용 (`.onnx`로 rename 시 422, 그대로면 확장자 400) |

모든 유효 샘플은 **50MB 미만**, opset **13** 기준입니다.

---

## 1. 샘플 재생성

```bash
cd backend && uv run python ../.doc/onnx-samples/generate_samples.py
```

의존성: `backend` uv 환경 (`onnx`, `numpy`).

---

## 2. 대시보드 UI 시험

1. `make dev` + `make dev-web` 실행
2. 홈에서 **Create demo run** 또는 기존 run 선택
3. Run 상세 하단 **Model graphs** → **Choose file**
4. `.doc/onnx-samples/02_tiny_mlp.onnx` 업로드
5. 목록에 graph 링크 생성 확인 → 클릭 후 **Neural / 3D View / Step Forward** 탭 확인

---

## 3. API(curl) 시험

```bash
# run에 연결해 import
RUN_ID="<your-run-id>"
curl -sf -X POST "http://localhost:8000/api/v1/graphs" \
  -F "run_id=${RUN_ID}" \
  -F "file=@.doc/onnx-samples/02_tiny_mlp.onnx" | python3 -m json.tool

# run에 연결된 graph 목록
curl -sf "http://localhost:8000/api/v1/runs/${RUN_ID}/graphs" | python3 -m json.tool
```

demo run id 확인:

```bash
curl -sf http://localhost:8000/api/v1/runs | python3 -m json.tool
```

---

## 4. 기대 결과

| 시나리오 | 기대 HTTP | UI |
|----------|-----------|-----|
| `01_minimal_identity.onnx` | 201 | graph 1건, node ≥ 2 |
| `02_tiny_mlp.onnx` | 201 | Architecture에 fc1/relu1/fc2 |
| `03_tiny_cnn.onnx` | 201 | Conv·GAP·FC 체인 표시 |
| `99_invalid_not_onnx.bin` | 400 | 확장자 거부 (`.onnx` 아님) |
| 임의 `.onnx`에 garbage bytes | 422 | Invalid ONNX |

---

## 5. 참고

- 파서 구현: `backend/app/services/onnx_graph.py`
- 업로드 API: `POST /api/v1/graphs` (multipart `file`, optional `run_id`)
- pytest fixture와 동일 패턴: `backend/tests/fixtures_onnx.py` (`01_minimal_identity`와 동일 구조)

---

## 출처 / 근거

- [ONNX Python API — helper / ModelProto](https://onnx.ai/onnx/api/helper.html)
- 프로젝트 PRD M2 ONNX graph import: [.doc/PRD.md](../PRD.md)
