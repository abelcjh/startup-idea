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

## 🚀 Day 1 Quick Start

Ensure you have **Node.js 20+**, **Python 3.11+**, **pnpm 9+**, and **Docker** installed.

### 1. Environment Setup
Copy the environment variable templates for both the app and the infrastructure:
```bash
cp .env.example .env.local
cp docker/.env.example docker/.env