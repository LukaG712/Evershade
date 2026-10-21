#!/bin/bash
# Unified Workflow — Stop Script (Linux/macOS)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Stopping all services..."

docker compose down

echo "Services stopped."
echo ""
echo "To remove volumes and data: docker compose down -v"
echo "To start again: ./start.sh"
