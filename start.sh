#!/bin/bash
# Unified Workflow — Startup Script (Linux/macOS)
# Validates configuration, checks dependencies, and starts all services.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting services..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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
        echo -e "${YELLOW}⚠${NC} Press Ctrl+C to edit, or Enter to continue with defaults..."
        read -r
    else
        echo -e "${RED}ERROR: Neither .env nor .env.example found.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓${NC} .env file found"

# Validate API keys are not using defaults
declare -A defaultKeys=(
    ["HUB_API_KEY"]="Greenie-dev-key-change-me"
    ["Slinker_API_KEY"]="Slinker-dev-key-change-me"
    ["Trapper_API_KEY"]="Trapper-dev-key-change-me"
    ["GOBBER_API_KEY"]="Gobber-dev-key-change-me"
    ["SNEAKER_API_KEY"]="Sneaker-dev-key-change-me"
    ["HIDER_API_KEY"]="Hider-dev-key-change-me"
    ["POLTERGEIST_API_KEY"]="Poltergeist-dev-key-change-me"
    ["SHREWD_API_KEY"]="Shrewd-dev-key-change-me"
    ["ENCRYPTION_KEY"]="change-me-in-production"
)

hasDefaultKeys=false
for key in "${!defaultKeys[@]}"; do
    defaultValue="${defaultKeys[$key]}"
    envValue=$(grep "^${key}=" .env 2>/dev/null | cut -d'=' -f2-)
    if [ "$envValue" = "$defaultValue" ]; then
        echo -e "${RED}✗${NC} WARNING: ${key} is using the default value '${defaultValue}'"
        hasDefaultKeys=true
    fi
done

if [ "$hasDefaultKeys" = true ]; then
    echo ""
    echo -e "${RED}[!] SECURITY RISK: Default API keys detected. These should be changed for production use.${NC}"
    echo -e "${YELLOW}[!] Generate secure keys: openssl rand -hex 32${NC}"
    echo ""
    echo -e "${YELLOW}[!] Press Ctrl+C to fix .env, or Enter to continue with defaults (NOT recommended)...${NC}"
    read -r
fi

echo -e "${GREEN}✓${NC} API key validation complete"

# Check required directories
for dir in Greenie Slinker Trapper Gobber Sneaker Hider Poltergeist Shrewd Slammer; do
    if [ ! -d "$dir" ]; then
        echo -e "${RED}ERROR: Directory '$dir' not found.${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✓${NC} All service directories found"

# Validate docker-compose.yml
if [ ! -f docker-compose.yml ]; then
    echo -e "${RED}ERROR: docker-compose.yml not found.${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} docker-compose.yml found"

# Check if Junie CLI is available (for code agents)
if command -v junie &> /dev/null; then
    echo -e "${GREEN}✓${NC} Junie CLI is available"
else
    echo -e "${YELLOW}⚠${NC} Junie CLI not found on PATH — code agents will not work"
fi

# Start services
echo ""
echo "Starting all services..."
echo ""

docker compose up -d

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
