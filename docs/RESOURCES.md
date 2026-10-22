# Evershade Resource Requirements

**Version:** 1.0.0
**Last Updated:** 2026-10-22

---

## 1. Minimum Requirements

| Profile | CPU | RAM | Disk | Network |
|---------|-----|-----|------|---------|
| **Minimal** | 2 cores | 4 GB | 10 GB | Local only |
| **Standard** | 4 cores | 8 GB | 20 GB | Local only |
| **Full** | 4 cores | 8 GB | 20 GB | Local only |
| **+ Ollama** | 8 cores | 16 GB | 40 GB | Local only |
| **Server** | 4 cores | 8 GB | 20 GB | LAN/Internet |

---

## 2. Per-Service Resource Limits

| Service | CPU Limit | Memory Limit | CPU Reserve | Memory Reserve |
|---------|-----------|--------------|-------------|----------------|
| Greenie | 2.0 | 2G | 0.50 | 512M |
| Slinker | 2.0 | 2G | 0.50 | 512M |
| Trapper-api | 2.0 | 1G | 0.50 | 256M |
| Trapper-worker | 2.0 | 1G | 0.50 | 256M |
| Gobber | 1.0 | 512M | 0.25 | 128M |
| Sneaker | 0.50 | 256M | 0.25 | 128M |
| Hider | 0.50 | 256M | 0.25 | 128M |
| Poltergeist | 0.50 | 256M | 0.25 | 128M |
| Shrewd | 1.0 | 512M | 0.25 | 128M |
| Slammer | 0.50 | 256M | 0.25 | 128M |
| Redis | 0.50 | 256M | 0.25 | 128M |
| Ollama | 4.0 | 8G | 1.0 | 2G |

---

## 3. Disk Usage

| Component | Typical Size | Growth Rate |
|-----------|-------------|-------------|
| Greenie SQLite | 10-100 MB | ~1 MB/day |
| Slinker SQLite + logs | 50-500 MB | ~5 MB/day |
| Gobber SQLite + KG | 50-500 MB | Depends on vault size |
| Redis AOF | 10-50 MB | ~1 MB/day |
| Docker images | 2-4 GB | One-time |
| Ollama models | 4-8 GB per model | One-time per model |

---

## 4. Network Bandwidth

| Operation | Typical Usage |
|-----------|--------------|
| API requests | < 1 MB/hour |
| Web scraping | Depends on target sites |
| LLM requests | 1-10 MB per conversation |
| Ollama download | 4-8 GB per model (one-time) |

---

## 5. Recommended VM Sizes

### Proxmox / Cloud VPS

| Tier | CPU | RAM | Disk | Use Case |
|------|-----|-----|------|----------|
| **Small** | 2 vCPU | 4 GB | 20 GB SSD | Minimal profile, light use |
| **Medium** | 4 vCPU | 8 GB | 40 GB SSD | Standard profile, normal use |
| **Large** | 8 vCPU | 16 GB | 80 GB SSD | Full + Ollama, heavy use |

---

## 6. Performance Benchmarks

Benchmarks are measured on a 4-core, 8GB RAM machine with SSD storage.

| Metric | Value |
|--------|-------|
| Startup time (minimal) | ~30 seconds |
| Startup time (standard) | ~45 seconds |
| API latency (p95) | < 100ms |
| Concurrent workflows | 1-4 (depends on workers) |
| Idle RAM (minimal) | ~1.5 GB |
| Idle RAM (standard) | ~2.5 GB |

---

## 7. Scaling Notes

- **Greenie:** Single-instance. For multi-instance, shared Redis/PostgreSQL is required.
- **Slinker:** Scale by increasing `MAX_CONCURRENT_WORKERS`. Each worker needs ~512MB RAM.
- **Trapper:** Scale workers independently. Each worker needs ~256MB RAM.
- **Ollama:** GPU acceleration recommended for models > 7B parameters.
