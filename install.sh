#!/bin/bash
# Evershade — Bootstrap Installation Script (Linux/macOS)
# Clones all service repositories into the expected directories.
# Safe to re-run: will skip existing repositories unless --force is used.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

FORCE=false
PROFILE="standard"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE=true
            shift
            ;;
        --profile)
            PROFILE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: ./install.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --force          Remove existing service directories before cloning"
            echo "  --profile NAME   Installation profile: minimal, standard, full (default: standard)"
            echo "  --help, -h       Show this help message"
            echo ""
            echo "Profiles:"
            echo "  minimal   Core services only (Greenie, Slinker, Trapper, Gobber)"
            echo "  standard  All services except dashboard (default)"
            echo "  full      Everything including Slammer dashboard"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Evershade Bootstrap Installer                               ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}ERROR: Git is not installed. Please install Git first.${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Git is available"

# Read version manifest
if [ ! -f version-manifest.json ]; then
    echo -e "${RED}ERROR: version-manifest.json not found. Are you in the Evershade root directory?${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} version-manifest.json found"

# Extract service info based on profile
get_service_info() {
    local profile="$1"
    python3 -c "
import json
with open('version-manifest.json') as f:
    manifest = json.load(f)
profile_services = manifest.get('profiles', {}).get('$profile', [])
for svc in profile_services:
    if svc not in ('redis', 'ollama', 'caddy'):  # Skip infrastructure
        info = manifest.get('services', {}).get(svc, {})
        repo = info.get('repository', 'https://github.com/LukaG712/' + svc)
        commit = info.get('commit', '')
        print(f'{svc}|{repo}|{commit}')
"
}

SERVICES_INFO=$(get_service_info "$PROFILE")
if [ -z "$SERVICES_INFO" ]; then
    echo -e "${RED}ERROR: Unknown profile '$PROFILE'. Available: minimal, standard, full${NC}"
    exit 1
fi

SERVICE_COUNT=$(echo "$SERVICES_INFO" | wc -l)
echo -e "${GREEN}✓${NC} Profile: ${BLUE}$PROFILE${NC}"
echo -e "${GREEN}✓${NC} Services to install: $SERVICE_COUNT"
echo ""

# Clone each service
FAILED=()
SKIPPED=()
CLONED=()
OUTDATED=()

while IFS='|' read -r SERVICE REPO_URL COMMIT; do
    # Check if directory already exists
    if [ -d "$SERVICE" ]; then
        if [ "$FORCE" = true ]; then
            echo -e "${YELLOW}⚠${NC} Removing existing $SERVICE directory (forced)..."
            rm -rf "$SERVICE"
        else
            # Check if it's a valid git repo and at the correct commit
            if [ -d "$SERVICE/.git" ]; then
                CURRENT_COMMIT=$(cd "$SERVICE" && git rev-parse --short=7 HEAD 2>/dev/null || echo "unknown")
                if [ -n "$COMMIT" ] && [ "$CURRENT_COMMIT" = "$COMMIT" ]; then
                    echo -e "${GREEN}✓${NC} $SERVICE already at correct commit ($COMMIT) — skipping"
                    SKIPPED+=("$SERVICE")
                    continue
                elif [ -n "$COMMIT" ]; then
                    echo -e "${YELLOW}⚠${NC} $SERVICE exists at commit $CURRENT_COMMIT (expected $COMMIT) — skipping. Use --force to update."
                    OUTDATED+=("$SERVICE")
                    SKIPPED+=("$SERVICE")
                    continue
                else
                    echo -e "${YELLOW}⚠${NC} $SERVICE already exists (git repo) — skipping. Use --force to reclone."
                    SKIPPED+=("$SERVICE")
                    continue
                fi
            else
                echo -e "${YELLOW}⚠${NC} $SERVICE directory exists but is not a git repo — skipping. Use --force to replace."
                SKIPPED+=("$SERVICE")
                continue
            fi
        fi
    fi

    echo -e "${BLUE}→${NC} Cloning $SERVICE from $REPO_URL ..."

    CLONE_SUCCESS=false
    if [ -n "$COMMIT" ]; then
        # Clone and checkout the specific commit
        if git clone --depth 100 "$REPO_URL" "$SERVICE" 2>&1; then
            if (cd "$SERVICE" && git checkout "$COMMIT" 2>&1); then
                echo -e "${GREEN}✓${NC} $SERVICE cloned and checked out at commit $COMMIT"
                CLONE_SUCCESS=true
            else
                echo -e "${RED}✗${NC} Failed to checkout commit $COMMIT for $SERVICE"
                echo -e "${YELLOW}    The pinned commit may not exist or the repo may have changed.${NC}"
                echo -e "${YELLOW}    Falling back to latest commit.${NC}"
                CLONE_SUCCESS=true  # Still cloned, just not at pinned commit
            fi
        else
            echo -e "${RED}✗${NC} Failed to clone $SERVICE"
        fi
    else
        # No pinned commit, clone latest
        if git clone --depth 1 "$REPO_URL" "$SERVICE" 2>&1; then
            echo -e "${GREEN}✓${NC} $SERVICE cloned successfully (no pinned commit)"
            CLONE_SUCCESS=true
        else
            echo -e "${RED}✗${NC} Failed to clone $SERVICE"
        fi
    fi

    if [ "$CLONE_SUCCESS" = true ]; then
        CLONED+=("$SERVICE")
    else
        FAILED+=("$SERVICE")
    fi
done <<< "$SERVICES_INFO"

echo ""
echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓${NC} Cloned: ${#CLONED[@]} services"

if [ ${#SKIPPED[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠${NC} Skipped: ${SKIPPED[*]}"
fi

if [ ${#OUTDATED[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠${NC} Outdated (commit mismatch): ${OUTDATED[*]}"
    echo -e "${YELLOW}    Use --force to update to the pinned version.${NC}"
fi

if [ ${#FAILED[@]} -gt 0 ]; then
    echo -e "${RED}✗${NC} Failed: ${FAILED[*]}"
    echo ""
    echo -e "${RED}Installation incomplete. Possible causes:${NC}"
    echo -e "  - Network connectivity issues"
    echo -e "  - Repository not found or private"
    echo -e "  - Insufficient permissions"
    echo -e "${YELLOW}Try re-running with --force to retry failed services.${NC}"
    exit 1
fi

# Create .env from .env.example if it doesn't exist
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo ""
        echo -e "${YELLOW}⚠${NC} .env not found. Copying from .env.example..."
        cp .env.example .env
        echo -e "${YELLOW}⚠${NC} Please edit .env with your API keys before starting.${NC}"
    fi
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Installation complete!                                     ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Run ./start.sh --profile $PROFILE to start services"
echo ""
