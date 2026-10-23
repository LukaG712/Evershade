# Changelog

All notable changes to the Evershade ecosystem will be documented in this file.

## [1.14.1] - 2026-10-23

### Fixed

- **GUI Installer Progressbar Crash**: Fixed `_tkinter.TclError: Layout Horizontal.Progressbar.Horizontal not found` on Linux (and potentially Windows) by replacing the invalid ttk style name `Progressbar.Horizontal` with the correct `Horizontal.TProgressbar` in both `install-gui.py` and `install-gui-win.py`.

## [1.14.0] - 2026-10-23

### Added

**First Official Release — GUI Installers for Linux and Windows**

This is the first official release of the Evershade ecosystem, including all services, installers, and documentation.

- **Linux GUI Installer** (`install-gui.py`, `run-install-gui.sh`): Visual wizard installer for Ubuntu Desktop with 9 steps: Welcome, System Check, Installation Options (profile + custom service selection), Install Docker, Clone & Install, Configure (.env with auto-generated API keys), System Integration (systemd + desktop launcher), Start Services, and Complete summary.
- **Windows GUI Installer** (`install-gui-win.py`, `run-install-gui.bat`): Visual wizard installer for Windows with 9 steps: Welcome, System Check, Installation Options (profile + custom service selection), Docker Desktop Check, Clone & Install, Configure (.env with auto-generated API keys), Desktop Shortcut, Start Services, and Complete summary.
- **Custom Service Selection**: All installers (CLI and GUI) now support custom mode where users can pick individual services via checkboxes/flags instead of predefined profiles.
- **Service Submodules**: All 10 services are included as git submodules under `services/` directory: Greenie, Slinker, Trapper, Gobber, Sneaker, Hider, Poltergeist, Shrewd, Slammer, and Speedy.
- **Documentation Website** (`website/`): Full documentation website with HTML pages for getting started, architecture, security, configuration, deployment, API reference, and individual service documentation.
- **Update Scripts** (`update.sh`, `update.ps1`, `update-ubuntu.sh`): Scripts to update an existing Evershade installation to the latest version.

### Changed

- All service repositories moved into `services/` directory for cleaner organization
- README updated with GUI Installer sections for both Linux and Windows
- Install scripts refactored to support custom service selection

### Breaking Changes

- All services require `Authorization: Bearer` header — query parameter auth removed
- Hider requires `ENCRYPTION_KEY` environment variable for AES-256-GCM encryption
- Hider secrets are now encrypted at rest in SQLite — migration required from in-memory data
- Slammer is the single dashboard — Greenie operates as API-only backend

---

## [1.12.0] - 2026-10-22

### Added – Agent Harness (Phase 11)

Factory-inspired agent harness capabilities for reusable workflows, specialized subagents, and event-driven automation.

- **Spec Mode**: Read-only research phase before implementation. Create specs, run repository analysis, approve/reject plans, and convert approved specs to missions. (`hub/mission/spec_mode.py`)
- **Custom Droids**: Specialized subagents defined in Markdown with own prompts, models, and tool policies. Built-in droids: worker, explorer, reviewer, validator. Discovery from project and personal directories. (`hub/mission/droids.py`)
- **Skills System**: Reusable SKILL.md workflows with trigger-based auto-discovery. Skills can be matched to tasks and invoked manually. (`hub/mission/skills.py`)
- **Hooks System**: Event-driven lifecycle hooks for mission events (PreToolUse, PostToolUse, MissionStart, MissionEnd, MilestoneComplete, ValidationFail). Support for script and webhook hooks. (`hub/mission/hooks.py`)
- **Environments**: Reusable sandbox definitions with repository, dependencies, setup commands, and health checks. (`hub/mission/environments.py`)
- **API Endpoints**: 30+ new REST endpoints for specs, droids, skills, hooks, and environments. (`hub/api/agent_harness.py`)
- **30 unit tests** covering all five components

## [1.11.0] - 2026-10-22

### Added

**CSRF Protection, Gobber Embeddings API, and Sneaker OTLP Export (Phase 10)**
- `Greenie/hub/api/csrf.py`: CSRF protection middleware – token generation with HMAC signing, validation with expiry, double-submit cookie pattern, configurable excluded paths, and middleware integration
- `Greenie/hub/api/csrf.py`: CSRF token endpoints – `GET /api/csrf/token` for token generation, `GET /api/csrf/verify` for pre-flight checks
- `Gobber/gobber/api.py`: Vector embedding API endpoints – `POST /api/embeddings/generate` for single text embedding, `POST /api/embeddings/search` for semantic search, `GET /api/embeddings/stats` for statistics, `POST /api/embeddings/batch` for batch embedding generation
- `Sneaker/sneaker/otlp_export.py`: OTLP (OpenTelemetry Protocol) export support – receives traces/metrics/logs via OTLP JSON format, parses and stores them, forwards to external OTLP collector if configured, exports data in OTLP JSON format
- `Sneaker/sneaker/api.py`: Integrated OTLP routes – `POST /v1/traces`, `POST /v1/metrics`, `POST /v1/logs`, `GET /api/otlp/stats`, `GET /api/otlp/export/*`
- `tests/unit/test_csrf.py`: 25 unit tests for CSRF token generation, validation, extraction, skip logic, and configuration
- `Sneaker/tests/test_otlp_export.py`: 12 unit tests for OTLP parsing (traces, metrics, logs), configuration, and store registration
- `Gobber/tests/test_embeddings.py`: 8 unit tests for embedding generation, search, stats, and batch endpoints

### Changed

- Greenie version bumped to 1.11.0

### Breaking Changes

- None

### Configuration

New environment variables:
- `CSRF_SECRET_KEY` – Secret key for CSRF token signing (required in production)
- `CSRF_ENABLED` – Enable/disable CSRF protection (default: true)
- `CSRF_TOKEN_EXPIRY` – CSRF token expiry in seconds (default: 3600)
- `CSRF_EXCLUDED_PATHS` – Comma-separated paths to exclude from CSRF (default: /health,/api/metrics)
- `OTLP_ENDPOINT` – OTLP collector endpoint for Sneaker forwarding (optional)
- `OTLP_INSECURE` – Use insecure connection for OTLP forwarding (default: true)

---

## [1.10.0] - 2026-10-22

### Added

**End-to-End Smoke Test, Cross-Service Integration, and Final Hardening (Phase 9)**
- `tests/integration/test_smoke.py`: End-to-end smoke test – 8 tests covering full mission lifecycle (create → plan → execute → validate → complete), validation failure handling, cancel/resume, pause/resume, stats, repo intelligence, checkpoint recovery, and completion report
- `tests/integration/test_mission_cross_service.py`: Cross-service mission integration tests – 13 tests covering API health, lifecycle via API, planning, validation, analytics, and logs
- `Slammer/src/components/Missions.tsx`: Fixed unused `formatDuration` helper – now used by `missionDuration()` to display mission duration in the detail view info cards

### Changed

- Greenie version bumped to 1.10.0

### Breaking Changes

- None

---

## [1.9.0] - 2026-10-22

### Added

**Mission Analytics, SSE Streaming, and Fix-Revalidate Cycle (Phase 8)**
- `Greenie/hub/mission/analytics.py`: Mission-specific analytics – success/failure rates, average durations per lifecycle stage, model usage tracking, validation findings summary, autonomy distribution, and mission timelines
- `Greenie/hub/mission/sse.py`: Server-Sent Events (SSE) streaming for real-time mission execution logs
- `Greenie/hub/mission/storage.py`: Execution log storage – `mission_logs` table with save, retrieve, filter, pagination, and since-timestamp queries
- `Greenie/hub/mission/controller.py`: Fix-revalidate cycle – `create_fix_features()` and `start_fix_revalidate()` to automatically create worker features from validation failures, with configurable max retries
- `Greenie/hub/mission/controller.py`: Execution logging at all lifecycle points (create, plan, execute, validate, cancel, pause, resume, approval)
- `Greenie/hub/api/missions.py`: New API endpoints – logs (`GET /logs`, `GET /logs/stream` SSE), analytics (`GET /analytics`, `GET /timeline`, `GET /validation-summary`), diffs (`GET /diff`), fix-revalidate (`POST /fix-revalidate`)
- `tests/unit/test_mission_analytics.py`: 17 unit tests for analytics functions
- `tests/unit/test_mission_logs.py`: 10 unit tests for log storage and SSE streaming
- `tests/unit/test_fix_revalidate.py`: 13 unit tests for fix-revalidate cycle and mission logging

## [1.8.0] - 2026-10-22

### Added

**Factory-Inspired Mission Control System (Phases 1–7)**
- `Greenie/hub/mission/models.py`: Mission, MissionMilestone, MissionFeature, ValidationContract, ValidationResult, MissionCheckpoint dataclasses with enums (MissionStatus, MilestoneStatus, FeatureStatus, ValidationSeverity, AutonomyLevel)
- `Greenie/hub/mission/storage.py`: SQLite persistence with WAL mode for missions, checkpoints, and validation results
- `Greenie/hub/mission/controller.py`: Full mission lifecycle controller – create, plan, execute, validate, complete, cancel, pause, resume, checkpoint recovery, and approval gates
- `Greenie/hub/mission/automation.py`: Event-driven automation engine – GitHub webhook handler (issues, PRs, CI failures), HMAC signature verification, schedule-based triggers with cron parsing, idempotency with TTL expiration, rate limiting, and action registry
- `Greenie/hub/mission/secret_redaction.py`: Secret redaction for logs and model context – pattern-based redaction of API keys, tokens, passwords, GitHub tokens, AWS keys, and email addresses; logging filter; env var and dict redaction
- `Greenie/hub/mission/planner.py`: LLM-based planning via Shrewd with heuristic fallback and repo context integration
- `Greenie/hub/mission/repo_intelligence.py`: Repository analysis – structure, frameworks, build/test commands, dependencies, conventions
- `Greenie/hub/mission/auto_review.py`: Automated code review – deterministic checks (test, lint, type), diff-based security/correctness review, structured findings
- `Greenie/hub/api/missions.py`: 18 REST endpoints – CRUD, planning, execution, validation, control, approval gates, and statistics
- Extended `Greenie/hub/workflow/models.py`: New StepType values (PLANNER, WORKER, VALIDATOR, MILESTONE); role, model_override, milestone_id fields
- Extended `Greenie/hub/workflow/executor.py`: Parallel step execution for independent workers within a milestone; opt-in via `parallel_workers` flag
- `Slammer/src/components/Missions.tsx`: Full-featured React mission dashboard – list view, create form, detail view with milestone progress, validation results, execution logs, and action buttons
- `Slammer/src/App.tsx`: Added Missions page to navigation
- `tests/unit/test_mission_models.py`: 23 unit tests for model serialization
- `tests/unit/test_automation.py`: 20 unit tests for webhook handling, idempotency, rate limiting, schedule triggers, and action registry
- `tests/unit/test_secret_redaction.py`: 15 unit tests for secret redaction patterns
- `tests/integration/test_missions.py`: 33 integration tests covering full lifecycle, approval gates, and checkpoint recovery
- `Slammer/src/components/__tests__/Missions.test.tsx`: 13 component tests for the Missions dashboard

**Approval Gates**
- Missions can pause and wait for human approval before sensitive operations
- Three autonomy levels: supervised (all operations require approval), restricted autonomous (only sensitive operations), full autonomous (no approval gates)
- `request_approval()`, `approve_mission()`, `reject_mission()` controller methods
- API endpoints: `POST /api/missions/{id}/request-approval`, `/approve`, `/reject`

### Changed

- `Greenie/hub/mission/storage.py`: `get_mission_stats()` now returns `validating`, `cancelled`, and `paused` counts (matches Slammer dashboard expectations)
- `Greenie/hub/mission/__init__.py`: Added sub-module documentation comments
- Greenie version bumped to 1.8.0

### Breaking Changes

- None

### Configuration

New environment variables:
- `GREENIE_MISSION_DB_PATH` – Mission control database path (default: data/missions.db)
- `GITHUB_WEBHOOK_SECRET` – GitHub webhook HMAC verification secret (set via `automation.set_webhook_secret()`)

---

## [1.7.0] - 2026-10-22

### Added

**Emergency Stop (Kill Switch)**
- `Greenie/hub/emergency_stop.py`: Global kill switch that pauses all workflow execution and triggers, cancels running Slinker jobs, sends critical notification via Poltergeist, and records audit events
- `Greenie/hub/api/emergency.py`: REST API – `GET /api/emergency/status`, `POST /api/emergency/stop`, `POST /api/emergency/resume`
- Can be reversed deliberately via resume endpoint

**Activity Timeline and Audit Trail**
- `Greenie/hub/activity_timeline.py`: Cross-service event history with SQLite persistence (WAL mode); records who initiated tasks, which services participated, which model was selected, which tools were invoked, which workstation executed work, approval gates, file modifications, failures, duration, cost, and outcome
- Separate security audit trail for compliance
- `Greenie/hub/api/timeline.py`: REST API – query timeline by correlation ID, workflow ID, task ID, agent ID, service, category; stats endpoint; event recording
- `Greenie/hub/api/audit/events`: Security audit trail query endpoint

**WORKSTATIONS.md Documentation**
- `docs/WORKSTATIONS.md`: Complete documentation of workstation model, templates, drivers, security, lifecycle operations, human access, quotas, integration, API endpoints, and limitations

**Slinker Pluggable Runner Interface**
- `Slinker/junie_adapter/runner_interface.py`: Abstract runner interface so Junie remains default but other runners (Ollama-backed, etc.) can be added; each runner declares capabilities, required binaries, and configuration; RunnerRegistry for discovery and selection; isolation levels (worktree, container, workstation)

**Alerting System**
- `Sneaker/sneaker/alerting.py`: Alert rules with deduplication, cooldown, severity levels, and per-rule enable/disable; default rules for service down, workflow failed, disk usage high, auth failures, budget exceeded; delivery via Poltergeist with graceful degradation

**Credential Rotation**
- `Greenie/hub/credential_rotation.py`: Rotation without data loss for service API keys, Hider encryption key (with re-encryption), and session secrets; records audit events; SQLite history
- `Greenie/hub/api/credentials.py`: REST API – `POST /api/credentials/rotate`, `GET /api/credentials/history`

**Final Implementation Report**
- `docs/FINAL_REPORT.md`: Complete 10-section report covering audit, changes by phase, architecture decisions, tests, integration verification, security, deployment, documentation, remaining work, and Definition of Done verification

### Changed

- Greenie version bumped to 1.7.0
- Greenie API: Registered 3 new route modules (emergency, timeline, credentials) – now 51 total
- ROADMAP: Phase 8 items checked off
- `docs/ECOSYSTEM_AUDIT.md`: Phase 8 marked complete

### Breaking Changes

- None

### Configuration

New environment variables:
- `GREENIE_TIMELINE_DB_PATH` – Activity timeline database path (default: data/timeline.db)
- `GREENIE_CREDENTIALS_DB_PATH` – Credential rotation history path (default: data/credentials.db)
- `SNEAKER_ALERTS_DB_PATH` – Alerting system database path (default: data/alerts.db)

---

## [1.6.0] - 2026-10-22

### Added

**Dashboard Strategy – Slammer as Single Dashboard**
- `docs/DASHBOARD_STRATEGY.md`: Decision document resolving Greenie/Slammer relationship
- Slammer is now the unified dashboard; Greenie operates as API-only backend
- Caddyfile updated with proxy routing: Slammer for static files, Greenie for `/api/*`, Sneaker for `/sneaker/*`

**Operational Dashboards**
- `Slammer/src/components/MetricsDashboard.tsx`: System metrics dashboard with CPU, memory, disk, uptime stats; metric series charts; alert display; time range selector (1h/6h/24h/7d)
- `Slammer/src/components/LogsView.tsx`: Aggregated log viewer with service/level/search filters, auto-scroll, level stats, and color-coded entries
- `Greenie/hub/api/system.py`: System stats API (`/api/system/stats`) and logs API (`/api/logs`, `/api/system/logs`) with filtering and search

**Workstations Live Terminal**
- `Slammer/src/components/Terminal.tsx`: WebSocket-based live terminal for workstation access with copy, clear, and connection status indicators

**MCP (Model Context Protocol) Support**
- `Greenie/hub/mcp/__init__.py`: Full MCP client implementation with SSE, HTTP, and stdio transport support; MCPManager for multi-server management; tool calling and resource access
- `Greenie/hub/api/mcp.py`: REST API for MCP server management – list, add, remove, connect/disconnect servers, list and call tools
- MCP server configuration persisted to `data/mcp_servers.json`

**Plugin Registry**
- `Greenie/hub/plugins/__init__.py`: Plugin registry with install/uninstall/enable/disable, configuration management, and type-based filtering (tool, resource, prompt, integration)
- `Greenie/hub/api/plugins.py`: REST API for plugin management – CRUD operations, enable/disable, config updates
- Plugin data persisted to `data/plugins.json`

**Slammer – Plugins & MCP Dashboard**
- `Slammer/src/components/Plugins.tsx`: Plugin management UI with install form, enable/disable toggle, uninstall, and MCP server management
- New "Metrics", "Logs", and "Plugins" tabs in Slammer navigation

**Greenie API Extensions**
- New route modules registered: `mcp`, `plugins`, `system`
- 20+ new API endpoints for MCP, plugins, system stats, and logs

### Changed

- Slammer App.tsx: Added 3 new pages (metrics, logs, plugins), updated navigation with flex-wrap
- Caddyfile: Updated proxy routing for unified dashboard architecture
- Greenie API: Registered mcp, plugins, and system route modules
- Greenie version bumped to 1.6.0
- Slammer version bumped to 1.4.0

### Configuration

New environment variables:
- `GREENIE_DATA_DIR` – Data directory for MCP config and plugin registry (default: data/)

---

## [1.5.0] - 2026-10-22

### Added

**Ecosystem-Wide Integration Tests**
- `tests/conftest.py`: Shared fixtures for service URLs and API keys
- `tests/integration/test_integration.py`: 15+ tests covering health checks, Bearer auth, Hider secrets, Shrewd chat, Poltergeist notifications, Gobber cache, Sneaker metrics, Greenie agents, and cross-service workflows
- `tests/run-all-tests.sh`: Test runner script with category filtering

**Security Tests**
- `tests/security/test_security.py`: 15+ tests for prompt injection defense, SSRF protection (private IP, cloud metadata, loopback), auth bypass (query params, empty Bearer, missing header, wrong header), XSS handling, rate limiting, and encryption at rest verification

**Performance Benchmarks**
- `tests/benchmarks/test_benchmarks.py`: API latency benchmarks (health, secrets, chat), throughput tests (Hider, Gobber), concurrent request handling, response size checks, and error response latency

**Agent Evaluation Suite**
- `tests/evaluation/test_evaluation.py`: 8-task evaluation suite (QA, code generation, summarization, math, safety refusal, JSON, translation, list generation) with scoring, latency tracking, and JSON report generation

**Failure Injection Tests**
- `tests/chaos/test_chaos.py`: Service crash handling, network failure resilience, data integrity under concurrent writes, malformed input (empty body, invalid JSON, SQL injection, oversized payload), and resource exhaustion stress tests

**Release Signing & Provenance**
- `scripts/release_sign.py`: HMAC-SHA256 signing for release artifacts with SLSA-style provenance generation
- `scripts/verify_release.py`: Release verification with checksum and signature validation
- Outputs: `checksums.txt`, `signatures.json`, `provenance.json`

**README Improvements**
- Expanded architecture diagram showing all 10 services
- Security model section
- Workflow Engine example
- Testing & Quality section with test categories
- Step-by-step tutorial: "Your First Agent"

### Changed

- Greenie version bumped to 1.5.0
- README expanded with architecture, security, testing, and tutorial sections
- ROADMAP: Phase 6 items checked off

---

## [1.4.0] - 2026-10-22

### Added

**Agent Workstations – Isolated Container Environments**
- `hub/workstation/models.py`: Data models for Workstation, WorkstationConfig, WorkstationAccess, and status enums
- `hub/workstation/driver.py`: Docker SDK-based container driver with create/start/stop/destroy, exec, logs, and health inspection
- `hub/workstation/storage.py`: SQLite persistence layer for workstation state with WAL mode
- `hub/workstation/lifecycle.py`: High-level lifecycle management (create, start, stop, destroy, health check)
- `hub/workstation/network_policy.py`: Default-deny network policy with IP validation, metadata endpoint blocking, and DNS allowlist
- `hub/workstation/access.py`: Terminal (TTY via WebSocket) and desktop (VNC/noVNC) access setup
- `hub/api/workstations.py`: Full REST API – 14 endpoints for CRUD, lifecycle, health, logs, exec, network policy, and access
- Graceful degradation when Docker is unavailable (simulation mode)
- Resource usage tracking: CPU percentage, memory usage, disk usage

**Workflow Engine – Workstation Step Type**
- New `workstation` step type in workflow executor
- Actions: create, start, exec, stop, destroy
- Automatic workstation discovery by workflow run ID
- Context variable interpolation in exec commands

**Slammer – Workstations Dashboard**
- `src/components/Workstations.tsx`: Workstations management page with stats, list, logs, and lifecycle actions
- Stats dashboard: total, running, stopped, errors, Docker availability
- Workstation cards with status, resource usage, tags, and action buttons
- Inline log viewer for running workstations
- New "Workstations" tab in dashboard navigation

### Changed

- Greenie version bumped to 1.4.0
- Slammer version bumped to 1.3.0
- Greenie API: new route module `workstations` registered in `hub/api/__init__.py`
- Workflow executor: new `WORKSTATION` step type added to `StepType` enum

### Configuration

New environment variables:
- `GREENIE_WORKSTATION_DB_PATH` – Workstation SQLite database path (default: Greenie/data/workstations.db)
- `WORKSTATION_GATEWAY_URL` – Gateway URL for terminal/desktop access (default: http://localhost:8080)
- `EVERSHADE_GREENIE_API_TOKEN` – API token for workstation access validation

---

## [1.3.0] - 2026-10-22

### Added

**Workflow Engine – Persistent Multi-Step Orchestration**
- `hub/workflow/models.py`: Data models for WorkflowDefinition, WorkflowStep, WorkflowRun, WorkflowTrigger, WorkflowApproval
- `hub/workflow/storage.py`: SQLite persistence layer with WAL mode for workflows, runs, and approvals
- `hub/workflow/executor.py`: Step-by-step workflow executor with approval gates, condition evaluation, and context passing
- `hub/workflow/triggers.py`: Schedule (cron), webhook (HMAC signature), and file change triggers
- `hub/api/workflows.py`: Full REST API – CRUD for definitions, execute runs, approve/deny, webhook handler, stats
- 5 step types: agent, service, approval, condition, notify
- 3 trigger types: schedule, webhook, file_change
- Approval gates with async pause/resume and configurable timeout
- Condition evaluation with dot-notation context keys (eq, ne, contains, gt, lt)
- Context passing between steps with automatic accumulation
- On-failure policy per step (stop/continue)
- Step dependencies for DAG-like execution

**Slammer – Visual Workflow Builder**
- `src/components/WorkflowBuilder.tsx`: Full workflow builder with stats, workflow list, create/edit form
- Step editing: add/remove steps of all 5 types with type-specific fields
- Trigger configuration: schedule (cron), webhook (secret), file watch (paths)
- Run history with step-by-step status display
- Workflow actions: run, enable/disable, edit, delete
- New "Workflows" tab in dashboard navigation

**Testing**
- `tests/test_workflow_engine.py`: 20+ integration tests covering models, storage, executor, triggers, API, and full lifecycle

### Changed

- Greenie version bumped to 1.3.0
- Slammer version bumped to 1.2.0
- Greenie API: new route module `workflows` registered in `hub/api/__init__.py`

### Configuration

New environment variables:
- `GREENIE_WORKFLOW_DB_PATH` – Workflow SQLite database path (default: Greenie/data/workflows.db)
- `WORKFLOW_FILE_POLL_INTERVAL` – File change trigger poll interval in seconds (default: 10)

---

## [1.2.0] - 2026-10-22

### Added

**Shrewd – Real LLM Provider Integration**
- `shrewd/providers.py`: Real provider classes for OpenAI, Anthropic, Google Gemini, and Ollama
- `shrewd/routing.py`: Model routing with cost tracking and privacy classification
- 16 models in registry (GPT-4o, Claude, Gemini, Llama, Gemma, Mistral, Phi)
- Cost estimation per request with per-model and per-provider summaries
- Privacy classification: public vs private (local-only) models
- Graceful fallback to simulated response when provider is not configured
- New endpoint: `GET /api/cost/summary` for usage tracking

**Poltergeist – Real Notification Delivery**
- `poltergeist/delivery.py`: Real delivery to Slack, Discord, Email (SMTP), Telegram, and generic webhooks
- `poltergeist/storage.py`: SQLite persistence for notifications and templates
- Retry logic with exponential backoff (configurable via `POLTERGEIST_MAX_RETRIES`)
- Delivery status tracking: pending → sent/failed with error messages
- New endpoint: `GET /api/notifications/{id}` for individual notification lookup

**Slammer – Real Dashboard**
- Service health polling every 10 seconds with online/offline/checking states
- Agents page: fetches and displays agents from Greenie API
- Runs page: displays recent runs with status, prompt, and timestamps
- Navigation bar with three pages: Services, Agents, Runs

**Speedy CLI – Full Command Set**
- `evershade install`: Docker Compose pull and build with profile selection
- `evershade start`: Start services via Docker Compose
- `evershade stop`: Stop services with optional volume removal
- `evershade logs`: View service logs (per-service, follow mode, tail)
- `evershade doctor`: Full diagnostics (Docker, Compose, services, config, env vars)
- `evershade backup create`: Archive data directories and configs to tar.gz
- `evershade backup restore`: Restore from backup archive

**Greenie → Gobber Migration**
- `hub/gobber_client.py`: Async HTTP client for Gobber storage service
- 15 hybrid store functions in `core.py` (cache, feature flags, webhooks, analytics, RBAC)
- Gobber-first strategy: persistent storage when available, local fallback when not
- Greenie operates independently when Gobber is unavailable

### Changed

- Shrewd version bumped to 1.1.0
- Poltergeist version bumped to 1.1.0
- Speedy CLI version bumped to 1.1.0
- Shrewd `ChatResponse` model now includes `cost_usd` field
- Poltergeist notifications persisted in SQLite instead of in-memory

### Configuration

New environment variables:
- `OPENAI_API_KEY`, `OPENAI_BASE_URL` – OpenAI provider
- `ANTHROPIC_API_KEY`, `ANTHROPIC_BASE_URL` – Anthropic provider
- `GOOGLE_API_KEY`, `GOOGLE_BASE_URL` – Google Gemini provider
- `OLLAMA_BASE_URL` – Ollama provider (default: http://localhost:11434)
- `SLACK_WEBHOOK_URL` – Slack notifications
- `DISCORD_WEBHOOK_URL` – Discord notifications
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_TLS` – Email notifications
- `TELEGRAM_BOT_TOKEN` – Telegram notifications
- `POLTERGEIST_MAX_RETRIES` – Retry count for failed deliveries (default: 3)
- `SHREWD_REQUEST_TIMEOUT` – LLM request timeout in seconds (default: 60)
- `POLTERGEIST_REQUEST_TIMEOUT` – Notification delivery timeout (default: 30)
- `SHREWD_DEFAULT_MODEL` – Default model when none specified (default: llama3)

---

## [1.1.0] - 2026-10-22

### Security
- **BREAKING:** All Python services (Hider, Gobber, Sneaker, Poltergeist, Shrewd) now require `Authorization: Bearer <key>` header – query parameter `x_key` auth is no longer supported
- **BREAKING:** Trapper now requires `Authorization: Bearer <key>` header – query parameter `api-key` auth is no longer supported
- Hider: AES-256-GCM encryption for all secrets at rest (requires `ENCRYPTION_KEY` env var)
- Hider: SQLite persistence for secrets and configs (data survives restarts)
- Trapper: SSRF protection – blocks requests to private IPs, loopback, link-local, and cloud metadata endpoints
- Container hardening: read-only filesystem (`read_only: true`) added to all services
- Container hardening: tmpfs mounts for writable directories (/tmp, /app/data, /app/logs)
- All services use constant-time comparison (`hmac.compare_digest`) for API key validation

### Changed
- Greenie health checks: removed hardcoded `localhost` – uses Docker service names (Slinker, Trapper-api)
- Speedy CLI: uses `EVERSHADE_` prefixed env vars with legacy fallback; sends Bearer auth headers
- Speedy CLI: renamed "clairvoya" service to "shrewd"
- Slammer: service URLs configurable via `VITE_*_URL` env vars; renamed "Clairvoya" to "Shrewd"
- Slammer: supports relative URLs when behind reverse proxy via `VITE_BASE_URL`

### Added
- `Hider/hider/encryption.py` – AES-256-GCM encryption utilities
- `Hider/hider/storage.py` – SQLite storage layer for secrets and configs
- `Trapper/src/utils/ssrfProtection.ts` – SSRF protection module

## [1.0.0] - 2026-10-22

### Added
- Complete ecosystem audit document (`docs/ECOSYSTEM_AUDIT.md`)
- Architecture documentation (`docs/ARCHITECTURE.md`)
- Version manifest (`version-manifest.json`)
- Standardized `.env.example` with `EVERSHADE_` prefix naming
- Docker Compose profiles: `minimal`, `standard`, `full`, `ollama`, `proxy`, `dev`
- Internal Docker network for service isolation
- Container hardening: capability dropping, no-new-privileges
- Caddy reverse proxy profile for TLS termination
- Configuration reference (`docs/CONFIGURATION.md`)
- Security model document (`docs/SECURITY.md`)
- Deployment guide (`docs/DEPLOYMENT.md`)
- Backup and restore guide (`docs/BACKUP_RESTORE.md`)
- Testing guide (`docs/TESTING.md`)
- Resource requirements (`docs/RESOURCES.md`)
- Development guide (`docs/DEVELOPMENT.md`)
- Release notes (`docs/RELEASES.md`)
- Service catalog (`docs/SERVICE_CATALOG.md`)
- Named volumes for all persistent data (Greenie, Sneaker, Hider, Poltergeist)
- DB_PATH environment variable for Sneaker, Hider, Poltergeist persistence

### Changed
- Environment variable naming: `EVERSHADE_<SERVICE>_<SETTING>` (legacy names still supported)
- Docker Compose: only Greenie exposed on host by default
- Docker Compose: all services on internal network
- Docker Compose: proper dependency ordering with health checks

### Security
- Container hardening applied to all services
- Network isolation: internal services not reachable from host
- Bind address configurable via `EVERSHADE_BIND_ADDRESS`
