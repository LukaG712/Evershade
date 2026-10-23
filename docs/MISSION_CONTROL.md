# Mission Control

**Version:** 1.0.0
**Last Updated:** 2026-10-23

Evershade's Mission Control system provides factory-inspired orchestration for complex AI-driven development workflows. Missions break down large tasks into milestones, features, and automated validation cycles.

---

## Table of Contents

- [Key Capabilities](#key-capabilities)
- [Mission Workflow](#mission-workflow)
- [API Endpoints](#api-endpoints)

---

## Key Capabilities

| Feature | Description |
|---------|-------------|
| **Mission Lifecycle** | Create, plan, execute, validate, complete, cancel, pause, and resume missions |
| **Automated Planning** | LLM-based planning via Shrewd with repository intelligence and heuristic fallback |
| **Milestones & Features** | Break missions into milestones with parallel worker execution |
| **Code Review** | Automated deterministic checks (test, lint, type) and diff-based security review |
| **Approval Gates** | Human-in-the-loop approval for sensitive operations with three autonomy levels |
| **Fix-Revalidate** | Automatically create fix features from validation failures with configurable retries |
| **SSE Streaming** | Real-time mission execution logs via Server-Sent Events |
| **Analytics** | Success/failure rates, duration tracking, model usage, and validation summaries |
| **Checkpoint Recovery** | Persist mission state and recover from failures |
| **Secret Redaction** | Pattern-based redaction of API keys, tokens, and passwords in logs |

---

## Mission Workflow

```
  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │ Create       │────►│ LLM Planning │────►│ Execute      │────►│ Validate     │
  │ Mission      │     │              │     │ Features     │     │ Results      │
  └──────────────┘     └──────────────┘     └──────────────┘     └──────┬───────┘
                                                                        │
                                                              ┌─────────▼─────────┐
                                                              │   All Pass?       │
                                                              └───┬───────────┬───┘
                                                                   │ Yes       │ No
                                                            ┌──────▼──────┐ ┌───▼──────────────┐
                                                            │ Complete    │ │ Fix-Revalidate   │
                                                            │ Mission     │ │ └────────┬───────┘
                                                            └─────────────┘          │
                                                                                     │
                                                                            ┌────────▼───────┐
                                                                            │ Execute        │
                                                                            │ Features       │
                                                                            └────────────────┘
```

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/missions` | Create a new mission |
| `GET /api/missions` | List all missions |
| `GET /api/missions/{id}` | Get mission details |
| `POST /api/missions/{id}/plan` | Trigger LLM planning |
| `POST /api/missions/{id}/execute` | Start execution |
| `POST /api/missions/{id}/validate` | Run validation |
| `POST /api/missions/{id}/fix-revalidate` | Auto-fix failures |
| `GET /api/missions/{id}/logs/stream` | SSE log stream |
| `GET /api/missions/analytics` | Mission analytics |

---

## See Also

- [Architecture](ARCHITECTURE.md) – How Mission Control fits into the system
- [Service Catalog](SERVICE_CATALOG.md) – Full API endpoint reference
- [Advanced Guide](ADVANCED.md) – Advanced Mission Control patterns
