#!/bin/bash
# Evershade — Update Script (Linux/macOS)
# Pulls the latest version-manifest.json and updates all service repositories
# to their pinned commits. Safe to re-run.
#
# Usage:
#   ./update.sh                  # Update with current profile (standard)
#   ./update.sh --profile full   # Update with a specific profile
#   ./update.sh --force          # Force update even if already up to date
#   ./update.sh --pull-main      # Also pull latest changes from main Evershade repo

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
PULL_MAIN=false
PROFILE="standard"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE=true
            shift
            ;;
        --pull-main)
            PULL_MAIN=true
            shift
            ;;
        --profile)
            PROFILE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: ./update.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --force          Force update all services even if already at correct commit"
            echo "  --pull-main      Pull latest changes from the main Evershade repository"
            echo "  --profile NAME   Update profile: minimal, standard, full (default: standard)"
            echo "  --help, -h       Show this help message"
            echo ""
            echo "This script will:"
            echo "  1. Pull the latest version-manifest.json (optional with --pull-main)"
            echo "  2. Update each service repository to its pinned commit"
            echo "  3. Report which services were updated, skipped, or failed"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Evershade Update Script                                     ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}ERROR: Git is not installed. Please install Git first.${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Git is available"

# Pull latest changes from main Evershade repo
if [ "$PULL_MAIN" = true ]; then
    echo ""
    echo -e "${BLUE}→${NC} Pulling latest changes from main Evershade repository..."
    if [ -d ".git" ]; then
        if git pull 2>&1; then
            echo -e "${GREEN}✓${NC} Main repository updated"
        else
            echo -e "${YELLOW}⚠${NC} No changes to pull or pull failed (this is okay if already up to date)"
        fi
    else
        echo -e "${YELLOW}⚠${NC} Not a git repository — skipping main repo pull"
    fi
fi

# Read version manifest
if [ ! -f version-manifest.json ]; then
    echo -e "${RED}ERROR: version-manifest.json not found. Are you in the Evershade root directory?${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} version-manifest.json found"

# Extract manifest version for display
MANIFEST_VERSION=$(python3 -c "
import json
with open('version-manifest.json') as f:
    manifest = json.load(f)
print(manifest.get('version', 'unknown'))
")
echo -e "${GREEN}✓${NC} Manifest version: ${BLUE}$MANIFEST_VERSION${NC}"

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
echo -e "${GREEN}✓${NC} Services to check: $SERVICE_COUNT"
echo ""

# Update each service
UPDATED=()
SKIPPED=()
FAILED=()
MISSING=()

while IFS='|' read -r SERVICE REPO_URL COMMIT; do
    # Check if directory exists
    if [ ! -d "$SERVICE" ]; then
        echo -e "${YELLOW}⚠${NC} $SERVICE directory not found — skipping. Run install.sh to clone it first."
        MISSING+=("$SERVICE")
        continue
    fi

    # Check if it's a valid git repo
    if [ ! -d "$SERVICE/.git" ]; then
        echo -e "${YELLOW}⚠${NC} $SERVICE exists but is not a git repo — skipping."
        SKIPPED+=("$SERVICE")
        continue
    fi

    # Get current commit
    CURRENT_COMMIT=$(cd "$SERVICE" && git rev-parse --short=7 HEAD 2>/dev/null || echo "unknown")

    # Check if already at correct commit
    if [ -n "$COMMIT" ] && [ "$CURRENT_COMMIT" = "$COMMIT" ] && [ "$FORCE" = false ]; then
        echo -e "${GREEN}✓${NC} $SERVICE already at correct commit ($COMMIT) — skipping"
        SKIPPED+=("$SERVICE")
        continue
    fi

    # Fetch latest changes
    echo -e "${BLUE}→${NC} Updating $SERVICE (current: $CURRENT_COMMIT, target: $COMMIT)..."

    UPDATE_SUCCESS=false
    if (cd "$SERVICE" && git fetch --depth 100 2>&1); then
        if [ -n "$COMMIT" ]; then
            # Checkout the pinned commit
            if (cd "$SERVICE" && git checkout "$COMMIT" 2>&1); then
                NEW_COMMIT=$(cd "$SERVICE" && git rev-parse --short=7 HEAD)
                echo -e "${GREEN}✓${NC} $SERVICE updated: $CURRENT_COMMIT → $NEW_COMMIT"
                UPDATE_SUCCESS=true
            else
                echo -e "${RED}✗${NC} Failed to checkout commit $COMMIT for $SERVICE"
                echo -e "${YELLOW}    The pinned commit may not exist or the repo may have changed.${NC}"
            fi
        else
            # No pinned commit, just pull latest
            if (cd "$SERVICE" && git pull --ff-only 2>&1); then
                NEW_COMMIT=$(cd "$SERVICE" && git rev-parse --short=7 HEAD)
                if [ "$NEW_COMMIT" != "$CURRENT_COMMIT" ]; then
                    echo -e "${GREEN}✓${NC} $SERVICE pulled latest: $CURRENT_COMMIT → $NEW_COMMIT"
                else
                    echo -e "${GREEN}✓${NC} $SERVICE already up to date ($NEW_COMMIT)"
                fi
                UPDATE_SUCCESS=true
            else
                echo -e "${YELLOW}⚠${NC} Could not fast-forward $SERVICE (no pinned commit) — skipping"
                SKIPPED+=("$SERVICE")
                continue
            fi
        fi
    else
        echo -e "${RED}✗${NC} Failed to fetch updates for $SERVICE"
    fi

    if [ "$UPDATE_SUCCESS" = true ]; then
        UPDATED+=("$SERVICE")
    else
        FAILED+=("$SERVICE")
    fi
done <<< "$SERVICES_INFO"

echo ""
echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓${NC} Updated: ${#UPDATED[@]} services"

if [ ${#SKIPPED[@]} -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Up to date: ${#SKIPPED[@]} services"
fi

if [ ${#MISSING[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠${NC} Missing (not cloned): ${MISSING[*]}"
    echo -e "${YELLOW}    Run ./install.sh --profile $PROFILE to clone missing services.${NC}"
fi

if [ ${#FAILED[@]} -gt 0 ]; then
    echo -e "${RED}✗${NC} Failed: ${FAILED[*]}"
    echo ""
    echo -e "${RED}Update incomplete. Possible causes:${NC}"
    echo -e "  - Network connectivity issues"
    echo -e "  - Repository not found or private"
    echo -e "  - Local modifications conflicting with update"
    echo -e "${YELLOW}Try re-running with --force to retry.${NC}"
    exit 1
fi

# Check for new services in manifest that aren't cloned
if [ ${#MISSING[@]} -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}⚠${NC} New services detected in manifest but not yet cloned."
    echo -e "${YELLOW}    Run ./install.sh --profile $PROFILE to install them.${NC}"
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Update complete!                                           ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Updated services:"
for svc in "${UPDATED[@]}"; do
    echo "  - $svc"
done
echo ""
echo "To apply changes, restart your services:"
echo "  ./stop.sh && ./start.sh --profile $PROFILE"
echo ""
