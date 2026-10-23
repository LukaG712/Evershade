# Agent Workstations

**Service:** Greenie (hub/workstation/)
**Description:** Isolated, persistent, computer-like environments for AI agents.

A workstation is an isolated Linux environment – its own filesystem, shell, installed tools, and optionally a browser and full desktop – assigned to an agent. The agent does real work there (builds, runs servers, executes tests, uses a browser) without touching the host, the user's files, other agents or the rest of the network.

---

## Model

- **Linux first.** Windows and macOS workstations are out of scope.
- **One workstation per agent** by default. Sharing across agents requires explicit configuration.
- **Declarative templates** define: base image, installed tools, resource limits, network policy, persistence mode, and desktop inclusion.
- **Persistence modes:**
  - `ephemeral`: Destroyed after the task.
  - `persistent`: Home volume survives restarts.
  - `snapshotted`: Can be restored to a previous state.

### Built-in Templates

| Template | Description | Base Image | Tools |
|----------|-------------|------------|-------|
| `minimal-shell` | Lightweight shell environment | `ubuntu:24.04` | bash, git, curl |
| `python-dev` | Python development | `python:3.12-slim` | python, pip, git, pytest |
| `node-dev` | Node.js development | `node:20-slim` | node, npm, git |
| `desktop-browser` | Full desktop with browser | `ubuntu:24.04` | firefox, TightVNC, noVNC |

---

## Drivers

All backends are behind one driver interface:

### 1. Container Driver (Default)

Hardened containers as the default workstation runtime. Headless with shell, files, and Git. Optional desktop image runs a lightweight desktop with browser, exposed through noVNC.

- Uses Docker SDK for container lifecycle
- Networks isolated via `evershade-workstations` Docker network
- Resource limits enforced via Docker CPU/memory constraints

### 2. VM Driver (Optional)

KVM virtual machines through libvirt or Proxmox API for stronger isolation. Supports Docker inside the workstation and full desktop.

### 3. Registered-Machine Driver (Experimental)

An existing physical PC or VM registered over SSH using a dedicated unprivileged account.

---

## Security

Every workstation is treated as untrusted and potentially compromised.

### Network Policy

- **Default-deny** for private address ranges, LAN, host, cloud metadata endpoints, other workstations, and Evershade internal services.
- Outbound internet access is configurable per template (off, allowlist, or open).
- DNS is controlled. No inbound access except through the gateway.
- Enforced at the Docker network level, not inside the container.

### Runtime Privilege

- No privileged mode, host networking, host mounts, devices, added capabilities, or Docker socket access.
- Seccomp and AppArmor profiles applied where available.
- Runs as non-root user with `no-new-privileges`.
- Read-only base layers.

### Secrets

- No long-lived credentials inside a workstation.
- Short-lived, scoped credentials from Hider when needed.
- Secrets redacted from logs and recordings.
- Credentials revoked on workstation destroy.

### No Lateral Movement

- Agents collaborate through Gobber, Git, or Greenie artifacts.
- Never through workstation-to-workstation network access.

---

## Lifecycle Operations

| Operation | Description |
|-----------|-------------|
| `create` | Allocate a new workstation from a template |
| `start` | Start a stopped workstation |
| `stop` | Stop a running workstation (preserves state) |
| `destroy` | Permanently remove workstation and its data |
| `health` | Check workstation health status |
| `exec` | Execute a command inside the workstation |
| `logs` | Retrieve container logs |

---

## Human Access

All access is proxied through the authenticated Greenie gateway.

- **Live Terminal:** WebSocket-based TTY access
- **Desktop View:** VNC/noVNC for desktop templates
- **File Browser:** View and download files from workstation
- **Status & Resources:** CPU, memory, disk usage
- **Take-over:** Requires permission, pauses or notifies the agent, and is recorded in audit trail

---

## Quotas and Admission Control

- Per-workstation CPU, memory, disk, and process limits
- Global cap on concurrent workstations derived from host capacity
- Excess requests queue visibly
- No silent overcommit

---

## Integration

### Workflow Engine

Workflow steps can allocate, use, snapshot, and release a workstation. The `WORKSTATION` step type supports: create, start, exec, stop, destroy actions.

### Slinker

Slinker's runner executes inside the workstation. Isolation levels: `worktree`, `container`, `workstation`.

### Activity Timeline

Records which workstation and driver were used, lifecycle events, command metadata, file changes, snapshots, and human attach sessions.

---

## API Endpoints

All endpoints require Bearer token authentication.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/workstations` | List all workstations |
| POST | `/api/workstations` | Create a workstation |
| GET | `/api/workstations/{id}` | Get workstation details |
| POST | `/api/workstations/{id}/start` | Start a workstation |
| POST | `/api/workstations/{id}/stop` | Stop a workstation |
| DELETE | `/api/workstations/{id}` | Destroy a workstation |
| GET | `/api/workstations/{id}/health` | Health check |
| GET | `/api/workstations/{id}/logs` | Container logs |
| POST | `/api/workstations/{id}/exec` | Execute command |
| GET | `/api/workstations/{id}/network-policy` | Get network policy |
| PUT | `/api/workstations/{id}/network-policy` | Update network policy |
| GET | `/api/workstations/{id}/access` | Get access info (VNC URL, etc.) |
| GET | `/api/workstations/stats` | Workstation statistics |

---

## Operations

### Reconciliation

On startup, the workstation manager detects orphaned containers, volumes, and networks and cleans them up or adopts them. Crashes do not leak resources.

### Cleanup

Destroying a workstation removes all containers, volumes, and networks. No residual state remains.

### Emergency Stop

The emergency stop pauses or destroys workstations as configured.

---

## Limitations

- Linux-only workstations
- VM driver requires KVM hardware virtualization
- Registered-machine driver is experimental
- GPU passthrough requires additional configuration
- Session recording is off by default
