# Evershade Advanced Guide

**Version:** 1.0.0
**Last Updated:** 2026-10-23
**Audience:** Power users, system architects, and developers who want to understand internals.

---

## Table of Contents

- [Internal Architecture Deep Dive](#internal-architecture-deep-dive)
- [Performance Tuning](#performance-tuning)
- [Custom Integrations](#custom-integrations)
- [Advanced Mission Control](#advanced-mission-control)
- [Advanced Agent Harness](#advanced-agent-harness)
- [Network & Security Hardening](#network--security-hardening)
- [Database Internals](#database-internals)
- [Custom Docker Images](#custom-docker-images)
- [Multi-Instance & Scaling](#multi-instance--scaling)
- [Debugging & Diagnostics](#debugging--diagnostics)
- [Custom Notification Channels](#custom-notification-channels)
- [LLM Provider Advanced Configuration](#llm-provider-advanced-configuration)

---

## Internal Architecture Deep Dive

### Request Lifecycle

Every request in Evershade follows this path:

```
Client → [CSRF Check] → [Auth Middleware] → [Rate Limiter] → [Idempotency Check]
                                              ↓
                                    Greenie Router
                                              ↓
                              ┌───────────────┼───────────────┐
                              ↓               ↓               ↓
                          Slinker          Trapper         Shrewd
                              ↓               ↓               ↓
                          Junie CLI       Playwright     External API
                              ↓               ↓               ↓
                              └───────────────┴───────────────┘
                                              ↓
                                    Gobber (persist)
                                              ↓
                                    Sneaker (observe)
                                              ↓
                                    Poltergeist (notify)
```

### Greenie Middleware Stack

Greenie's request pipeline (in order):

1. **Secret Redaction** – Scans request/response bodies for sensitive patterns
2. **CSRF Protection** – Validates double-submit cookie pattern for cookie sessions
3. **Authentication** – Bearer token (service-to-service) or session cookie (browser)
4. **Rate Limiting** – Sliding window per-IP and per-API-key
5. **Idempotency** – Checks `X-Idempotency-Key` header for retryable operations
6. **Request ID** – Generates `X-Request-ID` and `X-Correlation-ID` headers
7. **Routing** – FastAPI router dispatches to endpoint handlers

### Service Communication Protocol

All inter-service communication uses HTTP/JSON with these conventions:

- **Authentication:** `Authorization: Bearer <key>` header only (query params rejected)
- **Timing attack prevention:** Constant-time comparison via `hmac.compare_digest`
- **Correlation:** `X-Correlation-ID` header propagated across all downstream calls
- **Timeouts:** Configurable per-operation (see [ARCHITECTURE.md](ARCHITECTURE.md#timeouts-and-retries))
- **Error format:** Standard envelope with `success`, `data`, `error`, `requestId`, `timestamp`

### SQLite WAL Mode

All services use SQLite in WAL (Write-Ahead Logging) mode for:
- **Concurrent reads:** Multiple readers can access the database while writes occur
- **Crash safety:** WAL journal survives unexpected shutdowns
- **Performance:** Reduced lock contention compared to rollback journal

WAL mode is configured in each service's database initialization. Checkpointing occurs automatically when the WAL file reaches 1000 pages.

---

## Performance Tuning

### Slinker Worker Scaling

The `EVERSHADE_MAX_CONCURRENT_WORKERS` variable controls parallel task execution:

| Workers | RAM Usage | Use Case |
|---------|-----------|----------|
| 1 | ~512 MB | Default, safe for most machines |
| 2-4 | ~1-2 GB | Moderate workloads, 8+ GB RAM |
| 5+ | ~2.5+ GB | Heavy workloads, 16+ GB RAM |

Each worker gets its own Git worktree and Junie CLI process. Increasing workers beyond available CPU cores yields diminishing returns.

### Trapper Crawl Optimization

For large-scale crawling:

```bash
# Increase concurrency (default: 5)
EVERSHADE_CRAWL_MAX_CONCURRENCY=10

# Reduce delay between requests (default: 1000ms)
# Set via Trapper environment: CRAWL_DELAY=500

# Increase page limit (default: 100)
EVERSHADE_CRAWL_MAX_PAGES=500
```

**Warning:** Aggressive crawling may trigger rate limiting or IP blocks on target sites. Respect `robots.txt`.

### Redis Memory Management

Redis is used for Trapper job queues and caching. Tune memory:

```yaml
# docker-compose.yml
redis:
  command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
```

Policies: `noeviction`, `allkeys-lru`, `volatile-lru`, `allkeys-random`.

### Ollama Model Selection

For local LLM inference:

| Model | RAM | Performance | Use Case |
|-------|-----|-------------|----------|
| `gemma4:12b` | ~8 GB | Good | Default, balanced |
| `llama3.1:8b` | ~6 GB | Fast | Quick responses |
| `mistral:7b` | ~5 GB | Fast | Lightweight tasks |
| `qwen2.5:32b` | ~16 GB | Excellent | Complex reasoning |

GPU acceleration (NVIDIA) requires `nvidia-container-toolkit` and adding `runtime: nvidia` to the Ollama service.

---

## Custom Integrations

### MCP Server Integration

Greenie supports Model Context Protocol (MCP) servers for extending agent capabilities:

```bash
# Add an MCP server
curl -X POST http://localhost:8080/api/mcp/servers \
  -H "Authorization: Bearer $EVERSHADE_GREENIE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "filesystem",
    "transport": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
  }'
```

MCP servers expose tools that agents can invoke. Built-in transports: `stdio` and `sse`.

### Custom Plugin Development

Plugins extend Greenie with new routes, middleware, and background tasks:

```python
# Example plugin structure
class MyPlugin:
    name = "my-plugin"
    version = "1.0.0"

    def register_routes(self, app):
        @app.get("/api/my-plugin/data")
        async def get_data():
            return {"status": "ok"}

    def on_startup(self):
        # Initialize resources
        pass

    def on_shutdown(self):
        # Cleanup resources
        pass
```

Place plugins in `Greenie/plugins/` and enable via `hub.yaml`.

### Webhook Integration

Gobber manages webhook definitions. Create webhooks for external integrations:

```bash
# Create a webhook
curl -X POST http://localhost:8085/api/webhooks \
  -H "Authorization: Bearer $EVERSHADE_GOBBER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://hooks.example.com/evershade",
    "events": ["mission.completed", "validation.failed"],
    "secret": "webhook-signing-secret"
  }'
```

Webhook payloads include HMAC signatures for verification.

---

## Advanced Mission Control

### Custom Validation Contracts

Validation contracts define what "done" means for each feature:

```json
{
  "checks": [
    {"type": "test", "command": "pytest -x", "fail_on_error": true},
    {"type": "lint", "command": "ruff check .", "fail_on_error": true},
    {"type": "type", "command": "mypy .", "fail_on_error": false},
    {"type": "security", "command": "bandit -r .", "fail_on_error": true},
    {"type": "custom", "command": "./scripts/custom-check.sh", "fail_on_error": true}
  ]
}
```

### Fix-Revalidate Cycle Configuration

Control automatic retry behavior:

```json
{
  "max_retries": 3,
  "retry_on": ["test_failure", "lint_failure"],
  "exclude": ["security_failure"],
  "notify_on_retry": true,
  "cooldown_seconds": 30
}
```

### Parallel Worker Execution

Enable parallel execution within milestones:

```json
{
  "milestones": [
    {
      "name": "Implement features",
      "parallel_workers": 3,
      "features": [
        {"name": "Feature A", "worker": "worker-1"},
        {"name": "Feature B", "worker": "worker-2"},
        {"name": "Feature C", "worker": "worker-3"}
      ]
    }
  ]
}
```

Workers run concurrently but share the same Git worktree. Ensure features don't modify overlapping files.

### Autonomy Levels

| Level | Behavior |
|-------|----------|
| `supervised` | All operations require human approval |
| `restricted_autonomous` | Only sensitive operations (file deletion, credential access) require approval |
| `full_autonomous` | No approval gates; mission runs to completion |

### Mission Analytics Queries

```bash
# Get success rate by model
curl http://localhost:8080/api/missions/analytics \
  -H "Authorization: Bearer $EVERSHADE_GREENIE_API_KEY"

# Response includes:
# - success_rate: Overall mission success percentage
# - avg_duration: Average time from create to complete
# - model_usage: Token counts per model
# - validation_summary: Common failure patterns
```

---

## Advanced Agent Harness

### Custom Droid Development

Create specialized subagents in `.evershade/droids/`:

```markdown
# .evershade/droids/security-auditor.md

---
name: security-auditor
description: Reviews code for security vulnerabilities
model: gpt-4o
allowed_tools: [grep, read_file, run_command]
denied_tools: [write_file, delete_file, network_request]
---

You are a security auditor. When given code, you:
1. Scan for common vulnerabilities (SQL injection, XSS, CSRF)
2. Check for hardcoded secrets
3. Verify input validation
4. Report findings with severity levels
```

Droids are auto-discovered from `.evershade/droids/` (project) and `~/.evershade/droids/` (personal).

### Advanced Skills System

Skills are `SKILL.md` files with trigger-based auto-discovery:

```markdown
# .evershade/skills/database-migration/SKILL.md

---
name: database-migration
triggers: ["migration", "migrate", "schema change", "alter table"]
description: Creates and runs database migrations
---

## Steps
1. Analyze current schema
2. Generate migration script
3. Run migration in transaction
4. Verify data integrity
5. Rollback on failure
```

Skills can include supporting files (scripts, templates) in the same directory.

### Hooks System Deep Dive

Event-driven hooks for mission lifecycle:

```bash
# PreToolUse hook – can block execution
# Exit code 0: allow, 1: warn, 2: block

#!/bin/bash
# .evershade/hooks/pre-tool-use.sh
TOOL_NAME=$1
AGENT_ID=$2

# Block dangerous tools for non-admin agents
if [[ "$TOOL_NAME" == "delete_file" ]] && [[ "$AGENT_ID" != "admin-agent" ]]; then
    echo "Blocked: $AGENT_ID cannot use delete_file"
    exit 2
fi
```

Supported events: `PreToolUse`, `PostToolUse`, `SessionStart`, `SessionEnd`, `MissionStart`, `MissionEnd`, `MilestoneComplete`, `ValidationFail`.

Hook types:
- **Script:** Local shell script execution
- **Webhook:** HTTP POST to external URL with event payload

---

## Network & Security Hardening

### Docker Network Isolation

Evershade uses two Docker networks:

| Network | Purpose | Services |
|---------|---------|----------|
| `internal` | Service-to-service communication | All backend services, Redis |
| `frontend` | Host-accessible services | Greenie, Slammer, Caddy |

Only Greenie (and optionally Slammer/Caddy) are published to the host. All other services are internal-only.

### Container Hardening Checklist

Every container applies:
- [x] `cap_drop: ALL` – No Linux capabilities
- [x] `security_opt: no-new-privileges` – No privilege escalation
- [x] `read_only: true` – Immutable root filesystem
- [x] `tmpfs` mounts – Writable directories in memory
- [x] Resource limits – CPU and memory caps
- [x] Non-root user – Where applicable

### Custom Seccomp Profiles

For additional hardening, apply custom Seccomp profiles:

```yaml
services:
  Greenie:
    security_opt:
      - no-new-privileges:true
      - seccomp:/path/to/custom-seccomp.json
```

### Workstation Network Policies

Workstations use default-deny network policies:

```json
{
  "default_action": "deny",
  "allow_outbound": [
    {"dest": "0.0.0.0/0", "port": 80, "protocol": "tcp"},
    {"dest": "0.0.0.0/0", "port": 443, "protocol": "tcp"}
  ],
  "deny_private": true,
  "deny_metadata": true,
  "deny_internal_services": true
}
```

---

## Database Internals

### Schema Overview

| Service | Database | Key Tables |
|---------|----------|------------|
| Greenie | `evershade_valley.db` | agents, sessions, workflows, missions, milestones, features, validations |
| Slinker | `Slinker.db` | tasks, workers, projects, logs |
| Gobber | `gobber.db` | webhooks, analytics, flags, cache, roles, notes, embeddings |
| Sneaker | `sneaker.db` | metrics, traces, logs, alerts |
| Hider | `hider.db` | secrets (encrypted), configs |
| Poltergeist | `poltergeist.db` | notifications, templates, channels |

### Database Maintenance

```bash
# Vacuum and analyze (run during maintenance window)
docker compose exec Greenie sqlite3 /app/data/evershade_valley.db "VACUUM; ANALYZE;"

# Check integrity
docker compose exec Greenie sqlite3 /app/data/evershade_valley.db "PRAGMA integrity_check;"

# View table sizes
docker compose exec Greenie sqlite3 /app/data/evershade_valley.db \
  "SELECT name, pgsz FROM sqlite_master WHERE type='table' ORDER BY pgsz DESC;"
```

### WAL Checkpointing

Force WAL checkpoint (normally automatic):

```bash
docker compose exec Greenie sqlite3 /app/data/evershade_valley.db "PRAGMA wal_checkpoint(TRUNCATE);"
```

---

## Custom Docker Images

### Building Custom Service Images

Each service has its own `Dockerfile`. To customize:

```dockerfile
# Example: Add custom Python packages to Greenie
FROM evershade-greenie:latest
RUN pip install custom-package==1.0.0
COPY custom-scripts/ /app/custom-scripts/
```

Build and use:

```bash
docker build -t my-greenie:custom .

# Override in docker-compose.yml
services:
  Greenie:
    image: my-greenie:custom
    build: null  # Disable build context
```

### Custom Base Images

For air-gapped environments, build from scratch:

```bash
# Build all services locally
docker compose --profile standard build

# Export images for transfer
docker save $(docker compose --profile standard images -q) | gzip > evershade-images.tar.gz

# Import on target machine
gzip -dc evershade-images.tar.gz | docker load
```

---

## Multi-Instance & Scaling

### Current Limitations

Evershade is designed for single-instance deployment. Greenie runs as a single process with SQLite.

### Scaling Slinker

Slinker supports concurrent workers within a single instance:

```bash
# Increase workers
EVERSHADE_MAX_CONCURRENT_WORKERS=4
```

For true horizontal scaling, you would need:
- Shared database (PostgreSQL instead of SQLite)
- Shared workspace (NFS or distributed filesystem)
- Message queue (Redis is already present)

### Read Replicas

For read-heavy workloads, SQLite online backup can create read replicas:

```bash
# Create read-only replica
docker compose exec Greenie sqlite3 /app/data/evershade_valley.db \
  ".backup /tmp/readonly.db"
```

---

## Debugging & Diagnostics

### Advanced Logging

Enable debug logging for specific modules:

```bash
# All debug logging
EVERSHADE_LOG_LEVEL=DEBUG

# Module-specific (Python)
export PYTHONPATH=/app
docker compose exec Greenie python -c "
import logging
logging.getLogger('hub.mission').setLevel(logging.DEBUG)
"
```

### SQLite Debugging

```bash
# Enter interactive shell
docker compose exec Greenie sqlite3 /app/data/evershade_valley.db

# Useful commands
.schema              # Show all table schemas
.tables              # List tables
PRAGMA journal_mode; # Check WAL mode
PRAGMA page_count;   # Database size in pages
```

### Network Debugging

```bash
# Test service-to-service connectivity
docker compose exec Greenie curl -s http://Slinker:8000/health
docker compose exec Greenie curl -s http://Trapper-api:3000/health

# Check DNS resolution
docker compose exec Greenie nslookup Slinker

# Trace network calls
docker compose exec Greenie python -c "
import urllib.request
import time
start = time.time()
urllib.request.urlopen('http://Slinker:8000/health')
print(f'Response time: {time.time() - start:.3f}s')
"
```

### Memory Profiling

```bash
# Check container memory usage
docker stats --no-stream Greenie Slinker Trapper-api

# Profile Python memory
docker compose exec Greenie python -m memory_profiler script.py
```

---

## Custom Notification Channels

### Adding a New Channel to Poltergeist

Poltergeist supports custom notification channels via plugins:

```python
# Example: Custom webhook channel
class CustomWebhookChannel:
    name = "custom_webhook"

    async def send(self, message, config):
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(
                config["url"],
                json={"text": message, "timestamp": int(time.time())},
                headers={"Authorization": f"Bearer {config.get('token', '')}"},
            ) as response:
                if response.status != 200:
                    raise Exception(f"Webhook failed: {response.status}")
```

Register the channel in Poltergeist's configuration.

---

## LLM Provider Advanced Configuration

### Model Routing Rules

Shrewd supports conditional routing based on request properties:

```json
{
  "routing_rules": [
    {
      "condition": "cost_sensitive",
      "provider": "ollama",
      "model": "gemma4:12b"
    },
    {
      "condition": "high_quality",
      "provider": "openai",
      "model": "gpt-4o"
    },
    {
      "condition": "default",
      "provider": "anthropic",
      "model": "claude-sonnet-4-20250514"
    }
  ]
}
```

### Cost Tracking

Shrewd tracks token usage and estimated costs:

```bash
# Get usage stats
curl http://localhost:8089/api/usage \
  -H "Authorization: Bearer $EVERSHADE_SHREWD_API_KEY"

# Response includes:
# - total_tokens: Total tokens consumed
# - cost_by_provider: Breakdown by provider
# - cost_by_model: Breakdown by model
# - requests_by_hour: Request rate over time
```

### Fallback Configuration

Configure automatic fallback on provider failure:

```json
{
  "primary": {"provider": "openai", "model": "gpt-4o"},
  "fallbacks": [
    {"provider": "anthropic", "model": "claude-sonnet-4-20250514"},
    {"provider": "ollama", "model": "gemma4:12b"}
  ],
  "fallback_on": ["rate_limit", "timeout", "error"]
}
```

---

## Contributing Advanced Features

When contributing advanced features:

1. **Update this guide** – Document new internals and patterns
2. **Add integration tests** – Cover cross-service interactions
3. **Benchmark performance** – Measure impact on latency and resource usage
4. **Security review** – Ensure no new attack surfaces
5. **Backward compatibility** – Don't break existing configurations

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for the full process.
