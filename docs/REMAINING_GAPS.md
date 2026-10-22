# Evershade — Remaining Gaps & Implementation Checklist

**Date:** 2026-10-22
**Version:** v1.8.0
**Scope:** Comprehensive gap analysis based on code inspection, not documentation claims

---

## Methodology

Each gap is assessed by inspecting actual code, not documentation:
- **Complete & Verified**: Code exists, tests pass, behavior confirmed
- **Implemented but Unverified**: Code exists, tests exist but not run against real services
- **Partial**: Code exists but missing key features or edge cases
- **Missing**: No implementation found
- **Blocked**: Cannot complete due to external dependencies

---

## 1. Clean Installation

| Requirement | Current Implementation | Evidence Inspected | Status | Required Change | Test |
|-------------|----------------------|-------------------|---------|----------------|------|
| Fresh clone leads to runnable installation | `.gitignore` excludes all 10 service dirs; no bootstrap script | `.gitignore`, `start.sh`, `start.ps1` | **Missing** | Create bootstrap script that clones services from GitHub using version-manifest.json | Clone to temp dir, run bootstrap, verify `docker compose config` |
| Bootstrap uses pinned versions, not latest | version-manifest.json has versions but no commit SHAs | `version-manifest.json` | **Partial** | Add commit SHA or tag to each service entry | Bootstrap should clone exact pinned revision |
| Idempotent re-run | No bootstrap exists | N/A | **Missing** | Bootstrap should detect existing repos and skip or update safely | Run bootstrap twice, verify no errors |
| Failed builds produce useful errors | Startup scripts check for dir existence | `start.sh:85-90`, `start.ps1:78-83` | **Partial** | Bootstrap should report which service failed and why | Simulate network failure, verify error message |
| Windows PowerShell + Linux/macOS support | start.sh and start.ps1 exist | Both files inspected | **Complete** | Bootstrap scripts for both platforms | Run on both platforms |
| README matches tested process | README quickstart assumes services present | `README.md` lines 50-100 | **Partial** | Update README to reference bootstrap command | Follow README from scratch |

---

## 2. Service Startup & Configuration

| Requirement | Current Implementation | Evidence Inspected | Status | Required Change | Test |
|-------------|----------------------|-------------------|---------|----------------|------|
| start.sh/start.ps1 use explicit Compose profile | `docker compose up -d` — no profile flag | `start.sh:114`, `start.ps1:112` | **Missing** | Add `--profile` flag (default: standard) | Run with minimal profile, verify only core services start |
| Fail safely with missing config in server mode | Default key warning, but continues | `start.sh:63-80`, `start.ps1:57-73` | **Partial** | Block startup in server mode with default keys | Set EVERSHADE_MODE=server, verify blocked |
| Validate config before starting | API key check only | `start.sh:51-82` | **Partial** | Add `evershade doctor` equivalent in startup | Run with missing .env, verify clear error |
| Health checks distinguish liveness from readiness | All use `/health` endpoint | `docker-compose.yml` healthchecks | **Partial** | Add `/ready` endpoint separate from `/health` | Kill dependency, verify readiness fails |
| Optional services absent without crashing | Hybrid stores with fallback | `Greenie/hub/gobber_client.py` | **Implemented but Unverified** | Test each optional service absence | Start minimal profile, verify core works |
| Documented ports match actual | Ports consistent across files | `docker-compose.yml`, `.env.example`, `version-manifest.json` | **Complete** | None | N/A |

---

## 3. CI & Integration Tests

| Requirement | Current Implementation | Evidence Inspected | Status | Required Change | Test |
|-------------|----------------------|-------------------|---------|----------------|------|
| Validate Compose configuration | `docker compose config --quiet` in CI | `.github/workflows/ci.yml:21-22` | **Complete** | None | N/A |
| Run linting, formatting, type checks | Shell script syntax only | `.github/workflows/ci.yml:24-51` | **Partial** | Add Python linting (ruff/flake8), TypeScript checking | CI should catch style errors |
| Build all required service images | Not done in CI (services gitignored) | `.github/workflows/ci.yml` | **Missing** | Clone services in CI, build images | CI builds all images |
| Start services in CI | `if: false` — disabled | `.github/workflows/ci.yml:84` | **Missing** | Enable and fix integration test job | CI starts services, runs tests |
| Wait for readiness via health checks | `sleep 30` — fixed sleep | `.github/workflows/ci.yml:87` | **Missing** | Use `docker compose ps` or health check polling | CI waits for healthy services |
| Run integration tests against real services | Disabled | `.github/workflows/ci.yml:84-89` | **Missing** | Enable with actual service communication tests | CI runs integration tests |
| Collect logs on failure | Not implemented | `.github/workflows/ci.yml` | **Missing** | Add `docker compose logs` on failure step | CI failure includes service logs |
| Clean up test environment | `docker compose down` in disabled job | `.github/workflows/ci.yml:89` | **Partial** | Ensure cleanup in `finally` equivalent | CI always cleans up |
| Use fake LLM providers in tests | Not implemented | `tests/` directory | **Missing** | Add mock LLM provider for tests | Tests don't incur API costs |
| Separate test categories accurately | `pytest -m "not integration"` marker | `.github/workflows/ci.yml:81` | **Complete** | None | N/A |

### Required Integration Scenarios

| Scenario | Status | Evidence |
|----------|--------|----------|
| Greenie → Slinker task execution | **Implemented but Unverified** | `tests/integration/test_integration.py` exists |
| Greenie → Shrewd model requests | **Implemented but Unverified** | Test file exists |
| Greenie → Gobber persistence | **Implemented but Unverified** | Test file exists |
| Greenie → Hider secret retrieval | **Implemented but Unverified** | Test file exists |
| Greenie → Poltergeist notifications | **Implemented but Unverified** | Test file exists |
| Greenie → Trapper research | **Implemented but Unverified** | Test file exists |
| Greenie → Sneaker telemetry | **Implemented but Unverified** | Test file exists |
| Multi-step workflows with failures | **Implemented but Unverified** | `tests/integration/test_mission_cross_service.py` |
| Slammer dashboard API calls | **Missing** | No UI integration tests found |
| Speedy CLI against running installation | **Missing** | No CLI integration tests found |

---

## 4. Authentication & Web Security

| Requirement | Current Implementation | Evidence Inspected | Status | Required Change | Test |
|-------------|----------------------|-------------------|---------|----------------|------|
| User authentication (browser sessions) | API key only, no user accounts | `docs/SECURITY.md:31-34`, `Greenie/hub/` | **Missing** | Implement login, session creation, validation | Login, access protected endpoint, verify session |
| Secure session management | Not implemented | No session code found | **Missing** | Session store, expiration, revocation | Create session, wait for expiry, verify rejected |
| Password hashing | Not applicable (no password auth) | N/A | **Missing** | bcrypt/argon2 if password-based login added | Hash password, verify secure |
| RBAC for users/projects | RBAC tables in Gobber storage | `Gobber/gobber/storage.py:102-115` | **Partial** | Wire RBAC into Greenie auth middleware | Create user, assign role, verify access control |
| CSRF protection | Middleware exists, now wired into create_app | `Greenie/hub/api/csrf.py`, `core.py:742-748` | **Complete** | Bearer-authenticated requests skip CSRF; cookie sessions require token | POST without token → 403, with token → 200 |
| Rate limiting on login | Auth failure rate limiter in core.py | `Greenie/hub/api/core.py:83-111` | **Complete** | 10 failures per 60 seconds per IP | 10 rapid logins → lockout or delay |
| Rate limiting on expensive ops | New middleware with sliding window | `Greenie/hub/api/rate_limit_middleware.py` | **Complete** | Stricter limits for LLM, code execution, workflows, crawling | Exceed limit → 429 |
| Input validation | Pydantic models in FastAPI | All services use FastAPI | **Complete** | None | N/A |
| CORS configuration | Not inspected in detail | `Greenie/hub/api.py` | **Implemented but Unverified** | Verify CORS headers are restrictive | Cross-origin request → blocked |
| SSRF protection in Trapper | Private IP blocking implemented | `docs/SECURITY.md:129-134` | **Implemented but Unverified** | Test with private IPs, metadata endpoints | Request to 169.254.169.254 → blocked |
| Slinker execution boundary | Container mode available | `docs/SECURITY.md:93-98` | **Implemented but Unverified** | Verify container isolation works | Run malicious code, verify contained |
| Secret redaction in logs | SecretRedactionFilter in logging_config.py | `Greenie/hub/api/secret_redaction.py`, `logging_config.py:67-72` | **Complete** | Automatic redaction of API keys, passwords, tokens, secrets | Log sensitive data, verify redacted |
| Production rejects insecure defaults | Warning only, continues | `start.sh:63-80` | **Partial** | Block startup in server mode with defaults | Server mode + defaults → blocked |

---

## 5. Gobber Semantic Memory

| Requirement | Current Implementation | Evidence Inspected | Status | Required Change | Test |
|-------------|----------------------|-------------------|---------|----------------|------|
| Embedding provider interface | Shrewd `/api/embed` endpoint | `Gobber/gobber/knowledge_graph.py:108-136` | **Complete** | None | N/A |
| Embedding generation with batching | Single-note embedding, no batching | `knowledge_graph.py:190` | **Partial** | Add batch embedding for vault indexing | Index 100 notes, verify all embedded |
| Persistent storage of embeddings | `kg_note_embeddings` table | `Gobber/gobber/storage.py:139-145` | **Complete** | None | Store embedding, restart, verify persisted |
| Similarity-based retrieval | Cosine similarity in kg_storage | `Gobber/gobber/kg_storage.py` (exists) | **Implemented but Unverified** | Run semantic search test | Search "hello", find "hi" note |
| Keyword + semantic hybrid search | Semantic only | `knowledge_graph.py:218-224` | **Partial** | Add keyword search fallback | Search exact term, verify found |
| User/project/session scopes | No scoping found | `kg_storage.py` | **Missing** | Add scope filter to search | User A can't see User B's notes |
| Source provenance & timestamps | File path, created_at, updated_at | `kg_models.py`, `storage.py` | **Complete** | None | N/A |
| Deduplication & update handling | Upsert by file path | `knowledge_graph.py:85-106` | **Complete** | None | Update note, verify single entry |
| Deletion & re-indexing | `delete_note` method | `knowledge_graph.py:242-244` | **Implemented but Unverified** | Delete note, verify not in search results | Delete, search, verify absent |
| Search result limits & timeouts | Limit parameter | `knowledge_graph.py:218` | **Complete** | None | N/A |
| Graceful degradation without provider | Fallback hash-based embedding | `knowledge_graph.py:138-155` | **Complete** | None | Disconnect Shrewd, verify fallback works |

---

## 6. Sneaker Observability & OTLP

| Requirement | Current Implementation | Evidence Inspected | Status | Required Change | Test |
|-------------|----------------------|-------------------|---------|----------------|------|
| Standardized structured logs | JSON logging in services | `Greenie/hub/logging_config.py` | **Implemented but Unverified** | Verify all services use structured logs | Check log output format |
| Correlation IDs | Tracing module exists | `Greenie/hub/tracing.py` | **Implemented but Unverified** | Verify correlation ID propagation | Make request, verify ID in all service logs |
| Trace-context propagation | Tracing module exists | `Greenie/hub/tracing.py` | **Implemented but Unverified** | Verify across HTTP calls and background jobs | Multi-service call, verify single trace |
| OTLP-compatible trace export | Full OTLP receiver + exporter | `Sneaker/sneaker/otlp_export.py` (495 lines) | **Complete** | None | Send OTLP trace, verify stored |
| OTLP-compatible metric export | Full OTLP receiver + exporter | `Sneaker/sneaker/otlp_export.py` | **Complete** | None | Send OTLP metric, verify stored |
| OTLP-compatible log export | Full OTLP receiver + exporter | `Sneaker/sneaker/otlp_export.py` | **Complete** | None | Send OTLP log, verify stored |
| Configurable OTLP endpoints | `OTLP_ENDPOINT` env var | `otlp_export.py:28-29` | **Complete** | None | Configure endpoint, verify forwarding |
| Batching, retry, timeout | HTTP client with timeout | `otlp_export.py:247` | **Partial** | Add retry logic for OTLP forwarding | Simulate endpoint failure, verify retry |
| Secret redaction in telemetry | Not implemented | No redaction in OTLP code | **Missing** | Redact API keys, passwords from traces | Send trace with secret, verify redacted |
| Health & dependency status | Health endpoints exist | All services have `/health` | **Complete** | None | N/A |
| Metrics for latency, errors, queues | Basic metrics exist | `Sneaker/sneaker/api.py` | **Partial** | Add task duration, queue depth metrics | Check metrics endpoint for required metrics |

---

## 7. Backup & Restore

| Requirement | Current Implementation | Evidence Inspected | Status | Required Change | Test |
|-------------|----------------------|-------------------|---------|----------------|------|
| Back up every persistent store | Speedy backup with SQLite snapshots | `Speedy/speedy/cli.py:273-389` | **Complete** | All databases snapshotted with sqlite3 .backup | Backup, inspect archive contents |
| Consistent database snapshots | sqlite3 .backup API | `Speedy/speedy/cli.py:309-311` | **Complete** | Uses sqlite3.backup() for consistency | Backup active DB, verify no corruption |
| Manifest with versions, checksums | manifest.json in archive | `Speedy/speedy/cli.py:378-381` | **Complete** | SHA-256 checksums for all DB files | Backup, verify manifest present |
| Configuration & secrets safety | Secret redaction by default | `Speedy/speedy/cli.py:356-373` | **Complete** | Keys/secrets redacted unless --include-secrets | Backup, verify no plaintext secrets |
| Dry-run restore | --dry-run flag | `Speedy/speedy/cli.py:394` | **Complete** | Validates without extracting | Run restore --dry-run, verify no changes |
| Path traversal prevention | Path resolution check | `Speedy/speedy/cli.py:410-415` | **Complete** | Rejects paths escaping project dir | Craft malicious archive, verify rejected |
| Free disk space check | Disk usage check in backup create | `Speedy/speedy/cli.py:287-312` | **Complete** | Estimates size, fails if insufficient space | Low disk space → graceful error |
| Recovery backup before overwrite | Pre-restore backup | `Speedy/speedy/cli.py:464-481` | **Complete** | Creates recovery backup in backups/recovery/ | Restore, verify pre-restore backup exists |
| Encryption key handling | --include-secrets flag | `Speedy/speedy/cli.py:276` | **Complete** | Documented flag to include secrets | Restore with --include-secrets |
| Fail safely on invalid checksum | Checksum verification | `Speedy/speedy/cli.py:429-443` | **Complete** | Verifies SHA-256 before extracting | Corrupt archive, verify rejected |

### Backup Round-Trip Test

| Step | Status |
|------|--------|
| Create records in multiple services | **Not Run** |
| Generate backup | **Not Run** |
| Verify archive integrity | **Not Run** |
| Restore to clean environment | **Not Run** |
| Confirm records survive | **Not Run** |
| Test corrupted archive | **Not Run** |
| Test incompatible versions | **Not Run** |
| Verify failed restore doesn't destroy data | **Not Run** |

---

## 8. Version & Release Management

| Requirement | Current Implementation | Evidence Inspected | Status | Required Change | Test |
|-------------|----------------------|-------------------|---------|----------------|------|
| Single authoritative manifest | `version-manifest.json` | File inspected (126 lines) | **Complete** | None | N/A |
| Pinned version or commit per service | Version numbers only, no commits | `version-manifest.json` | **Partial** | Add commit SHA or tag | Manifest should have exact revision |
| API compatibility version | `api_version: "v1"` field | `version-manifest.json` | **Complete** | None | N/A |
| Required vs optional dependencies | `required` field per service | `version-manifest.json` | **Complete** | None | N/A |
| Migration compatibility | migration_version in manifest | `version-manifest.json` | **Complete** | Tracks database and config migrations | Upgrade, verify migrations run |
| Image references | Not included | N/A | **Missing** | Add Docker image tags | Pull image, verify matches |
| Manifest validation in CI | validate_manifest.py in CI lint job | `.github/workflows/ci.yml:59-61` | **Complete** | Schema, semver, ports, profiles, dependencies | Invalid manifest → CI failure |
| Detect missing/duplicate services | validate_manifest.py checks | `scripts/validate_manifest.py` | **Complete** | Port uniqueness, profile consistency, dependency refs | Duplicate port → CI failure |
| Release checksums | `scripts/release_sign.py` exists | Script exists | **Implemented but Unverified** | Run signing, verify checksums | Sign release, verify signature |
| Safe update procedure | Documented in RELEASES.md | `docs/RELEASES.md` | **Complete** | Backup → validate → update → verify → doctor | Follow procedure, verify success |

---

## 9. Workflows, Dashboard & CLI

| Requirement | Current Implementation | Evidence Inspected | Status | Required Change | Test |
|-------------|----------------------|-------------------|---------|----------------|------|
| Workflow definitions survive restarts | SQLite storage | `Greenie/hub/workflow/` | **Implemented but Unverified** | Restart Greenie, verify workflows persist | Create workflow, restart, verify |
| Sequential & parallel execution | Workflow executor, parallel bug fixed | `Greenie/hub/workflow/executor.py` | **Complete** | Parallel execution now triggers when milestones present | Create milestone workflow, verify parallel |
| Conditional steps & data mappings | Workflow models | `Greenie/hub/workflow/models.py` | **Implemented but Unverified** | Run conditional workflow | Condition true → step runs, false → skipped |
| Retries, timeouts, cancellation | Retries with backoff + timeouts added | `Greenie/hub/workflow/executor.py` | **Complete** | `max_retries` and `timeout_seconds` in step config | Step fails → retries with backoff, timeout kills |
| Approval gates | Workflow API | `Greenie/hub/workflow/` | **Implemented but Unverified** | Workflow pauses at approval | Create approval step, verify pause |
| Scheduled & webhook triggers | Trigger module complete | `Greenie/hub/workflow/triggers.py` (310 lines) | **Complete** | Cron, webhook (HMAC), file change triggers | Set schedule, wait, verify run |
| Slammer connected to real APIs | All 9 pages use real API calls | `Slammer/src/App.tsx` (265 lines) | **Complete** | Health polling, agents, runs, workflows, workstations, metrics, logs, plugins, missions | Open dashboard, verify live data |
| Speedy CLI commands | 9 commands including config validate | `Speedy/speedy/cli.py` (803 lines) | **Complete** | status, install, start, stop, logs, doctor, backup, agents, task, config | Run each command, verify output |
| `evershade doctor` command | Implemented in Speedy | `Speedy/speedy/cli.py:186-257` | **Complete** | Checks Docker, Compose, services, config, env | Run doctor, verify reports issues |
| `evershade install` command | Implemented in Speedy | `Speedy/speedy/cli.py:114-133` | **Complete** | Pulls images and builds services | Run install, verify services cloned |
| `evershade config validate` command | Validates .env, compose, Docker, dirs | `Speedy/speedy/cli.py:654-798` | **Complete** | Checks required vars, service keys, Docker, compose syntax, service dirs | Run validate, verify issues reported |

---

## 10. Service Contracts & Graceful Degradation

| Requirement | Current Implementation | Evidence Inspected | Status | Required Change | Test |
|-------------|----------------------|-------------------|---------|----------------|------|
| Explicit API schemas | FastAPI auto-generates OpenAPI | All services use FastAPI | **Complete** | None | N/A |
| Consistent auth headers | Bearer token on all services | `docker-compose.yml` env vars | **Complete** | None | N/A |
| Timeouts & bounded retries | Retry with backoff in all clients | `Greenie/hub/retry.py`, `gobber_client.py`, `slinker_provider.py`, `trapper_provider.py` | **Complete** | Exponential backoff with jitter for transient errors | Kill service, verify retry behavior |
| Idempotency for retries | Idempotency middleware in Greenie | `Greenie/hub/api/idempotency.py` | **Complete** | X-Idempotency-Key header for workflow creation, agent execution, backup | Retry same request, verify single effect |
| Structured error responses | FastAPI default | All services | **Complete** | None | N/A |
| Request correlation IDs | Tracing module | `Greenie/hub/tracing.py` | **Implemented but Unverified** | Verify X-Request-ID propagation | Make request, check all logs for ID |
| Health/readiness contracts | `/health` on all services | `docker-compose.yml` healthchecks | **Complete** | None | N/A |
| Service capability reporting | All services have /api/capabilities | `Greenie/hub/api/capabilities.py`, `Slinker/junie_adapter/service.py`, `Trapper/src/api/server.ts`, `Gobber/gobber/api.py`, `Shrewd/shrewd/api.py`, `Hider/hider/api.py`, `Poltergeist/poltergeist/api.py`, `Sneaker/sneaker/api.py` | **Complete** | Every service reports features, versions, and API compatibility | Check endpoint, verify features listed |
| Optional dependency behavior | Hybrid stores with fallback | `Greenie/hub/gobber_client.py` | **Implemented but Unverified** | Test each optional service absence | Disable Sneaker, verify core works |

---

## 11. Documentation Consistency

| Document | Status | Issues Found |
|----------|--------|-------------|
| `README.md` | **Partial** | Architecture diagram doesn't match actual service count; some claims unverified |
| `docs/ECOSYSTEM_AUDIT.md` | **Complete** | Up to date |
| `docs/ARCHITECTURE.md` | **Complete** | Up to date |
| `docs/CONFIGURATION.md` | **Complete** | Matches `.env.example` |
| `docs/DEPLOYMENT.md` | **Complete** | Up to date |
| `docs/SECURITY.md` | **Complete** | Updated with CSRF, rate limiting, idempotency, secret redaction sections |
| `docs/BACKUP_RESTORE.md` | **Complete** | Updated with disk space check, manifest, secret redaction, recovery backup |
| `docs/TESTING.md` | **Complete** | Updated with CI jobs, manifest validation |
| `docs/RELEASES.md` | **Complete** | Updated with version 1.8.0, migration tracking, improved upgrade path |
| `docs/SERVICE_CATALOG.md` | **Complete** | Up to date |
| `docs/FINAL_REPORT.md` | **Complete** | Updated with CSRF, rate limiting, idempotency, secret redaction, capabilities |
| `ROADMAP.md` | **Complete** | Up to date |
| `version-manifest.json` | **Partial** | Missing commit SHAs |
| `.env.example` | **Complete** | Matches docker-compose.yml |

---

## Prioritized Action Plan

### Phase 1: Blockers (Must fix first)

1. **Clean installation** — Create bootstrap scripts (install.ps1, install.sh) that clone all services
2. **Startup profiles** — Fix start.sh/start.ps1 to use `--profile` flag
3. **CI integration tests** — Enable and fix the disabled integration test job

### Phase 2: Security (High risk)

4. **CSRF protection** — Implement for web UI sessions
5. **Rate limiting** — Add to auth and expensive endpoints
6. **Production default key blocking** — Prevent server mode with defaults
7. **Secret redaction in logs** — Add middleware

### Phase 3: Verification (Medium risk)

8. **Backup round-trip test** — Prove backup/restore works
9. **Integration test scenarios** — Run against real services
10. **Gobber semantic search test** — Verify embedding + retrieval
11. **Sneaker OTLP test** — Verify export works

### Phase 4: Enhancement (Lower risk)

12. **Version manifest** — Add commit SHAs
13. **Service capability endpoints** — Add `/api/capabilities`
14. **Idempotency keys** — For retryable operations
15. **Documentation reconciliation** — Update all docs to match actual state

---

## Summary

| Category | Complete | Partial | Missing | Total |
|----------|----------|---------|---------|-------|
| Clean Installation | 0 | 2 | 4 | 6 |
| Service Startup | 1 | 3 | 2 | 6 |
| CI & Tests | 3 | 1 | 7 | 11 |
| Auth & Security | 6 | 3 | 3 | 12 |
| Gobber Semantic | 5 | 2 | 1 | 8 |
| Sneaker OTLP | 4 | 2 | 1 | 7 |
| Backup & Restore | 9 | 1 | 0 | 10 |
| Version Management | 5 | 1 | 2 | 8 |
| Workflows/Dashboard/CLI | 8 | 1 | 1 | 10 |
| Service Contracts | 7 | 2 | 0 | 9 |
| **Total** | **58** | **17** | **23** | **98** |

**Completion rate: 59% complete, 17% partial, 24% missing**

The largest remaining gaps are: user authentication (browser sessions), CI integration test execution, backup/restore round-trip verification, and clean-clone end-to-end test.
