#!/bin/bash
# Ultra-Simple NixOS AI Assistant Bootstrap
# Downloads and runs the simple installer

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

log "NixOS AI Assistant - Ultra-Simple Installer"
echo "=========================================="
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    error "Don't run as root! This installer works in user space."
    echo "Please run as a regular user:"
    echo "  curl -s https://raw.githubusercontent.com/yaseenTarek26/Smart-Nix-OS/main/scripts/bootstrap.sh | sh"
    exit 1
fi

# Download and run the standalone installer
log "Downloading standalone installer..."
curl -s https://raw.githubusercontent.com/yaseenTarek26/Smart-Nix-OS/main/scripts/standalone_install.sh -o /tmp/install-ai.sh

if [[ -f "/tmp/install-ai.sh" ]]; then
    log "Running installer..."
    chmod +x /tmp/install-ai.sh
    bash /tmp/install-ai.sh
    rm /tmp/install-ai.sh
else
    error "Failed to download installer"
    exit 1
fi