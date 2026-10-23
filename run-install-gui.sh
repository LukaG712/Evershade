#!/bin/bash
# Evershade — GUI Installer Launcher (Linux)
# Checks prerequisites and launches the GUI installer with sudo.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUI_SCRIPT="$SCRIPT_DIR/install-gui.py"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Evershade GUI Installer — Launcher                          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Python3
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}ERROR: Python3 is not installed.${NC}"
    echo "Please install Python3 first:"
    echo "  sudo apt install python3 python3-tk"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python3 found ($(python3 --version))"

# Check Tkinter
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC} Tkinter not found. Installing..."
    if ! sudo apt install -y python3-tk 2>/dev/null; then
        echo -e "${RED}ERROR: Failed to install python3-tk.${NC}"
        echo "Please install manually: sudo apt install python3-tk"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} Tkinter installed"
fi
echo -e "${GREEN}✓${NC} Tkinter available"

# Check GUI script exists
if [ ! -f "$GUI_SCRIPT" ]; then
    echo -e "${RED}ERROR: install-gui.py not found at $GUI_SCRIPT${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} GUI installer found"

# Check X11/Wayland display
if [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ]; then
    echo -e "${YELLOW}⚠${NC} No display detected. Are you running in a terminal without a GUI?"
    echo "   If using SSH, enable X11 forwarding: ssh -X user@host"
    echo ""
    read -rp "Continue anyway? (y/N): " cont
    if [[ ! "$cont" =~ ^[Yy] ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Check sudo
if [[ $EUID -ne 0 ]]; then
    echo ""
    echo -e "${YELLOW}⚠${NC} This installer requires sudo privileges for Docker installation."
    echo "   You will be prompted for your password."
    echo ""
    if ! sudo -v; then
        echo -e "${RED}ERROR: sudo access required.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} sudo access granted"
    LAUNCH_CMD="sudo python3 \"$GUI_SCRIPT\""
else
    LAUNCH_CMD="python3 \"$GUI_SCRIPT\""
fi

echo ""
echo -e "${GREEN}Launching Evershade GUI Installer...${NC}"
echo ""

# Launch
exec $LAUNCH_CMD
