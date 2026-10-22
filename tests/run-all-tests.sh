#!/usr/bin/env bash
# Run all ecosystem-wide tests.
# Usage: ./tests/run-all-tests.sh [test_category]
# Categories: integration, security, benchmarks, evaluation, chaos, all, unit
#
# Note: Integration tests require running services (via Docker Compose).
# Use 'unit' to run only tests that don't require live services.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
TESTS_DIR="$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "Evershade Ecosystem Test Suite"
echo "========================================"
echo ""

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest not found. Install with: pip install -r requirements-test.txt${NC}"
    exit 1
fi

# Check if requests is available
if ! python -c "import requests" 2>/dev/null; then
    echo -e "${RED}Error: requests not found. Install with: pip install -r requirements-test.txt${NC}"
    exit 1
fi

CATEGORY="${1:-all}"

run_tests() {
    local category="$1"
    local test_dir="$TESTS_DIR/$category"
    
    if [ ! -d "$test_dir" ]; then
        echo -e "${YELLOW}Warning: Test directory not found: $test_dir${NC}"
        return 0
    fi
    
    echo -e "${GREEN}Running $category tests...${NC}"
    echo "----------------------------------------"
    
    cd "$TESTS_DIR"
    if pytest "$category" -v --tb=short 2>&1; then
        echo -e "${GREEN}✓ $category tests passed${NC}"
    else
        echo -e "${RED}✗ $category tests failed${NC}"
        return 1
    fi
    echo ""
}

case "$CATEGORY" in
    unit)
        echo -e "${GREEN}Running unit tests (skipping integration tests)...${NC}"
        echo "----------------------------------------"
        cd "$TESTS_DIR"
        if pytest -v -m "not integration" --tb=short 2>&1; then
            echo -e "${GREEN}✓ Unit tests passed${NC}"
        else
            echo -e "${RED}✗ Unit tests failed${NC}"
            exit 1
        fi
        ;;
    integration)
        run_tests integration
        ;;
    security)
        run_tests security
        ;;
    benchmarks)
        run_tests benchmarks
        ;;
    evaluation)
        run_tests evaluation
        ;;
    chaos)
        run_tests chaos
        ;;
    all)
        echo -e "${YELLOW}Note: Running ALL tests requires live services.${NC}"
        echo -e "${YELLOW}Start services first: docker compose --profile minimal up -d${NC}"
        echo ""
        FAILED=0
        for cat in integration security benchmarks evaluation chaos; do
            if ! run_tests "$cat"; then
                FAILED=1
            fi
        done
        
        echo "========================================"
        if [ $FAILED -eq 0 ]; then
            echo -e "${GREEN}All tests passed!${NC}"
        else
            echo -e "${RED}Some tests failed.${NC}"
            exit 1
        fi
        ;;
    *)
        echo -e "${RED}Unknown category: $CATEGORY${NC}"
        echo "Available: unit, integration, security, benchmarks, evaluation, chaos, all"
        exit 1
        ;;
esac
