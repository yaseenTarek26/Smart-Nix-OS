#!/bin/bash

# NixOS AI Assistant - Apply Changes Script
# Safely applies changes made by the AI assistant

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AI_DIR="/etc/nixos/nixos-ai"
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
   error "This script must be run as root (use sudo)"
fi

log "Starting NixOS AI Assistant apply process..."

# Create backup
log "Creating backup of current configuration..."
mkdir -p "$BACKUP_DIR"
cp "$CONFIG_FILE" "$BACKUP_DIR/"
if [[ -d "$AI_DIR" ]]; then
    cp -r "$AI_DIR" "$BACKUP_DIR/nixos-ai"
fi
success "Backup created at $BACKUP_DIR"

# Change to AI directory
cd "$AI_DIR" || error "Could not change to AI directory: $AI_DIR"

# Test NixOS configuration
log "Testing NixOS configuration..."
if nixos-rebuild test --flake .; then
    success "NixOS configuration test passed"
else
    error "NixOS configuration test failed. Changes not applied."
fi

# Apply configuration
log "Applying NixOS configuration..."
if nixos-rebuild switch --flake .; then
    success "NixOS configuration applied successfully"
else
    error "Failed to apply NixOS configuration. Rolling back..."
    nixos-rebuild switch --rollback
    exit 1
fi

# Restart AI service if it exists
if systemctl is-active --quiet nixos-ai.service; then
    log "Restarting AI service..."
    systemctl restart nixos-ai.service
    success "AI service restarted"
fi

# Clean up old backups (keep last 10)
log "Cleaning up old backups..."
find /etc/nixos -name "backup-*" -type d | sort -r | tail -n +11 | xargs -r rm -rf

success "Apply process completed successfully!"
echo ""
echo "Configuration applied and system updated."
echo "Backup location: $BACKUP_DIR"
echo ""
echo "To rollback if needed:"
echo "  $AI_DIR/scripts/rollback.sh"
