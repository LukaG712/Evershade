# Evershade Backup and Restore Guide

**Version:** 1.0.0
**Last Updated:** 2026-10-22

---

## 1. What Gets Backed Up

| Data | Location | Method |
|------|----------|--------|
| Greenie database | `greenie_data` volume | SQLite online backup API |
| Slinker tasks | `slinker_logs` volume + Slinker.db | SQLite online backup API |
| Gobber data | `gobber_data` volume | SQLite online backup API |
| Sneaker data | `sneaker_data` volume | SQLite online backup API |
| Hider secrets | `hider_data` volume | SQLite online backup API |
| Poltergeist data | `poltergeist_data` volume | SQLite online backup API |
| Redis data | `redis_data` volume | `BGSAVE` + copy |
| Configuration | `.env`, `hub.yaml` | File copy |
| Workspace | `./workspace` | File copy (optional) |
| Obsidian vault | External mount | Not included (managed separately) |

---

## 2. Manual Backup

```bash
# Using the CLI (recommended)
evershade backup

# This creates a timestamped backup in ./backups/
# Example: backups/evershade_20261022_101500.tar.gz
```

The backup includes:
- All SQLite databases (using the online backup API, not raw file copy)
- Redis RDB snapshot
- Configuration files (`.env` is excluded unless explicitly requested)
- Backup manifest with checksums

---

## 3. Scheduled Backups

Configure scheduled backups in Greenie's dashboard or via API:

```bash
# Example: daily backup at 2 AM
curl -X POST http://localhost:8080/api/backups/schedule \
  -H "Authorization: Bearer $EVERSHADE_GREENIE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"schedule": "0 2 * * *", "retention_days": 7}'
```

---

## 4. Restore

```bash
# List available backups
evershade backup --list

# Restore from a specific backup
evershade restore backups/evershade_20261022_101500.tar.gz

# Dry run (validate without restoring)
evershade restore --dry-run backups/evershade_20261022_101500.tar.gz
```

**Warning:** Restore replaces current data. A pre-restore backup is created automatically.

---

## 5. Backup Integrity

```bash
# Verify backup integrity
evershade backup --verify backups/evershade_20261022_101500.tar.gz
```

This checks:
- Archive integrity (tar.gz validation)
- Checksums match manifest
- Database files are valid SQLite
- All expected services are present

---

## 6. Retention Policy

Default: 7 days for automated backups, unlimited for manual backups.

Configure via Greenie dashboard or API. Expired backups are deleted automatically.

---

## 7. Export for Migration

```bash
# Export data in portable format
evershade backup --export ./migration-export.tar.gz

# This creates a backup compatible across versions
```

---

## 8. Disaster Recovery

1. Stop all services: `docker compose down`
2. Restore from backup: `evershade restore <backup-file>`
3. Start services: `docker compose --profile standard up -d`
4. Verify: `evershade status`

If no backup exists:
- Greenie, Slinker, and Gobber data is in Docker volumes
- Volumes survive `docker compose down` (use `docker compose down -v` to delete)
- Recreate `.env` from your records
