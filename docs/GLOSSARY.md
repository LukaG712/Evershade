# Evershade Glossary

**Version:** 1.0.0
**Last Updated:** 2026-10-23

A complete glossary of terms used throughout Evershade documentation and codebase.

---

## A

### Agent
An AI-powered worker that can perform tasks like writing code, answering questions, or scraping the web. Agents are configured with a name, runner (e.g., Junie), and guidelines that shape their behavior.

### Agent Harness
A framework for advanced agent development, including Spec Mode, custom droids, skills, and event-driven hooks. It provides reusable workflows and specialized subagents.

### API Key
A secret string used for service-to-service authentication. Each Evershade service has its own API key. Keys are passed via the `Authorization: Bearer` header.

### Approval Gate
A checkpoint in a mission or workflow where execution pauses for human approval before proceeding. Used for sensitive operations like file deletion or credential access.

---

## C

### Caddy
A reverse proxy server used in Evershade's `proxy` profile. Provides automatic TLS termination and routes traffic to Greenie and Slammer.

### Container Hardening
Security measures applied to Docker containers: dropped capabilities, read-only filesystems, no-new-privileges, resource limits, and network isolation.

### CSRF (Cross-Site Request Forgery)
A web security vulnerability. Evershade protects against CSRF using the double-submit cookie pattern with HMAC-signed tokens for cookie-authenticated sessions.

---

## D

### Desktop Mode
The default deployment mode (`EVERSHADE_MODE=desktop`). Services bind to loopback (`127.0.0.1`) only, accessible from the local machine.

### Docker Compose Profiles
Named groups of services that can be started together. Profiles include `minimal`, `standard`, `full`, `ollama`, `proxy`, and `dev`.

### Droid
A specialized subagent with its own system prompt, model preference, and tool policy. Built-in droids: `worker` (implementation), `explorer` (research), `reviewer` (code review), `validator` (validation). Custom droids are defined in Markdown files.

---

## E

### Evershade
The name of the platform, inspired by Evershade Valley from Luigi's Mansion: Dark Moon. A self-hosted AI agent platform built as a collection of specialized microservices.

### Evershade Valley
The fictional setting from Luigi's Mansion: Dark Moon. The root repository and database are named after it.

---

## F

### Feature
A unit of work within a mission milestone. Features are executed by workers and validated independently. Multiple features can run in parallel within a milestone.

### Fix-Revalidate Cycle
An automated process where validation failures trigger the creation of fix features. The system attempts to fix issues automatically, then re-validates. Configurable max retries and cooldown periods.

---

## G

### Gobber
The persistent storage service (port 8085). Handles SQLite databases, knowledge graphs, Obsidian vault integration, semantic search, webhooks, analytics, feature flags, and RBAC. Named after a blob-like absorbing ghost from Luigi's Mansion.

### Greenie
The central orchestrator service (port 8080). All requests flow through Greenie, which routes them to the appropriate microservice. Manages agents, sessions, pipelines, workflows, missions, and workstations. Named after small green ghosts from Luigi's Mansion.

---

## H

### Hider
The secrets management service (port 8087). Encrypts API keys and sensitive data at rest using AES-256-GCM. Provides versioned configuration management. Named after a hiding ghost from Luigi's Mansion.

### Hook
An event-driven lifecycle callback for mission events. Supported events: `PreToolUse`, `PostToolUse`, `SessionStart`, `SessionEnd`, `MissionStart`, `MissionEnd`, `MilestoneComplete`, `ValidationFail`. Hook types: script (local execution) and webhook (HTTP POST).

---

## I

### Idempotency
The property that an operation can be safely retried without changing the result beyond the initial application. Evershade supports idempotency keys via the `X-Idempotency-Key` header for retryable operations.

### Internal Network
The Docker network (`evershade_internal`) where all backend services communicate. Services on this network are not directly accessible from the host.

---

## K

### Knowledge Graph
A structured representation of information stored in Gobber. Supports notes, links between notes, and semantic search via vector embeddings. Integrates with Obsidian vaults.

---

## L

### LLM (Large Language Model)
An AI model that can understand and generate human language. Evershade supports multiple LLM providers through the Shrewd abstraction layer.

---

## M

### MCP (Model Context Protocol)
A protocol for extending agent capabilities with external tools. Greenie supports MCP servers via `stdio` and `sse` transports.

### Milestone
A phase within a mission. Each milestone contains one or more features that can be executed in parallel. Milestones represent logical stages of a project.

### Mission
A high-level project broken into milestones, features, and validation steps. Missions include automated planning, execution, validation, and fix-revalidate cycles. Think of it as an AI-powered software engineering sprint.

### Mission Control
The factory-inspired orchestration system for complex AI-driven development workflows. Provides mission lifecycle management, automated planning, code review, and analytics.

---

## N

### Network Policy
Rules that control network access for workstations. Default-deny policy blocks private addresses, LAN, host, cloud metadata endpoints, and internal services. Outbound internet access is configurable per template.

---

## O

### Obsidian Vault
A directory of Markdown notes that Gobber can index for semantic search. Evershade integrates with Obsidian to provide AI-powered note search and knowledge graph features.

### Ollama
A local LLM inference engine. Evershade supports Ollama for running AI models on-premise without cloud API costs.

### OTLP (OpenTelemetry Protocol)
A standard protocol for sending traces, metrics, and logs to external monitoring systems. Sneaker supports OTLP export for integration with any OTLP collector.

---

## P

### Pipeline
A chain of cross-service steps executed in sequence. For example: scrape a page with Trapper → summarize with Greenie → save to Gobber. Pipelines enable complex multi-service workflows.

### Poltergeist
The notification service (port 8088). Sends alerts to Slack, Discord, email, and Telegram with templated messages and async delivery. Named after an ancient disturbance ghost from Luigi's Mansion.

### Prompt Injection
A security attack where untrusted content is treated as AI instructions. Evershade defends against this by treating all external content as data, not instructions.

### Proxy Profile
The `proxy` Docker Compose profile that adds Caddy reverse proxy with automatic TLS termination. Required for secure internet-facing deployments.

---

## R

### Rate Limiting
Protection against abuse by limiting request frequency. Evershade applies per-IP and per-API-key rate limits with sliding window algorithm. Default: 60 requests/minute.

### RBAC (Role-Based Access Control)
An authorization model where access is granted based on user roles. Evershade supports admin, user, and viewer roles.

### Redis
An in-memory data store used for job queues (Trapper crawling), caching, and inter-service communication. Runs on the internal Docker network.

---

## S

### Server Mode
Deployment mode (`EVERSHADE_MODE=server`) where services bind to all interfaces (`0.0.0.0`). Requires strong, unique API keys – refuses to start with defaults.

### Shrewd
The LLM abstraction layer (port 8089). Provides a unified interface for OpenAI, Anthropic, Google AI, and Ollama. Handles model routing, cost tracking, and fallback configuration. Named after a possessor ghost from Luigi's Mansion.

### Skill
A reusable `SKILL.md` workflow that can be auto-discovered and invoked by agents. Skills are matched to tasks based on trigger phrases. Stored in `.evershade/skills/` (project) or `~/.evershade/skills/` (personal).

### Slinker
The code execution engine (port 8000). Runs AI agents against codebases in isolated Git worktrees using the Junie CLI. Handles code generation, file modifications, and refactoring. Named after wall-crawling stealth ghosts from Luigi's Mansion.

### Slammer
The React-based web dashboard (port 5173). The primary visual interface for managing agents, runs, missions, workflows, workstations, metrics, and logs. Named after a heavy-hitting ground slammer from Luigi's Mansion.

### Sneaker
The observability service (port 8086). Collects metrics, distributed traces, and logs from all services. Provides alerting with deduplication and OTLP export. Named after a quiet sneaking ghost from Luigi's Mansion.

### Spec Mode
A research-first workflow: the agent analyzes a repository, proposes a concrete implementation plan, and requires human approval before any code changes. Part of the Agent Harness system.

### Speedy
The command-line interface (`evershade` command). Provides terminal-based management of services, agents, tasks, diagnostics, and backups. Built with Python, Click, and Rich. Named after a fast zooming ghost from Luigi's Mansion.

### SSRF (Server-Side Request Forgery)
An attack where a server is tricked into making requests to unintended destinations. Trapper protects against SSRF with private IP blocking, cloud metadata endpoint blocking, and redirect abuse prevention.

---

## T

### Trapper
The web scraping service (port 3000). Uses Playwright for headless browser automation. Supports single-page scraping, deep crawling, site mapping, and structured data extraction. Named after trap-setting ghosts from Luigi's Mansion.

---

## W

### WAL (Write-Ahead Logging)
A SQLite journaling mode that improves concurrent read performance and crash safety. All Evershade services use SQLite in WAL mode.

### Webhook
An HTTP callback that sends event notifications to external URLs. Gobber manages webhook definitions with HMAC signature verification.

### Workflow
An automated sequence of steps with triggers, conditions, and optional approval gates. Workflows can schedule recurring tasks, chain service calls, and require human approval at key points.

### Workstation
An isolated container-based environment for agent execution. Each workstation has its own filesystem, shell, installed tools, and network policy. Supports live terminal access and optional desktop interface.

---

## Related Documentation

- **[README](../README.md)** – Main documentation with inline glossary
- **[Architecture](ARCHITECTURE.md)** – Detailed service descriptions
- **[Service Catalog](SERVICE_CATALOG.md)** – Complete API endpoint reference
- **[Advanced Guide](ADVANCED.md)** – Expert-level deep dives
