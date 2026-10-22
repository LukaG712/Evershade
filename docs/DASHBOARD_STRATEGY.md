# Evershade Dashboard Strategy

**Version:** 1.0.0
**Last Updated:** 2026-10-22

## Decision: Slammer as the Single Dashboard

### Background

Evershade previously had two dashboard surfaces:
1. **Greenie** — A FastAPI backend with 45+ API route modules, potentially serving a built-in UI
2. **Slammer** — A standalone React-based dashboard

This created confusion about which dashboard to use and duplicated effort.

### Decision

**Slammer is the single unified dashboard for Evershade.** Greenie operates as an API-only backend service.

### Rationale

1. **Separation of concerns:** Greenie is the central orchestration API; Slammer is the presentation layer
2. **Technology fit:** React (Slammer) provides a better UX than FastAPI templates (Greenie)
3. **Extensibility:** Adding new dashboard pages is easier in a React SPA
4. **Proxy support:** Slammer can be deployed behind a reverse proxy (Caddy) that routes API calls to Greenie

### Architecture

```
Browser → Caddy (port 80/443) → Slammer (static files)
                        ↘ Greenie /api/* (reverse proxy)
                        ↘ Sneaker /api/sneaker/* (reverse proxy)
                        ↦ WebSocket upgrade for terminals
```

### Slammer Pages

| Page | Data Source | Description |
|------|-------------|-------------|
| Services | Direct health checks | Service status polling |
| Agents | Greenie `/api/agents` | Agent management |
| Runs | Greenie `/api/runs` | Run history |
| Workflows | Greenie `/api/workflows` | Workflow builder and execution |
| Workstations | Greenie `/api/workstations` | Container management, logs, terminal |
| Metrics | Sneaker `/api/metrics`, Greenie `/api/system/stats` | System resources and observability |
| Logs | Greenie `/api/logs` | Aggregated log viewer |
| Plugins | Greenie `/api/plugins`, `/api/mcp` | Plugin and MCP server management |

### Greenie API-Only Mode

Greenie no longer serves a frontend. All its endpoints are API-only:
- No static file serving
- No HTML templates
- CORS configured for Slammer's origin
- Bearer token auth on all protected endpoints

### Proxy Configuration

The Caddyfile provides reverse proxy rules:
- `/` → Slammer (static files)
- `/api/*` → Greenie
- `/sneaker/*` → Sneaker
- `/ws/*` → WebSocket upgrade to Greenie

### Deployment Modes

1. **Desktop mode:** All services on localhost, Slammer accessible at `http://localhost:8080`
2. **Server mode:** Caddy reverse proxy on port 80/443, only Caddy exposed to host
3. **Docker mode:** Internal Docker network, Caddy as gateway

### Migration Notes

- Any users accessing Greenie's built-in UI should switch to Slammer
- Greenie's static file routes are deprecated but preserved for backward compatibility
- All new dashboard features should be built in Slammer
