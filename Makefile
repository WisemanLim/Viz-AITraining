# Viz-AITraining — python-fastapi scaffold
# ENV: local (기본) | dev | staging | prod
#   local  — sqlite, compose 불필요, 빠른 로컬 반복
#   dev+   — postgres + redis + minio (make up 필요)

ROOT     := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
ENV      ?= local
ENV_FILE := $(ROOT)/.env.$(ENV)

.PHONY: help env-check sync sync-web dev dev-web test test-web up down build deploy seed-demo clean-web publish publish-build

help: ## 명령 목록 표시
	@echo "ENV=$(ENV)  (ENV_FILE=$(ENV_FILE))"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS=":.*?## "}; {printf "  make %-14s %s\n", $$1, $$2}'

env-check: ## 현재 ENV 및 .env.{ENV} 파일 존재 확인
	@echo "ENV=$(ENV)"
	@echo "ENV_FILE=$(ENV_FILE)"
	@test -f "$(ENV_FILE)" || (echo "ERROR: $(ENV_FILE) 없음. .env.example 을 복사하세요." && exit 1)

sync: ## backend + sdk 의존성 동기화 (uv sync)
	cd backend && uv sync
	cd sdk && uv sync

sync-web: ## frontend npm install
	cd frontend && npm install

clean-web: ## frontend .next 캐시 삭제 (Internal Server Error 시)
	rm -rf frontend/.next

dev: env-check ## API 실행 — 기본 local(sqlite), ENV=dev 시 postgres 등 연동
	@set -a; . "$(ENV_FILE)"; set +a; \
	cd backend && ENV=$(ENV) uv run uvicorn app.main:app \
		--reload --host $${API_HOST:-0.0.0.0} --port $${API_PORT:-8000}

dev-web: env-check sync-web ## Next.js dashboard (:3000)
	@set -a; . "$(ENV_FILE)"; set +a; \
	cd frontend && NEXT_PUBLIC_API_URL=http://localhost:$${API_PORT:-8000} \
		npm run dev -- -p $${WEB_PORT:-3000}

test: env-check ## pytest — 기본 ENV=local
	@set -a; . "$(ENV_FILE)"; set +a; \
	cd backend && ENV=$(ENV) uv run pytest

test-web: sync-web ## frontend lint + production build
	cd frontend && npm run lint && npm run build

seed-demo: env-check ## 샘플 experiment + metrics 생성 (대시보드 확인용)
	@set -a; . "$(ENV_FILE)"; set +a; \
	curl -sf -X POST "http://localhost:$${API_PORT:-8000}/api/v1/demo/seed" | python3 -m json.tool

up: env-check ## datastore 기동 — local 은 스킵, dev/staging 은 compose up
	@if [ "$(ENV)" = "local" ]; then \
		echo "INFO: ENV=local — sqlite 사용, compose 불필요."; \
		echo "      postgres/redis/minio 가 필요하면: ENV=dev make up"; \
	else \
		docker compose -f ops/docker-compose.yml --env-file "$(ENV_FILE)" up -d; \
	fi

down: ## compose 컨테이너 정리 (ENV=local 이면 안내 후 종료)
	@if [ "$(ENV)" = "local" ]; then \
		echo "INFO: ENV=local — 실행 중인 compose 서비스 없음."; \
	else \
		docker compose -f ops/docker-compose.yml --env-file "$(ENV_FILE)" \
			--profile app down --remove-orphans; \
	fi

build: env-check ## app Docker 이미지 빌드 (ENV=dev+)
	@if [ "$(ENV)" = "local" ]; then \
		echo "ERROR: ENV=local — build 는 ENV=dev 이상에서 실행하세요."; \
		exit 1; \
	else \
		docker compose -f ops/docker-compose.yml --env-file "$(ENV_FILE)" --profile app build; \
	fi

deploy: ## K8s Helm 배포 (ops/helm 구현 후)
	helm upgrade --install viz-ai-training ./ops/helm

publish: ## frontend 정적 export → 별도 GitHub Pages 저장소로 배포 (.env: DEPLOY_ACCOUNT/DEPLOY_REPO)
	bash scripts/publish-pages.sh

publish-build: ## 배포 없이 정적 export 산출물만 생성 (frontend/out)
	PUBLISH_BUILD_ONLY=1 DEPLOY_ACCOUNT=$(or $(DEPLOY_ACCOUNT),_) DEPLOY_REPO=$(or $(DEPLOY_REPO),viz-ai-training-pages) bash scripts/publish-pages.sh
