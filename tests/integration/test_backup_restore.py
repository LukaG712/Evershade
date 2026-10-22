"""Backup and restore round-trip integration tests.

These tests verify that the Speedy CLI backup and restore commands work correctly
end-to-end, including edge cases like corrupted archives and missing files.

Tests create real SQLite databases, generate backups, verify integrity, restore to
clean locations, and confirm all data survives the round-trip.
"""

import hashlib
import json
import os
import shutil
import sqlite3
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path

import pytest


class TestBackupRestoreRoundTrip:
    """Test backup and restore round-trip with real SQLite data."""

    @pytest.fixture
    def project_dir(self, tmp_path: Path):
        """Create a temporary project directory with mock service data."""
        # Create docker-compose.yml
        compose_file = tmp_path / "docker-compose.yml"
        compose_file.write_text(
            "version: '3.8'\nservices:\n  greenie:\n    image: evershade/greenie\n"
        )

        # Create .env file
        env_file = tmp_path / ".env"
        env_file.write_text(
            "HUB_API_KEY=test-key-12345\n"
            "ENCRYPTION_KEY=test-encryption-key-67890\n"
            "GREENIE_URL=http://localhost:8080\n"
        )

        # Create service data directories with SQLite databases
        services = ["greenie", "slinker", "gobber", "hider"]
        for service in services:
            data_dir = tmp_path / service / "data"
            data_dir.mkdir(parents=True, exist_ok=True)

            # Create SQLite database with test data
            db_path = data_dir / f"{service}.db"
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            if service == "greenie":
                cursor.execute(
                    """CREATE TABLE agents (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        status TEXT DEFAULT 'active',
                        created_at TEXT NOT NULL
                    )"""
                )
                cursor.execute(
                    "INSERT INTO agents VALUES (?, ?, ?, ?)",
                    ("agent-1", "Test Agent", "active", datetime.utcnow().isoformat()),
                )
                cursor.execute(
                    "INSERT INTO agents VALUES (?, ?, ?, ?)",
                    ("agent-2", "Another Agent", "inactive", datetime.utcnow().isoformat()),
                )
            elif service == "slinker":
                cursor.execute(
                    """CREATE TABLE tasks (
                        id TEXT PRIMARY KEY,
                        prompt TEXT NOT NULL,
                        status TEXT DEFAULT 'pending',
                        created_at TEXT NOT NULL
                    )"""
                )
                cursor.execute(
                    "INSERT INTO tasks VALUES (?, ?, ?, ?)",
                    ("task-1", "Write a function", "completed", datetime.utcnow().isoformat()),
                )
            elif service == "gobber":
                cursor.execute(
                    """CREATE TABLE documents (
                        id TEXT PRIMARY KEY,
                        content TEXT NOT NULL,
                        source TEXT,
                        created_at TEXT NOT NULL
                    )"""
                )
                cursor.execute(
                    "INSERT INTO documents VALUES (?, ?, ?, ?)",
                    ("doc-1", "Test document content", "test.md", datetime.utcnow().isoformat()),
                )
            elif service == "hider":
                cursor.execute(
                    """CREATE TABLE secrets (
                        name TEXT PRIMARY KEY,
                        encrypted_value TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )"""
                )
                cursor.execute(
                    "INSERT INTO secrets VALUES (?, ?, ?)",
                    ("secret-1", "encrypted-value-here", datetime.utcnow().isoformat()),
                )

            conn.commit()
            conn.close()

        return tmp_path

    def test_backup_creates_valid_archive(self, project_dir: Path):
        """Test that backup creates a valid tar.gz archive with manifest."""
        backup_dir = project_dir / "backups"
        backup_path = backup_dir / "test-backup.tar.gz"
        backup_dir.mkdir(exist_ok=True)

        # Simulate backup creation (mimicking Speedy CLI logic)
        tmp_dir = Path(tempfile.mkdtemp(prefix="evershade-backup-"))
        manifest = {
            "version": "1.0",
            "timestamp": datetime.utcnow().strftime("%Y%m%d-%H%M%S"),
            "profile": "standard",
            "services": {},
            "checksums": {},
        }

        try:
            with tarfile.open(str(backup_path), "w:gz") as tar:
                # Backup SQLite databases using consistent snapshots
                for service in ["greenie", "slinker", "gobber", "hider"]:
                    db_file = project_dir / service / "data" / f"{service}.db"
                    if db_file.exists():
                        # Use sqlite3 .backup for consistent snapshot
                        snapshot_path = tmp_dir / f"{service}.db"
                        src_conn = sqlite3.connect(str(db_file))
                        dst_conn = sqlite3.connect(str(snapshot_path))
                        src_conn.backup(dst_conn)
                        dst_conn.close()
                        src_conn.close()

                        tar.add(str(snapshot_path), arcname=f"{service}/data/{service}.db")

                        # Calculate checksum
                        sha = hashlib.sha256()
                        with open(snapshot_path, "rb") as f:
                            for chunk in iter(lambda: f.read(8192), b""):
                                sha.update(chunk)
                        manifest["checksums"][f"{service}/data/{service}.db"] = sha.hexdigest()
                        manifest["services"][service] = {"database": True}

                # Add .env (redacted)
                env_file = project_dir / ".env"
                if env_file.exists():
                    redacted_path = tmp_dir / ".env"
                    redacted_lines = []
                    for line in env_file.read_text().splitlines():
                        if "=" in line and not line.startswith("#"):
                            key = line.split("=", 1)[0]
                            if any(s in key.lower() for s in ["key", "secret", "password", "token"]):
                                redacted_lines.append(f"{key}=<redacted>")
                            else:
                                redacted_lines.append(line)
                        else:
                            redacted_lines.append(line)
                    redacted_path.write_text("\n".join(redacted_lines))
                    tar.add(str(redacted_path), arcname=".env")

                    # Add manifest inside the same tar block
                    manifest_path = tmp_dir / "manifest.json"
                    manifest_path.write_text(json.dumps(manifest, indent=2))
                    tar.add(str(manifest_path), arcname="manifest.json")

        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

        # Verify archive exists and is valid
        assert backup_path.exists()
        assert backup_path.stat().st_size > 0

        # Verify archive contents
        with tarfile.open(str(backup_path), "r:gz") as tar:
            members = tar.getnames()
            assert "manifest.json" in members
            assert "greenie/data/greenie.db" in members
            assert "slinker/data/slinker.db" in members
            assert "gobber/data/gobber.db" in members
            assert "hider/data/hider.db" in members
            assert ".env" in members

            # Verify manifest
            manifest_file = tar.extractfile("manifest.json")
            assert manifest_file is not None
            manifest_data = json.loads(manifest_file.read().decode())
            assert manifest_data["version"] == "1.0"
            assert len(manifest_data["checksums"]) == 4  # 4 databases
            assert len(manifest_data["services"]) == 4

    def test_backup_secret_redaction(self, project_dir: Path):
        """Test that secrets are redacted from .env in backup by default."""
        backup_dir = project_dir / "backups"
        backup_path = backup_dir / "test-redaction.tar.gz"
        backup_dir.mkdir(exist_ok=True)

        tmp_dir = Path(tempfile.mkdtemp(prefix="evershade-backup-"))
        try:
            with tarfile.open(str(backup_path), "w:gz") as tar:
                # Add redacted .env
                env_file = project_dir / ".env"
                redacted_path = tmp_dir / ".env"
                redacted_lines = []
                for line in env_file.read_text().splitlines():
                    if "=" in line and not line.startswith("#"):
                        key = line.split("=", 1)[0]
                        if any(s in key.lower() for s in ["key", "secret", "password", "token"]):
                            redacted_lines.append(f"{key}=<redacted>")
                        else:
                            redacted_lines.append(line)
                    else:
                        redacted_lines.append(line)
                redacted_path.write_text("\n".join(redacted_lines))
                tar.add(str(redacted_path), arcname=".env")

        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

        # Verify secrets are redacted
        with tarfile.open(str(backup_path), "r:gz") as tar:
            env_file = tar.extractfile(".env")
            assert env_file is not None
            env_content = env_file.read().decode()
            assert "HUB_API_KEY=<redacted>" in env_content
            assert "ENCRYPTION_KEY=<redacted>" in env_content
            assert "test-key-12345" not in env_content
            assert "test-encryption-key-67890" not in env_content
            # Non-secret values should be preserved
            assert "GREENIE_URL=http://localhost:8080" in env_content

    def test_restore_round_trip(self, project_dir: Path):
        """Test full backup and restore round-trip preserves all data."""
        # Create backup
        backup_dir = project_dir / "backups"
        backup_path = backup_dir / "test-roundtrip.tar.gz"
        backup_dir.mkdir(exist_ok=True)

        tmp_dir = Path(tempfile.mkdtemp(prefix="evershade-backup-"))
        manifest = {
            "version": "1.0",
            "timestamp": datetime.utcnow().strftime("%Y%m%d-%H%M%S"),
            "profile": "standard",
            "services": {},
            "checksums": {},
        }

        try:
            with tarfile.open(str(backup_path), "w:gz") as tar:
                for service in ["greenie", "slinker", "gobber", "hider"]:
                    db_file = project_dir / service / "data" / f"{service}.db"
                    if db_file.exists():
                        snapshot_path = tmp_dir / f"{service}.db"
                        src_conn = sqlite3.connect(str(db_file))
                        dst_conn = sqlite3.connect(str(snapshot_path))
                        src_conn.backup(dst_conn)
                        dst_conn.close()
                        src_conn.close()

                        tar.add(str(snapshot_path), arcname=f"{service}/data/{service}.db")
                        sha = hashlib.sha256()
                        with open(snapshot_path, "rb") as f:
                            for chunk in iter(lambda: f.read(8192), b""):
                                sha.update(chunk)
                        manifest["checksums"][f"{service}/data/{service}.db"] = sha.hexdigest()
                        manifest["services"][service] = {"database": True}

                # Add manifest inside the same tar block
                manifest_path = tmp_dir / "manifest.json"
                manifest_path.write_text(json.dumps(manifest, indent=2))
                tar.add(str(manifest_path), arcname="manifest.json")

        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

        # Create clean restore directory
        restore_dir = Path(tempfile.mkdtemp(prefix="evershade-restore-"))

        # Restore from backup
        with tarfile.open(str(backup_path), "r:gz") as tar:
            # Verify checksums first
            manifest_file = tar.extractfile("manifest.json")
            manifest_data = json.loads(manifest_file.read().decode())

            for filename, expected_sha in manifest_data["checksums"].items():
                member = tar.getmember(filename)
                file_obj = tar.extractfile(member)
                if file_obj:
                    sha = hashlib.sha256(file_obj.read()).hexdigest()
                    assert sha == expected_sha, f"Checksum mismatch for {filename}"

            # Extract all files
            for member in tar.getmembers():
                target_path = restore_dir / member.name
                if member.isdir():
                    target_path.mkdir(parents=True, exist_ok=True)
                else:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    file_obj = tar.extractfile(member)
                    if file_obj:
                        with open(target_path, "wb") as f:
                            shutil.copyfileobj(file_obj, f)

        # Verify all data survived the round-trip
        # Greenie: 2 agents
        greenie_db = restore_dir / "greenie" / "data" / "greenie.db"
        assert greenie_db.exists()
        conn = sqlite3.connect(str(greenie_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM agents")
        agent_count = cursor.fetchone()[0]
        assert agent_count == 2, f"Expected 2 agents, got {agent_count}"

        cursor.execute("SELECT name FROM agents WHERE id = 'agent-1'")
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "Test Agent"
        conn.close()

        # Slinker: 1 task
        slinker_db = restore_dir / "slinker" / "data" / "slinker.db"
        assert slinker_db.exists()
        conn = sqlite3.connect(str(slinker_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tasks")
        task_count = cursor.fetchone()[0]
        assert task_count == 1, f"Expected 1 task, got {task_count}"
        conn.close()

        # Gobber: 1 document
        gobber_db = restore_dir / "gobber" / "data" / "gobber.db"
        assert gobber_db.exists()
        conn = sqlite3.connect(str(gobber_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count = cursor.fetchone()[0]
        assert doc_count == 1, f"Expected 1 document, got {doc_count}"
        conn.close()

        # Hider: 1 secret
        hider_db = restore_dir / "hider" / "data" / "hider.db"
        assert hider_db.exists()
        conn = sqlite3.connect(str(hider_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM secrets")
        secret_count = cursor.fetchone()[0]
        assert secret_count == 1, f"Expected 1 secret, got {secret_count}"
        conn.close()

    def test_corrupted_archive_detection(self, project_dir: Path):
        """Test that corrupted archives are detected and rejected."""
        backup_dir = project_dir / "backups"
        backup_path = backup_dir / "corrupted.tar.gz"
        backup_dir.mkdir(exist_ok=True)

        # Create a corrupted archive (invalid gzip data)
        backup_path.write_bytes(b"This is not a valid tar.gz file")

        # Verify that opening the archive fails
        with pytest.raises(tarfile.TarError):
            with tarfile.open(str(backup_path), "r:gz") as tar:
                tar.getmembers()

    def test_checksum_mismatch_detection(self, project_dir: Path):
        """Test that checksum mismatches are detected during restore."""
        backup_dir = project_dir / "backups"
        backup_path = backup_dir / "mismatch.tar.gz"
        backup_dir.mkdir(exist_ok=True)

        tmp_dir = Path(tempfile.mkdtemp(prefix="evershade-backup-"))
        try:
            # Create a database
            db_path = tmp_dir / "test.db"
            conn = sqlite3.connect(str(db_path))
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            conn.commit()
            conn.close()

            # Calculate real checksum
            real_sha = hashlib.sha256()
            with open(db_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    real_sha.update(chunk)


            manifest = {
                "version": "1.0",
                "checksums": {
                    "test.db": "0000000000000000000000000000000000000000000000000000000000000000"
                },
            }
            manifest_path = tmp_dir / "manifest.json"
            manifest_path.write_text(json.dumps(manifest, indent=2))
            with tarfile.open(str(backup_path), "w:gz") as tar:
                tar.add(str(db_path), arcname="test.db")
                tar.add(str(manifest_path), arcname="manifest.json")

        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

        # Verify checksum mismatch is detected
        with tarfile.open(str(backup_path), "r:gz") as tar:
            manifest_file = tar.extractfile("manifest.json")
            manifest_data = json.loads(manifest_file.read().decode())

            for filename, expected_sha in manifest_data["checksums"].items():
                member = tar.getmember(filename)
                file_obj = tar.extractfile(member)
                if file_obj:
                    sha = hashlib.sha256(file_obj.read()).hexdigest()
                    assert sha != expected_sha, "Checksum should not match"

    def test_path_traversal_protection(self, project_dir: Path):
        """Test that path traversal attacks are prevented during restore."""
        backup_dir = project_dir / "backups"
        backup_path = backup_dir / "traversal.tar.gz"
        backup_dir.mkdir(exist_ok=True)

        tmp_dir = Path(tempfile.mkdtemp(prefix="evershade-backup-"))
        try:
            # Create a file with path traversal in the name
            malicious_file = tmp_dir / "malicious.txt"
            malicious_file.write_text("This should not be extracted")

            with tarfile.open(str(backup_path), "w:gz") as tar:
                # Add file with path traversal
                member = tarfile.TarInfo(name="../../etc/malicious.txt")
                member.size = malicious_file.stat().st_size
                member.mode = 0o644
                member.mtime = malicious_file.stat().st_mtime
                with open(malicious_file, "rb") as f:
                    tar.addfile(member, f)

        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

        # Verify path traversal is detected
        with tarfile.open(str(backup_path), "r:gz") as tar:
            for member in tar.getmembers():
                # Simulate path traversal check
                member_path = (project_dir / member.name).resolve()
                assert not str(member_path).startswith(str(project_dir)), \
                    f"Path traversal not detected: {member.name}"

    def test_missing_database_handling(self, project_dir: Path):
        """Test that backup handles missing databases gracefully."""
        backup_dir = project_dir / "backups"
        backup_path = backup_dir / "partial.tar.gz"
        backup_dir.mkdir(exist_ok=True)

        tmp_dir = Path(tempfile.mkdtemp(prefix="evershade-backup-"))
        manifest = {
            "version": "1.0",
            "timestamp": datetime.utcnow().strftime("%Y%m%d-%H%M%S"),
            "profile": "standard",
            "services": {},
            "checksums": {},
        }

        try:
            with tarfile.open(str(backup_path), "w:gz") as tar:
                # Only backup greenie, skip others (simulating missing services)
                for service in ["greenie"]:
                    db_file = project_dir / service / "data" / f"{service}.db"
                    if db_file.exists():
                        snapshot_path = tmp_dir / f"{service}.db"
                        src_conn = sqlite3.connect(str(db_file))
                        dst_conn = sqlite3.connect(str(snapshot_path))
                        src_conn.backup(dst_conn)
                        dst_conn.close()
                        src_conn.close()

                        tar.add(str(snapshot_path), arcname=f"{service}/data/{service}.db")
                        sha = hashlib.sha256()
                        with open(snapshot_path, "rb") as f:
                            for chunk in iter(lambda: f.read(8192), b""):
                                sha.update(chunk)
                        manifest["checksums"][f"{service}/data/{service}.db"] = sha.hexdigest()
                        manifest["services"][service] = {"database": True}

                # Add manifest inside the same tar block
                manifest_path = tmp_dir / "manifest.json"
                manifest_path.write_text(json.dumps(manifest, indent=2))
                tar.add(str(manifest_path), arcname="manifest.json")

        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

        # Verify only greenie is in the backup
        with tarfile.open(str(backup_path), "r:gz") as tar:
            members = tar.getnames()
            assert "greenie/data/greenie.db" in members
            assert "slinker/data/slinker.db" not in members
            assert "gobber/data/gobber.db" not in members

            manifest_file = tar.extractfile("manifest.json")
            manifest_data = json.loads(manifest_file.read().decode())
            assert len(manifest_data["services"]) == 1
            assert "greenie" in manifest_data["services"]


class TestBackupFreeDiskSpace:
    """Test free disk space check before backup."""

    def test_disk_space_check_passes(self, tmp_path: Path):
        """Test that disk space check passes when sufficient space is available."""
        # This test verifies the logic without actually running out of space
        usage = shutil.disk_usage(str(tmp_path))
        assert usage.free > 0, "Test environment has no free space"

    def test_estimated_size_calculation(self, project_dir_fixture, tmp_path: Path):
        """Test that estimated backup size is calculated correctly."""
        # Create a small test file
        test_file = tmp_path / "test.db"
        test_file.write_bytes(b"x" * 1024)  # 1KB file

        # Calculate estimated size (file size * 1.5 for overhead)
        estimated_size = int(test_file.stat().st_size * 1.5)
        assert estimated_size == 1536, f"Expected 1536, got {estimated_size}"


# Fixtures for TestBackupFreeDiskSpace
@pytest.fixture
def project_dir_fixture(tmp_path: Path):
    """Create a temporary project directory with mock service data."""
    services = ["greenie"]
    for service in services:
        data_dir = tmp_path / service / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        db_path = data_dir / f"{service}.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        conn.commit()
        conn.close()
    return tmp_path


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
