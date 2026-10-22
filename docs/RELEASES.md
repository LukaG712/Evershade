# Evershade Release Notes

**Version:** 1.0.0
**Last Updated:** 2026-10-22

---

## Version Compatibility

| Evershade | Greenie | Slinker | Trapper | Gobber | Others |
|-----------|---------|---------|---------|--------|--------|
| 1.0.0 | 1.0.3 | 1.0.0 | 1.0.0 | 1.0.0 | 1.0.0 |

---

## Upgrade Path

### From Previous Versions

1. **Backup your data:** `evershade backup`
2. **Pull latest code:** `git pull`
3. **Review .env.example:** Check for new variables
4. **Update .env:** Add any new required variables
5. **Rebuild and restart:** `docker compose up -d --build`
6. **Verify:** `evershade status`

### Breaking Changes in 1.0.0

- Environment variable naming standardized to `EVERSHADE_<SERVICE>_<SETTING>`
- Legacy names still work but are deprecated
- Docker Compose profiles introduced (use `--profile` flag)
- Internal Docker network — only Greenie exposed on host by default
- Container hardening applied (capability dropping, no-new-privileges)

---

## Rollback Procedure

1. Stop services: `docker compose down`
2. Restore backup: `evershade restore <backup-file>`
3. Checkout previous version: `git checkout <previous-tag>`
4. Restart: `docker compose up -d`

---

## Release Process

1. Update version in `version-manifest.json`
2. Update `CHANGELOG.md`
3. Tag release: `git tag -a v1.0.0 -m "Release v1.0.0"`
4. Push: `git push origin main --tags`
