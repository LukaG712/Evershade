#!/bin/bash
# Evershade — Ubuntu Desktop Installer
# All-in-one installer: prerequisites, Docker setup, repo clone, configuration, and launch.
# Designed for Ubuntu Desktop (20.04+). Safe to re-run.

set -euo pipefail

# ─── Colors ─────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ─── Configuration ──────────────────────────────────────────────────
REPO_URL="https://github.com/LukaG712/Evershade.git"
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
    echo "║       Evershade — Ubuntu Desktop Installer                   ║"
    echo "║                                                              ║"
    echo "║  Self-hosted AI agent platform (Docker-based microservices)  ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# ─── Argument Parsing ───────────────────────────────────────────────
FORCE=false
AUTO=false
SKIP_START=false
CUSTOM_SERVICES=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE=true
            shift
            ;;
        --auto)
            AUTO=true
            SKIP_START=true
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
        --dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        --skip-start)
            SKIP_START=true
            shift
            ;;
        --help|-h)
            echo "Usage: sudo bash install-ubuntu.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --force          Remove existing installation directory"
            echo "  --auto           Non-interactive: accept defaults, skip prompts"
            echo "  --profile NAME   Install profile: minimal, standard, full, custom (default: standard)"
            echo "  --custom LIST    Comma-separated services (requires --profile custom)"
            echo "  --dir PATH       Install directory (default: ~/Evershade)"
            echo "  --skip-start     Don't start services after install"
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
            echo ""
            echo "Note: Run with sudo for Docker installation, or as root."
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

# Check Ubuntu
if ! command -v lsb_release &>/dev/null && [ ! -f /etc/os-release ]; then
    error "This script is designed for Ubuntu Desktop."
    error "Detected non-Ubuntu system. Proceeding is not recommended."
    exit 1
fi

if [ -f /etc/os-release ]; then
    . /etc/os-release
    UBUNTU_VERSION="${VERSION_ID:-unknown}"
    info "Detected Ubuntu $UBUNTU_VERSION ($PRETTY_NAME)"

    # Check minimum version
    if [[ "$UBUNTU_VERSION" < "20.04" ]]; then
        error "Ubuntu 20.04 or later is required. Detected: $UBUNTU_VERSION"
        exit 1
    fi
fi

# Check architecture
ARCH=$(dpkg --print-architecture 2>/dev/null || echo "unknown")
info "System architecture: $ARCH"
if [[ "$ARCH" != "amd64" && "$ARCH" != "arm64" ]]; then
    warn "Architecture $ARCH may not be fully supported. Proceeding anyway."
fi

# Check sudo
if [[ $EUID -ne 0 ]]; then
    error "This installer requires root privileges for Docker installation."
    error "Please run: sudo bash $0"
    exit 1
fi

info "Install directory: $INSTALL_DIR"
info "Profile: $PROFILE"
echo ""

# ─── Step 1: Install System Dependencies ────────────────────────────
step "Step 1: Installing System Dependencies"

# Update package lists
info "Updating package lists..."
apt-get update -y > /dev/null 2>&1
success "Package lists updated"

# Install Git if missing
if ! command -v git &>/dev/null; then
    info "Installing Git..."
    apt-get install -y git > /dev/null 2>&1
    success "Git installed ($(git --version | awk '{print $3}'))"
else
    success "Git already installed ($(git --version | awk '{print $3}'))"
fi

# Install Python3 if missing
if ! command -v python3 &>/dev/null; then
    info "Installing Python3..."
    apt-get install -y python3 > /dev/null 2>&1
    success "Python3 installed ($(python3 --version))"
else
    success "Python3 already installed ($(python3 --version))"
fi

# Install curl, wget, ca-certificates (needed for Docker)
for pkg in curl wget ca-certificates gnupg lsb-release; do
    if ! dpkg -s "$pkg" &>/dev/null; then
        info "Installing $pkg..."
        apt-get install -y "$pkg" > /dev/null 2>&1
        success "$pkg installed"
    else
        success "$pkg already installed"
    fi
done

# ─── Step 2: Install Docker ─────────────────────────────────────────
step "Step 2: Setting Up Docker"

if command -v docker &>/dev/null && docker compose version &>/dev/null; then
    success "Docker already installed ($(docker --version | awk '{print $3}'))"
    success "Docker Compose available ($(docker compose version --short 2>/dev/null || echo 'available'))"
else
    info "Installing Docker Engine..."

    # Remove old versions
    for old in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
        apt-get remove -y "$old" 2>/dev/null || true
    done

    # Add Docker's official GPG key
    info "Adding Docker GPG key..."
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc

    # Add Docker repository
    ARCH_VAR="${ARCH}"
    if [[ "$ARCH_VAR" == "arm64" ]]; then
        ARCH_VAR="arm64"
    elif [[ "$ARCH_VAR" == "amd64" ]]; then
        ARCH_VAR="amd64"
    fi

    echo \
      "deb [arch=${ARCH_VAR} signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null

    info "Installing Docker Engine..."
    apt-get update -y > /dev/null 2>&1
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin > /dev/null 2>&1

    # Start and enable Docker
    systemctl enable docker > /dev/null 2>&1
    systemctl start docker > /dev/null 2>&1 || true

    success "Docker installed ($(docker --version | awk '{print $3}'))"
    success "Docker Compose installed ($(docker compose version --short 2>/dev/null || echo 'available'))"
fi

# ─── Step 3: Add User to Docker Group ───────────────────────────────
step "Step 3: Configuring Docker Permissions"

# Find the invoking user (before sudo)
INVOKING_USER="${SUDO_USER:-$(whoami)}"

if ! getent group docker &>/dev/null; then
    info "Creating docker group..."
    groupadd docker
fi

if id "$INVOKING_USER" &>/dev/null; then
    if ! id -nG "$INVOKING_USER" 2>/dev/null | grep -qw docker; then
        info "Adding user '$INVOKING_USER' to docker group..."
        usermod -aG docker "$INVOKING_USER"
        success "User '$INVOKING_USER' added to docker group"
        warn "You may need to log out and log back in for Docker permissions to take effect."
        warn "Or run: newgrp docker"
    else
        success "User '$INVOKING_USER' is already in the docker group"
    fi
else
    warn "User '$INVOKING_USER' not found. Skipping docker group setup."
fi

# ─── Step 4: Clone Evershade Repository ─────────────────────────────
step "Step 4: Cloning Evershade Repository"

if [ -d "$INSTALL_DIR" ]; then
    if [ -d "$INSTALL_DIR/.git" ]; then
        if [ "$FORCE" = true ]; then
            warn "Removing existing installation (forced)..."
            rm -rf "$INSTALL_DIR"
        else
            info "Evershade already exists at $INSTALL_DIR"
            if [ "$AUTO" = false ]; then
                read -rp "  Update existing installation? (y/N): " UPDATE_ANS
                if [[ "$UPDATE_ANS" =~ ^[Yy] ]]; then
                    info "Pulling latest changes..."
                    cd "$INSTALL_DIR"
                    git pull 2>&1 | tail -3
                    success "Repository updated"
                else
                    success "Keeping existing installation"
                fi
            else
                info "Pulling latest changes (auto mode)..."
                cd "$INSTALL_DIR"
                git pull 2>&1 | tail -3 || true
                success "Repository updated"
            fi
        fi
    else
        error "$INSTALL_DIR exists but is not a git repository."
        error "Use --force to remove it and start fresh."
        exit 1
    fi
else
    info "Cloning Evershade from $REPO_URL ..."
    git clone "$REPO_URL" "$INSTALL_DIR" 2>&1 | tail -5
    success "Evershade cloned to $INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# Set ownership for the invoking user
if id "$INVOKING_USER" &>/dev/null; then
    chown -R "$INVOKING_USER":"$INVOKING_USER" "$INSTALL_DIR" 2>/dev/null || true
fi

# ─── Step 5: Clone Service Repositories ─────────────────────────────
step "Step 5: Installing Service Repositories"

if [ -f "install.sh" ]; then
    info "Running service installer with profile: $PROFILE"
    chmod +x install.sh

    # Build install.sh command
    INSTALL_CMD="./install.sh --profile $PROFILE"
    if [ "$PROFILE" = "custom" ] && [ -n "$CUSTOM_SERVICES" ]; then
        INSTALL_CMD="$INSTALL_CMD --custom $CUSTOM_SERVICES"
    fi

    # Run as invoking user to avoid permission issues
    if id "$INVOKING_USER" &>/dev/null; then
        sudo -u "$INVOKING_USER" bash -c "cd '$INSTALL_DIR' && $INSTALL_CMD"
    else
        bash -c "$INSTALL_CMD"
    fi
    success "Service repositories installed"
else
    error "install.sh not found in $INSTALL_DIR"
    exit 1
fi

# ─── Step 6: Configure .env ─────────────────────────────────────────
step "Step 6: Configuring Environment"

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        info "Creating .env from .env.example..."
        cp .env.example .env

        # Auto-generate secure API keys
        info "Generating secure API keys..."

        generate_key() {
            if command -v openssl &>/dev/null; then
                openssl rand -hex 32
            else
                # Fallback: use /dev/urandom
                head -c 64 /dev/urandom | od -An -tx1 | tr -d ' \n' | head -c 64
            fi
        }

        # Replace default keys with generated ones
        sed -i "s/^EVERSHADE_GREENIE_API_KEY=.*/EVERSHADE_GREENIE_API_KEY=$(generate_key)/" .env
        sed -i "s/^EVERSHADE_SLINKER_API_KEY=.*/EVERSHADE_SLINKER_API_KEY=$(generate_key)/" .env
        sed -i "s/^EVERSHADE_TRAPPER_API_KEY=.*/EVERSHADE_TRAPPER_API_KEY=$(generate_key)/" .env
        sed -i "s/^EVERSHADE_GOBBER_API_KEY=.*/EVERSHADE_GOBBER_API_KEY=$(generate_key)/" .env
        sed -i "s/^EVERSHADE_SNEAKER_API_KEY=.*/EVERSHADE_SNEAKER_API_KEY=$(generate_key)/" .env
        sed -i "s/^EVERSHADE_HIDER_API_KEY=.*/EVERSHADE_HIDER_API_KEY=$(generate_key)/" .env
        sed -i "s/^EVERSHADE_POLTERGEIST_API_KEY=.*/EVERSHADE_POLTERGEIST_API_KEY=$(generate_key)/" .env
        sed -i "s/^EVERSHADE_SHREWD_API_KEY=.*/EVERSHADE_SHREWD_API_KEY=$(generate_key)/" .env
        sed -i "s/^EVERSHADE_ENCRYPTION_KEY=.*/EVERSHADE_ENCRYPTION_KEY=$(generate_key)/" .env

        # Fix Ollama URL for Linux Docker (host.docker.internal doesn't work by default)
        sed -i 's|EVERSHADE_OLLAMA_URL=http://host.docker.internal:11434|EVERSHADE_OLLAMA_URL=http://host.docker.internal:11434|' .env
        warn "For Ollama on Linux, you may need to add --add-host=host.docker.internal:host-gateway to Docker."
        warn "Or set EVERSHADE_OLLAMA_URL to your Ollama host IP in .env"

        # Set ownership
        if id "$INVOKING_USER" &>/dev/null; then
            chown "$INVOKING_USER":"$INVOKING_USER" .env 2>/dev/null || true
        fi

        success ".env created with auto-generated secure keys"
        success "Configuration saved to $INSTALL_DIR/.env"
    else
        error ".env.example not found. Cannot create configuration."
        exit 1
    fi
else
    info ".env already exists — skipping configuration"
    if [ "$AUTO" = false ]; then
        read -rp "  Regenerate .env with new keys? (y/N): " REGEN_ANS
        if [[ "$REGEN_ANS" =~ ^[Yy] ]]; then
            warn "This will overwrite your current .env!"
            read -rp "  Are you sure? (y/N): " CONFIRM
            if [[ "$CONFIRM" =~ ^[Yy] ]]; then
                info "Regenerating .env..."
                cp .env.example .env

                generate_key() {
                    openssl rand -hex 32
                }

                sed -i "s/^EVERSHADE_GREENIE_API_KEY=.*/EVERSHADE_GREENIE_API_KEY=$(generate_key)/" .env
                sed -i "s/^EVERSHADE_SLINKER_API_KEY=.*/EVERSHADE_SLINKER_API_KEY=$(generate_key)/" .env
                sed -i "s/^EVERSHADE_TRAPPER_API_KEY=.*/EVERSHADE_TRAPPER_API_KEY=$(generate_key)/" .env
                sed -i "s/^EVERSHADE_GOBBER_API_KEY=.*/EVERSHADE_GOBBER_API_KEY=$(generate_key)/" .env
                sed -i "s/^EVERSHADE_SNEAKER_API_KEY=.*/EVERSHADE_SNEAKER_API_KEY=$(generate_key)/" .env
                sed -i "s/^EVERSHADE_HIDER_API_KEY=.*/EVERSHADE_HIDER_API_KEY=$(generate_key)/" .env
                sed -i "s/^EVERSHADE_POLTERGEIST_API_KEY=.*/EVERSHADE_POLTERGEIST_API_KEY=$(generate_key)/" .env
                sed -i "s/^EVERSHADE_SHREWD_API_KEY=.*/EVERSHADE_SHREWD_API_KEY=$(generate_key)/" .env
                sed -i "s/^EVERSHADE_ENCRYPTION_KEY=.*/EVERSHADE_ENCRYPTION_KEY=$(generate_key)/" .env

                if id "$INVOKING_USER" &>/dev/null; then
                    chown "$INVOKING_USER":"$INVOKING_USER" .env 2>/dev/null || true
                fi

                success ".env regenerated with new keys"
            else
                info "Keeping existing .env"
            fi
        fi
    fi
fi

# ─── Step 7: Optional — Systemd Service ─────────────────────────────
step "Step 7: Optional Systemd Service"

SYSTEMD_WANT=false
if [ "$AUTO" = false ]; then
    read -rp "  Create systemd service for auto-start on boot? (Y/n): " SYSTEMD_ANS
    if [[ ! "$SYSTEMD_ANS" =~ ^[Nn] ]]; then
        SYSTEMD_WANT=true
    fi
else
    SYSTEMD_WANT=true
fi

if [ "$SYSTEMD_WANT" = true ]; then
    info "Creating systemd service: evershade.service"

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
    success "Systemd service created: evershade.service"
    info "Manage with:"
    echo "  sudo systemctl start evershade"
    echo "  sudo systemctl stop evershade"
    echo "  sudo systemctl status evershade"
    echo "  sudo systemctl enable evershade   # auto-start on boot"
else
    info "Skipping systemd service creation"
fi

# ─── Step 8: Optional — Desktop Entry ───────────────────────────────
step "Step 8: Optional Desktop Integration"

DESKTOP_WANT=false
if [ "$AUTO" = false ]; then
    read -rp "  Create desktop launcher icon? (Y/n): " DESKTOP_ANS
    if [[ ! "$DESKTOP_ANS" =~ ^[Nn] ]]; then
        DESKTOP_WANT=true
    fi
else
    DESKTOP_WANT=true
fi

if [ "$DESKTOP_WANT" = true ] && id "$INVOKING_USER" &>/dev/null; then
    USER_HOME=$(eval echo "~$INVOKING_USER")
    DESKTOP_DIR="$USER_HOME/.local/share/applications"
    mkdir -p "$DESKTOP_DIR"

    cat > "$DESKTOP_DIR/evershade.desktop" << DESKTOP_EOF
[Desktop Entry]
Name=Evershade
Comment=Self-hosted AI Agent Platform
Exec=gnome-terminal -- bash -c "cd $INSTALL_DIR && ./start.sh --profile $PROFILE; exec bash"
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Development;Utility;
StartupNotify=true
DESKTOP_EOF

    chown "$INVOKING_USER":"$INVOKING_USER" "$DESKTOP_DIR/evershade.desktop" 2>/dev/null || true
    success "Desktop launcher created at ~/.local/share/applications/evershade.desktop"
else
    info "Skipping desktop launcher"
fi

# ─── Step 9: Start Services ─────────────────────────────────────────
if [ "$SKIP_START" = false ]; then
    step "Step 9: Starting Evershade Services"

    if [ "$AUTO" = false ]; then
        read -rp "  Start services now? (Y/n): " START_ANS
        if [[ "$START_ANS" =~ ^[Nn] ]]; then
            START_NOW=false
        else
            START_NOW=true
        fi
    else
        START_NOW=true
    fi

    if [ "$START_NOW" = true ]; then
        info "Starting services with profile: $PROFILE"

        # Ensure start.sh is executable
        chmod +x start.sh

        if id "$INVOKING_USER" &>/dev/null; then
            sudo -u "$INVOKING_USER" bash -c "cd '$INSTALL_DIR' && ./start.sh --profile $PROFILE"
        else
            ./start.sh --profile "$PROFILE"
        fi

        success "Services started!"
        echo ""
        info "Evershade API is available at: http://localhost:8080"
    else
        info "Services not started. Run manually:"
        echo "  cd $INSTALL_DIR && ./start.sh --profile $PROFILE"
    fi
else
    info "Skipping service start (--skip-start)"
fi

# ─── Summary ─────────────────────────────────────────────────────────
echo ""
success "╔══════════════════════════════════════════════════════════════╗"
success "║  Evershade installation complete!                           ║"
success "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Installation summary:"
echo "  Directory:    $INSTALL_DIR"
echo "  Profile:      $PROFILE"
echo "  User:         $INVOKING_USER"
echo ""
echo "Quick commands:"
echo "  cd $INSTALL_DIR"
echo "  ./start.sh --profile $PROFILE     # Start services"
echo "  ./stop.sh                        # Stop services"
echo "  ./install.sh --profile $PROFILE   # Update service repos"
echo ""
echo "API endpoint:  http://localhost:8080"
echo ""

if [ "$SYSTEMD_WANT" = true ]; then
    echo "Systemd service:"
    echo "  sudo systemctl start evershade"
    echo "  sudo systemctl enable evershade   # Auto-start on boot"
    echo ""
fi

echo "For LLM providers, edit $INSTALL_DIR/.env and add your API keys:"
echo "  EVERSHADE_OPENAI_API_KEY"
echo "  EVERSHADE_ANTHROPIC_API_KEY"
echo "  EVERSHADE_GOOGLE_API_KEY"
echo ""
success "Welcome to Evershade! 🏚️"
