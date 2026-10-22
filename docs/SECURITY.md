# Evershade Security Model

**Version:** 1.1.0
**Last Updated:** 2026-10-22

---

## 1. Security Principles

1. **Least privilege** — Every service runs with minimal permissions.
2. **Defense in depth** — Multiple layers of protection; no single point of failure.
3. **Network isolation** — Services communicate on an internal network; only the gateway is exposed.
4. **Secrets protection** — Credentials are encrypted at rest and never logged.
5. **Untrusted content** — All external content (web pages, repositories, notes) is treated as untrusted data.

---

## 2. Authentication

### Service-to-Service

All services authenticate using API keys passed via the `Authorization: Bearer` header. Query parameter authentication (`x_key`, `api-key`) has been **removed** — it is no longer supported. All services use constant-time comparison (`hmac.compare_digest`) to prevent timing attacks.

**Auth header format:**
```
Authorization: Bearer <your-api-key>
```

### User Authentication

Greenie provides user authentication with:
- API key-based access for programmatic clients
- Session management for web UI users
- Role-based access control (RBAC) via Gobber

### API Tokens

- Scoped tokens (read-only, operator, admin)
- Revocable at any time
- Shown only once at creation
- Stored securely (Windows Credential Manager or permission-protected file)

---

## 3. Network Security

### Default Deployment

- Only Greenie (port 8080) is published to the host
- All other services are on an internal Docker network
- No direct host access to Slinker, Trapper, Gobber, or supporting services

### Server Mode

- Greenie binds to all interfaces (`0.0.0.0`)
- Reverse proxy (Caddy) provides TLS termination
- Trusted proxy headers (`X-Forwarded-For`, `X-Forwarded-Proto`) are validated

### Container Hardening

Every service container applies:
- `cap_drop: ALL` — Drop all Linux capabilities
- `security_opt: no-new-privileges` — Prevent privilege escalation
- `read_only: true` — Read-only root filesystem (all services)
- `tmpfs` mounts for writable directories (`/tmp`, `/app/data`, `/app/logs`)
- Resource limits (CPU, memory, processes)

---

## 4. Secrets Management

### Hider Service

- AES-256-GCM authenticated encryption for all secrets at rest
- Encryption key derived from `ENCRYPTION_KEY` environment variable via SHA-256
- SQLite persistence — secrets survive container restarts
- Secrets are never logged or exposed in list API responses (only in GET by key)
- 96-bit random nonce per encryption operation (no nonce reuse)
- **Important:** Set a strong `ENCRYPTION_KEY` in production. Default key will be blocked in server mode.

### API Keys

- Generate unique keys per service: `openssl rand -hex 32`
- Never commit `.env` files to version control
- Server mode refuses to start with default keys
- Key rotation supported without downtime

---

## 5. Agent Execution Security

### Slinker Isolation Levels

| Level | Security Boundary | Use Case |
|-------|-------------------|----------|
| `worktree` | **None** — shares host filesystem | Trusted development only |
| `container` | **Yes** — isolated container | Default for untrusted code |
| `workstation` | **Yes** — full VM isolation | Maximum isolation |

### Command Execution

- Per-task workspaces with explicit repository boundaries
- Execution time and resource limits
- Cancellation and cleanup on failure
- Concurrent job isolation

---

## 6. Prompt Injection Defense

All content from external sources is treated as **data, not instructions**:

- Web pages scraped by Trapper
- Repository files accessed by Slinker
- Obsidian notes indexed by Gobber
- Retrieved memory entries
- External tool output

**Rules:**
1. Untrusted content cannot trigger tool calls
2. Untrusted content cannot grant or bypass approvals
3. Untrusted content cannot change permissions or request secrets
4. Approval prompts show the concrete action, not model-written justification
5. Planning (reading untrusted content) is separated from execution (side effects)

---

## 7. Browser Security (Trapper)

- URL allowlisting and private IP blocking
- Cloud metadata endpoint blocking
- Redirect abuse prevention
- Resource exhaustion protection
- Browser isolation from host network

---

## 8. Emergency Stop

The emergency stop (`evershade panic`) provides a global kill switch:

1. Pauses all workflow execution and triggers
2. Cancels running Slinker jobs and cleans up sandboxes
3. Optionally revokes active sessions and tokens
4. Records an audit event
5. Sends notification via Poltergeist (if available)
6. Can be reversed deliberately

---

## 8. CSRF Protection

Greenie implements CSRF protection for cookie-authenticated browser sessions:

- CSRF tokens are required for state-changing requests (POST, PUT, DELETE)
- Bearer-authenticated API clients are exempt (not vulnerable to CSRF)
- Origin/Referer header validation for cross-origin requests
- Configurable excluded paths (health checks, metrics, etc.)

## 9. Rate Limiting

Greenie applies rate limiting to prevent abuse:

- **Authentication failures**: 10 failures per 60 seconds per IP address
- **Expensive operations**: Stricter limits for LLM requests (20/min), code execution (5/min), workflow creation (10/min), web crawling (10/min)
- **Default limit**: 60 requests per minute for other endpoints
- Sliding window algorithm with per-IP and per-API-key tracking
- Configurable via `RATE_LIMIT_ENABLED` and `RATE_LIMIT_DEFAULT_REQUESTS` environment variables

## 10. Idempotency

Retryable operations support idempotency keys via the `X-Idempotency-Key` header:

- Safe retries for workflow creation, agent execution, and backup operations
- Original response is returned for duplicate keys without re-execution
- Keys expire after 24 hours by default (configurable via `IDEMPOTENCY_TTL_SECONDS`)
- Enabled by default (disable via `IDEMPOTENCY_ENABLED=false`)

## 11. Secret Redaction

Sensitive data is automatically redacted from log output:

- API keys, passwords, tokens, and secrets are replaced with `[REDACTED]`
- Applies to all log levels and formats (JSON and plain text)
- Covers common patterns: Bearer tokens, AWS credentials, private keys, connection strings
- Enabled by default (disable via `REDACT_SECRETS=false`)

## 12. Residual Risks

| Risk | Status | Mitigation |
|------|--------|------------|
| Worktree mode is not a security boundary | **Documented** | Default to container mode; document worktree limitations |
| SSRF via Trapper | **Mitigated** | Private IP blocking, metadata endpoint blocking |
| Docker socket access for workstation manager | **Accepted** | Isolated behind narrow authenticated interface |
| DNS rebinding after SSRF check | **Accepted** | SSRF check validates URL at request time; DNS resolution happens at fetch time. Mitigated by network isolation. |
| User authentication (browser sessions) | **Planned** | Full user accounts with sessions not yet implemented; API key auth is sufficient for single-operator deployments |

---

## 13. Reporting Security Issues

Report security vulnerabilities to the repository maintainers. Do not open public issues for security concerns.

**Responsible disclosure:** Allow reasonable time for patches before public disclosure.
