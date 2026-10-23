# Evershade Development Guide

**Version:** 1.0.0
**Last Updated:** 2026-10-23

---

## 1. Development Environment

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Docker | 24+ | Container runtime |
| Python | 3.12+ | Python services (Greenie, Slinker, etc.) |
| Node.js | 18+ | TypeScript services (Trapper, Slammer) |
| Git | Latest | Version control |
| Junie CLI | Latest | Code agent execution (optional) |

### Recommended IDE Setup

- **PyCharm** or **VS Code** with Python extension for Python services
- **WebStorm** or **VS Code** with TypeScript extension for Trapper/Slammer
- Enable Docker integration for running and debugging containers

### Quick Start

```bash
# Clone the repository
git clone https://github.com/LukaG712/Evershade.git
cd Evershade

# Copy configuration
cp .env.example .env

# Start all services in dev mode
docker compose --profile dev up -d
```

The `dev` profile exposes all service ports on the host for direct access during development.

---

## 2. Service Development

### Python Services (Greenie, Slinker, etc.)

```bash
cd Greenie

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Lint and format
ruff check .
ruff format .

# Run locally
uvicorn hub.api:app --reload --port 8080
```

### TypeScript Services (Trapper)

```bash
cd Trapper

# Install dependencies
npm install

# Run tests
npm test

# Lint and format
npm run lint

# Run in development mode
npm run dev
```

---

## 3. Docker Development

```bash
# Rebuild a specific service
docker compose up -d --build Greenie

# View logs
docker compose logs -f Greenie

# Shell into a running container
docker compose exec Greenie bash

# Stop all services
docker compose down
```

---

## 4. Adding a New Service

1. Create the service directory: `mkdir NewService`
2. Add Dockerfile, `pyproject.toml`/`package.json`, and source code
3. Add to `docker-compose.yml` with appropriate profile
4. Add API key to `.env.example`
5. Add health check endpoint
6. Update `version-manifest.json`
7. Update `docs/ARCHITECTURE.md`

---

## 5. Debugging

### Greenie

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
docker compose up -d Greenie

# View logs
docker compose logs -f Greenie
```

### Database Inspection

```bash
# Greenie database
docker compose exec Greenie sqlite3 /app/data/evershade_valley.db ".tables"

# Slinker database
docker compose exec Slinker sqlite3 /workspace/Slinker.db ".tables"
```

---

## 6. Code Style

- **Python:** Follow PEP 8. Use `ruff` for linting and formatting.
- **TypeScript:** Follow the existing ESLint config. Use `prettier` for formatting.
- **Commit messages:** Use Conventional Commits format (`feat:`, `fix:`, `docs:`, etc.)

---

## 7. Pre-Commit Hooks

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

Hooks run: linting, formatting, and secret scanning on every commit.

---

## 8. Development Workflow

### Typical Development Cycle

```bash
# 1. Create a feature branch
git checkout -b feature/my-feature

# 2. Make changes to a service
cd Greenie
# ... edit code ...

# 3. Run tests
cd Greenie && pytest -v

# 4. Rebuild the service
cd .. && docker compose up -d --build Greenie

# 5. Test the changes
curl http://localhost:8080/api/health

# 6. Commit and push
git add -A && git commit -m "feat: add my feature" && git push
```

### Debugging Python Services

```bash
# Run with debug logging
docker compose exec Greenie python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
# Your debug code here
"

# Use pdb for interactive debugging
docker compose exec Greenie python -m pdb my_script.py
```

### Hot Reloading

For faster development, mount source code into containers:

```yaml
# docker-compose.yml (dev profile only)
services:
  Greenie:
    volumes:
      - ./Greenie:/app
    environment:
      - UVICORN_RELOAD=1
```

### Testing Service-to-Service Communication

```bash
# Test from Greenie to Slinker
docker compose exec Greenie curl -s http://Slinker:8000/health

# Test from Greenie to Trapper
docker compose exec Greenie curl -s http://Trapper-api:3000/health

# Test from Greenie to Gobber
docker compose exec Greenie curl -s http://Gobber:8085/health
```

---

## 9. Code Review Checklist

Before submitting a PR:

- [ ] Code follows existing style (ruff/prettier)
- [ ] Tests pass: `pytest -v` or `npm test`
- [ ] No secrets committed (pre-commit hook should catch this)
- [ ] Documentation updated if behavior changed
- [ ] Docker image builds successfully
- [ ] Service health check passes
- [ ] No new dependencies without justification
- [ ] Breaking changes documented in CHANGELOG.md
