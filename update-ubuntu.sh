#!/bin/bash
# Evershade — Ubuntu Update Script
# Updates the Evershade installation: pulls latest repo changes, updates services,
# and optionally restarts running services.
#
# Usage:
#   sudo bash update-ubuntu.sh              # Interactive update
#   sudo bash update-ubuntu.sh --auto       # Non-interactive update
#   sudo bash update-ubuntu.sh --profile full  # Update with specific profile
#   sudo bash update-ubuntu.sh --skip-restart  # Don't restart services

set -euo pipefail

# ─── Colors ─────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ─── Configuration ──────────────────────────────────────────────────
REPO_DIR="Evershade"
PROFILE="${INSTALL_PROFILE:-standard}"
INSTALL_DIR="${INSTALL_PATH:-$HOME/$REPO_DIR}"

# ─── Helpers ─────────────────────────────────────────────────────────
info()    { echo -e "${BLUE}[INFO]${NC}    $*"; }
success() { echo -e "${GREEN}[OK]${NC}      $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}    $*"; }
error()   { echo -e "${RED}[ERROR]${NC}   $*"; }
step()    { echo -e "\n${CYAN}═══════════════════════════════════════════════════════════════${NC}"; echo -e "${CYAN}  $*${NC}"; echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"; }

banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║       Evershade — Ubuntu Update Script                       ║"
    echo "║                                                              ║"
    echo "║  Updates repo, services, and optionally restarts              ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# ─── Argument Parsing ───────────────────────────────────────────────
AUTO=false
SKIP_RESTART=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --auto)
            AUTO=true
            SKIP_RESTART=true
            shift
            ;;
        --profile)
            PROFILE="$2"
            shift 2
            ;;
        --dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        --skip-restart)
            SKIP_RESTART=true
            shift
            ;;
        --help|-h)
            echo "Usage: sudo bash update-ubuntu.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --auto           Non-interactive: accept defaults, skip prompts"
            echo "  --profile NAME   Update profile: minimal, standard, full (default: standard)"
            echo "  --dir PATH       Installation directory (default: ~/Evershade)"
            echo "  --skip-restart   Don't restart services after update"
            echo "  --help, -h       Show this help message"
            echo ""
            echo "This script will:"
            echo "  1. Pull latest changes from the Evershade repository"
            echo "  2. Update all service repositories to their pinned commits"
            echo "  3. Optionally restart running services"
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# ─── Pre-flight Checks ──────────────────────────────────────────────
banner

# Check sudo
if [[ $EUID -ne 0 ]]; then
    error "This updater requires root privileges."
    error "Please run: sudo bash $0"
    exit 1
fi

INVOKING_USER="${SUDO_USER:-$(whoami)}"

info "Install directory: $INSTALL_DIR"
info "Profile: $PROFILE"
echo ""

# ─── Step 1: Pull Latest Repository ─────────────────────────────────
step "Step 1: Pulling Latest Repository"

if [ ! -d "$INSTALL_DIR" ]; then
    error "Evershade not found at $INSTALL_DIR"
    error "Run install-ubuntu.sh first to set up the installation."
    exit 1
fi

if [ ! -d "$INSTALL_DIR/.git" ]; then
    error "$INSTALL_DIR exists but is not a git repository."
    exit 1
fi

cd "$INSTALL_DIR"

info "Pulling latest changes..."
if git pull 2>&1; then
    success "Repository updated"
else
    warn "No changes to pull (already up to date)"
fi

# Set ownership
if id "$INVOKING_USER" &>/dev/null; then
    chown -R "$INVOKING_USER":"$INVOKING_USER" "$INSTALL_DIR" 2>/dev/null || true
fi

# ─── Step 2: Check for New Services ─────────────────────────────────
step "Step 2: Checking for New Services"

if [ -f "version-manifest.json" ]; then
    # Check if any services from the profile are missing
    MISSING_SERVICES=$(python3 -c "
import json
with open('version-manifest.json') as f:
    manifest = json.load(f)
profile_services = manifest.get('profiles', {}).get('$PROFILE', [])
import os
for svc in profile_services:
    if svc not in ('redis', 'ollama', 'caddy') and not os.path.isdir(svc):
        print(svc)
" 2>/dev/null || true)

    if [ -n "$MISSING_SERVICES" ]; then
        warn "New services detected: $MISSING_SERVICES"
        if [ "$AUTO" = false ]; then
            read -rp "  Install new services? (Y/n): " INSTALL_NEW
            if [[ ! "$INSTALL_NEW" =~ ^[Nn] ]]; then
                info "Installing new services..."
                chmod +x install.sh
                if id "$INVOKING_USER" &>/dev/null; then
                    sudo -u "$INVOKING_USER" bash -c "cd '$INSTALL_DIR' && ./install.sh --profile $PROFILE"
                else
                    ./install.sh --profile "$PROFILE"
                fi
                success "New services installed"
            else
                info "Skipping new service installation"
            fi
        else
            info "Installing new services (auto mode)..."
            chmod +x install.sh
            if id "$INVOKING_USER" &>/dev/null; then
                sudo -u "$INVOKING_USER" bash -c "cd '$INSTALL_DIR' && ./install.sh --profile $PROFILE"
            else
                ./install.sh --profile "$PROFILE"
            fi
            success "New services installed"
        fi
    else
        success "No new services to install"
    fi
else
    error "version-manifest.json not found"
    exit 1
fi

# ─── Step 3: Update Service Repositories ────────────────────────────
step "Step 3: Updating Service Repositories"

if [ -f "update.sh" ]; then
    info "Running service updater with profile: $PROFILE"
    chmod +x update.sh

    if id "$INVOKING_USER" &>/dev/null; then
        sudo -u "$INVOKING_USER" bash -c "cd '$INSTALL_DIR' && ./update.sh --profile $PROFILE --pull-main"
    else
        ./update.sh --profile "$PROFILE" --pull-main
    fi
    success "Service repositories updated"
else
    error "update.sh not found in $INSTALL_DIR"
    info "Falling back to install.sh --force..."
    chmod +x install.sh
    if id "$INVOKING_USER" &>/dev/null; then
        sudo -u "$INVOKING_USER" bash -c "cd '$INSTALL_DIR' && ./install.sh --profile $PROFILE --force"
    else
        ./install.sh --profile "$PROFILE" --force
    fi
    success "Service repositories reinstalled"
fi

# ─── Step 4: Restart Services ────────────────────────────────────────
if [ "$SKIP_RESTART" = false ]; then
    step "Step 4: Restarting Services"

    # Check if services are running
    RUNNING=false
    if command -v docker &>/dev/null; then
        if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "evershade\|greenie\|trapper\|gobber" 2>/dev/null; then
            RUNNING=true
        fi
    fi

    if [ "$RUNNING" = true ]; then
        if [ "$AUTO" = false ]; then
            read -rp "  Restart services to apply updates? (Y/n): " RESTART_ANS
            if [[ ! "$RESTART_ANS" =~ ^[Nn] ]]; then
                info "Stopping services..."
                chmod +x stop.sh
                if id "$INVOKING_USER" &>/dev/null; then
                    sudo -u "$INVOKING_USER" bash -c "cd '$INSTALL_DIR' && ./stop.sh"
                else
                    ./stop.sh
                fi

                info "Starting services..."
                chmod +x start.sh
                if id "$INVOKING_USER" &>/dev/null; then
                    sudo -u "$INVOKING_USER" bash -c "cd '$INSTALL_DIR' && ./start.sh --profile $PROFILE"
                else
                    ./start.sh --profile "$PROFILE"
                fi

                success "Services restarted!"
            else
                info "Services not restarted. Run manually:"
                echo "  cd $INSTALL_DIR && ./stop.sh && ./start.sh --profile $PROFILE"
            fi
        else
            info "Restarting services (auto mode)..."
            chmod +x stop.sh
            if id "$INVOKING_USER" &>/dev/null; then
                sudo -u "$INVOKING_USER" bash -c "cd '$INSTALL_DIR' && ./stop.sh"
            else
                ./stop.sh
            fi

            chmod +x start.sh
            if id "$INVOKING_USER" &>/dev/null; then
                sudo -u "$INVOKING_USER" bash -c "cd '$INSTALL_DIR' && ./start.sh --profile $PROFILE"
            else
                ./start.sh --profile "$PROFILE"
            fi

            success "Services restarted!"
        fi
    else
        info "No running services detected — skipping restart"
        info "Start services manually with:"
        echo "  cd $INSTALL_DIR && ./start.sh --profile $PROFILE"
    fi
else
    info "Skipping service restart (--skip-restart)"
fi

# ─── Update Systemd Service if exists ────────────────────────────────
if [ -f /etc/systemd/system/evershade.service ]; then
    step "Updating Systemd Service"

    # Update the systemd service with the current profile
    cat > /etc/systemd/system/evershade.service << SYSTEMD_EOF
[Unit]
Description=Evershade AI Agent Platform
After=docker.service network-online.target
Requires=docker.service

[Service]
Type=forking
User=$INVOKING_USER
Group=$INVOKING_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/start.sh --profile $PROFILE
ExecStop=$INSTALL_DIR/stop.sh
Restart=on-failure
RestartSec=10
Environment=HOME=$INSTALL_DIR

[Install]
WantedBy=multi-user.target
SYSTEMD_EOF

    systemctl daemon-reload
    success "Systemd service updated"
fi

# ─── Summary ─────────────────────────────────────────────────────────
echo ""
success "╔══════════════════════════════════════════════════════════════╗"
success "║  Evershade update complete!                                 ║"
success "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Update summary:"
echo "  Directory:    $INSTALL_DIR"
echo "  Profile:      $PROFILE"
echo ""
echo "Quick commands:"
echo "  cd $INSTALL_DIR"
echo "  ./start.sh --profile $PROFILE     # Start services"
echo "  ./stop.sh                        # Stop services"
echo "  ./update.sh --profile $PROFILE   # Update services"
echo ""
echo "API endpoint:  http://localhost:8080"
echo ""
success "Evershade is up to date! 🏚️"
