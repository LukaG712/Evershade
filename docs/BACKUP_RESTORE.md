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
evershade backup create

# This creates a timestamped backup in ./backups/
# Example: backups/evershade-20261022-101500.tar.gz

# Include secrets (default: redacted)
evershade backup create --include-secrets

# Custom output path
evershade backup create --output ./my-backup.tar.gz
```

The backup includes:
- All SQLite databases (using `sqlite3 .backup` API for consistent snapshots)
- Configuration files (`.env` is redacted by default – secrets replaced with `<redacted>`)
- Backup manifest (`manifest.json`) with SHA-256 checksums for all files
- **Free disk space check** before starting – fails gracefully if insufficient space

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

## 3. Restore

```bash
# Restore from a specific backup
evershade backup restore backups/evershade-20261022-101500.tar.gz

# Dry run (validate without restoring)
evershade backup restore --dry-run backups/evershade-20261022-101500.tar.gz
```

**Warning:** Restore replaces current data. A pre-restore recovery backup is created automatically in `backups/recovery/`.

The restore process:
1. Verifies archive integrity (SHA-256 checksums)
2. Checks for path traversal attacks in archive entries
3. Creates a recovery backup of current data
4. Stops services if running
5. Restores databases and configuration
6. Verifies restored data integrity

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
