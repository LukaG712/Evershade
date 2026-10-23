# Evershade v1.14.1 — GUI Installer Fix

**Release Date:** October 23, 2026

This patch release fixes a critical crash in the GUI installers for both Linux and Windows.

---

## What Is Evershade?

Evershade is a self-hosted AI agent platform that lets you create, manage, and run AI-powered agents on your own hardware. Think of it as your personal AI workforce that lives on your computer or server.

- **You own everything.** Your data, your agents, your conversations — nothing leaves your machine unless you explicitly connect an external AI provider.
- **It runs in Docker.** No complex setup. If you can run Docker, you can run Evershade.
- **Agents do real work.** Write code, scrape websites, search knowledge bases, send notifications, and chain tasks together.
- **Mission Control orchestrates complex projects.** Break large tasks into milestones, let AI plan and execute, then validate automatically.
- **It's modular.** Use just the core services or add observability, notifications, local LLMs — you choose what you need.

---

## Services Included

This release includes **10 microservices**, each maintained as a separate repository and included as a git submodule:

| Service | Version | Description |
|---------|---------|-------------|
| **Greenie** | 1.8.0 | Central API backend with auth, CSRF, rate limiting, retry, idempotency, secret redaction, workflow engine, workstations, and hybrid stores |
| **Slinker** | 1.2.0 | Code execution with pluggable runner interface (Junie default, extensible to Ollama and other runners) |
| **Trapper** | 1.1.0 | Web scraping with crawl, extract, map, interact, and search capabilities |
| **Gobber** | 1.1.0 | Storage & search with hybrid semantic+keyword search, batch embeddings, user/project scoping, and link resolution |
| **Sneaker** | 1.2.0 | Observability & alerting with OTLP support, secret redaction, alerting with deduplication and cooldown |
| **Hider** | 1.1.0 | Encrypted secrets management with AES-256-GCM encryption at rest in SQLite |
| **Poltergeist** | 1.2.0 | Notifications for Slack, Discord, Email, Telegram, and Webhooks with SQLite persistence |
| **Shrewd** | 1.2.0 | LLM providers: OpenAI, Anthropic, Google, Ollama with cost tracking and privacy classification |
| **Slammer** | 1.4.0 | Web dashboard for services, agents, runs, workflows, workstations, metrics, logs, and plugins/MCP management |
| **Speedy** | 1.2.0 | CLI tool for install, start, stop, restart, logs, doctor, backup/restore, and config validation |

---

## Installation

### Quick Start (CLI)

```bash
git clone https://github.com/LukaG712/Evershade.git && cd Evershade

# Linux/macOS
./install.sh --profile minimal
cp .env.example .env
./start.sh --profile minimal

# Windows PowerShell
.\install.ps1 -Profile minimal
Copy-Item .env.example .env
.\start.ps1 -Profile minimal
```

### GUI Installers

Evershade provides visual, step-by-step GUI installers for both **Linux** and **Windows**:

#### Linux
```bash
bash run-install-gui.sh
# Or: sudo python3 install-gui.py
```

#### Windows
```batch
run-install-gui.bat
:: Or: python install-gui-win.py
```

Both wizards guide you through 9 steps: Welcome, System Check, Installation Options (with custom service selection), Docker setup, Clone & Install, Configure, System Integration, Start Services, and Complete.

### Installation Profiles

| Profile | Services | Use Case |
|---------|----------|----------|
| **Minimal** | Greenie, Slinker, Trapper, Gobber | Core API + code, scraping, search |
| **Standard** | + Sneaker, Hider, Poltergeist, Shrewd | Full backend with observability, secrets, notifications, LLM |
| **Full** | + Slammer, Speedy | Everything including web dashboard and CLI |
| **Custom** | User-selected | Pick individual services via checkboxes |

---

## Infrastructure

The platform uses the following infrastructure services:

- **Redis 8 Alpine** — Message queue and caching (required)
- **Ollama** — Local LLM inference (optional)
- **Caddy 2 Alpine** — Reverse proxy and HTTPS (optional)

---

## Key Features

### Mission Control System
A factory-inspired mission control system for AI-powered project orchestration:
- Full mission lifecycle: create → plan → execute → validate → complete
- Milestone-based task breakdown with parallel worker execution
- Automated planning via LLM with heuristic fallback
- Repository intelligence for context-aware planning
- Automated code review with security and correctness checks
- Fix-revalidate cycle for automatic issue resolution
- Server-Sent Events (SSE) for real-time execution logs
- Mission analytics: success rates, durations, model usage, validation findings
- Approval gates for human-in-the-loop control
- Checkpoint recovery for fault tolerance

### Agent Harness
Factory-inspired agent harness capabilities:
- **Spec Mode**: Read-only research phase before implementation
- **Custom Droids**: Specialized subagents with own prompts, models, and tool policies
- **Skills System**: Reusable SKILL.md workflows with trigger-based auto-discovery
- **Hooks System**: Event-driven lifecycle hooks for mission events
- **Environments**: Reusable sandbox definitions with setup commands and health checks

### Security
- Bearer token authentication (query parameter auth removed)
- CSRF protection with HMAC-signed tokens
- AES-256-GCM encryption for secrets at rest
- Secret redaction in logs and model context
- Rate limiting and idempotency

---

## Breaking Changes

- All services require `Authorization: Bearer` header — query parameter auth removed
- Hider requires `ENCRYPTION_KEY` environment variable for AES-256-GCM encryption
- Hider secrets are now encrypted at rest in SQLite — migration required from in-memory data
- Slammer is the single dashboard — Greenie operates as API-only backend

---

## Documentation

Full documentation is available in the `website/` directory and includes:
- Getting started guide
- Architecture overview
- Security best practices
- Configuration reference
- Deployment guide
- API reference
- Individual service documentation
- FAQ and glossary

---

## System Requirements

- **Docker** and **Docker Compose** (minimum compose version 2.20)
- **Git** for cloning repositories
- **Python 3.6+** for GUI installers (Tkinter included by default)
- **Windows**: Docker Desktop required
- **Linux**: Docker Engine + Compose (auto-installed by GUI installer on Ubuntu)

---

## Scripts

| Script | Platform | Purpose |
|--------|----------|---------|
| `install.sh` | Linux/macOS | CLI installer |
| `install.ps1` | Windows | CLI installer |
| `install-ubuntu.sh` | Ubuntu | Ubuntu-specific installer |
| `install-gui.py` | Linux | GUI installer |
| `install-gui-win.py` | Windows | GUI installer |
| `run-install-gui.sh` | Linux | GUI launcher script |
| `run-install-gui.bat` | Windows | GUI launcher script |
| `start.sh` / `start.ps1` | All | Start services |
| `stop.sh` / `stop.ps1` | All | Stop services |
| `update.sh` / `update.ps1` / `update-ubuntu.sh` | All | Update installation |

---

## License

Evershade is released under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## Support & Contributing

- Report issues: [GitHub Issues](https://github.com/LukaG712/Evershade/issues)
- Contributing guide: [CONTRIBUTING.md](CONTRIBUTING.md)
- Roadmap: [ROADMAP.md](ROADMAP.md)
- Changelog: [CHANGELOG.md](CHANGELOG.md)

---

**Happy self-hosting!** 🏚️
