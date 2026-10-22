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

## Planned Service Decisions

| Service | Decision | Rationale |
|---------|----------|-----------|
| **Mnemos** | **DROP** | Gobber already covers semantic memory. Extend Gobber instead. |
| **Bridge** | **EVALUATE** | Only if new integration types beyond webhooks are needed. |
| **Courier** | **EVALUATE** | Only if persistent object storage beyond 50MB is required. |
