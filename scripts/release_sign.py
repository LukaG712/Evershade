#!/usr/bin/env python3
"""Release signing and provenance generation for Evershade.

Generates cryptographic signatures and SLSA-style provenance for releases.
Usage:
    python scripts/release_sign.py --version 1.5.0 --artifact path/to/file
    python scripts/release_sign.py --version 1.5.0 --sign-all
"""

import argparse
import hashlib
import json
import os
import sys
import base64
import hmac
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def compute_sha256(file_path: str) -> str:
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def compute_sha256_string(data: bytes) -> str:
    """Compute SHA-256 hash of bytes."""
    return hashlib.sha256(data).hexdigest()


def sign_artifact(file_path: str, secret_key: Optional[str] = None) -> dict[str, Any]:
    """Sign an artifact with HMAC-SHA256.

    Returns a signature record with hash, signature, and metadata.
    """
    path = Path(file_path)
    if not path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    file_hash = compute_sha256(str(path))
    file_size = path.stat().st_size

    # Sign with HMAC if secret key provided
    signature = ""
    if secret_key:
        h = hmac.new(secret_key.encode("utf-8"), file_hash.encode("utf-8"), hashlib.sha256)
        signature = h.hexdigest()

    return {
        "file": path.name,
        "path": str(path.resolve()),
        "sha256": file_hash,
        "size_bytes": file_size,
        "signature": signature,
        "signed_at": datetime.now(timezone.utc).isoformat(),
    }


def generate_provenance(version: str, artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate SLSA-style provenance for a release.

    Provenance follows the SLSA Provenance format (in-scope for SLSA 3).
    """
    return {
        "buildType": "https://slsa-framework.github.io/github-actions-buildtypes/script-at-rev/v1",
        "runnerProvided": {
            "invocationId": f"evershade-release-{version}",
            "source": {
                "uri": "git+https://github.com/evershade/workflow.git",
                "digest": {
                    "sha1": "placeholder-commit-sha"
                },
                "ref": {
                    "branch": f"v{version}"
                }
            },
            "config": {
                "os": "linux",
                "arch": "x86_64",
            },
        },
        "buildConfig": {
            "id": f"release-{version}",
            "provenance": {
                "builder": {
                    "id": "evershade-release-pipeline"
                },
                "version": {
                    "slsa-provenance": "0.2",
                },
            },
        },
        "metadata": {
            "buildInvocationId": f"evershade-{version}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "completeness": {
                "parameters": True,
                "environment": True,
                "materials": True,
            },
            "reproducible": False,
        },
        "materials": [
            {
                "uri": "git+https://github.com/evershade/workflow.git",
                "digest": {"sha1": "placeholder"},
            }
        ],
        "artifacts": artifacts,
        "version": version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def generate_checksums(artifacts: list[dict[str, Any]]) -> str:
    """Generate a checksums.txt file content."""
    lines = []
    for artifact in artifacts:
        lines.append(f"{artifact['sha256']}  {artifact['file']}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Sign Evershade release artifacts")
    parser.add_argument("--version", required=True, help="Release version (e.g., 1.5.0)")
    parser.add_argument("--artifact", help="Path to a single artifact to sign")
    parser.add_argument("--sign-all", action="store_true", help="Sign all services")
    parser.add_argument("--secret", default=os.getenv("RELEASE_SIGNING_KEY"), help="Signing secret key")
    parser.add_argument("--output", default="release", help="Output directory")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    artifacts = []

    if args.artifact:
        # Sign a single artifact
        record = sign_artifact(args.artifact, args.secret)
        artifacts.append(record)
    elif args.sign_all:
        # Sign all service directories
        root = Path(__file__).parent.parent
        services = ["Greenie", "Slinker", "Trapper", "Gobber", "Sneaker", "Hider", "Poltergeist", "Shrewd", "Speedy", "Slammer"]
        for service in services:
            service_dir = root / service
            if service_dir.exists():
                # Sign key files in each service
                for pattern in ["*.py", "*.ts", "*.json", "Dockerfile", "pyproject.toml", "package.json"]:
                    for file in service_dir.rglob(pattern):
                        if "node_modules" not in str(file) and "__pycache__" not in str(file) and ".git" not in str(file):
                            record = sign_artifact(str(file), args.secret)
                            artifacts.append(record)
    else:
        print("Error: Specify --artifact or --sign-all", file=sys.stderr)
        sys.exit(1)

    # Write checksums
    checksums_file = output_dir / "checksums.txt"
    checksums_file.write_text(generate_checksums(artifacts))
    print(f"Written: {checksums_file}")

    # Write signatures
    signatures_file = output_dir / "signatures.json"
    signatures_data = {
        "version": args.version,
        "signed_at": datetime.now(timezone.utc).isoformat(),
        "algorithm": "HMAC-SHA256" if args.secret else "SHA256",
        "artifacts": artifacts,
    }
    signatures_file.write_text(json.dumps(signatures_data, indent=2))
    print(f"Written: {signatures_file}")

    # Generate provenance
    provenance = generate_provenance(args.version, artifacts)
    provenance_file = output_dir / "provenance.json"
    provenance_file.write_text(json.dumps(provenance, indent=2))
    print(f"Written: {provenance_file}")

    # Print summary
    print(f"\nRelease {args.version}: {len(artifacts)} artifacts signed")
    if args.secret:
        print("Algorithm: HMAC-SHA256")
    else:
        print("Algorithm: SHA256 (no signature, hash only)")


if __name__ == "__main__":
    main()
