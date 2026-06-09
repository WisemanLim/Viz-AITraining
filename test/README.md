# 시험 표준 / Testing Standard

PRD 기반 시험 사이클: **시나리오 작성 → 시험 진행 → 오류 시 수정·재시험 → 결과 작성**

## 디렉터리

| 경로 | 용도 |
|------|------|
| `test/dev-env/` | 표준 환경 검증 (1회) |
| `test/impl/<Nth>/` | 구현 iteration별 시험 |
| `backend/tests/` | 단위·API 테스트 (pytest) |

## 러너

```bash
make sync    # uv sync
make up      # infra (dev)
make dev     # API
make test    # pytest
```

## edtech 추가 시험

`COMPLIANCE.md` §추가 시험 참조.
