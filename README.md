# Evershade

> *"E. Gadd to Luigi! Am I comin' in clear, do you read me?"* 
> ~ **Prof. E. Gadd**, Luigi's Mansion: Dark Moon

> **A self-hosted AI agent platform built as a collection of specialized microservices.**

All service names are inspired by [Luigi's Mansion ghosts](https://luigi-mansion.fandom.com/wiki/List_of_ghosts).

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
┌─────────────────────────────────────────────────────────────────────┐
│                        Your Browser                                 │
│              http://localhost:8080 (Greenie)                        │
│              http://localhost:5173 (Slammer Dashboard)              │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
     ┌────────▼────────┐ ┌────▼─────┐  ┌──────▼──────┐
     │   Greenie       │ │ Slammer  │  │   Speedy    │
     │   (8080)        │ │ (5173)   │  │   CLI       │
     │  Hub + Dashboard│ │ Dashboard│  │  Terminal   │
     └───┬─────┬───────┘ └──────────┘  └─────────────┘
         │     │
    ┌────▼─────▼────┐
    │  Service Mesh  │  ← Internal Docker network
    │  (Bearer Auth) │
    └───┬─────┬──────┘
        │     │
 ┌──────▼──┐ ┌▼──────────┐ ┌──────────┐ ┌──────────┐
 │ Slinker │ │ Trapper    │ │  Gobber  │ │  Hider   │
 │ (8000)  │ │ (3000)     │ │ (8085)   │ │ (8087)   │
 │ Execute │ │ Scrape     │ │ Storage  │ │ Secrets  │
 └─────────┘ └────────────┘ └──────────┘ └──────────┘
 
 ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
 │ Polter-  │ │  Shrewd  │ │ Sneaker  │ │  Caddy   │
 │ geist    │ │ (8089)   │ │ (8086)   │ │  Proxy   │
 │ (8088)   │ │ LLM      │ │ Metrics  │ │ (443)    │
 │ Notify   │ │ Routing  │ │ Traces   │ │ TLS      │
 └──────────┘ └──────────┘ └──────────┘ └──────────┘
```

### How they work together

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

### Security Model

- **Bearer token auth** on all services (query params rejected)
- **AES-256-GCM encryption** for secrets at rest (Hider)
- **SSRF protection** blocks private IPs and cloud metadata (Trapper)
- **Read-only containers** with capability dropping
- **Internal Docker network** — only Greenie exposed on host

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
# Edit .env with your API keys (see docs/CONFIGURATION.md)
docker compose --profile minimal up -d
```

The dashboard will be available at **http://localhost:8080**.

### Installation Profiles

| Profile | Services | Command |
|---------|----------|---------|
| **Minimal** | Core only | `docker compose --profile minimal up -d` |
| **Standard** | All services | `docker compose --profile standard up -d` |
| **Full** | + Dashboard | `docker compose --profile full up -d` |
| **+ Ollama** | Local LLM | `docker compose --profile standard --profile ollama up -d` |

### Remote Access

For server deployment (headless VM, access from another computer), see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

```bash
# Server mode: edit .env
EVERSHADE_MODE=server
EVERSHADE_BIND_ADDRESS=0.0.0.0
EVERSHADE_PUBLIC_URL=http://YOUR_SERVER_IP:8080
```

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

### Security Notes

- Server mode refuses to start with default API keys.
- Resource limits are applied to all services.
- Store your `.env` file securely and never commit it to version control.
- See [docs/SECURITY.md](docs/SECURITY.md) for the full security model.

---

## Testing & Quality

Evershade includes a comprehensive test suite covering integration, security, performance, and reliability:

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

## Tutorial: Your First Agent

This tutorial walks you through setting up Evershade and running your first AI agent.

### Step 1: Install and Start

```bash
# Clone and configure
git clone https://github.com/LukaG712/Evershade.git && cd Evershade
cp .env.example .env

# Edit .env — at minimum, set unique API keys
# (See docs/CONFIGURATION.md for all options)

# Start with minimal profile
docker compose --profile minimal up -d
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

## Future Expansion

The ecosystem is designed to grow. Planned service decisions after audit:

| Service | Role | Decision | Rationale |
|---------|------|----------|-----------|
| **Mnemos** | Semantic memory | **DROP** | Gobber already covers this. Extend Gobber instead. |
| **Bridge** | External integrations | **EVALUATE** | Greenie has webhooks. Only if new types needed. |
| **Courier** | File storage | **EVALUATE** | Greenie has 50MB upload. Only if more needed. |

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [ROADMAP.md](ROADMAP.md) for details.

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
