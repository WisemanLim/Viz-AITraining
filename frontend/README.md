# Viz-AITraining Dashboard (Next.js)

Epic **E3 + E4 + M1.1/M1.2** — Run list, WebSocket live metrics, multi-run compare, histogram view, ONNX + neural network visualization.

## Prerequisites

- API running: `make dev` (port 8000)
- Node.js 20+ (verified with Next.js 15)

## Quick start

```bash
make sync-web
make dev-web
```

Open http://localhost:3000

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | FastAPI backend |
| `WEB_PORT` | `3000` | Dev server port (Makefile) |

Copy `frontend/.env.example` → `frontend/.env.local` if needed.

Backend must allow CORS: `CORS_ORIGINS=http://localhost:3000` in `.env.local`.

WebSocket URL is derived from `NEXT_PUBLIC_API_URL` (`http` → `ws`).

## Features (MVP)

- **Run list** — auto-refresh every 4s
- **Run detail** — WebSocket live scalars (polling fallback), Recharts line/histogram charts
- **Compare** — `/compare` multi-run overlay charts + param diff table
- **ONNX graphs** — `/graphs` upload + React Flow operations viewer
- **Neural Network tab** — MLP-style SVG (glowing nodes, weight labels, formulas)
- **Run-linked graphs** — import from run detail page

## Scripts

```bash
npm run dev      # development (turbopack)
npm run build    # production build
npm run lint     # ESLint
```

## Backlog

- Redis-backed WebSocket fan-out
- Full weight matrix heatmap on neural edges
- PyTorch `.pt` export (M6.1)
