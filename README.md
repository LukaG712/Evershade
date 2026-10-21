# Evershade

> **A self-hosted AI agent platform built as a collection of specialized microservices.**

All service names are inspired by [Luigi's Mansion ghosts](https://luigi-mansion.fandom.com/wiki/List_of_ghosts).

---

## About

**Evershade** is a self-hosted AI agent platform built as a collection of specialized microservices, orchestrated together via Docker Compose. Each service is an independent repository that can run alone or as part of the full ecosystem.

| | |
|---|---|
| **Website** | [http://localhost:8080](http://localhost:8080) |
| **Services** | [Greenie](https://github.com/LukaG712/Greenie) · [Slinker](https://github.com/LukaG712/Slinker) · [Trapper](https://github.com/LukaG712/Trapper) |
| **Topics** | ai-agents · microservices · self-hosted · docker-compose · web-scraping · code-execution · luigis-mansion |
| **Built with** | Python · TypeScript · FastAPI · Playwright · Junie CLI |

---

## Services

### Greenie — Central Hub & Dashboard

**Luigi's Mansion origin:** *Greenie* — small green ghosts from Luigi's Mansion: Dark Moon (Evershade Valley).

The brain of the operation. Greenie is a full-featured API server with a built-in web dashboard. It manages AI agents, chat sessions, pipelines, analytics, and provides a unified view of the entire platform.

| Feature | Details |
|---------|---------|
| **Port** | `8080` |
| **Web UI** | Chat interface, management dashboard, task app |
| **API** | 320+ endpoints with Swagger/ReDoc docs |
| **Storage** | SQLite with feature-store persistence |
| **Role** | Orchestrator, agent manager, analytics hub |

Greenie is the only service with a web frontend. Everything you interact with visually runs through Greenie.

**Repo:** [LukaG712/Greenie](https://github.com/LukaG712/Greenie)

---

### Slinker — Execution Engine

**Luigi's Mansion origin:** *Slinker* — stealthy ghost enemies from Luigi's Mansion 3 that slink along walls and floors.

The worker behind the scenes. Slinker takes tasks from Greenie and executes them in isolated Git worktrees using the Junie CLI. It handles code generation, file modifications, refactoring, and any task that requires running AI agents against a codebase.

| Feature | Details |
|---------|---------|
| **Port** | `8000` |
| **UI** | API only (no web frontend) |
| **Isolation** | Git worktrees per task |
| **Runner** | Junie CLI integration |
| **Role** | Task execution, code agent runner |

Slinker has no dashboard — it's a pure API service. You manage tasks through Greenie's dashboard, which sends work to Slinker.

**Repo:** [LukaG712/Slinker](https://github.com/LukaG712/Slinker)

---

### Trapper — Web Scraping & Crawling

**Luigi's Mansion origin:** *Trapper* — ghost enemies from Luigi's Mansion 3 that trap and capture.

The eyes on the web. Trapper uses Playwright to scrape, crawl, search, and map websites, turning raw HTML into clean, structured, LLM-ready data. It supports single-page scraping, deep crawling, site mapping, and background job queues via Redis.

| Feature | Details |
|---------|---------|
| **Port** | `3000` |
| **UI** | API only (no web frontend) |
| **Browser** | Playwright headless |
| **Queue** | Redis-backed job queue |
| **Role** | Web scraping, crawling, content extraction |

**Repo:** [LukaG712/Trapper](https://github.com/LukaG712/Trapper)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Your Browser                            │
│                  http://localhost:8080                      │
│              (Greenie's Web Dashboard)                      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │    Greenie (8080)  │  ← Hub + Dashboard
                    │  ┌───────────────┐  │
                    │  │  Web UI + API │  │
                    │  │  SQLite DB    │  │
                    │  └───────────────┘  │
                    └──────┬──────┬──────┘
                           │      │
              ┌────────────┘      └────────────┐
              ▼                                  ▼
┌─────────────────────────┐      ┌─────────────────────────┐
│   Slinker (8000)       │      │   Trapper (3000)        │
│  ┌───────────────────┐  │      │  ┌───────────────────┐  │
│  │ Git worktree mgmt │  │      │  │ Playwright browser│  │
│  │ Junie CLI runner  │  │      │  │ Content cleaning  │  │
│  │ Task persistence  │  │      │  │ Redis queue       │  │
│  └───────────────────┘  │      │  └───────────────────┘  │
└─────────────────────────┘      └─────────────────────────┘
```

### How they work together

1. **You** interact with Greenie's web dashboard at `localhost:8080`
2. **Greenie** manages your agents, sessions, and pipelines
3. When a task needs code execution, Greenie sends it to **Slinker**
4. When a task needs web data, Greenie sends it to **Trapper**
5. Results flow back through Greenie to your dashboard

### Cross-service pipelines

Chain services together in a single request:

```json
POST /api/pipeline
{
  "steps": [
    { "service": "Trapper", "action": "scrape", "url": "https://example.com" },
    { "service": "Greenie", "action": "chat", "agent": "researcher" },
    { "service": "Slinker", "action": "execute", "prompt": "Create a summary document" }
  ]
}
```

---

## Quick Start

### Prerequisites

- **Docker** and **Docker Compose**
- **[Junie CLI](https://junie.jetbrains.com)** (for code agents) — optional

### One-Command Start

```bash
git clone https://github.com/LukaG712/Evershade.git && cd Evershade
cp .env.example .env
# Edit .env with your API keys
docker compose up -d --build
```

The dashboard will be available at **http://localhost:8080**.

### Startup Scripts

```bash
# Linux/macOS
./start.sh    # Start all services
./stop.sh     # Stop all services

# Windows PowerShell
.\start.ps1   # Start all services
.\stop.ps1    # Stop all services
```

---

## Web Interfaces

All visual interfaces are served by Greenie:

| Interface | URL | Description |
|-----------|-----|-------------|
| **Chat UI** | `http://localhost:8080/` | Agent chat, skills, memory, routines |
| **Dashboard** | `http://localhost:8080/dashboard/` | Agents, runs, pipelines, analytics, settings |
| **Tasks App** | `http://localhost:8080/app/` | Simple task list |
| **API Docs** | `http://localhost:8080/docs` | Swagger UI for all endpoints |

> **Note:** Slinker and Trapper are API-only services with no web frontend. All management happens through Greenie's dashboard.

---

## API Documentation

Each service exposes auto-generated API docs:

| Service | Swagger UI | ReDoc | OpenAPI JSON |
|---------|-----------|-------|-------------|
| **Greenie** | `localhost:8080/docs` | `localhost:8080/redoc` | `localhost:8080/openapi.json` |
| **Slinker** | `localhost:8000/docs` | `localhost:8000/redoc` | `localhost:8000/openapi.json` |
| **Trapper** | `localhost:3000/docs` | `localhost:3000/redoc` | `localhost:3000/openapi.json` |

---

## Naming Theme

All services are named after ghosts from the **Luigi's Mansion** series:

| Service | Ghost Origin | Game |
|---------|-------------|------|
| **Greenie** | Small green ghosts | Luigi's Mansion: Dark Moon |
| **Slinker** | Wall-crawling stealth ghosts | Luigi's Mansion 3 |
| **Trapper** | Trap-setting ghosts | Luigi's Mansion 3 |

The root repository is named **Evershade** after *Evershade Valley*, the setting of Luigi's Mansion: Dark Moon.

### Future service name ideas

More ghost names from the series available for new services:

| Name | Origin | Suggested Role |
|------|--------|---------------|
| **Gobber** | Dark Moon — blob-like ghost | Data storage / database service |
| **Slammer** | Dark Moon — heavy-hitting ghost | Build / CI service |
| **Creeper** | Dark Moon — creeping ghost | Monitoring / observability service |
| **Hider** | Dark Moon — hiding ghost | Secret / config management |
| **Polterpup** | Dark Moon — ghost dog | Notification / messaging service |
| **Boo** | Classic — iconic ghost | Authentication / gateway service |
| **Oozers** | LM3 — ooze-like ghosts | File storage / blob service |
| **Hammer** | LM3 — hammer-wielding ghost | Deployment / infrastructure service |
| **Goob** | LM3 — basic ghost | Task queue / job scheduler |
| **Speedy** | Series — fast ghost | CDN / caching service |
| **Grouchy** | Dark Moon — spider boss | Security / firewall service |
| **Nana** | Dark Moon — portrait ghost | Document processing service |
| **Shivers** | Dark Moon — ice ghost | Cooling / rate limiting service |
| **Biff** | Dark Moon — bouncer ghost | API gateway / load balancer |
| **Chauncey** | Dark Moon — ghostly figure | LLM provider abstraction |

---

## Repository Structure

```
Evershade/ (this repo — orchestration)
├── .github/workflows/ci.yml   ← Root CI pipeline
├── docker-compose.yml         ← Service orchestration
├── start.sh / stop.sh         ← Startup scripts
├── start.ps1 / stop.ps1       ← Windows scripts
├── Greenie/                   → Separate repo (LukaG712/Greenie)
├── Slinker/                   → Separate repo (LukaG712/Slinker)
└── Trapper/                   → Separate repo (LukaG712/Trapper)
```

Each sub-project is an independent Git repository with its own CI pipeline. The root repo tracks orchestration files (Docker Compose, CI, scripts) and excludes the sub-project directories via `.gitignore`.

---

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Default | Description |
|----------|---------|-------------|
| `HUB_API_KEY` | `Greenie-dev-key-change-me` | Greenie API key |
| `Slinker_API_KEY` | `Slinker-dev-key-change-me` | Slinker API key |
| `Trapper_API_KEY` | `Trapper-API-key-change-me` | Trapper API key |
| `OLLAMA_URL` | `http://host.docker.internal:11434` | Ollama API endpoint |
| `LOG_LEVEL` | `INFO` | Log verbosity |

---

## Planned Services

The ecosystem is designed to grow. Planned additions (names TBD from the ghost list above):

| Service | Role | Status |
|---------|------|--------|
| **Auth & Gateway** | Centralized OAuth, API keys, rate limiting | Planned |
| **Persistent Storage** | Dedicated storage for webhooks, analytics, RBAC | Planned |
| **Observability** | Metrics, traces, logs aggregation | Planned |
| **Semantic Memory** | Vector-based knowledge graph for agents | Planned |
| **Web Dashboard** | React/Vue frontend (beyond Greenie's built-in UI) | Planned |

See [ECOSYSTEM_EXPANSION.md](ECOSYSTEM_EXPANSION.md) for the full expansion roadmap.

---

## License

Each sub-project may have its own license. Check the individual repositories.
