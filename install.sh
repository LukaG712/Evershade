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
CUSTOM_SERVICES=""

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
        --custom)
            PROFILE="custom"
            CUSTOM_SERVICES="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: ./install.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --force          Remove existing service directories before cloning"
            echo "  --profile NAME   Installation profile: minimal, standard, full, custom (default: standard)"
            echo "  --custom LIST    Comma-separated list of services to install (requires --profile custom)"
            echo "  --help, -h       Show this help message"
            echo ""
            echo "Profiles:"
            echo "  minimal   Core services only (Greenie, Slinker, Trapper, Gobber)"
            echo "  standard  All services except dashboard (default)"
            echo "  full      Everything including Slammer dashboard"
            echo "  custom    Choose individual services interactively or via --custom"
            echo ""
            echo "Services:"
            echo "  Required:  Greenie, Slinker, Trapper, Gobber"
            echo "  Optional:  Sneaker, Hider, Poltergeist, Shrewd, Slammer, Speedy"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Interactive custom service selection
if [ "$PROFILE" = "custom" ]; then
    if [ -n "$CUSTOM_SERVICES" ]; then
        # Services provided via --custom flag
        SELECTED_SERVICES=($(echo "$CUSTOM_SERVICES" | tr ',' ' '))
    else
        # Interactive menu
        echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${BLUE}║  Custom Service Selection                                    ║${NC}"
        echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo -e "${YELLOW}Required services (cannot be removed):${NC}"
        echo "  [x] Greenie    - Central API backend"
        echo "  [x] Slinker    - Code execution"
        echo "  [x] Trapper    - Web scraping"
        echo "  [x] Gobber     - Storage & search"
        echo ""
        echo -e "${YELLOW}Optional services (press number to toggle):${NC}"
        echo "  [1] Sneaker      - Observability & alerting"
        echo "  [2] Hider        - Encrypted secrets management"
        echo "  [3] Poltergeist  - Notifications (Slack, Discord, Email, Telegram)"
        echo "  [4] Shrewd       - LLM providers (OpenAI, Anthropic, Google, Ollama)"
        echo "  [5] Slammer      - Web dashboard"
        echo "  [6] Speedy       - CLI tool"
        echo ""
        echo -e "${BLUE}Enter numbers to toggle, or 'done' to continue:${NC}"

        # Default: required services only
        SELECTED_SERVICES=("Greenie" "Slinker" "Trapper" "Gobber")
        declare -A OPTIONAL_MAP
        OPTIONAL_MAP[1]="Sneaker"
        OPTIONAL_MAP[2]="Hider"
        OPTIONAL_MAP[3]="Poltergeist"
        OPTIONAL_MAP[4]="Shrewd"
        OPTIONAL_MAP[5]="Slammer"
        OPTIONAL_MAP[6]="Speedy"

        while true; do
            read -rp "  > " choice
            if [ "$choice" = "done" ] || [ -z "$choice" ]; then
                break
            fi
            if [[ "$choice" =~ ^[1-6]$ ]]; then
                svc="${OPTIONAL_MAP[$choice]}"
                if printf '%s\n' "${SELECTED_SERVICES[@]}" | grep -qw "$svc"; then
                    # Remove service
                    SELECTED_SERVICES=($(printf '%s\n' "${SELECTED_SERVICES[@]}" | grep -vw "$svc"))
                    echo -e "  ${RED}✗${NC} Removed $svc"
                else
                    # Add service
                    SELECTED_SERVICES+=("$svc")
                    echo -e "  ${GREEN}✓${NC} Added $svc"
                fi
            else
                echo -e "  ${RED}Invalid choice. Enter 1-6, or 'done'.${NC}"
            fi
        done
    fi

    # Validate that required services are included
    for req in Greenie Slinker Trapper Gobber; do
        if ! printf '%s\n' "${SELECTED_SERVICES[@]}" | grep -qw "$req"; then
            echo -e "${RED}ERROR: Required service '$req' is missing. Cannot proceed.${NC}"
            exit 1
        fi
    done

    echo ""
    echo -e "${GREEN}✓${NC} Selected services: ${SELECTED_SERVICES[*]}"
    echo ""
fi

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

# Extract service info based on profile or custom selection
get_service_info() {
    local profile="$1"
    local custom_list="$2"
    python3 -c "
import json
with open('version-manifest.json') as f:
    manifest = json.load(f)
custom = '$custom_list'.strip()
if custom:
    profile_services = [s.strip() for s in custom.split(',') if s.strip()]
else:
    profile_services = manifest.get('profiles', {}).get('$profile', [])
for svc in profile_services:
    if svc not in ('redis', 'ollama', 'caddy'):  # Skip infrastructure
        info = manifest.get('services', {}).get(svc, {})
        repo = info.get('repository', 'https://github.com/LukaG712/' + svc)
        commit = info.get('commit', '')
        print(f'{svc}|{repo}|{commit}')
"
}

if [ "$PROFILE" = "custom" ]; then
    custom_csv=$(IFS=,; echo "${SELECTED_SERVICES[*]}")
    SERVICES_INFO=$(get_service_info "$PROFILE" "$custom_csv")
else
    SERVICES_INFO=$(get_service_info "$PROFILE" "")
fi

if [ -z "$SERVICES_INFO" ]; then
    echo -e "${RED}ERROR: Unknown profile '$PROFILE'. Available: minimal, standard, full, custom${NC}"
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
