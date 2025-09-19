#!/bin/bash

# NixOS AI Assistant - Demo Script
# Demonstrates the AI assistant capabilities

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

demo() {
    echo -e "${PURPLE}[DEMO]${NC} $1"
}

# Configuration
AI_DIR="/etc/nixos/nixos-ai"

echo -e "${PURPLE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                NixOS AI Assistant Demo                      ║"
echo "║                                                              ║"
echo "║  This demo shows the AI assistant in action                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if AI assistant is installed
if [[ ! -d "$AI_DIR" ]]; then
    error "AI assistant not installed. Please run the installation first."
    exit 1
fi

# Check if service is running
if ! systemctl is-active nixos-ai.service >/dev/null 2>&1; then
    warn "AI service is not running. Starting it..."
    systemctl start nixos-ai.service
    sleep 2
fi

echo ""
demo "Let's test the AI assistant with some example commands..."
echo ""

# Demo 1: Basic greeting
echo "Demo 1: Basic AI interaction"
echo "Command: nixos-ai 'hello, can you help me?'"
echo "---"
nixos-ai "hello, can you help me?" || warn "Command failed (this is expected in demo mode)"
echo "---"
echo ""

# Demo 2: System status check
echo "Demo 2: System status check"
echo "Command: nixos-ai 'check system status and show memory usage'"
echo "---"
nixos-ai "check system status and show memory usage" || warn "Command failed (this is expected in demo mode)"
echo "---"
echo ""

# Demo 3: Package installation simulation
echo "Demo 3: Package installation simulation"
echo "Command: nixos-ai 'install vscode and git'"
echo "---"
nixos-ai "install vscode and git" || warn "Command failed (this is expected in demo mode)"
echo "---"
echo ""

# Demo 4: Service management
echo "Demo 4: Service management"
echo "Command: nixos-ai 'enable docker service'"
echo "---"
nixos-ai "enable docker service" || warn "Command failed (this is expected in demo mode)"
echo "---"
echo ""

# Demo 5: Configuration editing
echo "Demo 5: Configuration editing"
echo "Command: nixos-ai 'add vscode to system packages'"
echo "---"
nixos-ai "add vscode to system packages" || warn "Command failed (this is expected in demo mode)"
echo "---"
echo ""

# Show AI logs
echo "Demo 6: Viewing AI logs"
echo "Command: tail -n 20 /etc/nixos/nixos-ai/logs/ai.log"
echo "---"
if [[ -f "$AI_DIR/logs/ai.log" ]]; then
    tail -n 20 "$AI_DIR/logs/ai.log" || warn "No logs available yet"
else
    warn "Log file not found"
fi
echo "---"
echo ""

# Show system status
echo "Demo 7: System service status"
echo "Command: systemctl status nixos-ai.service"
echo "---"
systemctl status nixos-ai.service --no-pager || warn "Service status check failed"
echo "---"
echo ""

# Show available commands
echo "Demo 8: Available commands"
echo "---"
echo "Available commands:"
echo "  nixos-ai 'your command here'     - Process a single command"
echo "  nixos-ai                         - Interactive mode"
echo "  nixos-ai --daemon                - Run as daemon"
echo ""
echo "Example commands:"
echo "  nixos-ai 'install docker'"
echo "  nixos-ai 'enable vscode'"
echo "  nixos-ai 'check system status'"
echo "  nixos-ai 'show recent logs'"
echo "---"
echo ""

# Show safety features
echo "Demo 9: Safety features"
echo "---"
echo "Safety features available:"
echo "  - Git snapshots of all changes"
echo "  - Configuration validation before applying"
echo "  - Automatic rollback on failures"
echo "  - Command safety checks"
echo "  - Path restrictions (configurable)"
echo ""
echo "Safety commands:"
echo "  $AI_DIR/scripts/rollback.sh      - Emergency rollback"
echo "  $AI_DIR/scripts/apply.sh         - Safe apply changes"
echo "  $AI_DIR/scripts/test.sh          - Test installation"
echo "---"
echo ""

success "Demo completed!"
echo ""
echo "The AI assistant is now running and ready to help you manage your NixOS system."
echo "Try some commands or check the logs to see it in action!"
echo ""
echo "For more information:"
echo "  - README: $AI_DIR/README.md"
echo "  - Installation guide: $AI_DIR/INSTALL.md"
echo "  - Logs: journalctl -u nixos-ai.service -f"
