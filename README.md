# Evershade

> *"E. Gadd to Luigi! Am I comin' in clear, do you read me?"*
> ~ **Prof. E. Gadd**, Luigi's Mansion: Dark Moon

**A self-hosted AI agent platform built as a collection of specialized microservices.**

[![Version](https://img.shields.io/badge/Version-1.12.0-brightgreen.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Required-blue.svg)](https://docker.com)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-React%20Dashboard-blue.svg)](https://www.typescriptlang.org)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

---

## Table of Contents

- [Why Evershade](#why-evershade) — Key features and capabilities
- [Quick Start](#quick-start) — Get up and running in 3 minutes
- [Your First Agent](#your-first-agent) — Step-by-step tutorial
- [Architecture](#architecture) — How everything fits together
- [Services](#services) — The 10 microservices at a glance
- [Mission Control](#mission-control) — Orchestrated AI missions with milestones
- [Agent Harness](#agent-harness) — Spec mode, droids, skills, and hooks
- [Workstations](#workstations) — Isolated agent environments
- [Web Interfaces](#web-interfaces) — Dashboards and UIs
- [API Documentation](#api-documentation) — Developer endpoints
- [Configuration](#configuration) — Environment variables and settings
- [Deployment](#deployment) — Production and remote access
- [Security](#security) — Security model and best practices
- [Testing](#testing) — Test suite and quality gates
- [Backup & Restore](#backup--restore) — Data protection
- [Troubleshooting](#troubleshooting) — Common issues and fixes
- [Contributing](#contributing) — How to help
- [Roadmap](#roadmap) — Development timeline and future plans
- [Naming Theme](#naming-theme) — The Luigi's Mansion connection
- [License](#license)

---

## Why Evershade

> *"The Dark Moon has shattered, Luigi! We need to find it and restore peace to Evershade Valley, posthaste!"*
> ~ **Prof. E. Gadd**, on why we built this

| Feature | Description |
|---------|-------------|
| **Modular Microservices** | 10 independent services, each with a single responsibility. Mix and match via Docker Compose profiles. |
| **AI Agent Orchestration** | Create, manage, and run AI agents with pipelines, workflows, and workstations — all from one dashboard. |
| **Mission Control** | Factory-inspired mission system with milestones, automated planning, code review, and fix-revalidate cycles. |
| **Agent Harness** | Spec mode for research-first development, custom droids (specialized subagents), reusable skills, and event-driven hooks. |
| **Multi-Provider LLM** | Route requests to OpenAI, Anthropic, Google, or Ollama with cost tracking and privacy classification. |
| **Web Scraping & Crawling** | Playwright-powered scraping, deep crawling, and site mapping with Redis-backed job queues. |
| **Encrypted Secrets** | AES-256-GCM encryption for secrets at rest with versioned configuration management. |
| **Full Observability** | Metrics, distributed traces, log aggregation, and alerting with deduplication and cooldown. |
| **OTLP Integration** | OpenTelemetry Protocol support for traces, metrics, and logs — integrate with any OTLP collector. |
| **CSRF Protection** | Double-submit cookie pattern with HMAC-signed tokens for web UI security. |
| **Semantic Search** | Vector embeddings and semantic search via Gobber — scan Obsidian vaults and search knowledge bases. |
| **Isolated Workstations** | Container-based isolated agent environments with network policies and live terminal access. |

---

## Quick Start

> *"Step into the dark! Five new spooky mansions!"*
> ~ **The Dark Moon Song**, on the adventure ahead

### Prerequisites

- **Docker** and **Docker Compose** installed
- **[Junie CLI](https://junie.jetbrains.com)** (optional, for code agents)

### One-Command Start

```bash
git clone https://github.com/LukaG712/Evershade.git && cd Evershade

# Install service repositories (required — services are in separate repos)
./install.sh --profile minimal    # Linux/macOS
# .\install.ps1 -Profile minimal  # Windows PowerShell

cp .env.example .env
# Edit .env with your API keys (see [Configuration](#configuration))

# Start services
./start.sh --profile minimal      # Linux/macOS
# .\start.ps1 -Profile minimal    # Windows PowerShell
```

The API will be available at **http://localhost:8080**.

> **Note:** The service repositories (Greenie, Slinker, etc.) are maintained separately and must be cloned by the install script. A fresh `git clone` of Evershade alone will not have the service code.

### Installation Profiles

| Profile | Services | Command |
|---------|----------|---------|
| **Minimal** | Core only (4 services) | `docker compose --profile minimal up -d` |
| **Standard** | All services (8 services) | `docker compose --profile standard up -d` |
| **Full** | + Slammer Dashboard | `docker compose --profile full up -d` |
| **+ Ollama** | Local LLM support | `docker compose --profile standard --profile ollama up -d` |
| **+ Proxy** | Caddy reverse proxy with TLS | `docker compose --profile standard --profile proxy up -d` |
| **Dev** | Development mode | `docker compose --profile dev up -d` |

### Startup Scripts

```bash
# Linux/macOS
./install.sh --profile standard   # Clone service repositories
./start.sh --profile standard     # Start services with profile
./stop.sh                         # Stop all services

# Windows PowerShell
.\install.ps1 -Profile standard   # Clone service repositories
.\start.ps1 -Profile standard     # Start services with profile
.\stop.ps1                        # Stop all services
```

**Profiles:** `minimal` (core only), `standard` (all services), `full` (+ dashboard).

**Modes:** Add `--mode server` for production deployment (requires secure API keys).

---

## Your First Agent

This tutorial walks you through setting up Evershade and running your first AI agent.

### Step 1: Install and Start

```bash
git clone https://github.com/LukaG712/Evershade.git && cd Evershade

# Install service repositories
./install.sh --profile minimal    # Linux/macOS
# .\install.ps1 -Profile minimal  # Windows PowerShell

cp .env.example .env
# Edit .env — at minimum, set unique API keys

# Start services
./start.sh --profile minimal      # Linux/macOS
# .\start.ps1 -Profile minimal    # Windows PowerShell
```

### Step 2: Access the Dashboard

Open **http://localhost:8080** in your browser. You'll see the Greenie dashboard with:

- **Chat** — Talk to AI agents
- **Dashboard** — Manage agents, runs, pipelines
- **API Docs** — Swagger UI at `/docs`

### Step 3: Create Your First Agent

1. Go to **Dashboard → Agents**
2. Click **Create Agent**
3. Fill in:
   - **Name**: `researcher`
   - **Runner**: `junie`
   - **Guidelines**: `Always cite your sources.`
4. Click **Save**

### Step 4: Run a Task

1. Go to **Chat**
2. Select your `researcher` agent
3. Type: `Summarize the key points of climate change`
4. Watch the agent work in real-time

### Step 5: Try a Pipeline

Create a cross-service pipeline via the API:

```bash
curl -X POST http://localhost:8080/api/pipeline \
  -H "Authorization: Bearer $EVERSHADE_GREENIE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "steps": [
      { "service": "Trapper", "action": "scrape", "url": "https://news.ycombinator.com" },
      { "service": "Greenie", "action": "chat", "agent": "researcher", "prompt": "Summarize the top 5 stories" }
    ]
  }'
```

### Step 6: Explore More

- **Workflows** — Automate recurring tasks with schedules and triggers
- **Slammer Dashboard** — Standalone dashboard at `http://localhost:5173`
- **Speedy CLI** — Manage everything from the terminal: `evershade agents list`
- **Notifications** — Configure Slack/Discord alerts via Poltergeist
- **LLM Providers** — Connect OpenAI, Anthropic, or Ollama via Shrewd

---

## Architecture

```
Evershade
├── 🌐 Browser (:8080/:5173)
├── ⚡ Speedy CLI
└── 🔒 Caddy Proxy (TLS)
    ├── 🟢 Greenie (:8080) — API backend
    │   ├── 🔧 Slinker (:8000) — Code execution
    │   ├── 🕸️ Trapper (:3000) — Web scraping
    │   ├── 🧠 Shrewd (:8089) — LLM routing
    │   ├── 💾 Gobber (:8085) — Storage & knowledge graph
    │   ├── 🔐 Hider (:8087) — Encrypted secrets
    │   ├── 📢 Poltergeist (:8088) — Notifications
    │   └── 👁️ Sneaker (:8086) — Observability & OTLP
    │       └── SQLite · Redis · Obsidian Vault · Git
    └── 🔵 Slammer (:5173) — React dashboard
```

### Data Flow

How requests flow through the system:

- **Greenie** ──► **Slinker** ──► **Gobber** (store execution results)
- **Greenie** ──► **Trapper** ──► **Gobber** (cache scraped data)
- **Greenie** ──► **Trapper** ──► **Redis** (job queue)
- **Greenie** ──► **Shrewd** ──► External LLM providers
- **Greenie** ──► **Gobber** ──► SQLite / Obsidian / Embeddings
- **Greenie** ──► **Hider** ──► Encrypted secrets vault
- **Greenie** ──► **Poltergeist** ──► Slack / Discord / Email / Telegram
- **Greenie** ──► **Sneaker** ──► Metrics / Traces / Logs / OTLP
- **Slinker** ──► **Shrewd** (code generation via LLM)

### How They Work Together

1. **You** interact with Greenie's web dashboard at `localhost:8080` or Slammer at `localhost:5173`
2. **Greenie** manages your agents, sessions, pipelines, workflows, and workstations
3. When a task needs code execution, Greenie sends it to **Slinker**
4. When a task needs web data, Greenie sends it to **Trapper**
5. **Shrewd** routes LLM requests to OpenAI, Anthropic, Google, or Ollama
6. **Hider** stores secrets encrypted at rest (AES-256-GCM)
7. **Gobber** provides persistent storage, cache, and knowledge graph
8. **Poltergeist** sends notifications to Slack, Discord, email, Telegram
9. **Sneaker** collects metrics and traces for observability
10. Results flow back through Greenie to your dashboard

### Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python, FastAPI, SQLite (WAL mode) |
| **Frontend** | React, TypeScript, Tailwind CSS (Slammer) |
| **Containerization** | Docker Compose |
| **Reverse Proxy** | Caddy (automatic TLS) |
| **Cache & Queues** | Redis 8 |
| **Web Scraping** | Playwright |
| **Notifications** | Slack, Discord, Email, Telegram |
| **LLM Providers** | OpenAI, Anthropic, Google AI, Ollama (local) |
| **Observability** | OpenTelemetry (OTLP), custom metrics & traces |
| **Encryption** | AES-256-GCM for secrets at rest |

### Cross-Service Pipelines

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

### Workflow Engine

Automate multi-step workflows with triggers, approvals, and conditions:

```json
POST /api/workflows
{
  "name": "Research Pipeline",
  "trigger": { "type": "schedule", "cron": "0 9 * * 1" },
  "steps": [
    { "type": "service", "service": "Trapper", "action": "scrape", "url": "https://news.example.com" },
    { "type": "agent", "agent": "researcher", "prompt": "Summarize the latest news" },
    { "type": "approval", "message": "Review the summary before sending" },
    { "type": "notify", "channel": "slack", "recipient": "#research" }
  ]
}
```

---

## Services

> *"The Dark Moon has shattered, Luigi! We need to find it and restore peace to Evershade Valley, posthaste!"*
> ~ **Prof. E. Gadd**, on the state of the valley

All service names are inspired by [Luigi's Mansion ghosts](https://luigi-mansion.fandom.com/wiki/List_of_ghosts). See the [Naming Theme](#naming-theme) section for details.

### Service Overview

| Service | Version | Port | Role | UI |
|---------|---------|------|------|-----|
| **Greenie** | `1.7.0` | `8080` | Central hub & orchestrator | API backend |
| **Slinker** | `1.1.0` | `8000` | Task execution engine | API only |
| **Trapper** | `1.0.0` | `3000` | Web scraping & crawling | API only |
| **Gobber** | `1.0.0` | `8085` | Persistent storage & knowledge graph | API only |
| **Sneaker** | `1.1.0` | `8086` | Observability (metrics, traces, logs) | API only |
| **Hider** | `1.0.0` | `8087` | Secrets & config management | API only |
| **Poltergeist** | `1.1.0` | `8088` | Notifications (Slack, Discord, email, Telegram) | API only |
| **Shrewd** | `1.1.0` | `8089` | LLM provider abstraction | API only |
| **Slammer** | `1.4.0` | `5173` | Standalone web dashboard | React web app |
| **Speedy** | `1.1.0` | — | CLI tool (`evershade` command) | Terminal |

> **🌐 Website:** Visit the [Evershade website](website/index.html) for interactive documentation, service details, and getting started guides.

### Service Details

#### Greenie — Central Hub & API Backend

The brain of the operation. Greenie is a full-featured API server that manages AI agents, chat sessions, pipelines, analytics, missions, workflows, and workstations. It serves as the central orchestrator for all Evershade services.

- **320+ API endpoints** with Swagger/ReDoc docs
- **SQLite** with feature-store persistence
- Mission Control, Agent Harness, and workflow engine
- MCP server and plugin support

**Repo:** [LukaG712/Greenie](https://github.com/LukaG712/Greenie)

---

#### Slinker — Execution Engine

The worker behind the scenes. Slinker takes tasks from Greenie and executes them in isolated Git worktrees using the Junie CLI. It handles code generation, file modifications, refactoring, and any task that requires running AI agents against a codebase.

- **Git worktrees** per task for isolation
- **Junie CLI** integration for code agents
- Pure API service — manage tasks through Greenie's dashboard

**Repo:** [LukaG712/Slinker](https://github.com/LukaG712/Slinker)

---

#### Trapper — Web Scraping & Crawling

The eyes on the web. Trapper uses Playwright to scrape, crawl, search, and map websites, turning raw HTML into clean, structured, LLM-ready data.

- **Playwright headless** browser automation
- **Redis-backed** job queue for background tasks
- Single-page scraping, deep crawling, and site mapping

**Repo:** [LukaG712/Trapper](https://github.com/LukaG712/Trapper)

---

#### Gobber — Persistent Storage & Knowledge Graph

The memory and brain of the ecosystem. Gobber provides persistent storage for webhooks, analytics, RBAC, cache, and feature flags — solving the in-memory data loss problem when services restart.

- **SQLite with WAL mode** for durability
- **Obsidian vault integration** — scan notes, generate embeddings, enable semantic search
- Centralized data layer and semantic memory

**Repo:** [LukaG712/Gobber](https://github.com/LukaG712/Gobber)

---

#### Sneaker — Observability

The eyes on your system. Sneaker collects metrics, traces, and logs from all services, providing unified observability with alerting and OTLP integration.

- **Metrics**, distributed traces, and log aggregation
- **OTLP export** — integrate with any OpenTelemetry collector
- **Alerting** with deduplication, cooldown, and Poltergeist delivery
- System health monitoring across all services

**Repo:** [LukaG712/Sneaker](https://github.com/LukaG712/Sneaker)

---

#### Hider — Secrets & Config

The vault for sensitive data. Hider provides encrypted storage for API keys, passwords, and centralized configuration management.

- **AES-256-GCM** encryption for secrets at rest
- Versioned configuration management

**Repo:** [LukaG712/Hider](https://github.com/LukaG712/Hider)

---

#### Poltergeist — Notifications

The messenger of the ecosystem. Poltergeist sends notifications to Slack, Discord, email, and Telegram with templated messages and async delivery.

- **Channels:** Slack, Discord, email, Telegram, webhooks
- Unified notification hub

**Repo:** [LukaG712/Poltergeist](https://github.com/LukaG712/Poltergeist)

---

#### Shrewd — LLM Abstraction

The brain behind the models. Shrewd provides a unified interface for OpenAI, Anthropic, Google, and Ollama — letting you swap models and manage costs.

- **Providers:** OpenAI, Anthropic, Google, Ollama
- LLM provider abstraction layer

**Repo:** [LukaG712/Shrewd](https://github.com/LukaG712/Shrewd)

---

#### Slammer — Web Dashboard

The command center. Slammer is the single unified React-based web dashboard for managing agents, runs, pipelines, missions, workflows, workstations, metrics, logs, and plugin/MCP management across all Evershade services.

- **Stack:** React, TypeScript, Tailwind CSS
- Mission dashboard with milestone progress and validation results
- Real-time SSE log streaming

**Repo:** [LukaG712/Slammer](https://github.com/LukaG712/Slammer)

---

#### Speedy — CLI Tool

The terminal companion. Speedy provides an `evershade` command for managing everything from the command line — services, agents, tasks, diagnostics, and backups.

- **Install:** `pip install speedy-cli`
- **Commands:** `install`, `start`, `stop`, `logs`, `doctor`, `backup`, `restore`

**Repo:** [LukaG712/Speedy](https://github.com/LukaG712/Speedy)

---

## Mission Control

> *"Now that all the ghosts of Evershade Valley are under my control..."*
> ~ **King Boo**, Luigi's Mansion: Dark Moon

Evershade's Mission Control system provides factory-inspired orchestration for complex AI-driven development workflows. Missions break down large tasks into milestones, features, and automated validation cycles.

### Key Capabilities

| Feature | Description |
|---------|-------------|
| **Mission Lifecycle** | Create, plan, execute, validate, complete, cancel, pause, and resume missions |
| **Automated Planning** | LLM-based planning via Shrewd with repository intelligence and heuristic fallback |
| **Milestones & Features** | Break missions into milestones with parallel worker execution |
| **Code Review** | Automated deterministic checks (test, lint, type) and diff-based security review |
| **Approval Gates** | Human-in-the-loop approval for sensitive operations with three autonomy levels |
| **Fix-Revalidate** | Automatically create fix features from validation failures with configurable retries |
| **SSE Streaming** | Real-time mission execution logs via Server-Sent Events |
| **Analytics** | Success/failure rates, duration tracking, model usage, and validation summaries |
| **Checkpoint Recovery** | Persist mission state and recover from failures |
| **Secret Redaction** | Pattern-based redaction of API keys, tokens, and passwords in logs |

### Mission Workflow

```
  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │ Create       │────►│ LLM Planning │────►│ Execute      │────►│ Validate     │
  │ Mission      │     │              │     │ Features     │     │ Results      │
  └──────────────┘     └──────────────┘     └──────────────┘     └──────┬───────┘
                                                                        │
                                                              ┌─────────▼─────────┐
                                                              │   All Pass?       │
                                                              └───┬───────────┬───┘
                                                                   │ Yes       │ No
                                                            ┌──────▼──────┐ ┌───▼──────────────┐
                                                            │ Complete    │ │ Fix-Revalidate   │
                                                            │ Mission     │ │ └────────┬───────┘
                                                            └─────────────┘          │
                                                                                     │
                                                                            ┌────────▼───────┐
                                                                            │ Execute        │
                                                                            │ Features       │
                                                                            └────────────────┘
```

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/missions` | Create a new mission |
| `GET /api/missions` | List all missions |
| `GET /api/missions/{id}` | Get mission details |
| `POST /api/missions/{id}/plan` | Trigger LLM planning |
| `POST /api/missions/{id}/execute` | Start execution |
| `POST /api/missions/{id}/validate` | Run validation |
| `POST /api/missions/{id}/fix-revalidate` | Auto-fix failures |
| `GET /api/missions/{id}/logs/stream` | SSE log stream |
| `GET /api/missions/analytics` | Mission analytics |

---

## Agent Harness

The Agent Harness provides reusable workflows, specialized subagents, and event-driven automation for advanced agent development.

### Spec Mode

Research-first development: create specs, analyze repositories, approve plans, then convert to missions.

| Endpoint | Description |
|----------|-------------|
| `POST /api/specs` | Create a new spec |
| `POST /api/specs/{id}/analyze` | Run repository analysis |
| `POST /api/specs/{id}/approve` | Approve and convert to mission |

### Custom Droids

Specialized subagents with their own prompts, models, and tool policies. Built-in droids: **worker**, **explorer**, **reviewer**, **validator**.

### Skills System

Reusable `SKILL.md` workflows with trigger-based auto-discovery. Skills are matched to tasks and can be invoked manually.

### Hooks System

Event-driven lifecycle hooks for mission events: `PreToolUse`, `PostToolUse`, `MissionStart`, `MissionEnd`, `MilestoneComplete`, `ValidationFail`. Supports script and webhook hooks.

### Environments

Reusable sandbox definitions with repository, dependencies, setup commands, and health checks.

---

## Workstations

> *"This place is crawling with ghosts, Luigi!"*
> ~ **Prof. E. Gadd**, on the mansion's defenses

Workstations provide isolated container-based environments for agent execution with full lifecycle management.

### Features

| Feature | Description |
|---------|-------------|
| **Container Driver** | Isolated agent environments with network policies |
| **Lifecycle Management** | Create, start, stop, and destroy workstations |
| **Network Policies** | Default-deny network access for security |
| **Live Terminal** | WebSocket-based terminal access for human interaction |
| **Desktop Access** | Optional desktop interface for visual tasks |
| **Integration** | Works with Slinker and workflow engine |

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/workstations` | Create a new workstation |
| `GET /api/workstations` | List all workstations |
| `POST /api/workstations/{id}/start` | Start a workstation |
| `POST /api/workstations/{id}/stop` | Stop a workstation |
| `DELETE /api/workstations/{id}` | Destroy a workstation |
| `WS /api/workstations/{id}/terminal` | Live terminal WebSocket |

---

## Web Interfaces

| Interface | URL | Description |
|-----------|-----|-------------|
| **Slammer Dashboard** | `http://localhost:5173` | Single unified dashboard — agents, runs, missions, workflows, workstations, metrics, logs |
| **Greenie API Docs** | `http://localhost:8080/docs` | Swagger UI for all Greenie endpoints |
| **Greenie ReDoc** | `http://localhost:8080/redoc` | Alternative API documentation |
| **Slinker API Docs** | `http://localhost:8000/docs` | Swagger UI for Slinker endpoints |
| **Trapper API Docs** | `http://localhost:3000/docs` | Swagger UI for Trapper endpoints |

> **Note:** Greenie operates as an API-only backend. Slammer is the single unified dashboard for all visual management. Slinker and Trapper are API-only services.

---

## API Documentation

Each service exposes auto-generated API docs:

| Service | Swagger UI | ReDoc | OpenAPI JSON |
|---------|-----------|-------|-------------|
| **Greenie** | `localhost:8080/docs` | `localhost:8080/redoc` | `localhost:8080/openapi.json` |
| **Slinker** | `localhost:8000/docs` | `localhost:8000/redoc` | `localhost:8000/openapi.json` |
| **Trapper** | `localhost:3000/docs` | `localhost:3000/redoc` | `localhost:3000/openapi.json` |

---

## Configuration

Copy `.env.example` to `.env` and configure. See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for the full reference.

### API Keys (Required)

Generate unique keys for each service. **Never use the default values in production.**

```bash
# Generate a secure key
openssl rand -hex 32
```

All variables use the `EVERSHADE_<SERVICE>_<SETTING>` naming convention. Legacy names (e.g., `HUB_API_KEY`) still work but are deprecated.

| Variable | Description |
|----------|-------------|
| `EVERSHADE_GREENIE_API_KEY` | Greenie API key |
| `EVERSHADE_SLINKER_API_KEY` | Slinker API key |
| `EVERSHADE_TRAPPER_API_KEY` | Trapper API key |
| `EVERSHADE_GOBBER_API_KEY` | Gobber API key |
| `EVERSHADE_ENCRYPTION_KEY` | Hider encryption key |

### Optional Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `EVERSHADE_OPENAI_API_KEY` | *(empty)* | OpenAI API key |
| `EVERSHADE_OLLAMA_URL` | `http://host.docker.internal:11434` | Ollama endpoint |
| `EVERSHADE_OLLAMA_MODEL` | `gemma4:12b` | Default Ollama model |
| `EVERSHADE_WORKSPACE_PATH` | `./workspace` | Workspace directory |
| `EVERSHADE_MAX_CONCURRENT_WORKERS` | `1` | Concurrent Slinker workers |
| `EVERSHADE_ISOLATION_MODE` | `worktree` | Isolation mode |
| `EVERSHADE_OBSIDIAN_VAULT_PATH` | `./obsidian-vault` | Obsidian vault path |
| `EVERSHADE_LOG_LEVEL` | `INFO` | Log verbosity |

### Deployment Mode

| Variable | Default | Description |
|----------|---------|-------------|
| `EVERSHADE_MODE` | `desktop` | `desktop` = loopback, `server` = all interfaces |
| `EVERSHADE_BIND_ADDRESS` | `127.0.0.1` | Bind address for host ports |
| `EVERSHADE_PUBLIC_URL` | `http://localhost:8080` | Public base URL |

---

## Deployment

For server deployment (headless VM, access from another computer), see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

```bash
# Server mode: edit .env
EVERSHADE_MODE=server
EVERSHADE_BIND_ADDRESS=0.0.0.0
EVERSHADE_PUBLIC_URL=http://YOUR_SERVER_IP:8080
```

---

## Security

- **Bearer token auth** on all services (query params rejected)
- **AES-256-GCM encryption** for secrets at rest (Hider)
- **SSRF protection** blocks private IPs and cloud metadata (Trapper)
- **Read-only containers** with capability dropping
- **Internal Docker network** — only Greenie exposed on host

### Security Notes

- Server mode refuses to start with default API keys
- Resource limits are applied to all services
- Store your `.env` file securely and never commit it to version control
- See [docs/SECURITY.md](docs/SECURITY.md) for the full security model

---

## Testing

Evershade includes a comprehensive test suite covering integration, security, performance, and reliability. See [docs/TESTING.md](docs/TESTING.md) for details.

| Category | Description | Command |
|----------|-------------|---------|
| **Unit** | Tests without live services | `./tests/run-all-tests.sh unit` |
| **Integration** | Cross-service communication | `./tests/run-all-tests.sh integration` |
| **Security** | Prompt injection, SSRF, auth bypass | `./tests/run-all-tests.sh security` |
| **Benchmarks** | Latency, throughput, concurrency | `./tests/run-all-tests.sh benchmarks` |
| **Evaluation** | Agent quality scoring | `./tests/run-all-tests.sh evaluation` |
| **Chaos** | Failure injection, resilience | `./tests/run-all-tests.sh chaos` |
| **All** | Run everything (requires services) | `./tests/run-all-tests.sh all` |

### Running Tests

```bash
# Run unit tests (no services required)
./tests/run-all-tests.sh unit

# Start all services first (for integration tests)
docker compose --profile standard up -d

# Run all tests (requires services)
./tests/run-all-tests.sh all

# Run a specific category
./tests/run-all-tests.sh security
```

### Release Signing

```bash
# Sign all artifacts for a release
python scripts/release_sign.py --version 1.5.0 --sign-all --secret "your-signing-key"

# Verify a release
python scripts/verify_release.py --release release/ --secret "your-signing-key"
```

---

## Backup & Restore

> *"Luigi, we gotta save all our progress before the ghosts strike again!"*
> ~ **Prof. E. Gadd**, on data safety

Evershade provides built-in backup and restore functionality via the Speedy CLI.

```bash
# Create a full backup
evershade backup --output ./evershade-backup.tar.gz

# Restore from a backup
evershade restore --input ./evershade-backup.tar.gz

# Backup specific services
evershade backup --services Greenie,Gobber,Hider --output ./partial-backup.tar.gz
```

### What's Backed Up

| Component | Data |
|-----------|------|
| **Greenie** | Agents, sessions, pipelines, workflows, missions |
| **Gobber** | SQLite databases, Obsidian vault, embeddings |
| **Hider** | Encrypted secrets and configurations |
| **Sneaker** | Metrics, traces, and logs |
| **Poltergeist** | Notification history |
| **Redis** | Cache and job queue data |

For detailed backup strategies, see [docs/BACKUP_RESTORE.md](docs/BACKUP_RESTORE.md).

---

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **Services won't start** | Run `evershade doctor` to diagnose issues |
| **Port already in use** | Change the port in `.env` or stop the conflicting service |
| **API key authentication failed** | Ensure all `EVERSHADE_*_API_KEY` values match between services |
| **Greenie can't reach Slinker/Trapper** | Verify Docker network: `docker network ls \| grep evershade` |
| **Ollama not responding** | Check `EVERSHADE_OLLAMA_URL` — use `http://host.docker.internal:11434` on Docker |
| **Redis connection refused** | Ensure Redis container is running: `docker compose ps redis` |
| **CSRF token missing** | Ensure cookies are enabled; check `CSRF_SECRET_KEY` is set |
| **Encryption key error** | Set `EVERSHADE_ENCRYPTION_KEY` to a 32-byte hex string |

### Diagnostic Commands

```bash
# Check service health
evershade doctor

# View service logs
docker compose logs -f Greenie
docker compose logs -f Slinker
docker compose logs -f Trapper

# Check network connectivity
docker compose exec Greenie ping Slinker
docker compose exec Greenie ping Trapper

# Verify API keys
curl -H "Authorization: Bearer $EVERSHADE_GREENIE_API_KEY" http://localhost:8080/health
```

### Health Check Endpoints

| Service | Health Endpoint |
|---------|----------------|
| **Greenie** | `GET http://localhost:8080/health` |
| **Slinker** | `GET http://localhost:8000/health` |
| **Trapper** | `GET http://localhost:3000/health` |
| **Gobber** | `GET http://localhost:8085/health` |
| **Sneaker** | `GET http://localhost:8086/health` |
| **Hider** | `GET http://localhost:8087/health` |
| **Poltergeist** | `GET http://localhost:8088/health` |
| **Shrewd** | `GET http://localhost:8089/health` |

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on reporting bugs, suggesting features, and submitting pull requests.

```bash
# Quick development setup
git clone https://github.com/LukaG712/Evershade.git
cd Evershade
cp .env.example .env
docker compose --profile dev up -d
```

For detailed development instructions, see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

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
├── Trapper/                   → Separate repo (LukaG712/Trapper)
├── Gobber/                    → Separate repo (LukaG712/Gobber)
├── Sneaker/                   → Separate repo (LukaG712/Sneaker)
├── Hider/                     → Separate repo (LukaG712/Hider)
├── Poltergeist/               → Separate repo (LukaG712/Poltergeist)
├── Shrewd/                    → Separate repo (LukaG712/Shrewd)
├── Slammer/                   → Separate repo (LukaG712/Slammer)
└── Speedy/                    → Separate repo (LukaG712/Speedy)
```

Each sub-project is an independent Git repository with its own CI pipeline. The root repo tracks orchestration files (Docker Compose, CI, scripts) and excludes the sub-project directories via `.gitignore`.

---

## Roadmap

> *"Everything was swell, until someone split the Dark Moon..."*
> ~ **The Dark Moon Song**, on how it all began

### Development Timeline

```
Phase  ─ Name ────────────────── Period ───────── Status
─────  ──────────────────────────────────────────────────────
  1   │ Foundations                Jan 2026       ✓ Complete
  2   │ Security & Persistence     Feb 2026       ✓ Complete
  3   │ Real Implementation        Mar 2026       ✓ Complete
  4   │ Workflow Engine            Apr 2026       ✓ Complete
  5   │ Agent Workstations         May 2026       ✓ Complete
  6   │ Quality & Release          Jun 2026       ✓ Complete
  7   │ UI and Extensibility       Jul 2026       ✓ Complete
  8   │ Emergency Stop & More      Aug 2026       ✓ Complete
  9   │ Mission Control            Sep 2026       ✓ Complete
 10   │ Security & OTLP            Oct 2026       ✓ Complete
 11   │ Agent Harness              Nov 2026       ✓ Complete
```

### Completed Phases

| Phase | Name | Key Deliverables |
|-------|------|------------------|
| **1** | Foundations | Ecosystem audit, architecture docs, Docker Compose profiles |
| **2** | Security & Persistence | AES-256-GCM encryption, Bearer token auth, SSRF protection |
| **3** | Real Implementation | LLM providers, notification delivery, Slammer dashboard |
| **4** | Workflow Engine | Persistent workflows, triggers, approval gates, audit trail |
| **5** | Agent Workstations | Container driver, lifecycle management, network policies |
| **6** | Quality & Release | Integration tests, security tests, benchmarks, release signing |
| **7** | UI and Extensibility | Slammer as single dashboard, MCP/plugin support |
| **8** | Emergency Stop & More | Global kill switch, activity timeline, credential rotation |
| **9** | Mission Control | Mission lifecycle, planning, validation, fix-revalidate cycle |
| **10** | Security & OTLP | CSRF protection, vector embeddings, OTLP export |
| **11** | Agent Harness | Spec mode, custom droids, skills system, hooks, environments |

### Planned Service Decisions

| Service | Role | Decision | Rationale |
|---------|------|----------|-----------|
| **Mnemos** | Semantic memory | **DROP** | Gobber already covers this. Extend Gobber instead. |
| **Bridge** | External integrations | **EVALUATE** | Greenie has webhooks. Only if new types needed. |
| **Courier** | File storage | **EVALUATE** | Greenie has 50MB upload. Only if more needed. |

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [ROADMAP.md](ROADMAP.md) for details.

---

## Naming Theme

> *"Oh boy..."*
> ~ **Luigi**, probably reacting to all these ghost names

All services are named after ghosts from the **Luigi's Mansion** series. The root repository is named **Evershade** after *Evershade Valley*, the setting of Luigi's Mansion: Dark Moon.

| Service | Ghost Origin | Game |
|---------|-------------|------|
| **Greenie** | Small green ghosts | Luigi's Mansion: Dark Moon |
| **Slinker** | Wall-crawling stealth ghosts | Luigi's Mansion 3 |
| **Trapper** | Trap-setting ghosts | Luigi's Mansion 3 |
| **Gobber** | Blob-like absorbing ghost | Luigi's Mansion: Dark Moon |
| **Sneaker** | Quiet sneaking ghost | Luigi's Mansion: Dark Moon |
| **Hider** | Hiding ghost | Luigi's Mansion: Dark Moon |
| **Poltergeist** | Ancient disturbance ghost | Luigi's Mansion: Dark Moon |
| **Shrewd** | Possessor (Three Sisters) | Luigi's Mansion: Dark Moon |
| **Slammer** | Heavy-hitting ground slammer | Luigi's Mansion: Dark Moon |
| **Speedy** | Fast zooming ghost | Luigi's Mansion: Dark Moon |

### Future Service Name Ideas

More ghost names from the series available for new services:

| Name | Origin | Suggested Role |
|------|--------|---------------|
| **Boo** | Classic iconic ghost | Authentication / gateway service |
| **Oozers** | LM3 ooze-like ghosts | File storage / blob service |
| **Hammer** | LM3 hammer-wielding ghost | Deployment / infrastructure service |
| **Goob** | LM3 basic ghost | Task queue / job scheduler |
| **Grouchy** | Dark Moon spider boss | Security / firewall service |
| **Nana** | Dark Moon portrait ghost | Document processing service |
| **Shivers** | Dark Moon ice ghost | Cooling / rate limiting service |
| **Biff** | Dark Moon bouncer ghost | API gateway / load balancer |

---

## License

This project is licensed under the [MIT License](LICENSE).

| Repository | License |
|------------|---------|
| Evershade (root) | MIT |
| Greenie | MIT (see [Greenie/LICENSE](Greenie/LICENSE)) |
| Slinker | MIT |
| Trapper | MIT (see [Trapper/LICENSE](Trapper/LICENSE)) |
| Other services | MIT |

---

> *"Now that all the ghosts of Evershade Valley are under my control..."*
> ~ **King Boo**, Luigi's Mansion: Dark Moon

> *"Oh boy..."*
> ~ **Luigi**, probably

---

> **Disclaimer:** This project is a fan-made, independent software project. It is not affiliated with, endorsed by, or in any way connected to Nintendo, Next Level Games, or any of their subsidiaries. All Luigi's Mansion trademarks and character names are property of their respective owners. Service names are used purely for thematic inspiration.
