# Evershade

**A self-hosted AI agent platform built as a collection of specialized microservices.**

[![Version](https://img.shields.io/badge/Version-1.12.0-brightgreen.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Required-blue.svg)](https://docker.com)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-React%20Dashboard-blue.svg)](https://www.typescriptlang.org)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

---

## What Is Evershade

Evershade is a **self-hosted AI agent platform** that lets you create, manage, and run AI-powered agents on your own hardware. Think of it as your personal AI workforce that lives on your computer or server.

- **You own everything.** Your data, your agents, your conversations – nothing leaves your machine unless you explicitly connect an external AI provider.
- **It runs in Docker.** No complex setup. If you can run Docker, you can run Evershade.
- **Agents do real work.** Write code, scrape websites, search knowledge bases, send notifications, and chain tasks together.
- **Mission Control orchestrates complex projects.** Break large tasks into milestones, let AI plan and execute, then validate automatically.
- **It's modular.** Use just the core services or add observability, notifications, local LLMs – you choose what you need.

---

## Quick Start

### Prerequisites

- **Docker** and **Docker Compose** installed
- **[Junie CLI](https://junie.jetbrains.com)** (optional, for code agents)

### Get Started

```bash
git clone https://github.com/LukaG712/Evershade.git && cd Evershade

# Install service repositories (required)
./install.sh --profile minimal    # Linux/macOS
# .\install.ps1 -Profile minimal  # Windows PowerShell

cp .env.example .env
# Edit .env with your API keys

# Start services
./start.sh --profile minimal      # Linux/macOS
# .\start.ps1 -Profile minimal    # Windows PowerShell
```

The API will be available at **http://localhost:8080**.

> **Note:** Service repositories are maintained separately and must be cloned by the install script.

### Installation Profiles

| Profile | Services | Command |
|---------|----------|---------|
| **Minimal** | Core only (4 services) | `docker compose --profile minimal up -d` |
| **Standard** | All services (8 services) | `docker compose --profile standard up -d` |
| **Full** | + Slammer Dashboard | `docker compose --profile full up -d` |
| **+ Ollama** | Local LLM support | `docker compose --profile standard --profile ollama up -d` |
| **+ Proxy** | Caddy reverse proxy with TLS | `docker compose --profile standard --profile proxy up -d` |

---

## Your First Agent

1. **Install and start** using the Quick Start commands above
2. **Open** http://localhost:8080 in your browser
3. **Create an agent:** Dashboard → Agents → Create Agent (e.g., name: `researcher`, runner: `junie`)
4. **Run a task:** Go to Chat, select your agent, and type a prompt
5. **Explore more:** Workflows, Slammer Dashboard (`:5173`), Speedy CLI (`evershade agents list`)

---

## Services at a Glance

| Service | Port | Role |
|---------|------|------|
| **Greenie** | `8080` | Central orchestrator & API backend |
| **Slinker** | `8000` | Code execution engine |
| **Trapper** | `3000` | Web scraping & crawling |
| **Gobber** | `8085` | Persistent storage & knowledge graph |
| **Sneaker** | `8086` | Observability (metrics, traces, logs) |
| **Hider** | `8087` | Encrypted secrets management |
| **Poltergeist** | `8088` | Notifications (Slack, Discord, email, Telegram) |
| **Shrewd** | `8089` | LLM provider abstraction |
| **Slammer** | `5173` | React web dashboard |
| **Speedy** | – | CLI tool (`evershade` command) |

> **🌐 Website:** Visit the [Evershade website](website/index.html) for interactive documentation.

---

## Web Interfaces

| Interface | URL |
|-----------|-----|
| **Slammer Dashboard** | `http://localhost:5173` |
| **Greenie API Docs** | `http://localhost:8080/docs` |
| **Slinker API Docs** | `http://localhost:8000/docs` |
| **Trapper API Docs** | `http://localhost:3000/docs` |

---

## Documentation

### Getting Started

| Document | Description |
|----------|-------------|
| [Getting Started Guide](docs/GETTING_STARTED.md) | Detailed walkthrough for first-time users |
| [FAQ](docs/FAQ.md) | Answers to common questions |
| [Glossary](docs/GLOSSARY.md) | Key terms explained |

### Core Reference

| Document | Description |
|----------|-------------|
| [Architecture](docs/ARCHITECTURE.md) | System architecture, service boundaries, data flow |
| [Service Catalog](docs/SERVICE_CATALOG.md) | Every API endpoint for every service |
| [Mission Control](docs/MISSION_CONTROL.md) | Orchestrated AI missions with milestones |
| [Agent Harness](docs/AGENT_HARNESS.md) | Spec mode, droids, skills, and hooks |
| [Workstations](docs/WORKSTATIONS.md) | Isolated agent environments |

### Configuration & Deployment

| Document | Description |
|----------|-------------|
| [Configuration](docs/CONFIGURATION.md) | Complete environment variable reference |
| [Deployment](docs/DEPLOYMENT.md) | Server mode, Proxmox, auto-start, firewall |
| [Security](docs/SECURITY.md) | Security model and best practices |

### Operations

| Document | Description |
|----------|-------------|
| [Backup & Restore](docs/BACKUP_RESTORE.md) | Data protection strategies |
| [Testing](docs/TESTING.md) | Test suite and quality gates |
| [Resource Requirements](docs/RESOURCES.md) | CPU, RAM, disk requirements |
| [Releases](docs/RELEASES.md) | Version compatibility and upgrade paths |

### Development

| Document | Description |
|----------|-------------|
| [Development Guide](docs/DEVELOPMENT.md) | Local setup, debugging, code style |
| [Contributing](CONTRIBUTING.md) | How to report bugs and submit PRs |

### Advanced

| Document | Description |
|----------|-------------|
| [Advanced Guide](docs/ADVANCED.md) | Internals, performance tuning, power-user patterns |

---

## Naming Theme

All services are named after ghosts from the **Luigi's Mansion** series. The repository is named **Evershade** after *Evershade Valley* from Luigi's Mansion: Dark Moon.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

> **Disclaimer:** This project is a fan-made, independent software project. It is not affiliated with, endorsed by, or in any way connected to Nintendo, Next Level Games, or any of their subsidiaries. All Luigi's Mansion trademarks and character names are property of their respective owners. Service names are used purely for thematic inspiration.
