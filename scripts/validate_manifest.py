#!/usr/bin/env python3
"""Validate the Evershade version manifest.

Checks:
- JSON schema validity
- Required fields present
- No duplicate services
- Version format (semver)
- Port uniqueness
- Repository URL format
- Profile consistency (all referenced services exist)
- Dependency references (all dependencies are defined services)
- Docker image references format
- Infrastructure services consistency
"""

import json
import re
import sys
from pathlib import Path

SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{7,40}$")

REQUIRED_SERVICE_FIELDS = {"version", "repository", "required", "port", "api_version"}

def load_manifest(path: str = "version-manifest.json") -> dict:
    manifest_path = Path(path)
    if not manifest_path.exists():
        print(f"ERROR: {manifest_path} not found")
        sys.exit(1)

    try:
        with open(manifest_path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {manifest_path}: {e}")
        sys.exit(1)


def validate_manifest(manifest: dict) -> list[str]:
    errors = []
    warnings = []

    # Top-level required fields
    for field in ("version", "services", "profiles"):
        if field not in manifest:
            errors.append(f"Missing top-level field: {field}")

    if errors:
        return errors, []  # Can't continue without basic structure

    # Validate top-level version
    version = manifest.get("version", "")
    if not SEMVER_PATTERN.match(version):
        errors.append(f"Top-level version '{version}' is not valid semver (X.Y.Z)")

    # Validate services
    services = manifest.get("services", {})
    if not isinstance(services, dict) or not services:
        errors.append("No services defined in manifest")
        return errors, []

    ports = {}
    service_names = set(services.keys())

    for name, service in services.items():
        prefix = f"Service '{name}'"

        # Required fields
        for field in REQUIRED_SERVICE_FIELDS:
            if field not in service:
                errors.append(f"{prefix}: missing required field '{field}'")

        # Version format
        svc_version = service.get("version", "")
        if svc_version and not SEMVER_PATTERN.match(svc_version):
            errors.append(f"{prefix}: version '{svc_version}' is not valid semver")

        # Repository URL
        repo = service.get("repository", "")
        if repo and not repo.startswith("http"):
            errors.append(f"{prefix}: repository URL is invalid: {repo}")

        # Commit SHA format (optional but validated if present)
        commit = service.get("commit", "")
        if commit and not COMMIT_PATTERN.match(commit):
            errors.append(f"{prefix}: commit SHA '{commit}' is invalid (expected hex, 7-40 chars)")

        # Port uniqueness
        port = service.get("port")
        if port is not None:
            if port in ports:
                errors.append(f"{prefix}: port {port} is already used by '{ports[port]}'")
            else:
                ports[port] = name

        # Dependencies must reference defined services
        for dep in service.get("dependencies", []):
            if dep not in service_names and dep != "redis":
                warnings.append(f"{prefix}: dependency '{dep}' is not a defined service")

        for dep in service.get("optional_dependencies", []):
            if dep not in service_names and dep != "redis":
                warnings.append(f"{prefix}: optional dependency '{dep}' is not a defined service")

    # Validate profiles
    profiles = manifest.get("profiles", {})
    for profile_name, profile_services in profiles.items():
        for svc in profile_services:
            if svc not in service_names and svc not in ("redis", "ollama", "caddy"):
                errors.append(f"Profile '{profile_name}': references undefined service '{svc}'")

    # Validate Docker image references
    docker_images = manifest.get("docker_images", {})
    if docker_images:
        image_values = {k: v for k, v in docker_images.items() if k != "description"}
        for name, image in image_values.items():
            if not isinstance(image, str) or ":" not in image:
                errors.append(f"Docker image '{name}': invalid format '{image}' (expected name:tag)")
            if image.startswith("http"):
                errors.append(f"Docker image '{name}': should be an image reference, not a URL")

    # Validate infrastructure services
    infrastructure = manifest.get("infrastructure", {})
    for name, infra in infrastructure.items():
        if not isinstance(infra, dict):
            errors.append(f"Infrastructure '{name}': should be a dict with image and required fields")
            continue
        image = infra.get("image", "")
        if image and ":" not in image:
            errors.append(f"Infrastructure '{name}': image '{image}' missing tag")
        if "required" not in infra:
            warnings.append(f"Infrastructure '{name}': missing 'required' field")

    # Cross-check: infrastructure images should match docker_images if both exist
    if docker_images and infrastructure:
        image_values = {k: v for k, v in docker_images.items() if k != "description"}
        for name, infra in infrastructure.items():
            if isinstance(infra, dict) and name in image_values:
                infra_image = infra.get("image", "")
                manifest_image = image_values[name]
                if infra_image and manifest_image and infra_image != manifest_image:
                    warnings.append(
                        f"Infrastructure '{name}' image '{infra_image}' differs from "
                        f"docker_images '{manifest_image}'"
                    )

    return errors, warnings


def main():
    manifest_path = sys.argv[1] if len(sys.argv) > 1 else "version-manifest.json"
    print(f"Validating manifest: {manifest_path}")

    manifest = load_manifest(manifest_path)
    errors, warnings = validate_manifest(manifest)

    # Report
    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for w in warnings:
            print(f"  ⚠ {w}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors:
            print(f"  ✗ {e}")
        print("\nManifest validation FAILED.")
        sys.exit(1)
    else:
        services = manifest.get("services", {})
        profiles = manifest.get("profiles", {})
        print(f"\n✓ Manifest validation passed. ({len(services)} services, {len(profiles)} profiles)")
        if warnings:
            print(f"  ({len(warnings)} warnings)")


if __name__ == "__main__":
    main()
