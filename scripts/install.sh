#!/bin/bash
# Ultra-Simple NixOS AI Assistant Installer
# No systemd, no NixOS configuration, just works!

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Functions
log() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
REPO_URL="https://github.com/yaseenTarek26/Smart-Nix-OS.git"
INSTALL_DIR="/home/$USER/nixos-ai"
CLI_PATH="/home/$USER/.local/bin/nixos-ai"

log "Starting ultra-simple NixOS AI Assistant installation..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    error "Don't run as root! This installer works in user space."
    exit 1
fi

# Create installation directory
log "Creating installation directory..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Clone or update repository
if [[ -d ".git" ]]; then
    log "Updating existing installation..."
    git pull origin main || {
        warn "Git pull failed, continuing with existing files..."
    }
else
    log "Cloning repository..."
    git clone "$REPO_URL" . || {
        error "Failed to clone repository. Please check your internet connection."
        exit 1
    }
fi

# Install Python dependencies
log "Installing Python dependencies..."
python3 -m pip install --user --break-system-packages -r requirements.txt 2>/dev/null || {
    warn "Pip failed, trying without --break-system-packages..."
    python3 -m pip install --user -r requirements.txt || {
        warn "Pip failed, trying minimal installation..."
        python3 -m pip install --user httpx aiohttp psutil structlog pydantic typer || {
            error "Failed to install Python dependencies"
            exit 1
        }
    }
}

# Create directories
log "Creating directories..."
mkdir -p logs state cache

# Create simple startup script
log "Creating startup script..."
cat > start-ai.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)"
export AI_CONFIG_PATH="$(pwd)/ai/config.json"
export AI_LOGS_PATH="$(pwd)/logs"
export AI_STATE_PATH="$(pwd)/state"
export AI_CACHE_PATH="$(pwd)/cache"

echo "Starting NixOS AI Assistant..."
python3 ai/agent.py "$@"
EOF

chmod +x start-ai.sh

# Create CLI wrapper
log "Creating CLI wrapper..."
mkdir -p "$(dirname "$CLI_PATH")"
cat > "$CLI_PATH" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
./start-ai.sh "\$@"
EOF

chmod +x "$CLI_PATH"

# Add to PATH if not already there
if ! echo "$PATH" | grep -q "$(dirname "$CLI_PATH")"; then
    log "Adding to PATH..."
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    export PATH="$HOME/.local/bin:$PATH"
fi

# Test the installation
log "Testing installation..."
if "$CLI_PATH" --help >/dev/null 2>&1; then
    success "Installation test passed!"
else
    warn "Installation test failed, but continuing..."
fi

success "NixOS AI Assistant installed successfully!"
echo ""
echo "Usage:"
echo "  nixos-ai 'your command here'"
echo "  nixos-ai 'install docker and enable it'"
echo "  nixos-ai 'add vscode to system packages'"
echo ""
echo "Configuration:"
echo "  Edit: $INSTALL_DIR/ai/config.json"
echo "  Logs: $INSTALL_DIR/logs/"
echo ""
echo "To start manually:"
echo "  cd $INSTALL_DIR && ./start-ai.sh"
echo ""
echo "Installation complete! 🎉"
