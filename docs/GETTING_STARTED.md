# Evershade Getting Started Guide

**Version:** 1.0.0
**Last Updated:** 2026-10-23
**Audience:** First-time users who want a detailed, hand-holding walkthrough.

---

## Table of Contents

- [Before You Begin](#before-you-begin)
- [Step 1: Install Prerequisites](#step-1-install-prerequisites)
- [Step 2: Clone and Install Evershade](#step-2-clone-and-install-evershade)
- [Step 3: Configure Your Environment](#step-3-configure-your-environment)
- [Step 4: Start Evershade](#step-4-start-evershade)
- [Step 5: Verify Everything Works](#step-5-verify-everything-works)
- [Step 6: Create Your First Agent](#step-6-create-your-first-agent)
- [Step 7: Run Your First Task](#step-7-run-your-first-task)
- [Step 8: Explore the Dashboard](#step-8-explore-the-dashboard)
- [Next Steps](#next-steps)
- [Troubleshooting](#troubleshooting)

---

## Before You Begin

### What You'll Need

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **OS** | Windows 10/11, macOS 12+, Ubuntu 22.04+ | Any supported OS |
| **Docker** | Docker Engine 24+ | Docker Desktop (latest) |
| **RAM** | 4 GB | 8+ GB |
| **CPU** | 2 cores | 4+ cores |
| **Disk** | 10 GB free | 20+ GB free |
| **Internet** | For initial clone | For LLM providers (optional) |

### What You'll Accomplish

By the end of this guide, you will:
1. Have Evershade running on your machine
2. Understand the basic architecture
3. Have created your first AI agent
4. Have run your first task
5. Know how to explore and extend the platform

---

## Step 1: Install Prerequisites

### Docker

Evershade runs entirely in Docker containers. You need Docker and Docker Compose.

**Windows:**
1. Download [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Install and launch Docker Desktop
3. Ensure WSL2 backend is enabled (Docker Desktop does this by default)
4. Verify: Open PowerShell and run `docker --version`

**macOS:**
1. Download [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Install and launch Docker Desktop
3. Verify: Open Terminal and run `docker --version`

**Linux (Ubuntu):**
```bash
# Install Docker from official repo
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect

# Verify
docker --version
docker compose version
```

### Git

You need Git to clone the repository.

**Windows:** Download from [git-scm.com](https://git-scm.com/download/win)
**macOS:** `xcode-select --install` or download from [git-scm.com](https://git-scm.com/download/mac)
**Linux:** `sudo apt install git`

### Verify Installation

```bash
# All three should return version numbers
docker --version
docker compose version
git --version
```

---

## Step 2: Clone and Install Evershade

### Clone the Repository

```bash
# Open a terminal (PowerShell on Windows, Terminal on macOS/Linux)
git clone https://github.com/LukaG712/Evershade.git
cd Evershade
```

### Install Service Repositories

Evershade's services live in separate Git repositories. The install script clones them:

**Linux/macOS:**
```bash
./install.sh --profile minimal
```

**Windows PowerShell:**
```powershell
.\install.ps1 -Profile minimal
```

This downloads the core services (Greenie, Slinker, Trapper, Gobber) into the correct directories. The `minimal` profile is recommended for first-time users.

**What just happened:**
- `Greenie/` – Central orchestrator (Python/FastAPI)
- `Slinker/` – Code execution engine (Python/FastAPI)
- `Trapper/` – Web scraping service (TypeScript/Fastify)
- `Gobber/` – Storage and knowledge graph (Python/FastAPI)

---

## Step 3: Configure Your Environment

### Create the Configuration File

```bash
# Copy the example configuration
cp .env.example .env
```

The `.env` file contains all configuration. Let's walk through the important settings.

### Generate API Keys

Evershade uses API keys for service-to-service authentication. You need unique keys for each service.

**Generate a key:**
```bash
# Linux/macOS
openssl rand -hex 32

# Windows PowerShell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
```

**Update `.env`:**
```bash
# Edit .env with your text editor
# Replace each "change-me" value with a generated key

EVERSHADE_GREENIE_API_KEY=your-generated-key-here
EVERSHADE_SLINKER_API_KEY=another-generated-key-here
EVERSHADE_TRAPPER_API_KEY=another-generated-key-here
EVERSHADE_GOBBER_API_KEY=another-generated-key-here
EVERSHADE_ENCRYPTION_KEY=your-encryption-key-here
```

> **Important:** Never commit your `.env` file to Git. It's already in `.gitignore`.

### Optional: Configure LLM Provider

If you want to use AI features, you have two options:

**Option A: Cloud LLM (OpenAI)**
```bash
# Add to .env
EVERSHADE_OPENAI_API_KEY=sk-your-openai-key
```

**Option B: Local LLM (Ollama)**
```bash
# Install Ollama separately from https://ollama.ai
# Then add to .env:
EVERSHADE_OLLAMA_URL=http://host.docker.internal:11434
EVERSHADE_OLLAMA_MODEL=gemma4:12b
```

> **Note:** You can start without any LLM provider and add one later. Basic agent management and web scraping work without LLM.

---

## Step 4: Start Evershade

### Start the Services

**Linux/macOS:**
```bash
./start.sh --profile minimal
```

**Windows PowerShell:**
```powershell
.\start.ps1 -Profile minimal
```

This builds Docker images and starts the core services. First startup takes 2-5 minutes while images are built.

### What's Starting

| Service | Port | Role |
|---------|------|------|
| Greenie | 8080 | Central API and orchestrator |
| Slinker | Internal | Code execution engine |
| Trapper | Internal | Web scraping |
| Gobber | Internal | Storage and knowledge graph |
| Redis | Internal | Job queues and caching |

### Check Status

```bash
# See running containers
docker compose ps

# All services should show "healthy" status
# Wait a moment if they're still starting up
```

---

## Step 5: Verify Everything Works

### Health Checks

```bash
# Check Greenie health
curl http://localhost:8080/health

# Expected response:
# {"status": "ok", "service": "Greenie", "version": "1.8.0"}
```

### View Logs

```bash
# Follow Greenie logs
docker compose logs -f Greenie

# You should see startup messages and no errors
# Press Ctrl+C to stop following logs
```

### Access the API Docs

Open **http://localhost:8080/docs** in your browser. You'll see the Swagger UI with all available API endpoints.

---

## Step 6: Create Your First Agent

### Via the API

```bash
# Create an agent
curl -X POST http://localhost:8080/api/agents \
  -H "Authorization: Bearer $EVERSHADE_GREENIE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "researcher",
    "runner": "junie",
    "guidelines": "Always cite your sources. Be concise and accurate."
  }'
```

### What Is an Agent?

An agent is an AI-powered worker with:
- **Name:** How you identify it (e.g., "researcher")
- **Runner:** The execution engine (e.g., "junie" for Junie CLI)
- **Guidelines:** Instructions that shape its behavior

### List Your Agents

```bash
curl http://localhost:8080/api/agents \
  -H "Authorization: Bearer $EVERSHADE_GREENIE_API_KEY"
```

---

## Step 7: Run Your First Task

### Send a Chat Message

```bash
curl -X POST http://localhost:8080/api/chat \
  -H "Authorization: Bearer $EVERSHADE_GREENIE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "researcher",
    "message": "What are the three most important principles of clean code?"
  }'
```

### Try Web Scraping

```bash
# Scrape a webpage
curl -X POST http://localhost:8080/api/scrape \
  -H "Authorization: Bearer $EVERSHADE_GREENIE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://httpbin.org/html"
  }'
```

---

## Step 8: Explore the Dashboard

### Start the Full Dashboard

If you want the visual dashboard (Slammer), restart with the `full` profile:

```bash
# Stop current services
./stop.sh

# Start with dashboard
./start.sh --profile full
```

### Access the Dashboard

Open **http://localhost:5173** in your browser. You'll see:

| Section | What You'll Find |
|---------|-----------------|
| **Services** | Real-time health status of all services |
| **Agents** | Your agent list and management |
| **Runs** | History of agent executions |
| **Workflows** | Automated task sequences |
| **Metrics** | System resource usage (with Sneaker) |
| **Logs** | Aggregated logs from all services |

---

## Next Steps

Now that you have Evershade running, here's where to go next:

### For Beginners
- **[FAQ](FAQ.md)** – Answers to common questions
- **[Glossary](GLOSSARY.md)** – Key terms explained
- **[README - Your First Agent](../../README.md#your-first-agent)** – Quick tutorial

### For Power Users
- **[Advanced Guide](ADVANCED.md)** – Deep dives into internals
- **[Architecture](ARCHITECTURE.md)** – Full system architecture
- **[Service Catalog](SERVICE_CATALOG.md)** – Every API endpoint

### For Operations
- **[Configuration](CONFIGURATION.md)** – All environment variables
- **[Deployment](DEPLOYMENT.md)** – Server and production deployment
- **[Security](SECURITY.md)** – Security model and hardening
- **[Backup & Restore](BACKUP_RESTORE.md)** – Data protection

---

## Troubleshooting

### Services Won't Start

```bash
# Run diagnostics
evershade doctor

# Check logs
docker compose logs Greenie
docker compose logs Slinker
```

### Port Already in Use

If port 8080 is occupied:
1. Find the conflicting process
2. Stop it, or change the port in `docker-compose.yml`

### API Key Authentication Failed

Ensure your `.env` values match what you're passing in requests:
```bash
# Verify the key in .env
grep EVERSHADE_GREENIE_API_KEY .env
```

### Docker Out of Memory

Increase Docker's memory allocation:
- **Docker Desktop:** Settings → Resources → Memory → Set to 8 GB+
- **Linux:** Check `docker info` for memory limits

### Can't Reach Dashboard

1. Verify services are running: `docker compose ps`
2. Check bind address: `EVERSHADE_BIND_ADDRESS` should be `127.0.0.1` for desktop
3. Try `http://localhost:8080` (Greenie API) and `http://localhost:5173` (Slammer)

### Reset Everything

If you want to start fresh:
```bash
# Stop and remove all containers and volumes
docker compose down -v

# Start again
./start.sh --profile minimal
```

---

## Need Help?

- **[Troubleshooting Guide](../../README.md#troubleshooting)** – Common issues and fixes
- **[Contributing](../../CONTRIBUTING.md)** – Report bugs and suggest features
- **[GitHub Issues](https://github.com/LukaG712/Evershade/issues)** – File an issue
