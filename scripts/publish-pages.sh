#!/usr/bin/env bash
# publish-pages.sh — frontend(Next.js dashboard)를 정적 HTML/CSS/JS 로 빌드해
# 별도 GitHub Pages 저장소로 배포한다. `make publish` 진입점.
#
# 동작:
#   1. frontend 정적 export (next.config: output 'export', basePath=/<repo>)
#   2. DEPLOY_ACCOUNT 토큰 확보(gh) → deploy 저장소 clone → out/ 복사 → commit → push
#
# 설정(.env / .env.local 또는 환경변수):
#   DEPLOY_ACCOUNT   GitHub Pages 소유 계정 (예: WisemanLim)
#   DEPLOY_REPO      Pages 저장소명     (예: viz-ai-training-pages) → basePath = /<DEPLOY_REPO>
#   DEPLOY_BRANCH    배포 브랜치        (기본: main)
#   GIT_USER_NAME / GIT_USER_EMAIL  커밋 작성자 (선택)
#
# 사용:
#   make publish
#   DEPLOY_REPO=viz-ai-training-pages make publish
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

info()  { printf '\033[36m[publish]\033[0m %s\n' "$*"; }
ok()    { printf '\033[32m[publish]\033[0m %s\n' "$*"; }
warn()  { printf '\033[33m[publish]\033[0m %s\n' "$*"; }
err()   { printf '\033[31m[publish]\033[0m %s\n' "$*" >&2; }

# ── .env 로드 (있으면) ────────────────────────────────────────────────────────
for f in .env .env.local; do
  if [ -f "${ROOT_DIR}/${f}" ]; then
    set -a; . "${ROOT_DIR}/${f}"; set +a
  fi
done

DEPLOY_ACCOUNT="${DEPLOY_ACCOUNT:-}"
DEPLOY_REPO="${DEPLOY_REPO:-}"
DEPLOY_BRANCH="${DEPLOY_BRANCH:-main}"

if [ -z "${DEPLOY_ACCOUNT}" ] || [ -z "${DEPLOY_REPO}" ]; then
  err "DEPLOY_ACCOUNT / DEPLOY_REPO 미설정 — .env 또는 환경변수로 지정하세요."
  err "  예) DEPLOY_ACCOUNT=WisemanLim DEPLOY_REPO=viz-ai-training-pages make publish"
  exit 1
fi

BASE_PATH="/${DEPLOY_REPO}"
WEB_DIR="${ROOT_DIR}/frontend"
OUT_DIR="${WEB_DIR}/out"

# ── 1. 정적 export 빌드 ───────────────────────────────────────────────────────
if [ ! -d "${WEB_DIR}/node_modules" ]; then
  info "frontend 의존성 설치 (npm install)"
  (cd "${WEB_DIR}" && npm install)
fi

info "정적 export 빌드 (basePath=${BASE_PATH})"
rm -rf "${OUT_DIR}" "${WEB_DIR}/.next"
# NEXT_PUBLIC_STATIC_EXPORT 로 next.config 의 output:'export' + basePath 활성화.
# NODE_ENV 강제 production — dev 모드 export 시 pages _error 끌어와 실패 가능.
(cd "${WEB_DIR}" && \
  NODE_ENV=production \
  NEXT_PUBLIC_STATIC_EXPORT=true \
  NEXT_PUBLIC_BASE_PATH="${BASE_PATH}" \
  npm run build)

if [ ! -d "${OUT_DIR}" ]; then
  err "export 산출물 없음: ${OUT_DIR} (next.config 의 output:'export' 확인)"
  exit 1
fi

# Jekyll 비활성화 — _next/ 디렉터리(언더스코어 시작)가 무시되지 않도록.
touch "${OUT_DIR}/.nojekyll"
ok "빌드 완료 → ${OUT_DIR}"

# 배포 없이 산출물만 원할 때 (make publish-build) 여기서 종료.
if [ "${PUBLISH_BUILD_ONLY:-}" = "1" ]; then
  ok "build-only 모드 — 배포 생략 (산출물: ${OUT_DIR})"
  exit 0
fi

# ── 2. deploy 토큰 확보 (gh) ──────────────────────────────────────────────────
# gh auth switch 는 GH_TOKEN/GITHUB_TOKEN env 설정 시 거부됨 → 해제.
unset GH_TOKEN GITHUB_TOKEN 2>/dev/null || true

deploy_token=""
if command -v gh &>/dev/null; then
  active_now="$(gh api user --jq .login 2>/dev/null || true)"
  if [ "${active_now}" != "${DEPLOY_ACCOUNT}" ]; then
    if gh auth status 2>&1 | grep -qwF "${DEPLOY_ACCOUNT}"; then
      info "gh 계정 전환 → ${DEPLOY_ACCOUNT}"
      gh auth switch -u "${DEPLOY_ACCOUNT}" >/dev/null 2>&1 || true
    else
      err "${DEPLOY_ACCOUNT} 가 gh 에 인증돼 있지 않음 — 'gh auth login' (${DEPLOY_ACCOUNT}) 실행"
      exit 1
    fi
  fi
  deploy_token="$(gh auth token 2>/dev/null || true)"
fi

if [ -z "${deploy_token}" ]; then
  err "${DEPLOY_ACCOUNT} 토큰 확보 실패 — gh CLI 인증 확인"
  exit 1
fi

DEPLOY_URL="https://github.com/${DEPLOY_ACCOUNT}/${DEPLOY_REPO}.git"
DEPLOY_TMP="$(mktemp -d "${TMPDIR:-/tmp}/viz-ai-pages-XXXXXX")"

# GIT_ASKPASS 로 토큰 주입 — credential-helper 캐시 우회.
askpass="$(mktemp "${TMPDIR:-/tmp}/git-askpass-XXXXXX")"
cat > "${askpass}" <<'ASKPASS'
#!/bin/sh
case "$1" in *sername*) printf 'x-access-token' ;; *) printf '%s' "${_GIT_TOKEN}" ;; esac
ASKPASS
chmod 700 "${askpass}"
trap 'rm -rf "${DEPLOY_TMP}"; rm -f "${askpass}"' EXIT
export _GIT_TOKEN="${deploy_token}" GIT_ASKPASS="${askpass}" GIT_TERMINAL_PROMPT=0

# ── 3. deploy 저장소 clone / init ─────────────────────────────────────────────
info "deploy 저장소: ${DEPLOY_URL} (branch: ${DEPLOY_BRANCH})"
if ! git clone --depth 1 --branch "${DEPLOY_BRANCH}" "${DEPLOY_URL}" "${DEPLOY_TMP}" 2>/dev/null; then
  warn "clone 실패 — 빈 저장소 초기화"
  rm -rf "${DEPLOY_TMP}"; mkdir -p "${DEPLOY_TMP}"
  git -C "${DEPLOY_TMP}" init -q
  git -C "${DEPLOY_TMP}" checkout -q -b "${DEPLOY_BRANCH}"
  git -C "${DEPLOY_TMP}" remote add origin "${DEPLOY_URL}"
fi

# ── 4. 산출물 동기화 ─────────────────────────────────────────────────────────
find "${DEPLOY_TMP}" -maxdepth 1 ! -name '.git' ! -path "${DEPLOY_TMP}" -exec rm -rf {} + 2>/dev/null || true
cp -rp "${OUT_DIR}/." "${DEPLOY_TMP}/"

git -C "${DEPLOY_TMP}" config user.name  "${GIT_USER_NAME:-viz-ai-training-bot}"
git -C "${DEPLOY_TMP}" config user.email "${GIT_USER_EMAIL:-viz-ai-training-bot@users.noreply.github.com}"
git -C "${DEPLOY_TMP}" add -A

if git -C "${DEPLOY_TMP}" diff --cached --quiet; then
  ok "변경 없음 — 배포 생략"
else
  git -C "${DEPLOY_TMP}" commit -q -m "chore: publish Viz-AITraining web $(date '+%Y-%m-%d %H:%M %Z')"
  info "push → ${DEPLOY_ACCOUNT}/${DEPLOY_REPO}:${DEPLOY_BRANCH}"
  if ! git -C "${DEPLOY_TMP}" push -u origin "${DEPLOY_BRANCH}" 2>&1; then
    err "push 실패 — ${DEPLOY_ACCOUNT} 가 ${DEPLOY_ACCOUNT}/${DEPLOY_REPO} 쓰기 권한 있는지 확인"
    exit 1
  fi
fi

unset _GIT_TOKEN GIT_ASKPASS GIT_TERMINAL_PROMPT
echo ""
ok "배포 완료"
echo "  Repo  → https://github.com/${DEPLOY_ACCOUNT}/${DEPLOY_REPO}"
echo "  Pages → https://${DEPLOY_ACCOUNT}.github.io/${DEPLOY_REPO}/"
echo ""
echo "  최초 배포 시 GitHub → Settings → Pages → Source: 'Deploy from a branch',"
echo "  Branch: ${DEPLOY_BRANCH} /(root) 로 설정하세요."
