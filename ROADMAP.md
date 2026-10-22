# Evershade Roadmap

**Version:** 1.1.0
**Last Updated:** 2026-10-22

---

## Phase 1 — Foundations (Current)

- [x] Complete ecosystem audit
- [x] Architecture documentation
- [x] Version manifest
- [x] Standardized configuration (.env.example)
- [x] Docker Compose profiles and hardening
- [x] Core documentation (SECURITY, DEPLOYMENT, CONFIGURATION, etc.)

---

## Phase 2 — Security & Persistence ✓

- [x] Hider: Implement AES-256-GCM encryption for secrets
- [x] Hider: SQLite persistence for secrets and configs
- [x] Migrate all services to Bearer token auth (Hider, Gobber, Sneaker, Poltergeist, Shrewd, Trapper)
- [x] Trapper: SSRF protection (private IP blocking, metadata endpoint blocking)
- [x] Container hardening: read-only filesystem, capability dropping, tmpfs
- [x] Remove hardcoded localhost references (Greenie, Speedy, Slammer)
- [ ] Sneaker: SQLite persistence for metrics, traces, logs
- [ ] Poltergeist: SQLite persistence for notifications
- [ ] Emergency stop implementation in Greenie
- [ ] CSRF protection for web UI sessions
- [ ] Rate limiting on authentication endpoints

---

## Phase 3 — Real Implementation ✓

- [x] Shrewd: Real LLM provider integration (OpenAI, Anthropic, Google, Ollama)
- [x] Shrewd: Model routing with cost tracking and privacy classification
- [x] Poltergeist: Real notification delivery (Slack, Discord, email, Telegram)
- [x] Poltergeist: SQLite persistence for notifications
- [x] Slammer: Real dashboard with Greenie API integration
- [x] Speedy CLI: Full command set (install, start, stop, doctor, logs, backup, restore)
- [x] Greenie → Gobber migration: Hybrid stores with Gobber-first, local fallback

---

## Phase 4 — Workflow Engine ✓

- [x] Persistent workflow definitions
- [x] Workflow triggers (schedule, webhook, file changes)
- [x] Visual workflow builder in dashboard
- [x] Approval gates with human-in-the-loop
- [x] Workflow execution history and audit trail
- [x] End-to-end workflow integration test

---

## Phase 5 — Agent Workstations ✓

- [x] Container driver for isolated agent environments
- [x] Workstation lifecycle management (create, start, stop, destroy)
- [x] Network policy enforcement (default-deny)
- [x] Human access: live terminal and desktop via gateway
- [x] Integration with Slinker and workflow engine

---

## Phase 6 — Quality & Release ✓

- [x] Ecosystem-wide integration tests
- [x] Security tests (prompt injection, SSRF, auth bypass)
- [x] Performance benchmarks and baselines
- [x] Agent evaluation suite
- [x] Failure injection tests
- [x] Release signing and provenance
- [x] Complete README with tutorial

---

## Phase 7 — UI and Extensibility ✓

- [x] Resolve Greenie/Slammer relationship (Slammer as single dashboard)
- [x] Integrate workflow builder (already in Phase 4)
- [x] Improve operational dashboards (Metrics, Logs pages)
- [x] Add Workstations live terminal (WebSocket-based)
- [x] Add MCP and plugin support (MCP server, plugin registry)
- [x] Ensure every visible control connects to real functionality

---

## Phase 8 — Quality and Release ✓

- [x] Emergency stop: Global kill switch (pause workflows, cancel jobs, notify)
- [x] Activity Timeline: Cross-service event history with audit trail
- [x] WORKSTATIONS.md: Complete workstation documentation
- [x] Slinker runner interface: Pluggable runner abstraction (Junie default, extensible)
- [x] Alerting system: Alert rules, deduplication, Poltergeist delivery
- [x] Credential rotation: API key, encryption key, session secret rotation
- [x] Final Implementation Report: Complete audit of all 8 phases
- [x] Documentation: Updated ROADMAP, CHANGELOG, version-manifest, .env.example

---

## Phase 9 — Mission Control System ✓

- [x] Mission data models: Mission, Milestone, Feature, ValidationContract, ValidationResult, Checkpoint
- [x] SQLite persistence: WAL mode for missions, checkpoints, and validation results
- [x] Mission lifecycle controller: Create, plan, execute, validate, complete, cancel, pause, resume
- [x] Extended workflow engine: New StepType values (PLANNER, WORKER, VALIDATOR, MILESTONE), parallel execution
- [x] Planning and repository intelligence: LLM-based planning via Shrewd, repo analysis
- [x] Automated code review: Deterministic checks (test, lint, type), diff-based security review
- [x] Automation engine: GitHub webhooks, schedule triggers, idempotency, rate limiting
- [x] Secret redaction: Pattern-based redaction for logs and model context
- [x] Approval gates: Human approval for sensitive operations, three autonomy levels
- [x] Slammer mission dashboard: List view, create form, detail view with milestone progress
- [x] Mission analytics: Success/failure rates, duration tracking, validation summaries
- [x] SSE log streaming: Real-time execution logs
- [x] Fix-revalidate cycle: Automatic fix features from validation failures
- [x] End-to-end smoke test: Full mission lifecycle test without external dependencies
- [x] Cross-service integration tests: Mission API health, lifecycle, planning, validation, analytics
- [x] 147 tests: Unit tests for models, automation, secret redaction, analytics, logs, fix-revalidate; integration tests for lifecycle, approval gates, smoke tests

---

## Phase 10 — Security, Embeddings, and OTLP ✓

- [x] CSRF protection for web UI: Token generation, validation, middleware, excluded paths
- [x] Rate limiting on auth endpoints: Already implemented in Phase 2 (core.py)
- [x] Gobber vector embeddings and semantic search: API endpoints for generate, search, batch, stats
- [x] Sneaker OTLP export: OTLP JSON endpoints for traces/metrics/logs, external forwarding
- [x] 45 tests: 25 CSRF, 12 OTLP, 8 Gobber embeddings

### Deferred (requires external infrastructure)

- [ ] User authentication and session management (requires substantial infra)
- [ ] Real Junie CLI integration for code execution (requires CLI installation)
- [ ] Clean-clone installation verification (requires fresh environment)
- [ ] Ubuntu VM + remote access end-to-end test (requires VM)
- [ ] Reboot persistence verification (requires reboot)

## Phase 11 — Agent Harness ✓

- [x] Spec Mode: Read-only research phase before implementation, persistent spec store, approval gate
- [x] Custom Droids: Specialized subagents with own prompts/models/tools, built-in droids (worker, explorer, reviewer, validator)
- [x] Skills System: Reusable SKILL.md workflows, trigger-based auto-discovery, manual invocation
- [x] Hooks System: Event-driven lifecycle hooks (PreToolUse, PostToolUse, MissionStart, etc.), script and webhook support
- [x] Environments: Reusable sandbox definitions with health checks
- [x] 30+ API endpoints for all five components
- [x] 30 unit tests covering all components

## Planned Service Decisions

| Service | Decision | Rationale |
|---------|----------|-----------|
| **Mnemos** | **DROP** | Gobber already covers semantic memory. Extend Gobber instead. |
| **Bridge** | **EVALUATE** | Only if new integration types beyond webhooks are needed. |
| **Courier** | **EVALUATE** | Only if persistent object storage beyond 50MB is required. |
