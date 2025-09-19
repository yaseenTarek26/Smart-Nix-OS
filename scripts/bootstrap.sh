#!/bin/bash

# NixOS AI Assistant Bootstrap Script
# One-command installer for the NixOS AI system

set -euo pipefail

# Parse command line arguments
FORCE_UPDATE=false
if [[ "${1:-}" == "--force" || "${1:-}" == "-f" ]]; then
    FORCE_UPDATE=true
    log "Force update mode enabled"
fi

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
   
   curl -s https://raw.githubusercontent.com/yaseenTarek26/Smart-Nix-OS/main/scripts/bootstrap.sh | sudo sh
   
   Or download and run manually:
   curl -s https://raw.githubusercontent.com/yaseenTarek26/Smart-Nix-OS/main/scripts/bootstrap.sh -o bootstrap.sh
   sudo sh bootstrap.sh
   rm bootstrap.sh"
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
    
    # Check for local changes
    if ! git diff --quiet; then
        if [[ "$FORCE_UPDATE" == "true" ]]; then
            warn "Force update mode: discarding local changes..."
            git reset --hard HEAD
            git clean -fd
            success "Local changes discarded"
        else
            warn "Local changes detected. Attempting to handle them..."
            
            # Try to stash first
            if git stash push -m "Auto-stash before update $(date)" 2>/dev/null; then
                success "Local changes stashed successfully"
            else
                warn "Failed to stash local changes, trying to reset..."
                
                # Try to reset to clean state
                if git reset --hard HEAD 2>/dev/null; then
                    success "Reset to clean state"
                else
                    warn "Failed to reset, trying to clean untracked files..."
                    
                    # Clean untracked files
                    git clean -fd 2>/dev/null || {
                        error "Failed to handle local changes. Please resolve manually:
                        
                        cd $INSTALL_DIR
                        git status
                        git stash
                        git pull origin main
                        
                        Or force update with:
                        curl -s https://raw.githubusercontent.com/yaseenTarek26/Smart-Nix-OS/main/scripts/bootstrap.sh | sudo sh -- --force"
                    }
                fi
            fi
        fi
    fi
    
    # Pull latest changes
    if git pull origin main 2>/dev/null; then
        success "Repository updated successfully"
        
        # Restore stashed changes if any
        if git stash list | grep -q "Auto-stash before update"; then
            log "Restoring stashed changes..."
            git stash pop || {
                warn "Failed to restore stashed changes. You can recover them with:
                cd $INSTALL_DIR
                git stash list
                git stash show -p stash@{0}"
            }
        fi
    else
        warn "Pull failed, trying force update..."
        
        # Force update as last resort
        if git fetch origin main && git reset --hard origin/main 2>/dev/null; then
            success "Repository force updated successfully"
        else
            error "Failed to update existing repository. Please resolve manually:
            
            cd $INSTALL_DIR
            git status
            git pull origin main
            
            Or force update with:
            git fetch origin main
            git reset --hard origin/main"
        fi
    fi
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

# Try different installation methods for NixOS
log "Attempting to install Python dependencies..."

# Method 1: Try with --break-system-packages (for externally-managed environments)
if python3 -m pip install --user --break-system-packages -r requirements.txt 2>/dev/null; then
    success "Python dependencies installed with --break-system-packages"
elif python3 -m pip install --user -r requirements.txt 2>/dev/null; then
    success "Python dependencies installed normally"
else
    warn "Pip installation failed, trying with nix-shell..."
    
    # Method 2: Use nix-shell with proper Python environment
    if nix-shell -p python3Packages.pip python3Packages.setuptools python3Packages.openai python3Packages.anthropic python3Packages.google-generativeai python3Packages.httpx python3Packages.aiohttp python3Packages.psutil python3Packages.watchdog python3Packages.structlog python3Packages.pydantic python3Packages.typer --run "pip install --user -r requirements.txt" 2>/dev/null; then
        success "Python dependencies installed via nix-shell"
    else
        warn "nix-shell installation failed, trying minimal installation..."
        
        # Method 3: Install only essential packages
        nix-shell -p python3Packages.openai python3Packages.anthropic python3Packages.google-generativeai python3Packages.httpx python3Packages.aiohttp python3Packages.psutil python3Packages.watchdog python3Packages.structlog python3Packages.pydantic python3Packages.typer --run "echo 'Essential packages installed via nix-shell'" || {
            error "Failed to install Python dependencies. Please install them manually:
            
            nix-shell -p python3Packages.openai python3Packages.anthropic python3Packages.google-generativeai python3Packages.httpx python3Packages.aiohttp python3Packages.psutil python3Packages.watchdog python3Packages.structlog python3Packages.pydantic python3Packages.typer
            
            Then run: pip install --user -r requirements.txt"
        }
    fi
fi

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
if nixos-rebuild test --flake "$INSTALL_DIR" 2>/dev/null; then
    success "NixOS configuration test passed"
else
    warn "NixOS configuration test failed, trying without flake..."
    
    # Try without flake if flake test fails
    if nixos-rebuild test 2>/dev/null; then
        success "NixOS configuration test passed (without flake)"
    else
        error "NixOS configuration test failed. Please check:
        
        1. Your configuration.nix syntax
        2. Available packages in nixpkgs
        3. Run: nixos-rebuild test --show-trace
        
        The AI module may not be compatible with your NixOS version."
    fi
fi

# Apply the configuration
log "Applying NixOS configuration..."
if nixos-rebuild switch --flake "$INSTALL_DIR" 2>/dev/null; then
    success "NixOS configuration applied successfully"
elif nixos-rebuild switch 2>/dev/null; then
    success "NixOS configuration applied successfully (without flake)"
else
    warn "Failed to apply NixOS configuration, attempting rollback..."
    
    if nixos-rebuild switch --rollback 2>/dev/null; then
        error "Configuration failed and rolled back. Please check your configuration manually:
        
        1. Check /etc/nixos/configuration.nix syntax
        2. Verify the AI module import is correct
        3. Run: nixos-rebuild test --show-trace
        
        You can try installing manually by adding to your configuration.nix:
        imports = [ ./nixos-ai/nix/ai.nix ];
        services.nixos-ai.enable = true;"
    else
        error "Configuration failed and rollback also failed. System may be in an unstable state.
        
        Please manually check your configuration and run:
        nixos-rebuild switch --rollback"
    fi
fi

# Enable and start the AI service
log "Starting AI assistant service..."
if systemctl enable nixos-ai.service 2>/dev/null; then
    success "AI service enabled"
else
    warn "Failed to enable AI service, continuing..."
fi

if systemctl start nixos-ai.service 2>/dev/null; then
    success "AI service started"
else
    warn "Failed to start AI service. This may be due to missing dependencies.
    
    You can try starting it manually later with:
    systemctl start nixos-ai.service
    
    Check the service status with:
    systemctl status nixos-ai.service"
fi

# Create command-line interface
log "Setting up command-line interface..."
if cat > /usr/local/bin/nixos-ai << 'EOF'
#!/bin/bash
# NixOS AI Assistant CLI
cd /etc/nixos/nixos-ai
python3 ai/agent.py "$@"
EOF
then
    if chmod +x /usr/local/bin/nixos-ai 2>/dev/null; then
        success "Command-line interface created"
    else
        warn "Failed to make CLI executable, but file was created"
    fi
else
    warn "Failed to create command-line interface"
fi

# Final verification
log "Performing final verification..."
if [[ -f "$INSTALL_DIR/ai/agent.py" ]]; then
    success "AI agent file found"
else
    error "AI agent file missing - installation may be incomplete"
fi

if [[ -f "/usr/local/bin/nixos-ai" ]]; then
    success "CLI interface found"
else
    warn "CLI interface missing - you can create it manually"
fi

if systemctl is-enabled nixos-ai.service >/dev/null 2>&1; then
    success "AI service is enabled"
else
    warn "AI service is not enabled - you may need to enable it manually"
fi

success "NixOS AI Assistant installation completed!"
echo ""
echo "Features:"
echo "  ✅ Multi-provider AI support (OpenAI, Anthropic, Ollama, Gemini)"
echo "  ✅ Safe file editing with git snapshots"
echo "  ✅ Command execution with validation"
echo "  ✅ Real-time system monitoring"
echo "  ✅ Comprehensive safety mechanisms"
echo "  ✅ Robust update handling with conflict resolution"
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
echo "Updates:"
echo "  Normal update: curl -s https://raw.githubusercontent.com/yaseenTarek26/Smart-Nix-OS/main/scripts/bootstrap.sh | sudo sh"
echo "  Force update:  curl -s https://raw.githubusercontent.com/yaseenTarek26/Smart-Nix-OS/main/scripts/bootstrap.sh | sudo sh -- --force"
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
