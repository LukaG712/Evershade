# Agent Harness

**Version:** 1.0.0
**Last Updated:** 2026-10-23

The Agent Harness provides reusable workflows, specialized subagents, and event-driven automation for advanced agent development.

---

## Table of Contents

- [Spec Mode](#spec-mode)
- [Custom Droids](#custom-droids)
- [Skills System](#skills-system)
- [Hooks System](#hooks-system)
- [Environments](#environments)
- [API Endpoints](#api-endpoints)

---

## Spec Mode

Research-first development: create specs, analyze repositories, approve plans, then convert to missions.

| Endpoint | Description |
|----------|-------------|
| `POST /api/specs` | Create a new spec |
| `POST /api/specs/{id}/analyze` | Run repository analysis |
| `POST /api/specs/{id}/approve` | Approve and convert to mission |

---

## Custom Droids

Specialized subagents with their own prompts, models, and tool policies. Built-in droids: **worker**, **explorer**, **reviewer**, **validator**.

---

## Skills System

Reusable `SKILL.md` workflows with trigger-based auto-discovery. Skills are matched to tasks and can be invoked manually.

---

## Hooks System

Event-driven lifecycle hooks for mission events: `PreToolUse`, `PostToolUse`, `MissionStart`, `MissionEnd`, `MilestoneComplete`, `ValidationFail`. Supports script and webhook hooks.

---

## Environments

Reusable sandbox definitions with repository, dependencies, setup commands, and health checks.

---

## API Endpoints

### Specs

| Endpoint | Description |
|----------|-------------|
| `POST /api/specs` | Create a new spec |
| `GET /api/specs` | List all specs |
| `GET /api/specs/{id}` | Get spec details |
| `POST /api/specs/{id}/analyze` | Run repository analysis |
| `POST /api/specs/{id}/approve` | Approve and convert to mission |
| `POST /api/specs/{id}/reject` | Reject a spec |

### Droids

| Endpoint | Description |
|----------|-------------|
| `GET /api/droids` | List available droids |
| `GET /api/droids/{id}` | Get droid details |
| `POST /api/droids` | Create a custom droid |

### Skills

| Endpoint | Description |
|----------|-------------|
| `GET /api/skills` | List available skills |
| `GET /api/skills/{id}` | Get skill details |
| `POST /api/skills/{id}/invoke` | Invoke a skill manually |

### Hooks

| Endpoint | Description |
|----------|-------------|
| `GET /api/hooks` | List configured hooks |
| `POST /api/hooks` | Create a new hook |
| `DELETE /api/hooks/{id}` | Remove a hook |

### Environments

| Endpoint | Description |
|----------|-------------|
| `GET /api/environments` | List environments |
| `POST /api/environments` | Create a new environment |
| `GET /api/environments/{id}` | Get environment details |

---

## See Also

- [Mission Control](MISSION_CONTROL.md) – How specs convert to missions
- [Advanced Guide](ADVANCED.md) – Advanced Agent Harness patterns
- [Service Catalog](SERVICE_CATALOG.md) – Full API endpoint reference
