# Evershade Release Notes

**Version:** 1.14.0
**Last Updated:** 2026-10-23

---

## Version Compatibility

| Evershade | Greenie | Slinker | Trapper | Gobber | Sneaker | Hider | Poltergeist | Shrewd | Slammer | Speedy |
|-----------|---------|---------|---------|--------|---------|-------|-------------|--------|---------|--------|
| 1.14.0 | 1.8.0 | 1.2.0 | 1.1.0 | 1.1.0 | 1.2.0 | 1.1.0 | 1.2.0 | 1.2.0 | 1.4.0 | 1.2.0 |
| 1.12.0 | 1.7.0 | 1.1.0 | 1.0.0 | 1.0.0 | 1.1.0 | 1.0.0 | 1.1.0 | 1.1.0 | 1.4.0 | 1.1.0 |
| 1.0.0 | 1.0.3 | 1.0.0 | 1.0.0 | 1.0.0 | 1.0.0 | 1.0.0 | 1.0.0 | 1.0.0 | 1.0.0 | 1.0.0 |

> Service versions are pinned in `version-manifest.json`. Always check the manifest for the authoritative compatibility matrix.

---

## Upgrade Path

### From Previous Versions

1. **Backup your data:** `evershade backup`
2. **Validate current config:** `evershade config validate`
3. **Pull latest code:** `git pull`
4. **Review .env.example:** Check for new variables
5. **Update .env:** Add any new required variables
6. **Rebuild and restart:** `docker compose up -d --build`
7. **Verify health:** `evershade status`
8. **Run doctor check:** `evershade doctor`

### Breaking Changes in 1.14.0

- All services require `Authorization: Bearer` header — query parameter auth removed
- Hider requires `ENCRYPTION_KEY` environment variable for AES-256-GCM encryption
- Hider secrets are now encrypted at rest in SQLite — migration required from in-memory data
- Slammer is the single dashboard — Greenie operates as API-only backend
- **GUI Installers added**: Linux (`install-gui.py`) and Windows (`install-gui-win.py`) visual wizards

### Breaking Changes in 1.8.0

- Workflow executor: parallel execution enabled by default when milestones are present
- Workflow steps support `max_retries` and `timeout_seconds` in config
- Speedy CLI: new `config validate` command for configuration validation
- Manifest validation added to CI pipeline

### Breaking Changes in 1.7.0

- CSRF protection wired into Greenie; cookie sessions require CSRF token
- Rate limiting on expensive operations (LLM, code execution, workflows)
- Idempotency keys for retryable operations (`X-Idempotency-Key` header)
- Secret redaction in all log output

### Breaking Changes in 1.0.0

- Environment variable naming standardized to `EVERSHADE_<SERVICE>_<SETTING>`
- Legacy names still work but are deprecated
- Docker Compose profiles introduced (use `--profile` flag)
- Internal Docker network – only Greenie exposed on host by default
- Container hardening applied (capability dropping, no-new-privileges)
- All services require `Authorization: Bearer` header – query parameter auth removed
- Hider requires `ENCRYPTION_KEY` environment variable for AES-256-GCM encryption

---

## Rollback Procedure

1. Stop services: `docker compose down`
2. Restore backup: `evershade restore <backup-file>`
3. Checkout previous version: `git checkout <previous-tag>`
4. Restart: `docker compose up -d`
5. Verify: `evershade status`

---

## Release Process

1. Update version in `version-manifest.json`
2. Update `CHANGELOG.md`
3. Validate manifest: `python scripts/validate_manifest.py`
4. Sign release: `python scripts/release_sign.py --version X.Y.Z --sign-all`
5. Tag release: `git tag -a v1.14.0 -m "Release v1.14.0"`
6. Push: `git push origin master --tags`

---

## Migration Tracking

The `version-manifest.json` file tracks database and configuration migrations:

| Migration | Version | Description | Breaking |
|-----------|---------|-------------|----------|
| 1 | 1.0.0 | Hider secrets encrypted at rest in SQLite | Yes |

When upgrading, check `migration_version` in the manifest to ensure all required migrations have been applied.
