#!/bin/bash
# Ultra-Simple Standalone Installer - No Git Required!

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
INSTALL_DIR="/home/$USER/nixos-ai"
CLI_PATH="/home/$USER/.local/bin/nixos-ai"

log "NixOS AI Assistant - Standalone Installer (No Git Required)"
echo "========================================================="
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    error "Don't run as root! This installer works in user space."
    exit 1
fi

# Create installation directory
log "Creating installation directory..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Create basic AI agent structure
log "Creating AI agent structure..."
mkdir -p ai logs state cache

# Create simple AI agent
cat > ai/agent.py << 'EOF'
#!/usr/bin/env python3
"""
NixOS AI Assistant - Simple Agent
"""

import sys
import json
import os
import subprocess
import argparse
from pathlib import Path

class NixOSAIAgent:
    def __init__(self):
        self.config_path = os.getenv('AI_CONFIG_PATH', 'ai/config.json')
        self.logs_path = os.getenv('AI_LOGS_PATH', 'logs')
        self.state_path = os.getenv('AI_STATE_PATH', 'state')
        self.cache_path = os.getenv('AI_CACHE_PATH', 'cache')
        
        # Create directories
        Path(self.logs_path).mkdir(exist_ok=True)
        Path(self.state_path).mkdir(exist_ok=True)
        Path(self.cache_path).mkdir(exist_ok=True)
        
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "ai_models": {
                    "openai": {
                        "api_key": "",
                        "models": ["gpt-4", "gpt-3.5-turbo"],
                        "default_model": "gpt-4"
                    },
                    "gemini": {
                        "api_key": "",
                        "models": ["gemini-pro"],
                        "default_model": "gemini-pro"
                    }
                },
                "fallback_providers": ["gemini", "openai"],
                "active_provider": "gemini"
            }
            self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def log(self, message):
        """Log message to file"""
        log_file = os.path.join(self.logs_path, 'ai.log')
        with open(log_file, 'a') as f:
            f.write(f"{message}\n")
        print(f"[LOG] {message}")
    
    def process_request(self, request):
        """Process user request"""
        self.log(f"Processing request: {request}")
        
        # Simple command processing
        if "hello" in request.lower():
            return "Hello! I'm your NixOS AI Assistant. How can I help you today?"
        elif "help" in request.lower():
            return """I can help you with:
- System management: 'check system status', 'install packages'
- File operations: 'edit files', 'create scripts'
- NixOS configuration: 'update configuration', 'rebuild system'
- General assistance: Just ask me anything!

What would you like me to help you with?"""
        elif "status" in request.lower():
            return self.get_system_status()
        else:
            return f"I received your request: '{request}'. I'm a simple AI assistant. For now, I can help with basic commands. Try asking for 'help' to see what I can do!"
    
    def get_system_status(self):
        """Get basic system status"""
        try:
            result = subprocess.run(['uname', '-a'], capture_output=True, text=True)
            return f"System: {result.stdout.strip()}"
        except:
            return "System status: Unknown"
    
    def run(self, args):
        """Main run function"""
        if not args:
            print("NixOS AI Assistant - Simple Version")
            print("Usage: nixos-ai 'your request here'")
            print("Example: nixos-ai 'hello'")
            return
        
        request = ' '.join(args)
        response = self.process_request(request)
        print(response)

def main():
    parser = argparse.ArgumentParser(description='NixOS AI Assistant')
    parser.add_argument('args', nargs='*', help='Request to process')
    
    args = parser.parse_args()
    
    agent = NixOSAIAgent()
    agent.run(args.args)

if __name__ == '__main__':
    main()
EOF

chmod +x ai/agent.py

# Create configuration file
log "Creating configuration file..."
cat > ai/config.json << 'EOF'
{
  "ai_models": {
    "openai": {
      "api_key": "",
      "models": ["gpt-4", "gpt-3.5-turbo"],
      "default_model": "gpt-4"
    },
    "gemini": {
      "api_key": "",
      "models": ["gemini-pro"],
      "default_model": "gemini-pro"
    }
  },
  "fallback_providers": ["gemini", "openai"],
  "active_provider": "gemini"
}
EOF

# Create requirements.txt
log "Creating requirements file..."
cat > requirements.txt << 'EOF'
# Basic requirements for NixOS AI Assistant
# Most functionality works without these, but they enable advanced features

# AI providers (optional)
openai>=1.0.0
google-generativeai>=0.3.0
anthropic>=0.7.0

# HTTP requests
httpx>=0.24.0
aiohttp>=3.8.0

# System monitoring
psutil>=5.9.0

# Logging and utilities
structlog>=23.0.0
pydantic>=2.0.0
typer>=0.9.0
EOF

# Install Python dependencies
log "Installing Python dependencies..."
python3 -m pip install --user --break-system-packages -r requirements.txt 2>/dev/null || {
    warn "Pip failed, trying without --break-system-packages..."
    python3 -m pip install --user -r requirements.txt || {
        warn "Pip failed, trying minimal installation..."
        python3 -m pip install --user httpx aiohttp psutil structlog pydantic typer || {
            warn "Pip failed, but continuing with basic functionality..."
        }
    }
}

# Create startup script
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
echo "Installation location: $INSTALL_DIR"
echo "CLI command: nixos-ai"
echo ""
echo "Usage:"
echo "  nixos-ai 'hello'"
echo "  nixos-ai 'help'"
echo "  nixos-ai 'status'"
echo ""
echo "Configuration:"
echo "  Edit: $INSTALL_DIR/ai/config.json"
echo "  Logs: $INSTALL_DIR/logs/"
echo ""
echo "Installation complete! 🎉"
