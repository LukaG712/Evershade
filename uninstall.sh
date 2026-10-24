#!/bin/bash
# Evershade — Uninstall Script (Linux/macOS)
# Removes all Evershade components: Docker containers, systemd service, desktop entry.
# Run with: sudo bash uninstall.sh [OPTIONS]
#
# WARNING: This will stop and remove all Evershade Docker containers and data.

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

REMOVE_DIR=false
REMOVE_DATA=false
FORCE=false

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Evershade Uninstaller                                      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --remove-dir)
            REMOVE_DIR=true
            shift
            ;;
        --remove-data)
            REMOVE_DATA=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --help|-h)
            echo "Usage: sudo bash uninstall.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --remove-dir    Remove the Evershade installation directory"
            echo "  --remove-data   Remove Docker volumes (persistent data)"
            echo "  --force         Skip confirmation prompts"
            echo "  --help, -h      Show this help message"
            echo ""
            echo "WARNING: This will stop and remove all Evershade Docker containers."
            echo "Data in Docker volumes will be preserved unless --remove-data is used."
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Detect install directory
INSTALL_DIR=""
if [ -f "/etc/systemd/system/evershade.service" ]; then
    INSTALL_DIR=$(grep -oP 'WorkingDirectory=\K.*' /etc/systemd/system/evershade.service 2>/dev/null || echo "")
fi

if [ -z "$INSTALL_DIR" ]; then
    # Try common locations
    SUDO_USER="${SUDO_USER:-${USER:-root}}"
    if [ -d "/home/$SUDO_USER/Evershade" ]; then
        INSTALL_DIR="/home/$SUDO_USER/Evershade"
    elif [ -d "$HOME/Evershade" ]; then
        INSTALL_DIR="$HOME/Evershade"
    elif [ -d "/root/Evershade" ]; then
        INSTALL_DIR="/root/Evershade"
    fi
fi

if [ -z "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}⚠${NC} Could not detect Evershade installation directory."
    echo -e "${YELLOW}   Please specify it manually or run this from the Evershade directory.${NC}"
    echo ""
    read -rp "Installation directory: " INSTALL_DIR
fi

if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${RED}ERROR: Directory '$INSTALL_DIR' does not exist.${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Installation directory: $INSTALL_DIR"
echo ""

# Confirmation prompt
if [ "$FORCE" != true ]; then
    echo -e "${YELLOW}The following components will be removed:${NC}"
    echo ""
    
    if [ -f "/etc/systemd/system/evershade.service" ]; then
        echo "  [x] Systemd service (evershade.service)"
    fi
    
    if [ -d "/home/$SUDO_USER/.local/share/applications" ] && [ -f "/home/$SUDO_USER/.local/share/applications/evershade.desktop" ]; then
        echo "  [x] Desktop launcher"
    fi
    
    if [ -d "$INSTALL_DIR" ]; then
        echo "  [x] Docker containers and networks"
        if [ "$REMOVE_DIR" = true ]; then
            echo "  [x] Installation directory: $INSTALL_DIR"
        fi
        if [ "$REMOVE_DATA" = true ]; then
            echo "  [x] Docker volumes (all persistent data)"
        fi
    fi
    
    echo ""
    read -rp "Are you sure you want to continue? (y/N) " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}✓${NC} Uninstall cancelled."
        exit 0
    fi
fi

echo ""

# Step 1: Stop Docker containers
echo -e "${BLUE}→${NC} Stopping Evershade Docker containers..."
if [ -f "$INSTALL_DIR/docker-compose.yml" ]; then
    cd "$INSTALL_DIR"
    if docker compose down --remove-orphans 2>&1; then
        echo -e "${GREEN}✓${NC} Docker containers stopped"
    else
        echo -e "${YELLOW}⚠${NC} Failed to stop Docker containers (they may already be stopped)"
    fi
else
    echo -e "${YELLOW}⚠${NC} docker-compose.yml not found, skipping Docker cleanup"
fi

# Step 2: Remove Docker volumes (optional)
if [ "$REMOVE_DATA" = true ]; then
    echo ""
    echo -e "${BLUE}→${NC} Removing Docker volumes..."
    if [ -f "$INSTALL_DIR/docker-compose.yml" ]; then
        cd "$INSTALL_DIR"
        if docker compose down -v 2>&1; then
            echo -e "${GREEN}✓${NC} Docker volumes removed"
        else
            echo -e "${YELLOW}⚠${NC} Failed to remove Docker volumes"
        fi
    fi
fi

# Step 3: Stop and remove systemd service
echo ""
echo -e "${BLUE}→${NC} Removing systemd service..."
if [ -f "/etc/systemd/system/evershade.service" ]; then
    systemctl stop evershade 2>/dev/null || true
    systemctl disable evershade 2>/dev/null || true
    rm -f /etc/systemd/system/evershade.service
    systemctl daemon-reload
    echo -e "${GREEN}✓${NC} Systemd service removed"
else
    echo -e "${YELLOW}⚠${NC} No systemd service found"
fi

# Step 4: Remove desktop entry
echo ""
echo -e "${BLUE}→${NC} Removing desktop launcher..."
SUDO_USER="${SUDO_USER:-${USER:-root}}"
DESKTOP_FILE="/home/$SUDO_USER/.local/share/applications/evershade.desktop"
if [ -f "$DESKTOP_FILE" ]; then
    rm -f "$DESKTOP_FILE"
    echo -e "${GREEN}✓${NC} Desktop launcher removed"
else
    echo -e "${YELLOW}⚠${NC} No desktop launcher found"
fi

# Step 5: Remove installation directory (optional)
if [ "$REMOVE_DIR" = true ]; then
    echo ""
    echo -e "${BLUE}→${NC} Removing installation directory: $INSTALL_DIR"
    rm -rf "$INSTALL_DIR"
    echo -e "${GREEN}✓${NC} Installation directory removed"
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Uninstall complete!                                        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$REMOVE_DIR" != true ]; then
    echo -e "${YELLOW}⚠${NC} Installation directory preserved at: $INSTALL_DIR"
    echo -e "${YELLOW}   To remove it manually: rm -rf $INSTALL_DIR${NC}"
fi

if [ "$REMOVE_DATA" != true ]; then
    echo -e "${YELLOW}⚠${NC} Docker volumes preserved. To remove them:"
    echo -e "${YELLOW}   cd $INSTALL_DIR && docker compose down -v${NC}"
fi

echo ""
