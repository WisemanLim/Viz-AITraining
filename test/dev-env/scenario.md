# 표준 환경 검증 시나리오 / Dev Environment Verification

## 전제

- Python 3.12+, [uv](https://docs.astral.sh/uv/) 설치
- (dev) Docker + Docker Compose

## 케이스

### 1. 의존성 설치

```bash
make sync
```

**기대**: `backend/.venv`, `sdk/.venv` 생성, exit 0

### 2. ENV 확인 (local)

```bash
make env-check
make help
```

**기대**: `ENV=local`, `.env.local` 존재

### 3. Local API (sqlite)

```bash
make dev
curl http://localhost:8000/health
```

**기대**: `{"status":"ok","env":"local",...}`

### 4. Infra 기동 (dev)

```bash
ENV=dev make up
docker compose -f ops/docker-compose.yml ps
```

**기대**: postgres, redis, minio `healthy` 또는 `running`

### 5. DB 연결 (dev — Phase 1.5)

```bash
ENV=dev make env-check
cd backend && ENV=dev uv run python -c "from app.core.config import settings; print(settings.database_url)"
```

**기대**: `postgresql://...` 출력

### 6. 단위 테스트

```bash
make test
```

**기대**: `test_health` PASS

### 7. OpenAPI

```bash
curl http://localhost:8000/docs
```

**기대**: Swagger UI 200

## edtech 추가 (Phase 2)

- [ ] a11y: Playground 키보드 내비게이션
- [ ] 만14세 미만 가입 차단 (보호자 동의 없음)
- [ ] 30 concurrent WebSocket metric clients, p95 latency ≤ 5s

## 로그

결과는 `test/dev-env/logs/` 에 저장 (gitignore).
