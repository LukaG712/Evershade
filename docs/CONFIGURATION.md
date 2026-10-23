# Evershade Configuration Reference

**Version:** 1.0.0
**Last Updated:** 2026-10-23

---

## 1. Configuration Overview

Evershade uses environment variables for all configuration. Copy `.env.example` to `.env` and edit the values. The `docker-compose.yml` file references these variables with sensible defaults.

### Quick Start for Beginners

1. **Copy the template:** `cp .env.example .env`
2. **Generate API keys:** Replace every `change-me` value with a random hex string
3. **Optional:** Add your LLM provider key (OpenAI, Anthropic, etc.)
4. **Save and start:** `./start.sh --profile minimal`

That's it for a basic setup. The sections below cover every available option.

### Configuration File Locations

| File | Purpose | Edit? |
|------|---------|-------|
| `.env.example` | Template with all variables and documentation | No (reference only) |
| `.env` | Your actual configuration | Yes |
| `Greenie/hub.yaml` | Greenie-specific agent and bot configuration | Yes (optional) |
| `version-manifest.json` | Compatible service versions | No (managed by releases) |

### Variable Naming Convention

All new variables follow the pattern: `EVERSHADE_<SERVICE>_<SETTING>`

Legacy variable names are still supported as deprecated aliases. Run `evershade config validate` to detect deprecated names.

| Legacy Name | New Name | Status |
|-------------|----------|--------|
| `HUB_API_KEY` | `EVERSHADE_GREENIE_API_KEY` | Deprecated alias |
| `Slinker_API_KEY` | `EVERSHADE_SLINKER_API_KEY` | Deprecated alias |
| `Trapper_API_KEY` | `EVERSHADE_TRAPPER_API_KEY` | Deprecated alias |
| `GOBBER_API_KEY` | `EVERSHADE_GOBBER_API_KEY` | Deprecated alias |
| `SNEAKER_API_KEY` | `EVERSHADE_SNEAKER_API_KEY` | Deprecated alias |
| `HIDER_API_KEY` | `EVERSHADE_HIDER_API_KEY` | Deprecated alias |
| `POLTERGEIST_API_KEY` | `EVERSHADE_POLTERGEIST_API_KEY` | Deprecated alias |
| `SHREWD_API_KEY` | `EVERSHADE_SHREWD_API_KEY` | Deprecated alias |
| `ENCRYPTION_KEY` | `EVERSHADE_ENCRYPTION_KEY` | Deprecated alias |

---

## 2. Required Configuration

### Service API Keys

Generate unique keys for each service. **Never use the default values in production.**

```bash
# Generate a secure key
openssl rand -hex 32
```

| Variable | Required | Description |
|----------|----------|-------------|
| `EVERSHADE_GREENIE_API_KEY` | Yes | Greenie API key |
| `EVERSHADE_SLINKER_API_KEY` | Yes | Slinker API key |
| `EVERSHADE_TRAPPER_API_KEY` | Yes | Trapper API key |
| `EVERSHADE_GOBBER_API_KEY` | Yes | Gobber API key |
| `EVERSHADE_ENCRYPTION_KEY` | Yes | Hider encryption key (AES-256) |

### Optional Service Keys

| Variable | Required | Description |
|----------|----------|-------------|
| `EVERSHADE_SNEAKER_API_KEY` | Optional | Sneaker API key |
| `EVERSHADE_HIDER_API_KEY` | Optional | Hider API key |
| `EVERSHADE_POLTERGEIST_API_KEY` | Optional | Poltergeist API key |
| `EVERSHADE_SHREWD_API_KEY` | Optional | Shrewd API key |

---

## 3. Deployment Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `EVERSHADE_MODE` | `desktop` | `desktop` = loopback only, `server` = all interfaces |
| `EVERSHADE_BIND_ADDRESS` | `127.0.0.1` | Bind address for host ports |
| `EVERSHADE_PUBLIC_URL` | `http://localhost:8080` | Public base URL for links and CORS |

---

## 4. LLM Provider Configuration

### Cloud Providers (Optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `EVERSHADE_OPENAI_API_KEY` | *(empty)* | OpenAI API key |
| `EVERSHADE_ANTHROPIC_API_KEY` | *(empty)* | Anthropic API key |
| `EVERSHADE_GOOGLE_API_KEY` | *(empty)* | Google AI API key |

### Local Model (Ollama)

| Variable | Default | Description |
|----------|---------|-------------|
| `EVERSHADE_OLLAMA_URL` | `http://host.docker.internal:11434` | Ollama API endpoint |
| `EVERSHADE_OLLAMA_MODEL` | `gemma4:12b` | Default Ollama model |

**Note:** On Linux Docker, `host.docker.internal` requires `extra_hosts: ["host.docker.internal:host-gateway"]` in docker-compose.yml. This is already configured for Greenie, Slinker, and Shrewd.

---

## 5. Slinker Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `EVERSHADE_WORKSPACE_PATH` | `./workspace` | Path to workspace directory |
| `EVERSHADE_MAX_CONCURRENT_WORKERS` | `1` | Maximum concurrent Slinker workers |
| `EVERSHADE_ISOLATION_MODE` | `worktree` | Isolation mode: `worktree`, `container`, `workstation` |
| `EVERSHADE_JUNIE_BIN` | `junie` | Junie CLI binary path |
| `EVERSHADE_REFINE_PROMPT` | `false` | Refine prompts via Ollama before sending to Junie |

---

## 6. Trapper Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `EVERSHADE_SCRAPE_TIMEOUT` | `30000` | Scrape timeout in milliseconds |
| `EVERSHADE_CRAWL_MAX_DEPTH` | `10` | Maximum crawl depth |
| `EVERSHADE_CRAWL_MAX_PAGES` | `100` | Maximum pages per crawl |
| `EVERSHADE_CRAWL_MAX_CONCURRENCY` | `5` | Concurrent crawl requests |
| `EVERSHADE_BROWSER_HEADLESS` | `true` | Run browser in headless mode |

---

## 7. Gobber Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `EVERSHADE_OBSIDIAN_VAULT_PATH` | `./obsidian-vault` | Path to Obsidian vault (optional) |

---

## 8. General Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `EVERSHADE_LOG_LEVEL` | `INFO` | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `EVERSHADE_REDIS_PASSWORD` | *(empty)* | Redis password (optional) |

---

## 9. Configuration Validation

Use the CLI to validate your configuration:

```bash
evershade config validate
```

This checks for:
- Missing required variables
- Deprecated variable names (with warnings)
- Default API keys in production mode
- Invalid bind addresses
- Port conflicts

---

## 11. Advanced Configuration Tips

### Using Docker Secrets

For production deployments, consider Docker secrets instead of `.env` files:

```yaml
# docker-compose.yml
services:
  Greenie:
    secrets:
      - greenie_api_key
    environment:
      - EVERSHADE_GREENIE_API_KEY_FILE=/run/secrets/greenie_api_key

secrets:
  greenie_api_key:
    file: ./secrets/greenie_api_key.txt
```

### Environment-Specific Configuration

Use separate `.env` files for different environments:

```
.env.local      # Local development (gitignored)
.env.staging    # Staging server
.env.production # Production server
```

Load with: `set -a; source .env.production; set +a; docker compose up -d`

### Validating Configuration Changes

After editing `.env`, validate before restarting:

```bash
# Check for issues
evershade config validate

# Apply changes
docker compose up -d
```

### Hot-Reloading Configuration

Some settings can be changed without restarting:
- Log level (`EVERSHADE_LOG_LEVEL`)
- Rate limit thresholds
- Feature flags (via Gobber API)

Most settings require a service restart: `docker compose restart <service>`
