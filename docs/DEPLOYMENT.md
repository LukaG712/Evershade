# Evershade Deployment Guide

**Version:** 1.0.0
**Last Updated:** 2026-10-23

---

## 1. Quick Start (Desktop)

The fastest way to get Evershade running on your local machine:

```bash
# Clone and configure
git clone https://github.com/LukaG712/Evershade.git && cd Evershade
cp .env.example .env
# Edit .env with your API keys

# Start core services
docker compose --profile minimal up -d

# Dashboard: http://localhost:8080
```

### Before Deploying

| Check | Command |
|-------|---------|
| Docker is running | `docker info` |
| Docker Compose available | `docker compose version` |
| Ports are free | `netstat -ano \| findstr :8080` (Windows) |
| Enough disk space | `df -h` (Linux/macOS) or `Get-PSDrive C \| Select Used,Free` (Windows) |
| Enough RAM | At least 4 GB available |

---

## 2. Installation Profiles

| Profile | Services | Use Case |
|---------|----------|----------|
| `minimal` | Greenie, Slinker, Trapper, Gobber, Redis | Core functionality only |
| `standard` | + Sneaker, Hider, Poltergeist, Shrewd | Full feature set |
| `full` | + Slammer dashboard | Everything |
| `ollama` | Ollama service | Local LLM support |
| `proxy` | Caddy reverse proxy | TLS termination |
| `dev` | All services, all ports exposed | Development |

```bash
# Standard installation
docker compose --profile standard up -d

# With local Ollama
docker compose --profile standard --profile ollama up -d

# With reverse proxy
docker compose --profile standard --profile proxy up -d
```

---

## 3. Server Mode (Headless VM)

### Prerequisites

- Ubuntu 22.04 or 24.04 LTS (headless server install)
- Docker Engine + Compose plugin (from Docker's official apt repo, not snap)
- Minimum 4 CPU, 8 GB RAM, 20 GB disk

### Installation

```bash
# SSH into your server
ssh user@server

# Install Docker (if not already installed)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Clone and configure
git clone https://github.com/LukaG712/Evershade.git && cd Evershade
cp .env.example .env

# Edit .env for server mode
sed -i 's/EVERSHADE_MODE=desktop/EVERSHADE_MODE=server/' .env
sed -i 's/EVERSHADE_BIND_ADDRESS=127.0.0.1/EVERSHADE_BIND_ADDRESS=0.0.0.0/' .env
sed -i 's|EVERSHADE_PUBLIC_URL=http://localhost:8080|EVERSHADE_PUBLIC_URL=http://YOUR_SERVER_IP:8080|' .env

# Generate secure API keys
openssl rand -hex 32  # Replace each change-me-* value

# Start
docker compose --profile standard up -d
```

### Access from Windows PC

#### Option 1: SSH Tunnel (Recommended)

```powershell
# PowerShell on Windows
ssh -L 8080:localhost:8080 user@server

# Browser: http://localhost:8080
```

#### Option 2: VPN (Tailscale/WireGuard)

Install Tailscale on both the server and Windows PC. Access via the Tailscale IP.

#### Option 3: Reverse Proxy with TLS

```bash
# On the server
docker compose --profile standard --profile proxy up -d

# Trust Caddy's internal CA on Windows:
# 1. Copy the Caddy CA certificate to Windows
# 2. Import into Trusted Root Certification Authorities
```

#### Option 4: LAN HTTP (Explicit Opt-In)

Access via `http://SERVER_IP:8080`. **Warning:** Credentials and cookies are sent in plain text on the network.

---

## 4. Proxmox VM Setup

1. Create a KVM virtual machine (not LXC)
2. Bridged networking on `vmbr0` for LAN address
3. DHCP reservation or static IP
4. QEMU guest agent enabled
5. CPU type: `host`
6. Disk: 20+ GB, RAM: 8+ GB (see `docs/RESOURCES.md`)
7. Install Ubuntu server, then follow server mode instructions

**Note:** Docker inside LXC containers is unsupported unless specifically configured. KVM VMs are recommended.

---

## 5. Auto-Start After Reboot

Services use `restart: unless-stopped` policy. To ensure Docker starts on boot:

```bash
sudo systemctl enable docker
```

For systemd integration:

```bash
# Create a systemd service
sudo tee /etc/systemd/system/evershade.service > /dev/null << 'EOF'
[Unit]
Description=Evershade Platform
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/Evershade
ExecStart=/usr/local/bin/docker compose --profile standard up -d
ExecStop=/usr/local/bin/docker compose down

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable evershade
```

---

## 6. Firewall Configuration

Docker bypasses UFW. Use the `DOCKER-USER` chain:

```bash
# Allow gateway port from LAN subnet only
sudo iptables -I DOCKER-USER -i eth0 -p tcp --dport 8080 -s 192.168.1.0/24 -j ACCEPT
sudo iptables -I DOCKER-USER -i eth0 -p tcp --dport 8080 -j DROP
```

Or bind published ports to a specific address in docker-compose.yml.

---

## 7. Troubleshooting

### "I can't reach the dashboard"

1. **Check bind address:** `EVERSHADE_BIND_ADDRESS` must be `0.0.0.0` for remote access
2. **Check firewall:** Verify port 8080 is reachable from your network
3. **Check NAT:** If behind a router, port forwarding may be needed (or use SSH tunnel)
4. **Check IP:** Verify you're using the correct server IP
5. **Run diagnostics:** `evershade doctor` (on server) or `evershade remote test` (from Windows)

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Port already in use | Another service on port 8080 | Change port in docker-compose.yml |
| Default API key warning | Using example keys | Generate new keys in `.env` |
| Ollama unreachable | Wrong URL for Linux Docker | Set `EVERSHADE_OLLAMA_URL` to actual IP |
| Database locked | Multiple processes accessing SQLite | Ensure only one Greenie instance |

---

## 8. Upgrades

```bash
# Pull latest changes
git pull

# Backup first
evershade backup

# Restart with new images
docker compose up -d --build
```

See `docs/RELEASES.md` for version compatibility and migration notes.

---

## 9. Production Hardening Checklist

Before deploying to production:

- [ ] **API keys:** All default keys replaced with strong random values
- [ ] **TLS:** Caddy proxy profile enabled or external reverse proxy configured
- [ ] **Firewall:** Only ports 80/443 exposed; internal services not accessible from host
- [ ] **Backups:** Automated backup schedule configured
- [ ] **Monitoring:** Sneaker alerts configured with Poltergeist delivery
- [ ] **Resource limits:** CPU and memory limits appropriate for workload
- [ ] **Log rotation:** Logs configured to prevent disk exhaustion
- [ ] **Health checks:** All service health endpoints responding
- [ ] **Rate limiting:** Configured for expected traffic patterns
- [ ] **Secrets:** `.env` file permissions restricted (e.g., `chmod 600 .env`)

---

## 10. High Availability Considerations

Evershade is designed for single-instance deployment. For higher availability:

### What Survives Restart

- **Docker volumes:** All SQLite databases persist across restarts
- **Redis AOF:** Job queue data survives restarts
- **Workspace:** Git worktrees and files persist

### What Doesn't Survive Restart

- **In-memory state:** Active sessions, in-memory caches
- **Running tasks:** In-progress agent tasks are cancelled
- **Ollama models:** Models persist in `ollama_data` volume

### Recommended Backup Strategy

| Frequency | What | Method |
|-----------|------|--------|
| Every hour | SQLite databases | `evershade backup --incremental` |
| Daily | Full system | `evershade backup --full` |
| Weekly | Off-site copy | SCP backup to remote server |
| Before upgrade | Full system | Manual backup before `git pull` |
