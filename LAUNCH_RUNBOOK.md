# ProductOS — Launch Runbook

## Prerequisites

- Node.js 20+, pnpm 9+
- Python 3.11+ with `uv` (`pip install uv`)
- Docker Desktop running

## One-Time Setup

```bash
# 1. Install JS deps + boot Docker (Postgres, Redis, LiteLLM) + push schema + seed
pnpm setup
```

```bash
# 2. Install Python deps
cd apps/api && uv pip install --system ".[dev]" && cd ../..
```

```bash
# 3. Copy environment variables
cp .env.example .env.local
cp docker/.env.example docker/.env
```

## Boot Everything

```bash
# Starts Next.js (:3000) + FastAPI (:8000) + Arq worker — all concurrent
pnpm dev
```

## Verify

| Service          | URL                               |
| ---------------- | --------------------------------- |
| Next.js frontend | http://localhost:3000              |
| FastAPI docs     | http://localhost:8000/docs         |
| FastAPI health   | http://localhost:8000/healthz      |
| MCP SSE          | http://localhost:8000/mcp/sse      |
| Supabase Studio  | http://localhost:54323             |

## Useful Commands

| Command              | Description                        |
| -------------------- | ---------------------------------- |
| `pnpm dev:web`       | Start only Next.js                 |
| `pnpm dev:api`       | Start only FastAPI                 |
| `pnpm dev:worker`    | Start only Arq worker              |
| `pnpm db:push`       | Push Prisma schema to DB           |
| `pnpm db:seed`       | Re-run seed script                 |
| `pnpm db:reset`      | Push schema + seed (destructive)   |
| `pnpm docker:up`     | Start Docker infra                 |
| `pnpm docker:down`   | Stop Docker infra                  |
| `pnpm lint`          | Lint all workspaces                |
| `pnpm test`          | Test all workspaces                |
