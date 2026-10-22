# Evershade Architecture

**Version:** 1.0.0
**Last Updated:** 2026-10-22

---

## 1. Platform Overview

Evershade is a self-hosted AI agent platform composed of specialized microservices. Each service has a single responsibility, communicates via HTTP APIs, and can run independently while contributing to the cohesive platform.

### Design Principles

1. **Modular services** — Each service has a clear boundary and public interface.
2. **SQLite-first** — Use SQLite where it satisfies requirements; introduce other databases only when necessary.
3. **No heavy infrastructure** — Avoid Kubernetes, Kafka, Elasticsearch, or distributed databases unless the audit identifies concrete need.
4. **Self-hosted practical** — Must run on ordinary developer hardware without excessive resource consumption.
5. **Security by default** — Least privilege, network isolation, and container hardening are the default, not an afterthought.

---

## 2. Service Catalog

### Core Services (Required)

| Service | Role | Port | Language | Persistence |
|---------|------|------|----------|-------------|
| **Greenie** | Central API, orchestration, chat, dashboard | 8080 | Python/FastAPI | SQLite |
| **Slinker** | Code execution engine, Junie CLI runner | 8000 | Python/FastAPI | SQLite |
| **Trapper** | Web scraping, crawling, browser automation | 3000 | TypeScript/Fastify | Redis (queues) |
| **Gobber** | Persistent storage, knowledge graph, semantic memory | 8085 | Python/FastAPI | SQLite |

### Supporting Services (Optional)

| Service | Role | Port | Language | Persistence |
|---------|------|------|----------|-------------|
| **Sneaker** | Metrics, logs, traces, observability | 8086 | Python/FastAPI | SQLite (planned) |
| **Hider** | Encrypted secrets and configuration management | 8087 | Python/FastAPI | SQLite (planned) |
| **Poltergeist** | Notifications and async delivery | 8088 | Python/FastAPI | SQLite (planned) |
| **Shrewd** | LLM provider abstraction and model routing | 8089 | Python/FastAPI | In-memory |

### Frontend Services

| Service | Role | Port | Stack |
|---------|------|------|-------|
| **Slammer** | React-based standalone dashboard | 5173 | React/TypeScript/Tailwind |

### Tools

| Service | Role | Stack |
|---------|------|-------|
| **Speedy** | Command-line interface (`evershade`) | Python/Click/Rich |

---

## 3. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Access                              │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Browser    │  │   Windows    │  │   CLI (Speedy)       │  │
│  │  (Slammer)   │  │   PC         │  │                      │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │              │
│         │  HTTPS/HTTP     │  SSH/HTTPS           │  HTTP        │
│         ▼                 ▼                      ▼              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Greenie (8080) — Gateway                     │  │
│  │  ┌────────────┬────────────┬────────────┬──────────────┐ │  │
│  │  │  Web UI    │  Chat API  │  Workflow  │  Management  │ │  │
│  │  │  (static)  │  + SSE     │  Engine    │  + RBAC      │ │  │
│  │  └────────────┴────────────┴────────────┴──────────────┘ │  │
│  │                    │                  │                   │  │
│  │              SQLite DB          Feature Stores           │  │
│  └────────────────────┼────────────────┼────────────────────┘  │
│                       │                  │                     │
└───────────────────────┼──────────────────┼─────────────────────┘
                        │                  │
          ┌─────────────┼──────────────────┼─────────────┐
          │             │                  │             │
          ▼             ▼                  ▼             ▼
   ┌──────────────┐ ┌──────────┐   ┌──────────┐  ┌──────────┐
   │  Slinker     │ │ Trapper  │   │ Gobber   │  │ Shrewd   │
   │  (8000)      │ │ (3000)   │   │ (8085)   │  │ (8089)   │
   │              │ │          │   │          │  │          │
   │ Git worktree │ │ Playwright│  │ SQLite   │  │ Provider │
   │ Junie CLI    │ │ Redis Q   │  │ KG +     │  │ routing  │
   │ SQLite       │ │ Browser   │  │ Obsidian │  │          │
   └──────────────┘ └──────────┘   └──────────┘  └──────────┘
          │             │                  │             │
          ▼             ▼                  ▼             ▼
   ┌──────────────┐ ┌──────────┐   ┌──────────┐  ┌──────────┐
   │  Hider       │ │ Sneaker  │   │ Polter-  │  │  (External│
   │  (8087)      │ │ (8086)   │   │ geist    │  │   LLM     │
   │              │ │          │   │ (8088)   │  │  APIs)    │
   │ Encrypted    │ │ Metrics  │   │ Slack,   │  │           │
   │ secrets      │ │ Traces   │   │ Discord, │  │  OpenAI,  │
   │ Config       │ │ Logs     │   │ Email    │  │  Anthropic│
   └──────────────┘ └──────────┘   └──────────┘  │  Google   │
                                                  └──────────┘
```

---

## 4. Service Boundaries

### Greenie — Central Hub & Dashboard

**Responsibility:** Orchestration, agent management, chat sessions, workflow execution, user interface.

**Owns:**
- Agent definitions and configuration
- Chat sessions and conversation history
- Workflow definitions and execution state
- User accounts and RBAC policies
- Approval workflows
- Analytics events (delegates storage to Gobber)
- Feature flags (delegates storage to Gobber)
- Webhook definitions (delegates storage to Gobber)

**Dependencies:**
- Slinker (code execution tasks)
- Trapper (web scraping tasks)
- Gobber (persistent feature stores, knowledge graph)
- Shrewd (LLM requests)
- Poltergeist (notifications) — optional
- Sneaker (observability) — optional
- Hider (secrets) — optional

**Public Interface:**
- REST API: `/api/*`
- WebSocket: `/ws/feed`
- SSE: Various streaming endpoints
- Static files: Web dashboard

### Slinker — Code Execution Engine

**Responsibility:** Execute AI agent tasks in isolated Git worktrees using the Junie CLI.

**Owns:**
- Task execution state
- Worker registry
- Project registrations
- Session logs
- Worktree management

**Dependencies:**
- Junie CLI (external binary)
- Ollama (optional, for prompt refinement)

**Public Interface:**
- REST API: `/api/v1/*`
- OpenAI-compatible: `/v1/chat/completions`, `/v1/models`
- Health: `/health`, `/ready`

### Trapper — Web Scraping & Crawling

**Responsibility:** Scrape, crawl, search, and interact with websites using Playwright.

**Owns:**
- Scraping jobs and results
- Crawl queues (Redis/BullMQ)
- Browser instances

**Dependencies:**
- Redis (job queues)
- Playwright/Chromium (browser automation)

**Public Interface:**
- REST API: `/api/*` (scrape, crawl, map, search, extract, interact, agent)
- Health: `/health`

### Gobber — Persistent Storage & Knowledge Graph

**Responsibility:** Centralized persistent storage for ecosystem feature stores and semantic memory.

**Owns:**
- Webhook definitions and delivery history
- Analytics events
- RBAC roles and user assignments
- Response cache
- Feature flags
- Knowledge graph (notes, embeddings, links)
- Obsidian vault index

**Dependencies:**
- Shrewd (optional, for embedding generation)

**Public Interface:**
- REST API: `/api/*` (webhooks, analytics, flags, cache, roles, vault)
- Health: `/health`

### Sneaker — Observability

**Responsibility:** Collect and query metrics, distributed traces, and structured logs.

**Owns:**
- Metric time series
- Trace spans
- Log entries
- Alert rules

**Dependencies:** None (leaf service)

**Public Interface:**
- REST API: `/api/*` (metrics, traces, logs, alerts)
- OTLP endpoint: `/otlp/*` (planned)
- Health: `/health`

### Hider — Secrets & Configuration

**Responsibility:** Encrypted storage and retrieval of secrets and centralized configuration.

**Owns:**
- Encrypted secrets (AES-256)
- Versioned configuration entries
- Secret access audit log

**Dependencies:** None (leaf service)

**Public Interface:**
- REST API: `/api/*` (secrets, configs)
- Health: `/health`

### Poltergeist — Notifications

**Responsibility:** Send notifications through multiple channels with templating and async delivery.

**Owns:**
- Notification templates
- Delivery history
- Channel configurations

**Dependencies:**
- External services (Slack, Discord, email SMTP, Telegram API)

**Public Interface:**
- REST API: `/api/*` (notifications, templates)
- Health: `/health`

### Shrewd — LLM Abstraction

**Responsibility:** Unified interface for multiple LLM providers with model routing.

**Owns:**
- Model registry
- Provider configurations
- Usage tracking and cost estimation
- Routing rules

**Dependencies:**
- External LLM APIs (OpenAI, Anthropic, Google, Ollama)

**Public Interface:**
- REST API: `/api/*` (chat, models, providers)
- Health: `/health`

### Slammer — Web Dashboard

**Responsibility:** React-based standalone dashboard for platform management.

**Owns:**
- Frontend application code
- UI state management

**Dependencies:**
- Greenie (all API calls proxied through Greenie)

**Public Interface:**
- Static web application served on port 5173

### Speedy — CLI

**Responsibility:** Command-line interface for platform management.

**Owns:**
- CLI commands and configuration
- Remote connection profiles

**Dependencies:**
- Greenie API (primary)
- Docker Compose (for install/start/stop)

**Public Interface:**
- `evershade` command with subcommands

---

## 5. Communication Standards

### Synchronous Communication

All service-to-service communication uses HTTP/JSON REST APIs.

**Standard headers:**
- `Authorization: Bearer <service-api-key>` — Service authentication
- `X-Request-ID: <uuid>` — Unique request identifier
- `X-Correlation-ID: <uuid>` — Correlates requests across services
- `X-Service-Name: <service>` — Source service identification
- `Content-Type: application/json` — Request format
- `Accept: application/json` — Response format

**Standard response envelope:**
```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "requestId": "uuid",
  "timestamp": "2026-10-22T10:00:00Z"
}
```

**Standard error response:**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "Trapper service is not reachable",
    "details": "Connection timeout after 5s"
  },
  "requestId": "uuid",
  "timestamp": "2026-10-22T10:00:00Z"
}
```

**Error codes:**
| Code | HTTP Status | Meaning |
|------|-------------|---------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource conflict (e.g., duplicate) |
| `SERVICE_UNAVAILABLE` | 503 | Downstream service unavailable |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

### Timeouts and Retries

| Operation | Timeout | Retries | Backoff |
|-----------|---------|---------|---------|
| Health check | 5s | 0 | — |
| Synchronous API call | 30s | 1 | 1s fixed |
| Long-running task (Slinker) | 1800s | 0 | — |
| Web scraping (Trapper) | 60s | 1 | 2s fixed |
| LLM request (Shrewd) | 120s | 1 | 5s fixed |

### Asynchronous Communication

Used only where genuinely required:
- **Trapper crawl jobs:** Redis/BullMQ for background crawl processing
- **Poltergeist notifications:** Async delivery queue for notification channels
- **Slinker workers:** Concurrent worker pool with semaphore

---

## 6. Data Ownership

| Data Type | Owner | Consumers | Storage |
|-----------|-------|-----------|---------|
| Agent definitions | Greenie | Slinker, Shrewd | Greenie SQLite |
| Chat sessions | Greenie | — | Greenie SQLite |
| Workflow definitions | Greenie | All services | Greenie SQLite |
| Task execution state | Slinker | Greenie | Slinker SQLite |
| Web scraping results | Trapper | Greenie, Gobber | Return value (ephemeral) |
| Feature stores (webhooks, RBAC, etc.) | Gobber | Greenie | Gobber SQLite |
| Knowledge graph | Gobber | Greenie, Slinker | Gobber SQLite |
| Metrics and traces | Sneaker | Greenie (dashboard) | Sneaker (planned SQLite) |
| Secrets | Hider | All services (on demand) | Hider (planned SQLite, encrypted) |
| Notification history | Poltergeist | Greenie (dashboard) | Poltergeist (planned SQLite) |
| Model registry | Shrewd | Greenie, Slinker | Shrewd (in-memory) |

**Rules:**
1. Services access other services' data only through public APIs.
2. No direct database access across service boundaries.
3. Schema changes are the responsibility of the owning service.
4. No duplicated sources of truth — if Gobber owns webhooks, Greenie does not store them.

---

## 7. Deployment Topology

### Default (Desktop) Mode

```
┌──────────────────────────────────────────────┐
│                 Host Machine                 │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │         Docker Network (internal)      │  │
│  │                                        │  │
│  │  Greenie ←── Slinker                   │  │
│  │    │        Trapper                     │  │
│  │    ├── Gobber                          │  │
│  │    ├── Sneaker                         │  │
│  │    ├── Hider                           │  │
│  │    ├── Poltergeist                     │  │
│  │    └── Shrewd                          │  │
│  │                                        │  │
│  │  Redis (internal)                      │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  Host: localhost:8080 → Greenie only         │
│  All other services: internal only           │
└──────────────────────────────────────────────┘
```

### Server Mode

```
┌──────────────────────────────────────────────┐
│              Ubuntu Server / VM              │
│                                              │
│  ┌────────────┐    ┌──────────────────────┐  │
│  │  Caddy     │    │  Docker Network      │  │
│  │  (TLS)     │───→│  (internal)          │  │
│  │  :443      │    │                      │  │
│  └────────────┘    │  Greenie ←─ Slinker  │  │
│                    │       └─ Trapper      │  │
│                    │       └─ Gobber       │  │
│                    │       └─ (others)     │  │
│                    └──────────────────────┘  │
│                                              │
│  Host: :443 → Caddy → Greenie               │
│  All other services: internal only           │
└──────────────────────────────────────────────┘
         ▲
         │ HTTPS
         │
   ┌─────────┐
   │ Windows │
   │  PC     │
   └─────────┘
```

---

## 8. Service Health Contract

Every service exposes:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Liveness check — returns 200 if process is running |
| `/ready` | GET | Readiness check — returns 200 if fully initialized (DB, config, deps) |
| `/api/status` | GET | Detailed status — version, capabilities, dependency health |

**Health response:**
```json
{
  "status": "ok",
  "service": "Greenie",
  "version": "1.0.3"
}
```

**Readiness response:**
```json
{
  "ready": true,
  "issues": []
}
```

---

## 9. Optional Services Policy

Services are classified as required or optional:

- **Required:** Greenie, Slinker, Trapper, Gobber
- **Optional:** Sneaker, Hider, Poltergeist, Shrewd, Slammer

When an optional service is unavailable:
1. The platform continues to operate.
2. Greenie logs a warning and marks the service as unavailable in the dashboard.
3. Features depending on the unavailable service degrade gracefully (e.g., notifications are logged but not sent if Poltergeist is down).
4. No cascade failure — a missing optional service never brings down the entire platform.

---

## 10. Planned Service Decisions

| Planned Service | Decision | Rationale |
|-----------------|----------|-----------|
| **Mnemos** (semantic memory) | **DROP** | Gobber already provides embeddings, semantic search, and knowledge graph. Extend Gobber instead. |
| **Bridge** (external integrations) | **EVALUATE** | Greenie has webhook and GitHub integration. Only build if new integration types are needed beyond webhooks. |
| **Courier** (file storage) | **EVALUATE** | Greenie has 50MB file upload. Only build if persistent object storage beyond 50MB is required. |

---

## 11. Naming Convention

All services follow the Luigi's Mansion ghost naming theme. Each service name is paired with a plain-language subtitle:

| Service | Plain-Language Role |
|---------|-------------------|
| Greenie | Central hub and dashboard |
| Slinker | Code execution engine |
| Trapper | Web scraping and crawling |
| Gobber | Persistent storage and knowledge graph |
| Sneaker | Observability and monitoring |
| Hider | Secrets and configuration management |
| Poltergeist | Notification delivery |
| Shrewd | LLM provider abstraction |
| Slammer | Web dashboard |
| Speedy | Command-line interface |
