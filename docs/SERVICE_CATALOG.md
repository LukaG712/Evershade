# Evershade Service Catalog

**Version:** 1.7.0
**Last Updated:** 2026-10-22

---

## Service Overview

| Service | Role | Port | Required | API Version |
|---------|------|------|----------|-------------|
| **Greenie** | Central hub API (API-only) | 8080 | Yes | v1 |
| **Slinker** | Code execution engine | 8000 | Yes | v1 |
| **Trapper** | Web scraping and crawling | 3000 | Yes | v1 |
| **Gobber** | Persistent storage and knowledge graph | 8085 | Yes | v1 |
| **Sneaker** | Observability and monitoring | 8086 | No | v1 |
| **Hider** | Secrets and configuration management | 8087 | No | v1 |
| **Poltergeist** | Notification delivery | 8088 | No | v1 |
| **Shrewd** | LLM provider abstraction | 8089 | No | v1 |
| **Slammer** | Unified web dashboard | 5173 | No | N/A |
| **Speedy** | Command-line interface | N/A | No | N/A |

---

## Greenie – Central Hub API

**Repository:** [LukaG712/Greenie](https://github.com/LukaG712/Greenie)
**Port:** 8080
**Technology:** Python, FastAPI, SQLite
**Note:** API-only backend. Slammer is the unified dashboard frontend.

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/ready` | Readiness check |
| GET | `/api/status` | Agent and service status |
| GET | `/api/agents` | List agents |
| POST | `/api/agents` | Create agent |
| GET | `/api/sessions` | List sessions |
| POST | `/api/chat` | Send chat message |
| GET | `/api/workflows` | List workflows |
| POST | `/api/workflows` | Create workflow |
| GET | `/api/workstations` | List workstations |
| POST | `/api/workstations` | Create workstation |
| GET | `/api/mcp/servers` | List MCP servers |
| POST | `/api/mcp/servers` | Add MCP server |
| GET | `/api/plugins` | List plugins |
| POST | `/api/plugins` | Install plugin |
| GET | `/api/system/stats` | System resource stats |
| GET | `/api/system/logs` | Aggregated logs |
| POST | `/api/system/logs` | Push log entry |
| GET | `/api/emergency/status` | Emergency stop status |
| POST | `/api/emergency/stop` | Activate emergency stop |
| POST | `/api/emergency/resume` | Resume after emergency stop |
| GET | `/api/timeline/events` | Query activity timeline |
| GET | `/api/timeline/workflow/{id}` | Workflow activity timeline |
| GET | `/api/timeline/correlation/{id}` | Cross-service correlation |
| GET | `/api/timeline/stats` | Timeline statistics |
| POST | `/api/timeline/record` | Record timeline event |
| GET | `/api/audit/events` | Security audit trail |
| POST | `/api/credentials/rotate` | Rotate credential |
| GET | `/api/credentials/history` | Rotation history |
| GET | `/api/backup` | List backups |
| POST | `/api/backup` | Create backup |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc UI |

### Dependencies
- Slinker, Trapper, Gobber (required)
- Sneaker, Hider, Poltergeist, Shrewd (optional)

---

## Slinker – Code Execution Engine

**Repository:** [LukaG712/Slinker](https://github.com/LukaG712/Slinker)
**Port:** 8000
**Technology:** Python, FastAPI, SQLite

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/ready` | Readiness check |
| GET | `/api/v1/tasks` | List tasks |
| GET | `/api/v1/tasks/{id}` | Get task details |
| GET | `/api/v1/workers` | List workers |
| GET | `/api/v1/projects` | List projects |
| POST | `/api/v1/projects` | Register project |
| GET | `/api/v1/queue` | Queue status |
| POST | `/api/v1/backup` | Create backup |
| POST | `/v1/chat/completions` | OpenAI-compatible chat |

### Dependencies
- Junie CLI (external binary)
- Ollama (optional, for prompt refinement)

---

## Trapper – Web Scraping & Crawling

**Repository:** [LukaG712/Trapper](https://github.com/LukaG712/Trapper)
**Port:** 3000
**Technology:** TypeScript, Fastify, Playwright, Redis

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/scrape` | Scrape a single page |
| POST | `/api/crawl` | Start a crawl job |
| POST | `/api/map` | Map a website |
| POST | `/api/search` | Search the web |
| POST | `/api/extract` | Extract structured data |
| POST | `/api/interact` | Browser interaction |
| POST | `/api/agent` | Autonomous browsing agent |

### Dependencies
- Redis (job queues)
- Playwright/Chromium (browser)

---

## Gobber – Persistent Storage & Knowledge Graph

**Repository:** [LukaG712/Gobber](https://github.com/LukaG712/Gobber)
**Port:** 8085
**Technology:** Python, FastAPI, SQLite

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/webhooks` | Create webhook |
| GET | `/api/webhooks` | List webhooks |
| POST | `/api/analytics/events` | Record event |
| GET | `/api/analytics/events` | Query events |
| POST | `/api/flags` | Create feature flag |
| GET | `/api/flags` | List feature flags |
| POST | `/api/cache` | Set cache entry |
| GET | `/api/cache/{key}` | Get cache entry |
| POST | `/api/roles` | Create role |
| GET | `/api/roles` | List roles |
| POST | `/api/vault/index` | Index Obsidian vault |
| POST | `/api/vault/search` | Semantic search |
| GET | `/api/vault/notes` | List notes |

### Dependencies
- Shrewd (optional, for embeddings)

---

## Sneaker – Observability

**Repository:** [LukaG712/Sneaker](https://github.com/LukaG712/Sneaker)
**Port:** 8086
**Technology:** Python, FastAPI, SQLite

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/metrics` | Record metric |
| GET | `/api/metrics` | Query metrics |
| POST | `/api/traces` | Record trace span |
| GET | `/api/traces` | Query traces |
| POST | `/api/logs` | Record log entry |
| GET | `/api/logs` | Query logs |
| GET | `/api/alerts` | List fired alerts |
| GET | `/api/alerts/rules` | List alert rules |
| PUT | `/api/alerts/rules/{id}` | Update alert rule |
| POST | `/api/alerts/{id}/ack` | Acknowledge alert |
| GET | `/api/alerts/stats` | Alert statistics |

### Dependencies
- Poltergeist (optional, for alert delivery)

---

## Hider – Secrets & Configuration

**Repository:** [LukaG712/Hider](https://github.com/LukaG712/Hider)
**Port:** 8087
**Technology:** Python, FastAPI

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/secrets` | Create secret |
| GET | `/api/secrets` | List secrets |
| GET | `/api/secrets/{key}` | Get secret |
| PUT | `/api/secrets/{key}` | Update secret |
| DELETE | `/api/secrets/{key}` | Delete secret |
| POST | `/api/configs` | Create config |
| GET | `/api/configs` | List configs |
| GET | `/api/configs/{key}` | Get config |

### Dependencies
- None (leaf service)

---

## Poltergeist – Notifications

**Repository:** [LukaG712/Poltergeist](https://github.com/LukaG712/Poltergeist)
**Port:** 8088
**Technology:** Python, FastAPI

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/notifications` | Send notification |
| GET | `/api/notifications` | List notifications |
| POST | `/api/templates` | Create template |
| GET | `/api/templates` | List templates |
| POST | `/api/templates/{name}/send` | Send from template |

### Dependencies
- External services (Slack, Discord, SMTP, Telegram)

---

## Shrewd – LLM Abstraction

**Repository:** [LukaG712/Shrewd](https://github.com/LukaG712/Shrewd)
**Port:** 8089
**Technology:** Python, FastAPI

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/chat` | Chat completion |
| GET | `/api/models` | List available models |
| GET | `/api/providers` | List providers |

### Dependencies
- External LLM APIs (OpenAI, Anthropic, Google, Ollama)

---

## Slammer – Unified Web Dashboard

**Repository:** [LukaG712/Slammer](https://github.com/LukaG712/Slammer)
**Port:** 5173
**Technology:** React, TypeScript, Tailwind CSS, Vite

### Description
The single unified dashboard for Evershade. Greenie operates as API-only backend.
Deployed behind Caddy reverse proxy in server mode.

### Pages

| Page | Data Source | Description |
|------|-------------|-------------|
| Services | Direct health checks | Service status polling every 10s |
| Agents | Greenie `/api/agents` | Agent management |
| Runs | Greenie `/api/runs` | Run history |
| Workflows | Greenie `/api/workflows` | Visual workflow builder |
| Workstations | Greenie `/api/workstations` | Container management, logs, terminal |
| Metrics | Sneaker + Greenie | System resources, alerts, charts |
| Logs | Greenie `/api/logs` | Aggregated log viewer |
| Plugins | Greenie `/api/plugins` | Plugin and MCP server management |

### Dependencies
- Greenie (all API calls)
- Sneaker (optional, for metrics)

---

## Speedy – CLI

**Repository:** [LukaG712/Speedy](https://github.com/LukaG712/Speedy)
**Command:** `evershade`
**Technology:** Python, Click, Rich

### Commands

| Command | Description |
|---------|-------------|
| `evershade status` | Check service status |
| `evershade agents list` | List agents |
| `evershade task submit` | Submit a task |
| `evershade config show` | Show configuration |
| `evershade config set` | Set configuration value |

### Dependencies
- Greenie API (primary)
- Docker Compose (for install/start/stop)
