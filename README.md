# Evershade

> *"E. Gadd to Luigi! Am I comin' in clear, do you read me?"* 
> ~ **Prof. E. Gadd**, Luigi's Mansion: Dark Moon

> **A self-hosted AI agent platform built as a collection of specialized microservices.**

All service names are inspired by [Luigi's Mansion ghosts](https://luigi-mansion.fandom.com/wiki/List_of_ghosts).

---

## About

**Evershade** is a self-hosted AI agent platform built as a collection of specialized microservices, orchestrated together via Docker Compose. Each service is an independent repository that can run alone or as part of the full ecosystem.

| | |
|---|---|
| **Website** | [http://localhost:8080](http://localhost:8080) |
| **Services** | [Greenie](https://github.com/LukaG712/Greenie) · [Slinker](https://github.com/LukaG712/Slinker) · [Trapper](https://github.com/LukaG712/Trapper) · [Gobber](https://github.com/LukaG712/Gobber) · [Sneaker](https://github.com/LukaG712/Sneaker) · [Hider](https://github.com/LukaG712/Hider) · [Poltergeist](https://github.com/LukaG712/Poltergeist) · [Shrewd](https://github.com/LukaG712/Shrewd) · [Slammer](https://github.com/LukaG712/Slammer) · [Speedy](https://github.com/LukaG712/Speedy) |
| **Topics** | ai-agents · microservices · self-hosted · docker-compose · web-scraping · code-execution · luigis-mansion |
| **Built with** | Python · TypeScript · FastAPI · Playwright · Junie CLI |

---

## Services

> *"The Dark Moon has shattered, Luigi! We need to find it and restore peace to Evershade Valley, posthaste!"*
> ~ **Prof. E. Gadd**, on the state of the valley

### Greenie ~ Central Hub & Dashboard

**Luigi's Mansion origin:** *Greenie* ~ small green ghosts from Luigi's Mansion: Dark Moon (Evershade Valley).

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

> *"You really got to be OCD like the worst guest at an Airbnb ~ get gold, get cash, get blings!"*
> ~ **The Dark Moon Song**, on collecting everything

---

### Slinker ~ Execution Engine

**Luigi's Mansion origin:** *Slinker* ~ stealthy ghost enemies from Luigi's Mansion 3 that slink along walls and floors.

The worker behind the scenes. Slinker takes tasks from Greenie and executes them in isolated Git worktrees using the Junie CLI. It handles code generation, file modifications, refactoring, and any task that requires running AI agents against a codebase.

| Feature | Details |
|---------|---------|
| **Port** | `8000` |
| **UI** | API only (no web frontend) |
| **Isolation** | Git worktrees per task |
| **Runner** | Junie CLI integration |
| **Role** | Task execution, code agent runner |

Slinker has no dashboard ~ it's a pure API service. You manage tasks through Greenie's dashboard, which sends work to Slinker.

**Repo:** [LukaG712/Slinker](https://github.com/LukaG712/Slinker)

> *"These ghosts seem unassailable, don't worry they're still inhalable!"*
> ~ **Prof. E. Gadd**, on facing any challenge

---

### Trapper ~ Web Scraping & Crawling

**Luigi's Mansion origin:** *Trapper* ~ ghost enemies from Luigi's Mansion 3 that trap and capture.

The eyes on the web. Trapper uses Playwright to scrape, crawl, search, and map websites, turning raw HTML into clean, structured, LLM-ready data. It supports single-page scraping, deep crawling, site mapping, and background job queues via Redis.

| Feature | Details |
|---------|---------|
| **Port** | `3000` |
| **UI** | API only (no web frontend) |
| **Browser** | Playwright headless |
| **Queue** | Redis-backed job queue |
| **Role** | Web scraping, crawling, content extraction |

**Repo:** [LukaG712/Trapper](https://github.com/LukaG712/Trapper)

> *"Gotta stop dat King Boo, 'cause he broke up the whole Dark Moon dude!"*
> ~ **Prof. E. Gadd**, on the mission ahead

---

### Gobber ~ Persistent Storage & Knowledge Graph

**Luigi's Mansion origin:** *Gobber* ~ blob-like ghosts from Luigi's Mansion: Dark Moon that absorb and store everything.

The memory and brain of the ecosystem. Gobber provides persistent storage for webhooks, analytics, RBAC, cache, and feature flags ~ solving the in-memory data loss problem when services restart. It also integrates **Obsidian vault as a second brain** ~ scanning your notes, generating embeddings, and enabling semantic search.

| Feature | Details |
|---------|---------|
| **Port** | `8085` |
| **Storage** | SQLite with WAL mode |
| **Features** | Webhooks, analytics, RBAC, cache, feature flags, knowledge graph |
| **Obsidian** | Vault scanning, semantic search, graph traversal |
| **Role** | Centralized data layer & semantic memory |

**Repo:** [LukaG712/Gobber](https://github.com/LukaG712/Gobber)

---

### Sneaker ~ Observability

**Luigi's Mansion origin:** *Sneaker* ~ quiet ghosts from Luigi's Mansion: Dark Moon that sneak up silently, perfect for quietly monitoring everything.

The eyes on your system. Sneaker collects metrics, traces, and logs from all services, providing unified observability.

| Feature | Details |
|---------|---------|
| **Port** | `8086` |
| **Features** | Metrics, distributed traces, log aggregation |
| **Role** | System health monitoring |

**Repo:** [LukaG712/Sneaker](https://github.com/LukaG712/Sneaker)

---

### Hider ~ Secrets & Config

**Luigi's Mansion origin:** *Hider* ~ ghosts from Luigi's Mansion: Dark Moon that hide in plain sight.

The vault for sensitive data. Hider provides encrypted storage for API keys, passwords, and centralized configuration management.

| Feature | Details |
|---------|---------|
| **Port** | `8087` |
| **Features** | Encrypted secrets, versioned config |
| **Role** | Secret and configuration management |

**Repo:** [LukaG712/Hider](https://github.com/LukaG712/Hider)

---

### Poltergeist ~ Notifications

**Luigi's Mansion origin:** *Poltergeist* ~ the ancient ghosts from Luigi's Mansion: Dark Moon that cause disturbances and ruckuses, perfect for sending notifications.

The messenger of the ecosystem. Poltergeist sends notifications to Slack, Discord, email, and Telegram with templated messages and async delivery.

| Feature | Details |
|---------|---------|
| **Port** | `8088` |
| **Channels** | Slack, Discord, email, Telegram, webhooks |
| **Role** | Unified notification hub |

**Repo:** [LukaG712/Poltergeist](https://github.com/LukaG712/Poltergeist)

---

### Shrewd ~ LLM Abstraction

**Luigi's Mansion origin:** *Shrewd* ~ one of the Three Sisters (Possessors) from Luigi's Mansion: Dark Moon, known for being cunning and intelligent, perfect for an LLM service.

The brain behind the models. Shrewd provides a unified interface for OpenAI, Anthropic, Google, and Ollama ~ letting you swap models and manage costs.

| Feature | Details |
|---------|---------|
| **Port** | `8089` |
| **Providers** | OpenAI, Anthropic, Google, Ollama |
| **Role** | LLM provider abstraction |

**Repo:** [LukaG712/Shrewd](https://github.com/LukaG712/Shrewd)

---

### Slammer ~ Web Dashboard

**Luigi's Mansion origin:** *Slammer* ~ blue ghosts from Luigi's Mansion: Dark Moon that slam the ground with force, perfect for a dashboard that slams you with the big picture.

The command center. Slammer is a React-based standalone web dashboard for managing agents, runs, pipelines, and analytics across all Evershade services.

| Feature | Details |
|---------|---------|
| **Port** | `5173` |
| **Stack** | React, TypeScript, Tailwind CSS |
| **Role** | Standalone web dashboard |

**Repo:** [LukaG712/Slammer](https://github.com/LukaG712/Slammer)

---

### Speedy ~ CLI Tool

**Luigi's Mansion origin:** *Speedy Spirit* ~ fast ghosts from Luigi's Mansion that zoom around at high speed, perfect for a CLI that executes commands quickly.

The terminal companion. Speedy provides an `evershade` command for managing services, agents, tasks, and configuration from the command line.

| Feature | Details |
|---------|---------|
| **Install** | `pip install speedy-cli` |
| **Command** | `evershade` |
| **Role** | Command-line interface |

**Repo:** [LukaG712/Speedy](https://github.com/LukaG712/Speedy)

> *"Gotta stop dat King Boo, 'cause he broke up the whole Dark Moon dude!"*
> ~ **Prof. E. Gadd**, on the mission ahead

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

> *"Step into the dark! Five new spooky mansions!"*
> ~ **The Dark Moon Song**, on the adventure ahead

### Prerequisites

- **Docker** and **Docker Compose**
- **[Junie CLI](https://junie.jetbrains.com)** (for code agents) ~ optional

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

> *"Everything was swell, until someone split the Dark Moon..."*
> ~ **The Dark Moon Song**, on how it all began

All services are named after ghosts from the **Luigi's Mansion** series:

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

The root repository is named **Evershade** after *Evershade Valley*, the setting of Luigi's Mansion: Dark Moon.

### Future service name ideas

More ghost names from the series available for new services:

| Name | Origin | Suggested Role |
|------|--------|---------------|
| **Boo** | Classic ~ iconic ghost | Authentication / gateway service |
| **Oozers** | LM3 ~ ooze-like ghosts | File storage / blob service |
| **Hammer** | LM3 ~ hammer-wielding ghost | Deployment / infrastructure service |
| **Goob** | LM3 ~ basic ghost | Task queue / job scheduler |
| **Grouchy** | Dark Moon ~ spider boss | Security / firewall service |
| **Nana** | Dark Moon ~ portrait ghost | Document processing service |
| **Shivers** | Dark Moon ~ ice ghost | Cooling / rate limiting service |
| **Biff** | Dark Moon ~ bouncer ghost | API gateway / load balancer |

---

## Repository Structure

```
Evershade/ (this repo ~ orchestration)
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

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

#### API Keys (Required)

Generate unique keys for each service. **Never use the default values in production.**

```bash
# Generate a secure key
openssl rand -hex 32
```

| Variable | Description |
|----------|-------------|
| `HUB_API_KEY` | Greenie API key |
| `Slinker_API_KEY` | Slinker API key |
| `Trapper_API_KEY` | Trapper API key |
| `GOBBER_API_KEY` | Gobber API key |
| `SNEAKER_API_KEY` | Sneaker API key |
| `HIDER_API_KEY` | Hider API key |
| `POLTERGEIST_API_KEY` | Poltergeist API key |
| `SHREWD_API_KEY` | Shrewd API key |
| `ENCRYPTION_KEY` | Hider encryption key for stored secrets |

#### Optional Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(empty)* | OpenAI API key for Shrewd LLM abstraction |
| `OLLAMA_URL` | `http://host.docker.internal:11434` | Ollama API endpoint for local LLM inference |
| `OLLAMA_MODEL` | `gemma4:12b` | Ollama model name for Slinker |
| `REDIS_PASSWORD` | *(empty)* | Redis password for cluster support |
| `WORKSPACE_PATH` | `./workspace` | Path to workspace directory (use absolute path in production) |
| `MAX_CONCURRENT_WORKERS` | `1` | Maximum concurrent Slinker workers |
| `ISOLATION_MODE` | `worktree` | Slinker task isolation mode (`worktree` or `none`) |
| `JUNIE_BIN` | `junie` | Junie CLI binary path |
| `REFINE_PROMPT` | `false` | Whether to refine prompts before sending to Junie |
| `OBSIDIAN_VAULT_PATH` | `./obsidian-vault` | Path to Obsidian vault for Gobber knowledge graph |
| `LOG_LEVEL` | `INFO` | Log verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

#### Workspace Path

The `WORKSPACE_PATH` variable controls where agents access projects. Use an **absolute path** in production to avoid issues if docker-compose is run from a different directory:

```bash
# Recommended for production
WORKSPACE_PATH=/home/user/projects

# Development default (relative path)
WORKSPACE_PATH=./workspace
```

#### Security Notes

- The startup scripts (`start.sh` / `start.ps1`) will warn you if default API keys are detected.
- Resource limits are applied to all services to prevent any single service from consuming all host resources.
- Store your `.env` file securely and never commit it to version control.

---

## Future Expansion

The ecosystem is designed to grow. Future additions (names TBD from the ghost list above):

| Service | Role | Status |
|---------|------|--------|
| **Mnemos** | Semantic memory using vector embeddings | Planned |
| **Bridge** | External integrations (GitHub, calendar, email) | Planned |
| **Courier** | S3-compatible file storage service | Planned |

See [ECOSYSTEM_EXPANSION.md](ECOSYSTEM_EXPANSION.md) for the full expansion roadmap.

---

## License

Each sub-project may have its own license. Check the individual repositories.

---

> *"Now that all the ghosts of Evershade Valley are under my control..."*
> ~ **King Boo**, Luigi's Mansion: Dark Moon

> *"Oh boy..."* 
> ~ **Luigi**, probably
