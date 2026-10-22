#!/usr/bin/env python3
"""Verify release signatures and checksums.

Usage:
    python scripts/verify_release.py --release release/
    python scripts/verify_release.py --release release/ --artifact path/to/file
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def compute_sha256(file_path: str) -> str:
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def verify_checksum(file_path: str, expected_hash: str) -> bool:
    """Verify a file's SHA-256 checksum."""
    actual = compute_sha256(file_path)
    return actual == expected_hash


def verify_signature(file_path: str, expected_sig: str, secret: str) -> bool:
    """Verify HMAC-SHA256 signature."""
    import hmac as hmac_mod
    file_hash = compute_sha256(file_path)
    h = hmac_mod.new(secret.encode("utf-8"), file_hash.encode("utf-8"), hashlib.sha256)
    actual_sig = h.hexdigest()
    return hmac_mod.compare_digest(actual_sig, expected_sig)


def main():
    parser = argparse.ArgumentParser(description="Verify Evershade release signatures")
    parser.add_argument("--release", required=True, help="Release directory")
    parser.add_argument("--artifact", help="Specific artifact to verify")
    parser.add_argument("--secret", default="", help="Signing secret key (for signature verification)")
    args = parser.parse_args()

    release_dir = Path(args.release)
    if not release_dir.exists():
        print(f"Error: Release directory not found: {args.release}", file=sys.stderr)
        sys.exit(1)

    # Load signatures
    signatures_file = release_dir / "signatures.json"
    if not signatures_file.exists():
        print(f"Error: Signatures file not found: {signatures_file}", file=sys.stderr)
        sys.exit(1)

    with open(signatures_file) as f:
        signatures_data: dict[str, Any] = json.load(f)

    artifacts = signatures_data.get("artifacts", [])
    algorithm = signatures_data.get("algorithm", "SHA256")

    print(f"Release: {signatures_data.get('version', 'unknown')}")
    print(f"Algorithm: {algorithm}")
    print(f"Artifacts: {len(artifacts)}")
    print()

    errors = 0
    verified = 0

    for artifact in artifacts:
        file_name = artifact["file"]
        expected_hash = artifact["sha256"]
        expected_sig = artifact.get("signature", "")

        # Find the file — search in common locations
        file_path = None
        for search_dir in [Path("."), Path(__file__).parent.parent]:
            candidate = search_dir / file_name
            if candidate.exists():
                file_path = str(candidate)
                break

            # Search recursively
            for f in search_dir.rglob(file_name):
                if f.is_file():
                    file_path = str(f)
                    break
            if file_path:
                break

        if not file_path or not Path(file_path).exists():
            print(f"⚠ {file_name}: File not found (skipping)")
            continue

        # Verify checksum
        if verify_checksum(file_path, expected_hash):
            print(f"✓ {file_name}: Checksum OK")
            verified += 1
        else:
            print(f"✗ {file_name}: Checksum MISMATCH")
            errors += 1

        # Verify signature if applicable
        if algorithm == "HMAC-SHA256" and args.secret and expected_sig:
            if verify_signature(file_path, expected_sig, args.secret):
                print(f"  ✓ Signature OK")
            else:
                print(f"  ✗ Signature MISMATCH")
                errors += 1

    # Load and display provenance
    provenance_file = release_dir / "provenance.json"
    if provenance_file.exists():
        with open(provenance_file) as f:
            provenance = json.load(f)
        print(f"\nProvenance:")
        print(f"  Build type: {provenance.get('buildType', 'unknown')}")
        print(f"  Builder: {provenance.get('buildConfig', {}).get('provenance', {}).get('builder', {}).get('id', 'unknown')}")
        print(f"  Generated: {provenance.get('generated_at', 'unknown')}")

    print(f"\n{'=' * 40}")
    if errors == 0:
        print(f"Verification PASSED: {verified}/{len(artifacts)} artifacts verified")
        sys.exit(0)
    else:
        print(f"Verification FAILED: {errors} errors, {verified}/{len(artifacts)} verified")
        sys.exit(1)


if __name__ == "__main__":
    main()
