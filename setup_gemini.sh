#!/bin/bash
# Setup script for Gemini API key

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to setup Gemini API key
setup_gemini() {
    print_status "Setting up Gemini API key..."
    
    # Create environment file
    cat > /tmp/nixos-agent-gemini.env << EOF
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyBjj5weW0GXXecUIfN2GHfa0zX9A9MAvm0
AI_AGENT_PORT=8999
NIXOS_CONFIG_PATH=/etc/nixos
CACHE_DIR=/var/lib/nixos-agent/cache
LOG_DIR=/var/log/nixos-agent
EOF
    
    # Move to proper location
    sudo mkdir -p /etc/nixos-agent
    sudo mv /tmp/nixos-agent-gemini.env /etc/nixos-agent/.env
    sudo chown root:root /etc/nixos-agent/.env
    sudo chmod 600 /etc/nixos-agent/.env
    
    print_success "Gemini API key configured"
    print_status "Environment file created at /etc/nixos-agent/.env"
}

# Function to test Gemini integration
test_gemini() {
    print_status "Testing Gemini integration..."
    
    if python3 test_gemini.py; then
        print_success "Gemini integration test passed"
    else
        print_error "Gemini integration test failed"
        print_warning "Make sure you have internet connection and the API key is valid"
    fi
}

# Function to show usage instructions
show_usage() {
    print_success "Gemini API key setup completed!"
    echo
    echo "📋 Next steps:"
    echo "1. Run the installation: ./install.sh"
    echo "2. Choose 'Gemini' as your LLM provider when prompted"
    echo "3. Press Enter to use the default API key"
    echo "4. Reboot your system"
    echo
    echo "🔧 Manual configuration:"
    echo "• Edit /etc/nixos-agent/.env to change settings"
    echo "• Restart service: sudo systemctl restart nixos-agent"
    echo "• Check logs: journalctl -u nixos-agent -f"
    echo
    echo "🎯 Usage:"
    echo "• Web UI: http://127.0.0.1:8999"
    echo "• Hotkey: Super+Space (chat), Super+Shift+Space (voice)"
    echo "• Commands: ai-chat, ai-voice"
}

# Main function
main() {
    echo "🤖 NixOS AI Hyprland - Gemini Setup"
    echo "===================================="
    echo
    
    setup_gemini
    echo
    test_gemini
    echo
    show_usage
}

# Run main function
main "$@"
