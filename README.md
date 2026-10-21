```
 :::::::::: :::     ::: :::::::::: :::::::::   ::::::::  :::    :::     :::     :::::::::  ::::::::::
:+:        :+:     :+: :+:        :+:    :+: :+:    :+: :+:    :+:   :+: :+:   :+:    :+: :+:        
+:+        +:+     +:+ +:+        +:+    +:+ +:+        +:+    +:+  +:+   +:+  +:+    +:+ +:+        
+#++:++#   +#+     +:+ +#++:++#   +#++:++#:  +#++:++#++ +#++:++#++ +#++:++#++: +#+    +:+ +#++:++#   
+#+         +#+   +#+  +#+        +#+    +#+        +#+ +#+    +#+ +#+     +#+ +#+    +#+ +#+        
#+#          #+#+#+#   #+#        #+#    #+# #+#    #+# #+#    #+# #+#     #+# #+#    #+# #+#        
##########     ###     ########## ###    ###  ########  ###    ### ###     ### #########  ##########
```

# Unified Workflow

A complete self-hosted AI agent platform combining three services into one integrated system.

**[Architecture Audit & Improvement Plan →](ARCHITECTURE_AUDIT.md)** — Full analysis of the ecosystem, identified issues, and implementation roadmap.

| Service | Role | Port |
|---------|------|------|
| **Greenie** | 🏠 Central API + Web UI — agents, pipelines, analytics, 320 endpoints | `8080` |
| **Slinker** | ⚙️ Execution engine — Git worktree isolation, persistent task storage | `8000` |
| **Trapper** | 🌐 Web scraping — scrape, crawl, search, and map websites | `3000` |

### Web Interfaces

| Interface | URL | Description |
|-----------|-----|-------------|
| **Chat UI** | http://localhost:8080/ | Agent chat, skills, memory, routines |
| **Management Dashboard** | http://localhost:8080/dashboard/ | Agents, runs, pipelines, analytics, settings |
| **Tasks App** | http://localhost:8080/app/ | Simple task list |
| **API Docs** | http://localhost:8080/docs | Swagger UI for all 320 endpoints |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Your Browser                            │
│                  http://localhost:8080                      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │    Greenie (8080)  │  ← Main dashboard
                    │  ┌───────────────┐  │
                    │  │  Web UI + API │  │
                    │  │  SQLite DB    │  │
                    │  └───────────────┘  │
                    └──────┬──────┬──────┘
                           │      │
              ┌────────────┘      └────────────┐
              ▼                                  ▼
┌─────────────────────────┐      ┌─────────────────────────┐
│   Slinker (8000)       │      │   Trapper (3000)      │
│  ┌───────────────────┐  │      │  ┌───────────────────┐  │
│  │ Git worktree mgmt │  │      │  │ Playwright browser│  │
│  │ Junie CLI runner  │  │      │  │ Content cleaning  │  │
│  │ Task persistence  │  │      │  │ Redis queue       │  │
│  └───────────────────┘  │      │  └───────────────────┘  │
└─────────────────────────┘      └─────────────────────────┘
```

## Quick Start

### Prerequisites

- **Docker** and **Docker Compose**
- **[Junie CLI](https://junie.jetbrains.com)** (for code agents) — optional, install on the host machine

### One-Command Start (Docker)

```bash
# Clone and start
git clone <repo-url> && cd Workflow
cp .env.example .env
# Edit .env with your API keys
docker compose up -d --build
```

The dashboard will be available at **http://localhost:8080**.

### Startup Scripts

Convenience scripts validate your environment before starting services:

```bash
# Linux/macOS
./start.sh    # Start all services
./stop.sh     # Stop all services

# Windows PowerShell
.\start.ps1   # Start all services
.\stop.ps1    # Stop all services
```

The startup scripts check for Docker, `.env` file, service directories, and Junie CLI availability before launching.

### API Documentation

All three services expose auto-generated API documentation:

| Service | Swagger UI | ReDoc | OpenAPI JSON |
|---------|-----------|-------|-------------|
| **Greenie** | http://localhost:8080/docs | http://localhost:8080/redoc | http://localhost:8080/openapi.json |
| **Slinker** | http://localhost:8000/docs | http://localhost:8000/redoc | http://localhost:8000/openapi.json |

### Structured Logging

All services output JSON-formatted logs for easy parsing and aggregation:

```json
{"timestamp": "2026-10-21T17:00:00", "level": "INFO", "service": "Greenie", "message": "GET /api/health 200 1.2ms", "request_id": "a1b2c3d4"}
```

Set log level via `LOG_LEVEL` environment variable (default: `INFO`):

```bash
LOG_LEVEL=DEBUG docker compose up
```

Each request receives a unique `X-Request-ID` header for correlation tracing across services.

### Database Backup & Restore

Protect your data with built-in backup endpoints:

```bash
# Create a backup
curl -X POST http://localhost:8080/api/backup \
  -H "Authorization: Bearer $HUB_API_KEY"

# List backups
curl http://localhost:8080/api/backups \
  -H "Authorization: Bearer $HUB_API_KEY"

# Restore from a backup
curl -X POST "http://localhost:8080/api/backup/restore/hub_backup_20261021_170000.db" \
  -H "Authorization: Bearer $HUB_API_KEY"

# Delete a backup
curl -X DELETE "http://localhost:8080/api/backup/hub_backup_20261021_170000.db" \
  -H "Authorization: Bearer $HUB_API_KEY"
```

Backups are stored in `Greenie/data/backups/` with timestamps. Restoring automatically creates a safety backup of the current database first.

Slinker also supports backups:

```bash
# Create Slinker backup
curl -X POST http://localhost:8000/api/v1/backup \
  -H "Authorization: Bearer $Slinker_API_KEY"

# List Slinker backups
curl http://localhost:8000/api/v1/backups \
  -H "Authorization: Bearer $Slinker_API_KEY"
```

### Health Check

The enhanced health endpoint reports database status, downstream services, and in-memory store sizes:

```bash
curl http://localhost:8080/api/health
```

```json
{
  "status": "ok",
  "version": "1.0.3",
  "database": {"status": "ok", "file": "/app/data/hub.db", "size_bytes": 524288},
  "downstream": {
    "Slinker": {"status": "ok", "url": "http://Slinker:8000"},
    "Trapper": {"status": "ok", "url": "http://Trapper:3000"}
  },
  "stores": {"webhooks": 5, "analytics_events": 120, "audit_log": 45, ...}
}
```

### CI/CD Pipeline

A GitHub Actions pipeline (`.github/workflows/ci.yml`) runs on every push and pull request:

- **Greenie Tests** — Python tests with pytest
- **Slinker Tests** — Python tests with pytest
- **Trapper Build** — Node.js build verification
- **Docker Build** — Builds all service images and validates docker-compose

### What You Get

| Agent Type | Runner | Use Case |
|------------|--------|----------|
| **vault** | `junie` | Local Junie CLI agent (Obsidian vault, notes) |
| **coder** | `Slinker` | Code development with Git worktree isolation |
| **researcher** | `Trapper` | Web scraping, searching, and crawling |

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Description |
|----------|-------------|
| `HUB_API_KEY` | Greenie dashboard authentication |
| `Slinker_API_KEY` | Slinker service authentication |
| `Trapper_API_KEY` | Trapper service authentication |
| `WORKSPACE_PATH` | Shared workspace for all agents |
| `JUNIE_BIN` | Path to Junie CLI binary |
| `OLLAMA_URL` | Optional Ollama endpoint for prompt refinement |

### Agent Configuration

Edit `Greenie/hub.yaml` to configure agents. Three runner types are available:

```yaml
runners:
  junie:       # Direct Junie CLI execution
  Slinker:    # Via Slinker (worktree isolation)
  Trapper:   # Via Trapper (web scraping)

agents:
  my-agent:
    runner: Slinker  # Choose your runner
    project_dir: "/workspace/my-project"
    guidelines: "Your instructions here"
```

## Using Agents

### Code Agent (Slinker runner)

Send tasks to a `Slinker` runner agent for code changes with Git worktree isolation:

```
"Refactor the authentication module to use async/await"
```

The Slinker provider also supports operation prefixes:

```
"TASK: Implement user authentication"          # Submit a task
"STATUS: abc-123-def"                          # Check task status by ID
"WORKERS:"                                     # List active workers
"QUEUE:"                                       # Get queue status
```

### Web Research Agent (Trapper runner)

Send tasks to an `Trapper` runner agent with operation prefixes:

```
"SCRAPE: https://example.com"
"CRAWL: https://example.com/blog"
"SEARCH: best Python web frameworks 2024"
"MAP: https://example.com"
"BATCH: https://a.com, https://b.com, https://c.com"
"INTERACT: {\"scrapeId\": \"...\", \"actions\": [{\"type\": \"click\", \"selector\": \"#btn\"}]}"
"EXTRACT: {\"urls\": [\"...\"], \"prompt\": \"Extract pricing\", \"schema\": {...}}"
"AGENT: Find the top 5 web scraping tools and their pricing"
```

### Direct API Access

Greenie provides proxy endpoints for direct access to integrated services:

**Trapper:**
- `POST /api/crawl/scrape` — Scrape a URL
- `POST /api/crawl/crawl` — Start a crawl job
- `GET /api/crawl/{job_id}` — Check crawl status
- `DELETE /api/crawl/{job_id}` — Cancel a crawl job
- `POST /api/crawl/search` — Search the web
- `POST /api/crawl/map` — Map site URLs
- `POST /api/crawl/batch` — Start a batch scrape job
- `GET /api/crawl/batch/{job_id}` — Check batch status
- `DELETE /api/crawl/batch/{job_id}` — Cancel a batch job
- `POST /api/crawl/interact` — Interact with a page
- `POST /api/crawl/extract` — Start an extract job
- `GET /api/crawl/extract/{job_id}` — Check extract status
- `DELETE /api/crawl/extract/{job_id}` — Cancel an extract job
- `POST /api/crawl/agent` — Start a research agent job
- `GET /api/crawl/agent/{job_id}` — Check agent status
- `DELETE /api/crawl/agent/{job_id}` — Cancel an agent job
- `GET /api/crawl/health` — Health check
- `POST /api/crawl/stream` — Stream job progress via SSE (crawl, agent, extract, batch)

**Slinker:**
- `GET /api/Slinker/health` — Health check
- `GET /api/Slinker/ready` — Readiness check
- `GET /api/Slinker/models` — List available models
- `GET /api/Slinker/tasks` — List tasks
- `POST /api/Slinker/tasks` — Submit a task
- `GET /api/Slinker/tasks/{task_id}` — Get task detail
- `GET /api/Slinker/tasks/{task_id}/output` — Get task output summary
- `GET /api/Slinker/projects` — List projects
- `POST /api/Slinker/projects` — Register a project
- `GET /api/Slinker/workers` — List active workers
- `GET /api/Slinker/workers/{worker_id}` — Get worker detail
- `GET /api/Slinker/sessions` — List sessions
- `GET /api/Slinker/queue` — Queue status
- `POST /api/Slinker/chat` — Execute via chat completions
- `POST /api/Slinker/chat/stream` — Stream chat via SSE
- `POST /api/Slinker/task/stream` — Stream task execution via SSE

**Platform:**
- `GET /api/dashboard` — Unified dashboard (all three services)
- `GET /api/integration/health` — All services health check
- `GET /api/integration/Slinker/health` — Slinker health
- `GET /api/integration/Trapper/health` — Trapper health
- `POST /api/pipeline` — Cross-service pipeline (chain multiple services)
- `GET /api/search?q=QUERY` — Unified search across all services
- `POST /api/batch` — Parallel batch execution across services
- `POST /api/schedules` — Create a scheduled pipeline (cron)
- `GET /api/schedules` — List scheduled pipelines
- `GET /api/schedules/{id}` — Get schedule detail
- `PUT /api/schedules/{id}` — Update a schedule
- `DELETE /api/schedules/{id}` — Delete a schedule

**Webhooks:**
- `POST /api/webhooks` — Create a webhook
- `GET /api/webhooks` — List all webhooks
- `GET /api/webhooks/{id}` — Get webhook detail
- `PUT /api/webhooks/{id}` — Update a webhook
- `DELETE /api/webhooks/{id}` — Delete a webhook
- `POST /api/webhooks/{id}/test` — Send test event
- `GET /api/events/types` — List available event types

**Notifications:**
- `POST /api/notifications/channels` — Create a notification channel
- `GET /api/notifications/channels` — List all channels
- `GET /api/notifications/channels/{id}` — Get channel detail
- `PUT /api/notifications/channels/{id}` — Update a channel
- `DELETE /api/notifications/channels/{id}` — Delete a channel
- `POST /api/notifications/test` — Send test notification
- `POST /api/notifications/broadcast` — Broadcast to all channels

**Analytics:**
- `GET /api/analytics/overview` — Full analytics overview
- `GET /api/analytics/api-calls` — API call counts by endpoint
- `GET /api/analytics/tasks` — Recent task execution records
- `GET /api/analytics/errors` — Error counts by type
- `GET /api/analytics/daily` — Daily aggregated stats
- `POST /api/analytics/reset` — Reset analytics data

**Data Export/Import:**
- `GET /api/export/sessions` — Export sessions (JSON/CSV)
- `GET /api/export/runs` — Export runs (JSON/CSV)
- `GET /api/export/memories` — Export memories (JSON)
- `GET /api/export/config` — Export configuration
- `POST /api/import/sessions` — Import sessions from JSON

**API Keys:**
- `POST /api/keys` — Create a new API key
- `GET /api/keys` — List all API keys
- `GET /api/keys/{id}` — Get key detail
- `PUT /api/keys/{id}` — Update key metadata
- `DELETE /api/keys/{id}` — Revoke a key
- `POST /api/keys/{id}/rotate` — Rotate a key

**Services:**
- `GET /api/services/status` — Current status of all services
- `GET /api/services/health-history` — Health check history

**WebSocket:**
- `WS /api/ws/connect` — Real-time event streaming

**Rate Limiting:**
- `POST /api/rate-limits` — Set custom rate limit for an API key
- `GET /api/rate-limits` — List all rate limit configurations
- `GET /api/rate-limits/{key_id}` — Get rate limit config and usage
- `DELETE /api/rate-limits/{key_id}` — Remove custom rate limit

**Audit Log:**
- `GET /api/audit` — Query audit log with filters
- `GET /api/audit/stats` — Audit log statistics
- `POST /api/audit/clear` — Clear audit log

**Templates:**
- `POST /api/templates` — Save a reusable template
- `GET /api/templates` — List all templates
- `GET /api/templates/{id}` — Get template detail
- `PUT /api/templates/{id}` — Update a template
- `DELETE /api/templates/{id}` — Delete a template
- `POST /api/templates/{id}/execute` — Execute a template with variables

**Approvals:**
- `POST /api/approvals/policy` — Configure approval policy
- `GET /api/approvals/policy` — Get approval policy
- `POST /api/approvals/request` — Create an approval request
- `GET /api/approvals` — List approval requests
- `POST /api/approvals/{id}/approve` — Approve a request
- `POST /api/approvals/{id}/deny` — Deny a request
- `GET /api/approvals/stats` — Approval statistics

**Files:**
- `POST /api/files/upload` — Upload a file
- `GET /api/files` — List uploaded files
- `GET /api/files/{id}` — Get file metadata
- `GET /api/files/{id}/download` — Download a file
- `DELETE /api/files/{id}` — Delete a file

**RBAC Roles:**
- `POST /api/roles` — Create a custom role
- `GET /api/roles` — List all roles
- `GET /api/roles/{name}` — Get role detail
- `PUT /api/roles/{name}` — Update a role
- `DELETE /api/roles/{name}` — Delete a custom role

**Users:**
- `POST /api/users` — Create a user with a role
- `GET /api/users` — List all users
- `GET /api/users/{username}` — Get user detail
- `PUT /api/users/{username}` — Update a user
- `DELETE /api/users/{username}` — Delete a user

**Jobs:**
- `POST /api/jobs` — Submit a background job
- `GET /api/jobs` — List all jobs
- `GET /api/jobs/{id}` — Get job detail
- `DELETE /api/jobs/{id}` — Cancel a pending job
- `POST /api/jobs/{id}/retry` — Retry a failed job
- `GET /api/jobs/dead-letter` — List dead letter queue
- `POST /api/jobs/dead-letter/{id}/replay` — Replay from dead letter
- `GET /api/jobs/stats` — Job queue statistics

All endpoints require `Authorization: Bearer <HUB_API_KEY>`.

## Cross-Service Pipelines

Chain multiple services together in a single request. Each step's output flows as context to the next:

```bash
curl -X POST http://localhost:8080/api/pipeline \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "steps": [
      {
        "service": "Trapper",
        "task": "SEARCH: latest Rust async best practices 2024"
      },
      {
        "service": "Slinker",
        "task": "Create a summary document of the research findings"
      }
    ]
  }'
```

Supported services in pipelines:
- **Trapper** — Web research (SEARCH, SCRAPE, CRAWL, MAP, AGENT, etc.)
- **Slinker** — Coding tasks via Slinker
- **agent** — Local Greenie agents (specify `"agent": "vault"`)

## Unified Dashboard

Get a single view of the entire platform:

```bash
curl http://localhost:8080/api/dashboard \
  -H "Authorization: Bearer $HUB_API_KEY"
```

Returns Greenie agents and recent runs, Slinker workers and queue status, and Trapper health — all in one response.

## Scheduled Pipelines

Set up recurring cross-service pipelines with cron-like scheduling:

```bash
curl -X POST http://localhost:8080/api/schedules \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily research digest",
    "schedule": "0 9 * * *",
    "steps": [
      {"service": "Trapper", "task": "SEARCH: latest AI news today"},
      {"service": "Slinker", "task": "Summarize the research findings in a report"}
    ]
  }'
```

Cron expression format: `minute hour day-of-month month day-of-week`. Supports `*`, `N`, `N-M`, `N/M` patterns.

Manage schedules:
- `GET /api/schedules` — List all schedules with run counts and last results
- `GET /api/schedules/{id}` — Get a schedule detail
- `PUT /api/schedules/{id}` — Update schedule (name, cron, steps, enabled)
- `DELETE /api/schedules/{id}` — Delete and stop a schedule

## Unified Search

Search across all three services in a single request:

```bash
curl "http://localhost:8080/api/search?q=authentication" \
  -H "Authorization: Bearer $HUB_API_KEY"
```

Returns matching web content from Trapper, tasks and projects from Slinker, and agents and runs from Greenie — all grouped by service.

## Parallel Batch Execution

Execute multiple tasks concurrently across services (unlike sequential pipelines):

```bash
curl -X POST http://localhost:8080/api/batch \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [
      {"service": "Trapper", "task": "SEARCH: latest Python news"},
      {"service": "Trapper", "task": "SEARCH: latest Rust news"},
      {"service": "Slinker", "task": "Compare Python vs Rust performance trends"}
    ]
  }'
```

All tasks run in parallel; results are returned together when all complete.

## SSE Streaming

Real-time progress streaming for long-running jobs:

**Trapper job streaming** — Start a crawl, agent, extract, or batch job and receive live progress:

```bash
curl -X POST http://localhost:8080/api/crawl/stream \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "crawl",
    "payload": {"url": "https://example.com"}
  }'
```

Events: `started`, `progress`, `complete`, `error`, `timeout`.

**Slinker task streaming** — Submit a task and stream its execution:

```bash
curl -X POST http://localhost:8080/api/Slinker/task/stream \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Refactor the authentication module",
    "project": "my-project"
  }'
```

## Service Management

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down

# Rebuild and restart
docker compose up -d --build

# Restart a single service
docker compose restart Greenie
```

## Webhooks

Set up event-driven notifications for platform events:

```bash
# Create a webhook
curl -X POST http://localhost:8080/api/webhooks \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-server.com/webhook",
    "events": ["run.completed", "run.failed"],
    "secret": "your-hmac-secret",
    "enabled": true
  }'

# Test a webhook
curl -X POST http://localhost:8080/api/webhooks/wh-abc123/test \
  -H "Authorization: Bearer $HUB_API_KEY"
```

Available event types: `run.completed`, `run.failed`, `run.started`, `schedule.executed`, `schedule.failed`, `pipeline.completed`, `pipeline.failed`, `batch.completed`, `batch.failed`, `agent.created`, `agent.deleted`, `session.created`, `session.deleted`, `approval.pending`, `approval.approved`, `approval.denied`.

Use `"events": ["*"]` to receive all event types. Webhooks support HMAC signature verification via the `X-Webhook-Signature` header.

Manage webhooks:
- `POST /api/webhooks` — Create a webhook
- `GET /api/webhooks` — List all webhooks
- `GET /api/webhooks/{id}` — Get webhook detail
- `PUT /api/webhooks/{id}` — Update a webhook
- `DELETE /api/webhooks/{id}` — Delete a webhook
- `POST /api/webhooks/{id}/test` — Send test event
- `GET /api/events/types` — List available event types

## Notification Channels

Send alerts to Slack, Discord, or generic webhooks:

```bash
# Create a Slack notification channel
curl -X POST http://localhost:8080/api/notifications/channels \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "DevOps Alerts",
    "type": "slack",
    "webhook_url": "https://hooks.slack.com/services/...",
    "enabled": true
  }'

# Broadcast a notification to all channels
curl -X POST http://localhost:8080/api/notifications/broadcast \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "System Alert",
    "message": "Greenie pipeline failed",
    "level": "error"
  }'
```

Supported channel types: `slack`, `discord`, `generic`. Notification levels: `info`, `warning`, `error`, `success`.

Manage channels:
- `POST /api/notifications/channels` — Create a channel
- `GET /api/notifications/channels` — List all channels
- `GET /api/notifications/channels/{id}` — Get channel detail
- `PUT /api/notifications/channels/{id}` — Update a channel
- `DELETE /api/notifications/channels/{id}` — Delete a channel
- `POST /api/notifications/test` — Send test notification
- `POST /api/notifications/broadcast` — Broadcast to all channels

## Analytics & Usage Tracking

Monitor platform usage, task performance, and error rates:

```bash
# Get analytics overview
curl http://localhost:8080/api/analytics/overview \
  -H "Authorization: Bearer $HUB_API_KEY"

# Get daily stats for last 30 days
curl "http://localhost:8080/api/analytics/daily?days=30" \
  -H "Authorization: Bearer $HUB_API_KEY"
```

Returns API call counts, task durations (avg, p95, max), runs by agent, error rates by type, and daily aggregated stats. Task durations are tracked per service (Trapper, Slinker, agent).

Analytics endpoints:
- `GET /api/analytics/overview` — Full analytics overview
- `GET /api/analytics/api-calls` — API call counts by endpoint
- `GET /api/analytics/tasks` — Recent task execution records
- `GET /api/analytics/errors` — Error counts by type
- `GET /api/analytics/daily` — Daily aggregated stats
- `POST /api/analytics/reset` — Reset analytics data

## Data Export/Import

Export and import platform data in JSON or CSV format:

```bash
# Export sessions as JSON
curl "http://localhost:8080/api/export/sessions?format=json" \
  -H "Authorization: Bearer $HUB_API_KEY"

# Export runs as CSV
curl "http://localhost:8080/api/export/runs?format=csv&limit=100" \
  -H "Authorization: Bearer $HUB_API_KEY"

# Export memories
curl http://localhost:8080/api/export/memories \
  -H "Authorization: Bearer $HUB_API_KEY"

# Export configuration (without secrets)
curl http://localhost:8080/api/export/config \
  -H "Authorization: Bearer $HUB_API_KEY"

# Import sessions from JSON
curl -X POST http://localhost:8080/api/import/sessions \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"sessions": [{"title": "My Session", "agent_id": "vault"}]}'
```

Export endpoints:
- `GET /api/export/sessions` — Export sessions (JSON/CSV)
- `GET /api/export/runs` — Export runs (JSON/CSV)
- `GET /api/export/memories` — Export memories (JSON)
- `GET /api/export/config` — Export configuration
- `POST /api/import/sessions` — Import sessions from JSON

## API Key Management

Create, manage, and rotate API keys with granular permissions:

```bash
# Create a new API key with expiration
curl -X POST http://localhost:8080/api/keys \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CI/CD Pipeline",
    "permissions": ["read", "runs"],
    "expires_in_days": 30
  }'

# Rotate an API key
curl -X POST http://localhost:8080/api/keys/key-abc123/rotate \
  -H "Authorization: Bearer $HUB_API_KEY"
```

Permissions: `*` (all access), `read`, `runs`, `agents`, `sessions`, `webhooks`, `analytics`. Keys support automatic expiration and usage tracking. The actual key value is only shown once at creation.

Manage keys:
- `POST /api/keys` — Create a new API key
- `GET /api/keys` — List all API keys
- `GET /api/keys/{id}` — Get key detail
- `PUT /api/keys/{id}` — Update key metadata
- `DELETE /api/keys/{id}` — Revoke a key
- `POST /api/keys/{id}/rotate` — Rotate a key

## Service Health Monitoring

Monitor integrated services with health history tracking:

```bash
# Get status of all services
curl http://localhost:8080/api/services/status \
  -H "Authorization: Bearer $HUB_API_KEY"

# Get health check history
curl http://localhost:8080/api/services/health-history \
  -H "Authorization: Bearer $HUB_API_KEY"
```

Returns detailed status for Greenie, Slinker, and Trapper with response times, health history, and overall platform health indicator (`healthy` or `degraded`).

Service endpoints:
- `GET /api/services/status` — Current status of all services
- `GET /api/services/health-history` — Health check history

## WebSocket Real-Time Feed

Connect via WebSocket for real-time event streaming:

```javascript
const ws = new WebSocket('ws://localhost:8080/api/ws/connect?token=YOUR_API_KEY&channel=runs');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event:', data.event, data);
};

// Send ping to keep connection alive
ws.send('ping');
```

Channels: `all` (all events), `runs` (run events only), `schedules` (schedule events only). Authentication via `token` query parameter. Supports ping/pong keep-alive.

WebSocket endpoint:
- `WS /api/ws/connect` — Real-time event streaming

## Rate Limiting

Set custom rate limits per API key to prevent abuse:

```bash
# Set a custom rate limit
curl -X POST http://localhost:8080/api/rate-limits \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "key_id": "key-abc123",
    "requests": 100,
    "window": 60
  }'

# Check current usage
curl http://localhost:8080/api/rate-limits/key-abc123 \
  -H "Authorization: Bearer $HUB_API_KEY"
```

Default rate limit is 60 requests per minute. When exceeded, the API returns HTTP 429 with a retry-after time. Configure per-key limits with custom request counts and time windows.

Rate limiting endpoints:
- `POST /api/rate-limits` — Set custom rate limit
- `GET /api/rate-limits` — List all configurations
- `GET /api/rate-limits/{key_id}` — Get config and usage
- `DELETE /api/rate-limits/{key_id}` — Remove custom limit

## Audit Log

Track all API actions for compliance and debugging:

```bash
# Query audit log with filters
curl "http://localhost:8080/api/audit?action=run.created&limit=50" \
  -H "Authorization: Bearer $HUB_API_KEY"

# Get audit statistics
curl http://localhost:8080/api/audit/stats \
  -H "Authorization: Bearer $HUB_API_KEY"
```

The audit log records every significant action (file uploads, role changes, job submissions) with timestamps, actors, and resource types. Bounded to 5000 entries to prevent unbounded memory growth. Filter by action type, actor, or resource.

Audit endpoints:
- `GET /api/audit` — Query with filters (action, actor, resource, limit)
- `GET /api/audit/stats` — Counts by action, actor, resource
- `POST /api/audit/clear` — Clear all entries

## Template Management

Save and reuse pipeline or task configurations:

```bash
# Create a template
curl -X POST http://localhost:8080/api/templates \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research & Summarize",
    "description": "Crawl a URL and summarize the content",
    "type": "pipeline",
    "steps": [
      {"service": "Trapper", "task": "SCRAPE:{{url}}"},
      {"service": "agent", "agent": "vault", "task": "Summarize: {{step0}}"}
    ],
    "variables": ["url"],
    "tags": ["research", "summary"]
  }'

# Execute a template with variables
curl -X POST http://localhost:8080/api/templates/tpl-abc123/execute \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"variables": {"url": "https://example.com"}}'
```

Templates support three types: `pipeline` (multi-step), `task` (single step), and `schedule` (recurring). Use `{{variable}}` syntax for parameterized values. Templates track usage counts and support tagging for organization.

Template endpoints:
- `POST /api/templates` — Create a template
- `GET /api/templates` — List all (filter by `?tag=...`)
- `GET /api/templates/{id}` — Get detail
- `PUT /api/templates/{id}` — Update
- `DELETE /api/templates/{id}` — Delete
- `POST /api/templates/{id}/execute` — Execute with variables

## Approval Workflows

Implement human-in-the-loop approval gates for sensitive operations:

```bash
# Configure approval policy
curl -X POST http://localhost:8080/api/approvals/policy \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "require_for": ["external_api", "file_write"],
    "auto_approve_agents": ["vault"]
  }'

# Create an approval request
curl -X POST http://localhost:8080/api/approvals/request \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "external_api",
    "description": "Agent wants to call external API",
    "agent": "researcher",
    "details": {"url": "https://api.example.com/data"},
    "timeout_minutes": 30
  }'

# Approve a request
curl -X POST http://localhost:8080/api/approvals/appr-abc123/approve \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user": "admin", "notes": "Approved for production"}'
```

Approval requests auto-expire after the configured timeout (default 30 minutes). Webhook events are emitted for `approval.pending`, `approval.approved`, and `approval.denied`.

Approval endpoints:
- `POST /api/approvals/policy` — Configure policy
- `GET /api/approvals/policy` — Get policy
- `POST /api/approvals/request` — Create request
- `GET /api/approvals` — List (filter by status, agent)
- `POST /api/approvals/{id}/approve` — Approve
- `POST /api/approvals/{id}/deny` — Deny
- `GET /api/approvals/stats` — Statistics

## File Storage

Upload, manage, and download files associated with runs:

```bash
# Upload a file
curl -X POST http://localhost:8080/api/files/upload \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -F "file=@report.pdf" \
  -F "run_id=run-abc123" \
  -F "description=Research report"

# List files
curl http://localhost:8080/api/files \
  -H "Authorization: Bearer $HUB_API_KEY"

# Download a file
curl http://localhost:8080/api/files/file-abc123/download \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -o report.pdf
```

Files are stored in `Greenie/hub/uploads/` with a 50MB size limit. Associate files with runs via the `run_id` field. All file operations are audit-logged.

File endpoints:
- `POST /api/files/upload` — Upload (multipart/form-data)
- `GET /api/files` — List (filter by `?run_id=...`)
- `GET /api/files/{id}` — Get metadata
- `GET /api/files/{id}/download` — Download file
- `DELETE /api/files/{id}` — Delete file

## RBAC (Role-Based Access Control)

Manage users and roles for fine-grained access control:

```bash
# Create a custom role
curl -X POST http://localhost:8080/api/roles \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "analyst",
    "permissions": ["read", "analytics", "export"],
    "description": "Can view analytics and export data"
  }'

# Create a user with a role
curl -X POST http://localhost:8080/api/users \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "role": "developer",
    "api_key": "key-abc123",
    "email": "alice@example.com"
  }'
```

Built-in roles: `admin` (full access), `developer` (agents, runs, files), `viewer` (read-only). Create custom roles with granular permissions. The primary API key always has full access; RBAC applies to created API keys.

Role endpoints:
- `POST /api/roles` — Create a role
- `GET /api/roles` — List all roles
- `GET /api/roles/{name}` — Get detail
- `PUT /api/roles/{name}` — Update permissions
- `DELETE /api/roles/{name}` — Delete custom role

User endpoints:
- `POST /api/users` — Create a user
- `GET /api/users` — List all users
- `GET /api/users/{username}` — Get detail
- `PUT /api/users/{username}` — Update role/status
- `DELETE /api/users/{username}` — Delete user

## Background Job Queue

Submit asynchronous jobs with retry logic and dead letter queue:

```bash
# Submit a background job
curl -X POST http://localhost:8080/api/jobs \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "run_agent",
    "payload": {
      "agent": "vault",
      "task": "Summarize the latest news"
    },
    "max_retries": 3,
    "priority": 0,
    "metadata": {"source": "webhook"}
  }'

# Check job status
curl http://localhost:8080/api/jobs/job-abc123 \
  -H "Authorization: Bearer $HUB_API_KEY"

# View dead letter queue
curl http://localhost:8080/api/jobs/dead-letter \
  -H "Authorization: Bearer $HUB_API_KEY"
```

Job types: `run_agent` (run an agent), `pipeline` (execute pipeline steps), `Trapper` (web scraping), `Slinker` (coding tasks), `webhook` (HTTP POST). Failed jobs automatically retry with exponential backoff (5s, 10s, 20s...). After max retries, jobs move to the dead letter queue for manual replay.

Job endpoints:
- `POST /api/jobs` — Submit a job
- `GET /api/jobs` — List all (filter by `?state=...`)
- `GET /api/jobs/{id}` — Get detail
- `DELETE /api/jobs/{id}` — Cancel pending job
- `POST /api/jobs/{id}/retry` — Manually retry
- `GET /api/jobs/dead-letter` — Dead letter queue
- `POST /api/jobs/dead-letter/{id}/replay` — Replay from dead letter
- `GET /api/jobs/stats` — Queue statistics

## Response Caching

Cache API responses with configurable TTL to reduce load on downstream services:

```bash
# View cache statistics
curl http://localhost:8080/api/cache/stats \
  -H "Authorization: Bearer $HUB_API_KEY"

# Set custom TTL for an endpoint
curl -X POST http://localhost:8080/api/cache/ttl \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "/api/dashboard", "ttl_seconds": 60}'

# Clear all cached entries
curl -X POST http://localhost:8080/api/cache/clear \
  -H "Authorization: Bearer $HUB_API_KEY"
```

Endpoints: `/api/cache/stats`, `/api/cache/clear`, `/api/cache/entries`, `/api/cache/ttl` (GET/POST), `/api/cache/ttl/{endpoint}` (DELETE). Default TTLs are set for dashboard (30s), search (60s), analytics (120s), and services status (30s). Cache is bounded at 500 entries with automatic expired entry eviction.

## Internal Message Bus

Pub/sub messaging system for inter-service communication with webhook delivery:

```bash
# Publish a message to a topic
curl -X POST http://localhost:8080/api/messages/publish \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"topic": "events.user.created", "payload": {"user_id": "u-123"}}'

# Subscribe to a topic via webhook
curl -X POST http://localhost:8080/api/messages/subscribe \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"topic": "events.*", "webhook_url": "https://your-server.com/messages"}'

# Read messages from a topic
curl http://localhost:8080/api/messages/events.user.created \
  -H "Authorization: Bearer $HUB_API_KEY"
```

Endpoints: `/api/messages/publish`, `/api/messages/topics`, `/api/messages/{topic}`, `/api/messages/subscribe`, `/api/messages/subscriptions`, `/api/messages/subscriptions/{id}` (DELETE), `/api/messages/clear`. Supports wildcard subscriptions (e.g., `events.*`) and bounded message storage (500 per topic).

## Feature Flags

Toggle features on/off with targeting rules for users, agents, percentages, or environments:

```bash
# Create a feature flag with percentage rollout
curl -X POST http://localhost:8080/api/flags \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "new_pipeline_ui",
    "description": "New pipeline UI for beta testers",
    "enabled": true,
    "rules": [
      {"type": "percentage", "percentage": 50, "enabled": true},
      {"type": "user", "users": ["admin"], "enabled": true}
    ]
  }'

# Evaluate a flag for a specific context
curl -X POST http://localhost:8080/api/flags/new_pipeline_ui/evaluate \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "u-123", "agent": "vault"}'
```

Endpoints: `/api/flags` (GET/POST), `/api/flags/{name}` (GET/PUT/DELETE), `/api/flags/{name}/evaluate`, `/api/flags/evaluations`. Rule types: `user` (target specific users), `agent` (target specific agents), `percentage` (randomized rollout), `environment` (target by environment). Evaluation history is bounded at 1000 entries.

## Deployment Management

Track deployments, rollbacks, and environment configuration:

```bash
# Record a new deployment
curl -X POST http://localhost:8080/api/deployments \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "1.2.0",
    "environment": "production",
    "commit": "abc123",
    "branch": "main",
    "deployer": "ci-pipeline"
  }'

# Mark deployment as completed
curl -X POST http://localhost:8080/api/deployments/deploy-abc123/complete \
  -H "Authorization: Bearer $HUB_API_KEY"

# View deployment statistics
curl http://localhost:8080/api/deployments/stats \
  -H "Authorization: Bearer $HUB_API_KEY"
```

Endpoints: `/api/deployments` (GET/POST), `/api/deployments/current`, `/api/deployments/{id}/complete`, `/api/deployments/{id}/rollback`, `/api/deployments/stats`. Tracks version, commit, branch, deployer, status, and duration for each deployment.

## Circuit Breaker

Protect against cascading failures to external services with configurable thresholds:

```bash
# Record a failure for a service
curl -X POST http://localhost:8080/api/circuit-breakers/Trapper/record \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"success": false}'

# Check if a service call is allowed
curl -X POST http://localhost:8080/api/circuit-breakers/Trapper/check \
  -H "Authorization: Bearer $HUB_API_KEY"

# Configure thresholds
curl -X POST http://localhost:8080/api/circuit-breakers/config \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"service": "Trapper", "failure_threshold": 5, "recovery_timeout": 60}'
```

Endpoints: `/api/circuit-breakers` (GET), `/api/circuit-breakers/{service}/record`, `/api/circuit-breakers/{service}/check`, `/api/circuit-breakers/{service}/reset`, `/api/circuit-breakers/config`. Three states: `closed` (normal), `open` (blocking calls after N failures), `half-open` (testing recovery after timeout). Default: 5 failures to open, 60s recovery timeout, 3 successes to close.

## API Versioning & Deprecation

Manage API versions and deprecation warnings with migration paths:

```bash
# Register a new API version
curl -X POST http://localhost:8080/api/versions \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"version": "v2", "status": "current", "description": "Enhanced API"}'

# Deprecate an old version
curl -X POST http://localhost:8080/api/versions/v1/deprecate \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"deprecation_date": "2025-06-01", "sunset_date": "2026-01-01"}'

# Register a deprecated endpoint with migration path
curl -X POST http://localhost:8080/api/deprecated-endpoints \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"old_path": "/api/v1/runs", "new_path": "/api/v2/runs"}'
```

Endpoints: `/api/versions` (GET/POST), `/api/versions/{version}/deprecate`, `/api/deprecated-endpoints` (GET/POST). Version statuses: `current`, `deprecated`, `sunset`.

## DAG Task Execution

Execute dependent tasks as a Directed Acyclic Graph with parallel independent task execution:

```bash
# Create a DAG of dependent tasks
curl -X POST http://localhost:8080/api/dags \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research Pipeline",
    "tasks": {
      "scrape": {"service": "Trapper", "task": "SCRAPE:https://example.com"},
      "analyze": {"service": "Slinker", "task": "Analyze content", "depends_on": ["scrape"]},
      "summarize": {"service": "agent", "agent": "vault", "task": "Summarize", "depends_on": ["analyze"]}
    }
  }'

# Execute the DAG
curl -X POST http://localhost:8080/api/dags/dag-abc123/execute \
  -H "Authorization: Bearer $HUB_API_KEY"
```

Endpoints: `/api/dags` (GET/POST), `/api/dags/{id}` (GET/DELETE), `/api/dags/{id}/execute`, `/api/dags/executions`. Tasks with no dependencies run in parallel; dependent tasks wait for prerequisites. Cycle detection validates DAG integrity. Results from dependencies are substituted into downstream tasks via `{{task_id}}` placeholders.

## Multi-Tenancy

Isolate resources by tenant (workspace) with configurable limits:

```bash
# Create a tenant with resource limits
curl -X POST http://localhost:8080/api/tenants \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corp",
    "limits": {"max_agents": 10, "max_runs_per_day": 1000},
    "allowed_services": ["Trapper", "Slinker", "agent"]
  }'

# Assign an agent to a tenant
curl -X POST http://localhost:8080/api/tenants/tenant-abc123/assign \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"resource_type": "agent", "resource_id": "vault"}'

# Check tenant usage
curl http://localhost:8080/api/tenants/tenant-abc123/usage \
  -H "Authorization: Bearer $HUB_API_KEY"
```

Endpoints: `/api/tenants` (GET/POST), `/api/tenants/{id}` (GET/PUT/DELETE), `/api/tenants/{id}/assign`, `/api/tenants/{id}/unassign`, `/api/tenants/{id}/resources`, `/api/tenants/{id}/usage`. Supports per-tenant limits on agents, runs, and API keys with enforcement on resource assignment.

## Web Dashboard

The management dashboard at **http://localhost:8080/dashboard/** provides a visual interface for all platform features:

- **Overview** — Service health, agent count, recent runs, and Slinker status at a glance
- **Agents** — List, create, run, and delete agents with search filtering
- **Runs** — View all runs with agent/status filters, stop running tasks
- **Pipelines** — Execute cross-service pipelines chaining Trapper → Slinker → Greenie
- **Schedules** — Manage cron-scheduled pipelines with enable/disable controls
- **Analytics** — API call stats, task performance metrics, and daily usage trends
- **Settings** — API key configuration, service health checks, and database backup/restore

The dashboard supports dark mode automatically, works offline with cached data, and stores API keys in localStorage for convenience.

## CLI Tool

The `workflow` CLI provides terminal access to all platform features. Run it directly from the Greenie directory:

```bash
# List agents
python Greenie/workflow_cli.py agents list

# Run a task
python Greenie/workflow_cli.py run my-agent "summarize the latest report"

# Check platform health
python Greenie/workflow_cli.py health

# Search across all services
python Greenie/workflow_cli.py search "error handling"

# View unified dashboard
python Greenie/workflow_cli.py dashboard

# Manage schedules
python Greenie/workflow_cli.py schedules list
python Greenie/workflow_cli.py schedules create daily-backup "0 2 * * *" Slinker:TASK:backup

# Run a cross-service pipeline
python Greenie/workflow_cli.py pipeline Trapper:SEARCH:latest news Slinker:TASK:summarize

# Database backup
python Greenie/workflow_cli.py backup create
python Greenie/workflow_cli.py backup list

# View analytics
python Greenie/workflow_cli.py analytics
```

Configuration via environment variables:
- `WORKFLOW_API_URL` — API base URL (default: `http://localhost:8080`)
- `WORKFLOW_API_KEY` — Authentication key

All commands support `--json` for machine-readable output and `--url` / `--key` flags for overrides.

## GitHub / GitLab Webhooks

Trigger pipelines automatically from code events (push, pull requests, issues):

```bash
# Configure GitHub webhook
curl -X POST http://localhost:8080/api/webhooks/github/config \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "secret": "your-github-webhook-secret",
    "pipelines": [
      {
        "events": ["push", "pull_request"],
        "actions": ["opened", "synchronized"],
        "steps": [
          {"service": "Slinker", "task": "Review changes: {{commit_message}}"},
          {"service": "Trapper", "task": "SEARCH:{{repo}} latest issues"}
        ]
      }
    ]
  }'

# Configure GitLab webhook
curl -X POST http://localhost:8080/api/webhooks/gitlab/config \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "secret": "your-gitlab-token",
    "pipelines": [
      {
        "events": ["Merge Request Hook"],
        "actions": ["open"],
        "steps": [
          {"service": "Slinker", "task": "Review MR: {{commit_message}}"}
        ]
      }
    ]
  }'

# List webhook configs (secrets redacted)
curl http://localhost:8080/api/webhooks/config \
  -H "Authorization: Bearer $HUB_API_KEY"
```

In GitHub/GitLab settings, point webhook URL to:
- GitHub: `http://your-server:8080/api/webhooks/github`
- GitLab: `http://your-server:8080/api/webhooks/gitlab`

Variable substitution in pipeline tasks: `{{repo}}`, `{{branch}}`, `{{commit_message}}`, `{{url}}`, `{{context}}`.

## Scheduled Reports

Create automated reports that run on cron schedules:

```bash
# Create a daily analytics report
curl -X POST http://localhost:8080/api/reports \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Summary",
    "cron": "0 9 * * *",
    "type": "analytics",
    "format": "json"
  }'

# List all reports
curl http://localhost:8080/api/reports \
  -H "Authorization: Bearer $HUB_API_KEY"

# Run a report immediately
curl -X POST http://localhost:8080/api/reports/report-abc123/run \
  -H "Authorization: Bearer $HUB_API_KEY"

# Update a report
curl -X PUT http://localhost:8080/api/reports/report-abc123 \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"cron": "0 8 * * 1-5", "type": "runs"}'

# Delete a report
curl -X DELETE http://localhost:8080/api/reports/report-abc123 \
  -H "Authorization: Bearer $HUB_API_KEY"
```

Report types: `analytics` (API usage stats), `runs` (recent run history), `agents` (agent inventory), `custom`. Full cron expressions supported (see Advanced Scheduling).

## Advanced Scheduling

The platform includes a full cron expression parser supporting:

- **Wildcards**: `*` (any value)
- **Ranges**: `1-5` (Monday to Friday)
- **Steps**: `*/5` (every 5 minutes)
- **Lists**: `1,15,30` (specific values)
- **Last day**: `L` (last day of month)
- **Nearest weekday**: `15W` (15th or nearest weekday)
- **Nth weekday**: `5#1` (first Friday)
- **Shortcuts**: `@daily`, `@weekly`, `@monthly`, `@yearly`, `@hourly`

Used by scheduled pipelines and reports for precise timing control.

## Observability

The platform includes built-in distributed tracing and metrics for debugging cross-service issues.

### OpenTelemetry Tracing

Automatic trace context propagation across all three services. A single request flowing from Greenie → Slinker → Trapper is traced as one distributed trace.

**Enable tracing** by setting an OTLP endpoint in `.env`:

```bash
# Send traces to Jaeger
OTEL_EXPORTER_OTLP_ENDPOINT=jaeger:4317

# Or Zipkin
OTEL_EXPORTER_OTLP_ENDPOINT=zipkin:9411
```

Without an endpoint, traces print to stdout as JSON for local debugging. Configure sampling via `OTEL_TRACES_SAMPLE_RATIO` (default: `1.0` = all requests).

### Prometheus Metrics

Greenie exposes a `/metrics` endpoint for Prometheus/Grafana scraping:

```bash
# View raw metrics
curl http://localhost:8080/metrics
```

**Available metrics:**
- `http_requests_total` — Request count by method, endpoint, and status code
- `http_request_duration_seconds` — Latency histogram with percentiles
- `http_active_requests` — In-flight request gauge
- `Greenie_runs_total` — Agent run count by agent and outcome
- `Greenie_pipeline_steps_total` — Pipeline step execution count
- `Greenie_queue_depth` — Background job queue depth
- `Greenie_store_sizes` — In-memory feature store sizes

### Health Check

The `/api/health` endpoint reports observability status alongside database, downstream services, and store sizes:

```json
{
  "status": "ok",
  "observability": {
    "tracing": "enabled",
    "metrics": "enabled"
  },
  "database": { "status": "ok", "size_bytes": 1048576 },
  "downstream": {
    "Slinker": { "status": "ok" },
    "Trapper": { "status": "ok" }
  }
}
```

## Plugin System

Add new providers without modifying core code by placing them in the `Greenie/plugins/` directory:

```
plugins/
└── my_provider/
    ├── __init__.py          # Required, can be empty
    ├── provider.py           # Must contain a Provider class
    └── manifest.json         # Optional metadata
```

**Provider interface** (in `provider.py`):

```python
class MyProvider:
    name = "my_provider"

    def check_available(self) -> bool:
        return True

    def run(self, task: str, **kwargs) -> str:
        return f"Executed: {task}"

    async def async_run(self, task: str, **kwargs) -> str:
        return f"Executed: {task}"
```

**Plugin management API:**

```bash
# List loaded plugins
curl http://localhost:8080/api/plugins \
  -H "Authorization: Bearer $HUB_API_KEY"

# Get plugin details
curl http://localhost:8080/api/plugins/my_provider \
  -H "Authorization: Bearer $HUB_API_KEY"

# Hot-reload a plugin
curl -X POST http://localhost:8080/api/plugins/my_provider/reload \
  -H "Authorization: Bearer $HUB_API_KEY"
```

Disable plugin loading via `PLUGINS_ENABLED=false` in `.env`.

## LLM Provider Abstraction

Use multiple AI backends as alternatives to the default Junie/Ollama runner. Switch providers via environment variables or API:

```bash
# List available providers
curl http://localhost:8080/api/llm/providers \
  -H "Authorization: Bearer $HUB_API_KEY"

# Send a completion request
curl -X POST http://localhost:8080/api/llm/complete \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"provider": "openai", "prompt": "What is 2+2?", "system": "Be concise."}'

# Stream a response via SSE
curl -N http://localhost:8080/api/llm/stream \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"provider": "ollama", "prompt": "Write a haiku"}'
```

**Supported providers:**
- **Ollama** — Local models via `OLLAMA_URL` and `OLLAMA_MODEL`
- **OpenAI** — GPT-4o via `OPENAI_API_KEY` and `OPENAI_MODEL`
- **Anthropic** — Claude via `ANTHROPIC_API_KEY` and `ANTHROPIC_MODEL`
- **Google AI** — Gemini via `GOOGLE_API_KEY` and `GOOGLE_MODEL`

Set `LLM_PROVIDER` in `.env` to choose the default backend. Custom providers can be registered via the plugin system.

## Knowledge Graph

Vector-based semantic memory for context-aware agent behavior. Index memories, sessions, and messages, then search semantically to find related information across all stored data:

```bash
# Semantic search across all indexed content
curl "http://localhost:8080/api/knowledge-graph/search?q=how+to+fix+authentication" \
  -H "Authorization: Bearer $HUB_API_KEY"

# Search with related entity expansion
curl "http://localhost:8080/api/knowledge-graph/search?q=database+errors&context=true" \
  -H "Authorization: Bearer $HUB_API_KEY"

# Filter by entity type
curl "http://localhost:8080/api/knowledge-graph/search?q=deployment&types=memory,session" \
  -H "Authorization: Bearer $HUB_API_KEY"

# Index all memories
curl -X POST http://localhost:8080/api/knowledge-graph/index/memories \
  -H "Authorization: Bearer $HUB_API_KEY"

# Index recent sessions
curl -X POST "http://localhost:8080/api/knowledge-graph/index/sessions?limit=50" \
  -H "Authorization: Bearer $HUB_API_KEY"

# Rebuild entire index
curl -X POST http://localhost:8080/api/knowledge-graph/rebuild \
  -H "Authorization: Bearer $HUB_API_KEY"

# Graph statistics
curl http://localhost:8080/api/knowledge-graph/stats \
  -H "Authorization: Bearer $HUB_API_KEY"

# Backend status
curl http://localhost:8080/api/knowledge-graph/backend \
  -H "Authorization: Bearer $HUB_API_KEY"
```

**How it works:**
- **Embeddings** — Uses Ollama's `nomic-embed-text` model by default; falls back to a simple hash-based embedding when Ollama is unavailable
- **Storage** — Vectors stored as BLOBs in SQLite alongside the existing `hub.db` database
- **Graph relationships** — Edges link related entities (e.g., session → messages, memory → session) for context expansion
- **Search** — Cosine similarity search with configurable threshold (default 0.3) and top-k results

**Configuration** (in `hub.yaml`):

```yaml
knowledge_graph:
  embedding_model: "nomic-embed-text"
  embedding_url: "http://localhost:11434"
  embedding_timeout: 30
```

**Entity types:** `memory`, `session`, `message`, `note`, `file` — any text content can be indexed.

## Multi-Instance Cluster Mode

Run multiple Greenie instances behind a load balancer with shared state via Redis. Enable horizontal scaling and high availability:

```bash
# Check cluster status
curl http://localhost:8080/api/cluster/status \
  -H "Authorization: Bearer $HUB_API_KEY"

# List all registered instances
curl http://localhost:8080/api/cluster/instances \
  -H "Authorization: Bearer $HUB_API_KEY"

# Shared job queue status
curl http://localhost:8080/api/cluster/jobs/status \
  -H "Authorization: Bearer $HUB_API_KEY"
```

**How it works:**
- **Distributed locks** — Redis-based locks prevent race conditions across instances
- **Shared job queue** — Jobs are distributed across instances via Redis lists
- **Instance registry** — Automatic registration with heartbeat-based health monitoring
- **Session affinity** — WebSocket sessions stick to their originating instance
- **Graceful fallback** — Single-instance mode when Redis is unavailable

**Configuration** (via environment variables):
- `REDIS_HOST` — Redis server hostname (default: `localhost`)
- `REDIS_PORT` — Redis port (default: `6379`)
- `REDIS_PASSWORD` — Optional Redis password
- `REDIS_DB` — Redis database number (default: `0`)

Redis is already included in `docker-compose.yml` — cluster mode activates automatically when the `redis` Python package is installed.

## Agent Marketplace

Share agents, skills, and templates across deployments via a local package registry:

```bash
# Browse available packages
curl http://localhost:8080/api/marketplace/packages \
  -H "Authorization: Bearer $HUB_API_KEY"

# Search packages
curl "http://localhost:8080/api/marketplace/packages?search=research&type=agent" \
  -H "Authorization: Bearer $HUB_API_KEY"

# Publish an existing agent
curl -X POST http://localhost:8080/api/marketplace/agents/my-agent/publish \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"version": "1.0.0", "author": "me", "category": "research", "tags": ["research", "web"]}'

# Publish a new package
curl -X POST http://localhost:8080/api/marketplace/packages \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "pkg_type": "agent",
    "name": "researcher",
    "version": "1.0.0",
    "title": "Web Researcher",
    "description": "Searches and summarizes web content",
    "config": {"runner": "junie", "skills": ["web-search"]}
  }'

# Install a package
curl -X POST http://localhost:8080/api/marketplace/packages/{pkg_id}/install \
  -H "Authorization: Bearer $HUB_API_KEY"

# Export a package as tar.gz
curl http://localhost:8080/api/marketplace/packages/{pkg_id}/export \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -o researcher-1.0.0.tar.gz

# Import a package from tar.gz
curl -X POST http://localhost:8080/api/marketplace/import \
  -H "Authorization: Bearer $HUB_API_KEY" \
  -F "file=@researcher-1.0.0.tar.gz"

# List installed packages
curl http://localhost:8080/api/marketplace/installed \
  -H "Authorization: Bearer $HUB_API_KEY"

# Uninstall a package
curl -X DELETE http://localhost:8080/api/marketplace/installed/{install_id} \
  -H "Authorization: Bearer $HUB_API_KEY"

# Marketplace statistics
curl http://localhost:8080/api/marketplace/stats \
  -H "Authorization: Bearer $HUB_API_KEY"
```

**How it works:**
- **3 package types** — `agent` (full agent config), `skill` (SKILL.md + references), `template` (pipeline/task templates)
- **Dependency resolution** — Packages declare dependencies; installer checks they're met before installing
- **Conflict detection** — Prevents overwriting existing agents, skills, or templates
- **Version management** — Track multiple versions per package; install any version
- **Export/Import** — Packages export as `tar.gz` archives for sharing between deployments
- **SQLite storage** — All registry data persists in `marketplace.db`

**API Endpoints (18 total):**
- `GET /api/marketplace/stats` — Marketplace statistics
- `GET /api/marketplace/packages` — Browse packages with filters
- `GET /api/marketplace/categories` — List categories
- `GET /api/marketplace/tags` — List tags
- `GET /api/marketplace/packages/{pkg_id}` — Package details
- `GET /api/marketplace/{type}/{name}` — Latest version by name
- `GET /api/marketplace/{type}/{name}/versions` — All versions
- `POST /api/marketplace/packages` — Publish new package
- `POST /api/marketplace/import` — Import from tar.gz
- `GET /api/marketplace/packages/{pkg_id}/export` — Export as tar.gz
- `POST /api/marketplace/agents/{name}/publish` — Publish existing agent
- `POST /api/marketplace/skills/{name}/publish` — Publish existing skill
- `POST /api/marketplace/templates/{id}/publish` — Publish existing template
- `POST /api/marketplace/packages/{pkg_id}/install` — Install package
- `GET /api/marketplace/installed` — List installed packages
- `DELETE /api/marketplace/installed/{install_id}` — Uninstall package
- `PUT /api/marketplace/packages/{pkg_id}/unpublish` — Soft delete
- `DELETE /api/marketplace/packages/{pkg_id}` — Permanent delete

## Adding More Parts

The platform is designed to be extensible:

1. **New Greenie providers** — Create a module in `Greenie/hub/` that implements `AgentProvider` and auto-registers it.
2. **New services** — Add the service to `docker-compose.yml` and create a provider in Greenie.
3. **New skills** — Add skill folders to `Greenie/skills/` with a `SKILL.md` file.

## Project Structure

```
Workflow/
├── docker-compose.yml       # Unified service orchestration
├── .env.example             # Environment variable template
├── Greenie/                # Main dashboard (Python/FastAPI)
│   ├── hub/
│   │   ├── api.py           # Thin factory (re-exports from hub.api package)
│   │   ├── api/             # 48 route modules (320 endpoints)
│   │   │   ├── core.py      # Shared infrastructure, stores, app factory
│   │   │   ├── __init__.py  # Route registration
│   │   │   └── ...          # agents.py, runs.py, webhooks.py, etc.
│   │   ├── providers.py     # Provider abstraction layer
│   │   ├── Slinker_provider.py  # Slinker integration
│   │   ├── Trapper_provider.py # Trapper integration
│   │   ├── runner.py        # Task execution engine
│   │   ├── tracing.py       # OpenTelemetry distributed tracing
│   │   ├── metrics.py       # Prometheus metrics collection
│   │   ├── plugins.py       # Dynamic provider loading system
│   │   ├── knowledge_graph.py # Vector-based semantic memory
│   │   ├── cluster.py         # Multi-instance cluster support (Redis)
│   │   ├── marketplace.py     # Agent marketplace registry (SQLite)
│   │   ├── llm_providers.py   # Multi-backend LLM abstraction (4 providers)
│   │   ├── feature_store.py # SQLite persistence for 29 feature stores
│   │   ├── cron_parser.py   # Full cron expression parser
│   │   ├── logging_config.py # Structured JSON logging
│   │   └── ...
│   ├── workflow_cli.py      # Standalone CLI tool
│   ├── plugins/             # Plugin directory (auto-loaded)
│   ├── hub.yaml             # Agent configuration
│   └── Dockerfile
├── Slinker/                # Execution engine (Python/FastAPI)
│   ├── junie_adapter/
│   │   ├── adapter.py       # Clean API for Greenie
│   │   ├── service.py       # HTTP service
│   │   ├── worktree_manager.py  # Git worktree isolation
│   │   └── ...
│   └── Dockerfile
└── Trapper/               # Web scraping (TypeScript/Fastify)
    ├── src/
    │   ├── api/             # REST API routes
    │   ├── services/        # Scrape, crawl, search, etc.
    │   └── ...
    ├── docker-compose.yml
    └── Dockerfile
```

## License

Each component has its own license:
- Greenie: Apache 2.0
- Slinker: MIT
- Trapper: MIT
