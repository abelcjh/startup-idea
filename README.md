# 🦄 ProductOS

**The "Cursor for Product Management."** An AI-native, enterprise-grade product discovery platform that automates the loop from customer feedback to technical Jira implementation.

## 🏗️ Architecture

ProductOS is a full-stack monorepo managed by Turborepo, designed for strict SOC2 compliance, multi-tenancy, and autonomous AI orchestration.

| Layer | Technologies Used | Purpose |
|---|---|---|
| **Frontend** | Next.js 15, Tailwind, Aceternity UI, Zustand | Awe-inspiring dashboard and PRD viewer |
| **API Gateway** | FastAPI, Python 3.12+, Pydantic v2 | High-performance, strictly typed backend |
| **AI Brain** | LangGraph, LlamaIndex, Mistral | Multi-agent reasoning and RAG pipeline |
| **Data/State** | Supabase (PostgreSQL + pgvector), Prisma | Zero-trust RLS tenant data and embeddings |
| **Background** | Arq, Redis | Async queues for long-running LangGraph jobs |
| **Security** | Microsoft Presidio, Structlog | Strict PII scrubbing and JSON audit trails |
| **Agent Handoff**| Anthropic MCP SDK (over SSE) | Exposes PRDs directly to IDEs (Cursor/Claude) |

---

## 🚀 Quick Start

### Prerequisites

- Node.js 20+, pnpm 9+
- Python 3.11+ (pip or uv)
- Docker Desktop (optional — only for Path B below)

### 1. Database: Supabase + pgvector

ProductOS requires **PostgreSQL with pgvector**. Choose one:

**Path A — Supabase Cloud (no Docker):**

1. Create a free project at [supabase.com](https://supabase.com).
2. **Enable extensions** — Supabase Dashboard → SQL Editor → run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   ```
3. In **Project Settings → API Keys**: copy `SUPABASE_PUBLISHABLE_KEY` (anon) and `SUPABASE_SECRET_KEY` (service role).

4. In **Project Overview**:
   - **Project URL** → use for `DATABASE_URL`
   - **Connection string** (pooled or direct) → use for `DIRECT_URL`
5. Put values in `.env.local` (step 2).

**Path B — Local Docker (Supabase stack):**

1. Start Docker Desktop.
2. Run `pnpm docker:up` — starts Postgres (with pgvector), Redis, LiteLLM, Supabase Studio.
3. `.env.local` uses `DIRECT_URL=postgresql://postgres:postgres@localhost:54322/postgres`.
4. Use demo JWTs from `docker/.env.example` for `SUPABASE_PUBLISHABLE_KEY` and `SUPABASE_SECRET_KEY`.

### 2. Environment & install

```bash
# Copy environment variables
cp .env.example .env.local
cp docker/.env.example docker/.env
```

Edit `.env.local` and set `DATABASE_URL`, `DIRECT_URL`, and Supabase keys per your chosen path.

```bash
# Install deps + push schema + seed
pnpm install
pnpm db:push
pnpm db:generate
pnpm db:seed
```

```bash
# Install Python deps (from repo root)
cd apps/api && pip install -e ".[dev]" && cd ../..
```

If using Docker: `pnpm setup` replaces the install step (runs `docker:up` + `db:push` + `db:generate` + `db:seed`).

### 3. Boot

```bash
# Starts Next.js (:3000) + FastAPI (:8000) + Arq worker — all concurrent
pnpm dev
```

### 4. Verify

| Service          | URL                       |
| ---------------- | ------------------------- |
| Next.js frontend | http://localhost:3000     |
| FastAPI docs     | http://localhost:8000/docs |
| FastAPI health   | http://localhost:8000/healthz |
| MCP SSE          | http://localhost:8000/mcp/sse |
| Supabase Studio  | http://localhost:54323    |

---

## Commands

| Command            | Description                      |
| ------------------ | -------------------------------- |
| `pnpm dev`         | Start all services               |
| `pnpm dev:web`     | Start only Next.js               |
| `pnpm dev:api`     | Start only FastAPI               |
| `pnpm dev:worker`  | Start only Arq worker             |
| `pnpm db:push`     | Push Prisma schema to DB         |
| `pnpm db:seed`     | Re-run seed script               |
| `pnpm db:reset`    | Push schema + seed (destructive)  |
| `pnpm docker:up`   | Start Docker infra               |
| `pnpm docker:down` | Stop Docker infra                |
| `pnpm lint`        | Lint all workspaces              |
| `pnpm test`        | Test all workspaces              |
