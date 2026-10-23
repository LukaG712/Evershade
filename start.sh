#!/bin/bash
# Evershade — Startup Script (Linux/macOS)
# Validates configuration, checks dependencies, and starts services.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROFILE="standard"
MODE="${EVERSHADE_MODE:-desktop}"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --profile)
            PROFILE="$2"
            shift 2
            ;;
        --mode)
            MODE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: ./start.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --profile NAME   Compose profile: minimal, standard, full (default: standard)"
            echo "  --mode MODE      Deployment mode: desktop, server (default: desktop)"
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
echo -e "${BLUE}║  Starting Evershade (profile: $PROFILE, mode: $MODE)                    ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERROR: Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker is available"

# Check Docker Compose
if ! docker compose version &> /dev/null; then
    echo -e "${RED}ERROR: Docker Compose is not available.${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker Compose is available"

# Create .env from .env.example if it doesn't exist
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo -e "${YELLOW}⚠${NC} .env not found. Copying from .env.example..."
        cp .env.example .env
        echo -e "${YELLOW}⚠${NC} Please edit .env with your API keys before starting."
    else
        echo -e "${RED}ERROR: Neither .env nor .env.example found.${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✓${NC} .env file found"

# Load .env for validation
set -a
source .env
set +a

# Validate API keys are not using defaults in server mode
if [ "$MODE" = "server" ] || [ "${EVERSHADE_MODE}" = "server" ]; then
    echo -e "${YELLOW}⚠${NC} Server mode detected — validating security configuration..."
    
    defaultKeys=(
        "EVERSHADE_GREENIE_API_KEY=change-me-greenie"
        "EVERSHADE_SLINKER_API_KEY=change-me-slinker"
        "EVERSHADE_TRAPPER_API_KEY=change-me-trapper"
        "EVERSHADE_GOBBER_API_KEY=change-me-gobber"
        "EVERSHADE_ENCRYPTION_KEY=change-me-encryption-key"
    )
    
    insecure=false
    for entry in "${defaultKeys[@]}"; do
        key="${entry%%=*}"
        defaultValue="${entry#*=}"
        actualValue="${!key:-}"
        if [ "$actualValue" = "$defaultValue" ] || [ -z "$actualValue" ]; then
            echo -e "${RED}✗${NC} INSECURE: ${key} is using the default or empty value"
            insecure=true
        fi
    done
    
    if [ "$insecure" = true ]; then
        echo ""
        echo -e "${RED}ERROR: Server mode refuses to start with default or insecure credentials.${NC}"
        echo -e "${YELLOW}Fix .env with secure keys, then retry.${NC}"
        echo -e "${YELLOW}Generate keys: openssl rand -hex 32${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} Security validation passed for server mode"
else
    # Desktop mode: warn about defaults but allow
    hasDefaultKeys=false
    for entry in "EVERSHADE_GREENIE_API_KEY=change-me-greenie" "EVERSHADE_ENCRYPTION_KEY=change-me-encryption-key"; do
        key="${entry%%=*}"
        defaultValue="${entry#*=}"
        actualValue="${!key:-}"
        if [ "$actualValue" = "$defaultValue" ]; then
            echo -e "${YELLOW}⚠${NC} ${key} is using the default value (ok for desktop mode)"
            hasDefaultKeys=true
        fi
    done
    if [ "$hasDefaultKeys" = true ]; then
        echo -e "${YELLOW}⚠${NC} Default keys detected — fine for local development, insecure for production${NC}"
    fi
fi

# Check required service directories based on profile
get_required_dirs() {
    python3 -c "
import json
with open('version-manifest.json') as f:
    manifest = json.load(f)
profile_services = manifest.get('profiles', {}).get('$PROFILE', [])
for svc in profile_services:
    if svc not in ('redis', 'ollama', 'caddy'):
        print(svc)
" 2>/dev/null || echo "Greenie Slinker Trapper Gobber"
}

REQUIRED_DIRS=$(get_required_dirs)
missing_dirs=false
for dir in $REQUIRED_DIRS; do
    if [ ! -d "services/$dir" ]; then
        echo -e "${RED}ERROR: Directory 'services/$dir' not found.${NC}"
        echo -e "${YELLOW}Run ./install.sh --profile $PROFILE to install missing services.${NC}"
        missing_dirs=true
    fi
done

if [ "$missing_dirs" = true ]; then
    exit 1
fi
echo -e "${GREEN}✓${NC} Required service directories found"

# Validate docker-compose.yml
if [ ! -f docker-compose.yml ]; then
    echo -e "${RED}ERROR: docker-compose.yml not found.${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} docker-compose.yml found"

# Validate docker-compose configuration
if ! docker compose --profile "$PROFILE" config --quiet 2>/dev/null; then
    echo -e "${RED}ERROR: Invalid docker-compose configuration for profile '$PROFILE'.${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker Compose configuration valid"

# Check if Junie CLI is available (for code agents)
if command -v junie &> /dev/null; then
    echo -e "${GREEN}✓${NC} Junie CLI is available"
else
    echo -e "${YELLOW}⚠${NC} Junie CLI not found on PATH — code agents will not work"
fi

# Start services
echo ""
echo -e "${BLUE}Starting services with profile: ${GREEN}$PROFILE${NC}"
echo ""

docker compose --profile "$PROFILE" up -d

echo ""
echo -e "${GREEN}✓${NC} Services started!"
echo ""
echo "Service URLs:"
echo "  Greenie:    http://localhost:8080"
echo "  Slinker:    http://localhost:8000"
echo "  Trapper:    http://localhost:3000"
echo "  Gobber:     http://localhost:8085"
echo "  Sneaker:    http://localhost:8086"
echo "  Hider:      http://localhost:8087"
echo "  Poltergeist: http://localhost:8088"
echo "  Shrewd:    http://localhost:8089"
echo "  Slammer:    http://localhost:5173"
echo ""
echo "API Documentation:"
echo "  Swagger:   http://localhost:8080/docs"
echo "  ReDoc:     http://localhost:8080/redoc"
echo ""
echo "Obsidian Vault:"
echo "  To enable semantic search, set OBSIDIAN_VAULT_PATH in .env"
echo "  Example: OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault"
echo ""
echo "To stop services:  ./stop.sh"
echo "To view logs:      docker compose logs -f"
echo ""
