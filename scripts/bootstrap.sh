#!/bin/bash

# NixOS AI Assistant Bootstrap Script
# One-command installer for the NixOS AI system

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/yaseenTarek26/Smart-Nix-OS.git"
INSTALL_DIR="/etc/nixos/nixos-ai"
CONFIG_FILE="/etc/nixos/configuration.nix"
BACKUP_DIR="/etc/nixos/backup-$(date +%Y%m%d-%H%M%S)"

log() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   error "This script must be run as root. Please run with sudo:
   
   sudo sh <(curl -s https://raw.githubusercontent.com/yaseenTarek26/Smart-Nix-OS/main/scripts/bootstrap.sh)
   
   Or download and run manually:
   curl -s https://raw.githubusercontent.com/yaseenTarek26/Smart-Nix-OS/main/scripts/bootstrap.sh -o bootstrap.sh
   sudo sh bootstrap.sh"
fi

# Check if we're on NixOS
if [[ ! -f /etc/nixos/configuration.nix ]]; then
    error "This script is designed for NixOS. /etc/nixos/configuration.nix not found."
fi

log "Starting NixOS AI Assistant installation..."

# Create backup of current configuration
log "Creating backup of current configuration..."
mkdir -p "$BACKUP_DIR"
cp "$CONFIG_FILE" "$BACKUP_DIR/"
success "Backup created at $BACKUP_DIR"

# Clone the repository
log "Cloning NixOS AI repository..."
if [[ -d "$INSTALL_DIR" ]]; then
    warn "Installation directory already exists. Updating..."
    cd "$INSTALL_DIR"
    git pull origin main || error "Failed to update existing repository"
else
    git clone "$REPO_URL" "$INSTALL_DIR" || error "Failed to clone repository"
fi

# Make scripts executable
chmod +x "$INSTALL_DIR/scripts"/*.sh

# Add import to configuration.nix if not already present
log "Adding AI module import to configuration.nix..."
if ! grep -q "nixos-ai/nix/ai.nix" "$CONFIG_FILE"; then
    # Create a backup of the original
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup"
    
    # Add the import
    if grep -q "imports = \[" "$CONFIG_FILE"; then
        # Add to existing imports array
        sed -i '/imports = \[/a\  ./nixos-ai/nix/ai.nix' "$CONFIG_FILE"
    else
        # Create imports array
        sed -i '1i\imports = [ ./nixos-ai/nix/ai.nix ];' "$CONFIG_FILE"
    fi
    success "Added AI module import to configuration.nix"
else
    warn "AI module import already present in configuration.nix"
fi

# Install Python dependencies
log "Installing Python dependencies..."
cd "$INSTALL_DIR"
python3 -m pip install --user -r requirements.txt || {
    warn "Failed to install via pip, trying with nix-shell..."
    nix-shell -p python3Packages.pip python3Packages.setuptools --run "pip install -r requirements.txt"
}

# Set up directories
mkdir -p "$INSTALL_DIR/logs"
mkdir -p "$INSTALL_DIR/state"
mkdir -p "$INSTALL_DIR/cache"
chmod 755 "$INSTALL_DIR/logs" "$INSTALL_DIR/state" "$INSTALL_DIR/cache"

# Initialize git repository for tracking changes
cd "$INSTALL_DIR"
if [[ ! -d .git ]]; then
    git init
    git config user.name "NixOS AI Assistant"
    git config user.email "ai@nixos.local"
    git add .
    git commit -m "Initial AI assistant setup"
fi

# Test the NixOS configuration
log "Testing NixOS configuration..."
nixos-rebuild test --flake "$INSTALL_DIR" || {
    error "NixOS configuration test failed. Check the configuration and try again."
}

# Apply the configuration
log "Applying NixOS configuration..."
nixos-rebuild switch --flake "$INSTALL_DIR" || {
    error "Failed to apply NixOS configuration. Rolling back..."
    nixos-rebuild switch --rollback
    exit 1
}

# Enable and start the AI service
log "Starting AI assistant service..."
systemctl enable nixos-ai.service
systemctl start nixos-ai.service

# Create command-line interface
log "Setting up command-line interface..."
cat > /usr/local/bin/nixos-ai << 'EOF'
#!/bin/bash
# NixOS AI Assistant CLI
cd /etc/nixos/nixos-ai
python3 ai/agent.py "$@"
EOF
chmod +x /usr/local/bin/nixos-ai

success "NixOS AI Assistant installed successfully!"
echo ""
echo "Features:"
echo "  ✅ Multi-provider AI support (OpenAI, Anthropic, Ollama)"
echo "  ✅ Safe file editing with git snapshots"
echo "  ✅ Command execution with validation"
echo "  ✅ Real-time system monitoring"
echo "  ✅ Comprehensive safety mechanisms"
echo ""
echo "Usage:"
echo "  nixos-ai 'your command here'"
echo "  nixos-ai 'install docker and enable it'"
echo "  nixos-ai 'add vscode to system packages'"
echo ""
echo "Configuration:"
echo "  Edit: /etc/nixos/nixos-ai/ai/config.json"
echo "  Add your API keys for AI providers"
echo ""
echo "Service status:"
echo "  systemctl status nixos-ai.service"
echo ""
echo "Logs:"
echo "  journalctl -u nixos-ai.service -f"
echo "  tail -f /etc/nixos/nixos-ai/logs/ai.log"
echo ""
echo "Emergency rollback:"
echo "  /etc/nixos/nixos-ai/scripts/rollback.sh"
