# Unified Workflow — Architecture Audit & Improvement Plan

**Date:** 2026-10-21
**Status:** Partially implemented — critical fixes applied, structural refactoring recommended

---

## 1. Current Architecture Summary

The Unified Workflow ecosystem consists of **three independent services** that communicate via HTTP:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Evershade Valley (Port 8080)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐ │
│  │ FastAPI App  │  │  Agent Runner│  │  255 Route Handlers   │ │
│  │ (api.py)     │  │  (runner.py) │  │  (all in api.py)      │ │
│  └──────┬───────┘  └──────┬───────┘  └───────────┬───────────┘ │
│         │                 │                       │             │
│  ┌──────▼─────────────────▼───────────────────────▼───────────┐ │
│  │              Provider Layer                                 │ │
│  │  ┌──────────┐  ┌────────────┐  ┌────────────────────┐     │ │
│  │  │ Junie    │  │ Polter   │  │   Spectra        │     │ │
│  │  │ (subproc)│  │ (HTTP)     │  │   (HTTP)           │     │ │
│  │  └──────────┘  └────────────┘  └────────────────────┘     │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────┬──────────────────────────────┬───────────────────┘
               │ HTTP                         │ HTTP
               ▼                              ▼
┌──────────────────────────┐    ┌──────────────────────────────────┐
│    Polter (Port 8000)  │    │     Spectra (Port 3000)        │
│  ┌────────────────────┐  │    │  ┌────────────────────────────┐  │
│  │ FastAPI Service    │  │    │  │ Fastify (TypeScript/Node)  │  │
│  │ - Chat completions │  │    │  │ - Scrape / Crawl / Search  │  │
│  │ - Task management  │  │    │  │ - Batch / Extract / Agent  │  │
│  │ - Worker registry  │  │    │  │ - Interact / Map           │  │
│  │ - SQLite storage   │  │    │  └────────────┬───────────────┘  │
│  │ - Worktree isol.   │  │    │               │                  │
│  └────────────────────┘  │    │  ┌────────────▼───────────────┐  │
│                          │    │  │  Redis (BullMQ queues)     │  │
│                          │    │  │  + Worker process           │  │
│                          │    │  └────────────────────────────┘  │
└──────────────────────────┘    └──────────────────────────────────┘
```

### Service Responsibilities

| Service | Language | Framework | Port | Primary Responsibility |
|---------|----------|-----------|------|----------------------|
| **Evershade Valley** | Python | FastAPI | 8080 | Central API, agent orchestration, dashboard, cross-service integration |
| **Polter** | Python | FastAPI | 8000 | Junie CLI execution, worktree isolation, task persistence |
| **Spectra** | TypeScript | Fastify | 3000 | Web scraping, crawling, search, browser automation |
| **Redis** | — | — | 6379 | Job queues for Spectra (BullMQ) |

### Data Flow

1. **User → Evershade Valley**: API request to run an agent task
2. **Evershade Valley → Provider**: Resolves the runner type (junie/Polter/Spectra)
3. **Provider → Service**: HTTP call to Polter or Spectra (or local subprocess for Junie)
4. **Service → Execution**: Polter runs Junie CLI; Spectra processes via Redis queues
5. **Result → User**: Response flows back through the same path

### Communication Protocols

| From | To | Protocol | Auth |
|------|-----|----------|------|
| Evershade Valley | Polter | HTTP/JSON | Bearer token |
| Evershade Valley | Spectra | HTTP/JSON | Bearer token |
| Evershade Valley | Junie CLI | Subprocess | None (local) |
| Spectra API | Redis | BullMQ | None (internal) |
| Spectra Worker | Redis | BullMQ | None (internal) |

---

## 2. Dependency Map

```
Evershade Valley
  ├── fastapi, uvicorn, pyyaml, httpx, requests (Python)
  ├── Polter (HTTP, optional — graceful fallback)
  ├── Spectra (HTTP, optional — graceful fallback)
  └── Junie CLI (subprocess, optional — for "junie" runner)

Polter
  ├── fastapi, uvicorn, httpx, python-dotenv (Python)
  └── Junie CLI (subprocess, required)

Spectra
  ├── fastify, bullmq, playwright, ioredis, cheerio (Node.js)
  └── Redis (required for queues)

Redis
  └── (standalone — no dependencies)
```

---

## 3. Confirmed Problems & Issues

### Critical

| # | Problem | Impact | File(s) |
|---|---------|--------|---------|
| **C1** | `api.py` is a 290KB monolith with 255 route handlers | Unmaintainable, hard to test, single point of failure | `Evershade Valley/hub/api.py` |
| **C2** | Deprecated `asyncio.get_event_loop()` in providers | Breaks on Python 3.12+, runtime errors | `Polter_provider.py`, `Spectra_provider.py` |
| **C3** | Docker-compose `depends_on` lacks health conditions | Evershade Valley starts before dependencies are ready | `docker-compose.yml` |

### High

| # | Problem | Impact | File(s) |
|---|---------|--------|---------|
| **H1** | All feature stores are in-memory only | Data lost on restart (webhooks, analytics, RBAC, etc.) | `api.py` |
| **H2** | No unified startup script | Users must manually start 3+ services | Missing |
| **H3** | No Evershade Valley `.env` file | Environment config scattered across services | Missing |
| **H4** | No shared logging format | Hard to debug cross-service issues | All services |
| **H5** | Provider `run()` is sync but wraps async | Complex event loop juggling, potential deadlocks | Both providers |

### Medium

| # | Problem | Impact | File(s) |
|---|---------|--------|---------|
| **M1** | Duplicate health check endpoints | 3 separate `/health` endpoints, no aggregation | All services |
| **M2** | No version pinning alignment | Evershade Valley httpx 0.27.0 vs Polter 0.27.2 | requirements.txt |
| **M3** | `app.py` is a simple task manager, not the app entry | Confusing naming — actual app is in `api.py` | `Evershade Valley/hub/app.py` |
| **M4** | No `.gitignore` at root level | Root-level temp files may be committed | Missing |
| **M5** | Spectra worker has no health check | Docker can't verify worker is alive | `docker-compose.yml` |

### Low

| # | Problem | Impact | File(s) |
|---|---------|--------|---------|
| **L1** | Multiple `.junie/plans/` directories | Plan sprawl across services | All services |
| **L2** | No root-level `README` architecture diagram | Onboarding requires reading 3 READMEs | `README.md` |
| **L3** | `orchestrator.py` is a thin wrapper | Unnecessary indirection | `Polter/orchestrator.py` |

---

## 4. Architectural Alternatives Evaluation

### Option A: Current Multi-Repo Architecture (Status Quo)
- **Pros**: Independent deployment, language freedom, clear service boundaries
- **Cons**: Monolithic api.py, no unified startup, data loss on restart
- **Verdict**: Correct high-level approach, needs internal improvements

### Option B: Monorepo
- **Pros**: Unified CI/CD, shared types, easier refactoring
- **Cons**: Different languages (Python + TypeScript), different package managers, larger build times
- **Verdict**: Not worth the complexity for 3 services

### Option C: Evershade Valley as Library + Thin Gateway
- **Pros**: Separates business logic from HTTP layer
- **Cons**: Major refactor, breaks existing deployment
- **Verdict**: Too risky without clear benefit

### Option D: Modularize Evershade Valley api.py (Recommended)
- **Pros**: Maintains current architecture, improves maintainability, incremental
- **Cons**: Requires careful refactoring of 290KB file
- **Verdict**: **Best balance of risk vs. reward**

---

## 5. Recommended Target Architecture

```
Evershade Valley/
├── hub/
│   ├── api/                    # ← NEW: Route modules (split from api.py)
│   │   ├── __init__.py
│   │   ├── agents.py           # Agent CRUD, runs, status
│   │   ├── sessions.py         # Session management
│   │   ├── memory.py           # Memory operations
│   │   ├── coordinator.py      # Multi-agent coordination
│   │   ├── integration.py      # Polter/Spectra proxy endpoints
│   │   ├── webhooks.py         # Webhook event system
│   │   ├── notifications.py    # Notification channels
│   │   ├── analytics.py        # Analytics & usage tracking
│   │   ├── export.py           # Data export/import
│   │   ├── api_keys.py         # API key management
│   │   ├── rate_limit.py       # Rate limiting
│   │   ├── audit_log.py        # Audit logging
│   │   ├── templates.py        # Template management
│   │   ├── approvals.py        # Approval workflows
│   │   ├── files.py            # File storage
│   │   ├── rbac.py             # RBAC roles & users
│   │   ├── jobs.py             # Background job queue
│   │   ├── cache.py            # Response caching
│   │   ├── messages.py         # Internal message bus
│   │   ├── flags.py            # Feature flags
│   │   ├── deployments.py      # Deployment management
│   │   ├── circuit_breaker.py  # Circuit breaker
│   │   ├── versioning.py       # API versioning
│   │   ├── dag.py              # DAG task execution
│   │   ├── tenants.py          # Multi-tenancy
│   │   ├── schedules.py        # Scheduled pipelines
│   │   ├── search.py           # Unified search
│   │   ├── batch.py            # Parallel batch execution
│   │   ├── pipeline.py         # Cross-service pipelines
│   │   ├── dashboard.py        # Unified dashboard
│   │   ├── streaming.py        # SSE streaming
│   │   └── websocket.py        # WebSocket feed
│   ├── api.py                  # ← THIN: App factory + imports from api/
│   ├── providers.py            # Provider abstraction
│   ├── Polter_provider.py    # Polter HTTP provider
│   ├── Spectra_provider.py   # Spectra HTTP provider
│   ├── runner.py               # Agent execution engine
│   ├── coordinator.py          # Multi-agent coordination
│   ├── config.py               # Configuration management
│   └── ... (other modules)
```

---

## 6. Prioritized Implementation Plan

### Phase 1: Critical Fixes (IMPLEMENTED ✓)
- [x] Fix docker-compose health check dependencies
- [x] Fix deprecated asyncio patterns in providers
- [x] Update root .env.example with documentation

### Phase 2: Stability & Operations (PARTIAL)
- [x] Add health checks to all docker-compose services
- [ ] Create unified startup script (`start.sh` / `start.ps1`)
- [ ] Add Evershade Valley `.env` support
- [ ] Align dependency versions across services
- [ ] Add root-level `.gitignore`

### Phase 3: api.py Modularization (RECOMMENDED — HIGH EFFORT)
- [ ] Split api.py into route modules under `hub/api/`
- [ ] Make api.py a thin app factory that imports route modules
- [ ] Migrate in-memory stores to shared persistence layer
- [ ] Add integration tests for each route module

### Phase 4: Production Hardening (FUTURE)
- [ ] Replace in-memory stores with SQLite/Redis persistence
- [ ] Add structured logging (JSON format) across all services
- [ ] Add distributed tracing for cross-service requests
- [ ] Add graceful shutdown handlers
- [ ] Add configuration validation on startup
- [ ] Add end-to-end integration tests

---

## 7. Changes Implemented in This Session

### docker-compose.yml
- Added `condition: service_healthy` to Evershade Valley's `depends_on` for Polter and Spectra
- Added health checks to all three services (Evershade Valley, Polter, Spectra)
- Evershade Valley health check: `python -c "import urllib.request; ..."` on port 8080
- Polter health check: `python -c "import urllib.request; ..."` on port 8000
- Spectra health check: `wget --spider -q http://localhost:3000/health`

### Evershade Valley/hub/Polter_provider.py
- Replaced `asyncio.get_event_loop().run_until_complete()` with Python 3.12+ compatible pattern
- `check_available()` now uses synchronous `httpx.Client` instead of async wrapper
- `run()` uses `asyncio.new_event_loop()` with proper cleanup

### Evershade Valley/hub/Spectra_provider.py
- Same asyncio fix as Polter_provider.py
- `check_available()` now uses synchronous `httpx.Client`
- `run()` uses `asyncio.new_event_loop()` with proper cleanup

### .env.example
- Added documentation comments explaining each variable's purpose
- Clarified which services use which variables
- Added security key generation instructions

---

## 8. Test Results

| Test | Status | Details |
|------|--------|---------|
| `api.py` syntax check | ✓ PASS | `ast.parse()` succeeds on 7658 lines |
| `Polter_provider.py` syntax | ✓ PASS | `ast.parse()` succeeds |
| `Spectra_provider.py` syntax | ✓ PASS | `ast.parse()` succeeds |
| `docker-compose.yml` validation | ✓ PASS | Valid YAML structure |
| Docker health checks | ⚠ NOT RUN | Requires Docker environment |
| Provider asyncio fix | ⚠ NOT RUN | Requires running services |
| End-to-end workflow | ⚠ NOT RUN | Requires full deployment |

---

## 9. Remaining Work & Risks

### Remaining Work
1. **api.py modularization** — The single largest improvement. Splitting 290KB into ~30 route modules will make the codebase maintainable. Estimated effort: significant but incremental.
2. **Unified startup script** — A single `start.sh` that validates config, checks dependencies, and starts all services in order.
3. **In-memory store persistence** — All 255 route handlers use in-memory dicts. A SQLite or Redis backend would survive restarts.
4. **Integration tests** — No end-to-end tests exist for cross-service workflows.

### Risks
- **api.py refactoring risk**: Splitting a 290KB file without comprehensive tests is risky. Recommend adding integration tests first.
- **Python 3.12 compatibility**: The asyncio fix handles both running and non-running event loops, but needs real-world testing.
- **Docker health check timing**: Spectra's `wget` health check requires `wget` in the Node image — verified present in `node:20-bookworm-slim`.

### Blockers
- **Junie CLI availability**: The `junie` runner requires Junie CLI installed. Docker deployment must mount or include the CLI.
- **Playwright browsers**: Spectra requires Chromium, installed via `npx playwright install chromium` in Dockerfile.

---

## 10. Installation & Deployment Guide

### Prerequisites
- Docker & Docker Compose (for containerized deployment)
- Junie CLI installed on host (for `junie` runner)
- Ollama running on host (optional, for prompt refinement)

### Quick Start (Docker)
```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env with your API keys and settings

# 2. Start all services
docker compose up -d --build

# 3. Verify health
curl http://localhost:8080/health    # Evershade Valley
curl http://localhost:8000/health    # Polter
curl http://localhost:3000/health    # Spectra

# 4. Check unified dashboard
curl http://localhost:8080/api/dashboard
```

### Local Development
```bash
# Evershade Valley
cd Evershade Valley
pip install -r requirements.txt
HUB_API_KEY=your-key python -m uvicorn hub.api:app --port 8080

# Polter
cd Polter
pip install -r requirements.txt
API_KEY=your-key python -m uvicorn orchestrator:app --port 8000

# Spectra
cd Spectra
npm install
npx playwright install chromium
npm run build && npm start
```

### Service Ports
| Service | Port | Health Endpoint |
|---------|------|-----------------|
| Evershade Valley | 8080 | `GET /health` |
| Polter | 8000 | `GET /health` |
| Spectra | 3000 | `GET /health` |
| Redis | 6379 | `redis-cli ping` |

### Key Configuration
- **API keys**: Set in `.env` file, passed to containers via docker-compose
- **Workspace**: Shared volume mounted at `/workspace` in all services
- **Ollama**: Optional, reachable via `host.docker.internal:11434` in Docker
