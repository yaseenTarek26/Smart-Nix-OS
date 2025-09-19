#!/bin/bash

# NixOS AI Assistant - Test Script
# Tests the installation and basic functionality

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Configuration
AI_DIR="/etc/nixos/nixos-ai"

log "Testing NixOS AI Assistant installation..."

# Check if AI directory exists
if [[ ! -d "$AI_DIR" ]]; then
    error "AI directory not found: $AI_DIR"
fi

# Check if Python files exist
required_files=(
    "$AI_DIR/ai/agent.py"
    "$AI_DIR/ai/editor.py"
    "$AI_DIR/ai/executor.py"
    "$AI_DIR/ai/watcher.py"
    "$AI_DIR/ai/config.py"
    "$AI_DIR/ai/config.json"
)

for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        error "Required file not found: $file"
    fi
done

success "All required files present"

# Check if scripts are executable
scripts=(
    "$AI_DIR/scripts/bootstrap.sh"
    "$AI_DIR/scripts/apply.sh"
    "$AI_DIR/scripts/rollback.sh"
)

for script in "${scripts[@]}"; do
    if [[ ! -x "$script" ]]; then
        warn "Script not executable: $script"
        chmod +x "$script"
    fi
done

success "All scripts are executable"

# Test Python imports
log "Testing Python imports..."
cd "$AI_DIR"

if python3 -c "
import sys
sys.path.insert(0, 'ai')
try:
    from config import AIConfig
    from editor import FileEditor
    from executor import CommandExecutor
    from watcher import LogWatcher
    print('All imports successful')
except ImportError as e:
    print(f'Import error: {e}')
    sys.exit(1)
"; then
    success "Python imports working"
else
    error "Python import test failed"
fi

# Test configuration loading
log "Testing configuration loading..."
if python3 -c "
import sys
sys.path.insert(0, 'ai')
from config import AIConfig
config = AIConfig()
print(f'Config loaded: {config.model}')
"; then
    success "Configuration loading working"
else
    error "Configuration loading test failed"
fi

# Test basic AI agent functionality
log "Testing AI agent basic functionality..."
if python3 -c "
import sys
sys.path.insert(0, 'ai')
from agent import NixOSAIAgent
agent = NixOSAIAgent()
print('AI agent initialized successfully')
"; then
    success "AI agent initialization working"
else
    error "AI agent initialization test failed"
fi

# Check if service is enabled (if running on NixOS)
if command -v systemctl >/dev/null 2>&1; then
    if systemctl is-enabled nixos-ai.service >/dev/null 2>&1; then
        success "AI service is enabled"
    else
        warn "AI service is not enabled (run: systemctl enable nixos-ai.service)"
    fi
    
    if systemctl is-active nixos-ai.service >/dev/null 2>&1; then
        success "AI service is running"
    else
        warn "AI service is not running (run: systemctl start nixos-ai.service)"
    fi
fi

# Test command line interface
log "Testing command line interface..."
if command -v nixos-ai >/dev/null 2>&1; then
    success "Command line interface available"
else
    warn "Command line interface not found (check installation)"
fi

# Test NixOS configuration
log "Testing NixOS configuration..."
if command -v nixos-rebuild >/dev/null 2>&1; then
    if nixos-rebuild test --flake "$AI_DIR" >/dev/null 2>&1; then
        success "NixOS configuration test passed"
    else
        warn "NixOS configuration test failed (check configuration)"
    fi
else
    warn "nixos-rebuild not available (not running on NixOS?)"
fi

echo ""
success "All tests completed!"
echo ""
echo "Next steps:"
echo "1. Set your OpenAI API key in $AI_DIR/ai/config.json (optional)"
echo "2. Enable the service: systemctl enable nixos-ai.service"
echo "3. Start the service: systemctl start nixos-ai.service"
echo "4. Test with: nixos-ai 'hello world'"
echo ""
echo "For more information, see: $AI_DIR/README.md"
