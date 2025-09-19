#!/bin/bash

# NixOS AI Assistant - Rollback Script
# Emergency rollback to previous working state

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

log "Starting NixOS AI Assistant rollback process..."

# Function to list available backups
list_backups() {
    echo "Available backups:"
    find /etc/nixos -name "backup-*" -type d | sort -r | nl
}

# Function to rollback to specific backup
rollback_to_backup() {
    local backup_dir="$1"
    
    if [[ ! -d "$backup_dir" ]]; then
        error "Backup directory does not exist: $backup_dir"
    fi
    
    log "Rolling back to backup: $backup_dir"
    
    # Restore configuration.nix
    if [[ -f "$backup_dir/configuration.nix" ]]; then
        cp "$backup_dir/configuration.nix" "$CONFIG_FILE"
        success "Restored configuration.nix"
    else
        warn "No configuration.nix found in backup"
    fi
    
    # Restore AI directory if it exists
    if [[ -d "$backup_dir/nixos-ai" ]]; then
        rm -rf "$AI_DIR"
        cp -r "$backup_dir/nixos-ai" "$AI_DIR"
        success "Restored AI directory"
    fi
    
    # Test configuration
    log "Testing restored configuration..."
    if nixos-rebuild test; then
        success "Configuration test passed"
    else
        error "Configuration test failed. Manual intervention required."
    fi
    
    # Apply configuration
    log "Applying restored configuration..."
    if nixos-rebuild switch; then
        success "Configuration applied successfully"
    else
        error "Failed to apply configuration. System may be in inconsistent state."
    fi
}

# Function to rollback using NixOS generations
rollback_generation() {
    log "Rolling back using NixOS generations..."
    
    # List available generations
    echo "Available NixOS generations:"
    nix-env --list-generations --profile /nix/var/nix/profiles/system | tail -10
    
    # Get the previous generation
    local prev_gen=$(nix-env --list-generations --profile /nix/var/nix/profiles/system | tail -2 | head -1 | awk '{print $1}')
    
    if [[ -z "$prev_gen" ]]; then
        error "No previous generation found"
    fi
    
    log "Rolling back to generation: $prev_gen"
    
    # Switch to previous generation
    nix-env --switch-generation "$prev_gen" --profile /nix/var/nix/profiles/system
    
    # Rebuild
    nixos-rebuild switch
    
    success "Rolled back to generation $prev_gen"
}

# Main rollback logic
if [[ $# -eq 0 ]]; then
    # Interactive mode
    echo "NixOS AI Assistant Rollback"
    echo "=========================="
    echo ""
    echo "Choose rollback method:"
    echo "1) Rollback to specific backup"
    echo "2) Rollback using NixOS generations"
    echo "3) List available backups"
    echo "4) Exit"
    echo ""
    read -p "Enter choice (1-4): " choice
    
    case $choice in
        1)
            list_backups
            echo ""
            read -p "Enter backup number: " backup_num
            backup_dir=$(find /etc/nixos -name "backup-*" -type d | sort -r | sed -n "${backup_num}p")
            if [[ -n "$backup_dir" ]]; then
                rollback_to_backup "$backup_dir"
            else
                error "Invalid backup number"
            fi
            ;;
        2)
            rollback_generation
            ;;
        3)
            list_backups
            exit 0
            ;;
        4)
            echo "Exiting..."
            exit 0
            ;;
        *)
            error "Invalid choice"
            ;;
    esac
else
    # Command line mode
    case "$1" in
        --backup)
            if [[ -z "${2:-}" ]]; then
                error "Backup directory required"
            fi
            rollback_to_backup "$2"
            ;;
        --generation)
            rollback_generation
            ;;
        --list)
            list_backups
            exit 0
            ;;
        *)
            echo "Usage: $0 [--backup <dir>] [--generation] [--list]"
            echo ""
            echo "Options:"
            echo "  --backup <dir>    Rollback to specific backup directory"
            echo "  --generation      Rollback using NixOS generations"
            echo "  --list            List available backups"
            exit 1
            ;;
    esac
fi

success "Rollback completed successfully!"
echo ""
echo "System has been restored to a previous working state."
echo "You may need to restart services or reboot if necessary."
