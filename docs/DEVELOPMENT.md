# Evershade Development Guide

**Version:** 1.0.0
**Last Updated:** 2026-10-22

---

## 1. Development Environment

### Prerequisites

- Docker Desktop (Mac/Windows) or Docker Engine + Compose (Linux)
- Python 3.12+ (for Python services)
- Node.js 18+ (for TypeScript services)
- Git

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
