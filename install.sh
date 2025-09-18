#!/bin/bash
# NixOS AI Hyprland Installation Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root"
        exit 1
    fi
}

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check if NixOS
    if [[ ! -f /etc/nixos/configuration.nix ]]; then
        print_error "This script requires NixOS"
        exit 1
    fi
    
    # Check if nix is available
    if ! command -v nix &> /dev/null; then
        print_error "Nix is not installed or not in PATH"
        exit 1
    fi
    
    # Check if git is available
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed or not in PATH"
        exit 1
    fi
    
    # Check if curl is available
    if ! command -v curl &> /dev/null; then
        print_error "Curl is not installed or not in PATH"
        exit 1
    fi
    
    print_success "System requirements check passed"
}

# Function to get user input
get_user_input() {
    print_status "Getting user configuration..."
    
    # Get username
    read -p "Enter your username (default: $USER): " USERNAME
    USERNAME=${USERNAME:-$USER}
    
    # Get host type
    echo "Select host type:"
    echo "1) Desktop"
    echo "2) Laptop"
    read -p "Enter choice (1-2, default: 1): " HOST_CHOICE
    HOST_CHOICE=${HOST_CHOICE:-1}
    
    case $HOST_CHOICE in
        1) HOST="desktop" ;;
        2) HOST="laptop" ;;
        *) HOST="desktop" ;;
    esac
    
    # Get LLM provider
    echo "Select LLM provider:"
    echo "1) OpenAI (requires API key)"
    echo "2) Gemini (requires API key)"
    echo "3) Local (experimental)"
    read -p "Enter choice (1-3, default: 1): " LLM_CHOICE
    LLM_CHOICE=${LLM_CHOICE:-1}
    
    case $LLM_CHOICE in
        1) LLM_PROVIDER="openai" ;;
        2) LLM_PROVIDER="gemini" ;;
        3) LLM_PROVIDER="local" ;;
        *) LLM_PROVIDER="openai" ;;
    esac
    
    # Get API key if needed
    if [[ "$LLM_PROVIDER" != "local" ]]; then
        if [[ "$LLM_PROVIDER" == "gemini" ]]; then
            read -p "Enter your Gemini API key (or press Enter to use default): " API_KEY
            API_KEY=${API_KEY:-"AIzaSyBjj5weW0GXXecUIfN2GHfa0zX9A9MAvm0"}
        else
            read -p "Enter your $LLM_PROVIDER API key: " API_KEY
        fi
        
        if [[ -z "$API_KEY" ]]; then
            print_error "API key is required for $LLM_PROVIDER"
            exit 1
        fi
    else
        API_KEY=""
    fi
    
    print_success "User configuration completed"
}

# Function to create directories
create_directories() {
    print_status "Creating directories..."
    
    # Create necessary directories
    sudo mkdir -p /var/lib/nixos-agent
    sudo mkdir -p /var/log/nixos-agent
    sudo mkdir -p /etc/nixos-agent
    sudo mkdir -p /opt/nixos-agent
    
    # Set permissions
    sudo chown -R nixos-agent:nixos-agent /var/lib/nixos-agent
    sudo chown -R nixos-agent:nixos-agent /var/log/nixos-agent
    sudo chmod 755 /etc/nixos-agent
    sudo chmod 755 /opt/nixos-agent
    
    print_success "Directories created"
}

# Function to setup git repository
setup_git_repo() {
    print_status "Setting up git repository..."
    
    # Initialize git repo in /etc/nixos if not exists
    if [[ ! -d /etc/nixos/.git ]]; then
        sudo git init /etc/nixos
        sudo git -C /etc/nixos config user.name "NixOS AI Agent"
        sudo git -C /etc/nixos config user.email "ai-agent@nixos.local"
        sudo git -C /etc/nixos add .
        sudo git -C /etc/nixos commit -m "Initial NixOS configuration"
    fi
    
    print_success "Git repository setup completed"
}

# Function to create environment file
create_env_file() {
    print_status "Creating environment file..."
    
    cat > /tmp/nixos-agent.env << EOF
LLM_PROVIDER=$LLM_PROVIDER
OPENAI_API_KEY=$API_KEY
GEMINI_API_KEY=$API_KEY
AI_AGENT_PORT=8999
NIXOS_CONFIG_PATH=/etc/nixos
CACHE_DIR=/var/lib/nixos-agent/cache
LOG_DIR=/var/log/nixos-agent
EOF
    
    sudo mv /tmp/nixos-agent.env /etc/nixos-agent/.env
    sudo chown root:root /etc/nixos-agent/.env
    sudo chmod 600 /etc/nixos-agent/.env
    
    print_success "Environment file created"
}

# Function to build the system
build_system() {
    print_status "Building NixOS system with AI agent..."
    
    # Build the system
    sudo nixos-rebuild switch --flake .#$HOST
    
    if [[ $? -eq 0 ]]; then
        print_success "System built successfully"
    else
        print_error "System build failed"
        exit 1
    fi
}

# Function to start services
start_services() {
    print_status "Starting AI agent services..."
    
    # Enable and start the service
    sudo systemctl enable nixos-agent.service
    sudo systemctl start nixos-agent.service
    
    # Wait a moment for service to start
    sleep 3
    
    # Check if service is running
    if systemctl is-active --quiet nixos-agent.service; then
        print_success "AI agent service started successfully"
    else
        print_warning "AI agent service may not be running. Check with: systemctl status nixos-agent"
    fi
}

# Function to test the installation
test_installation() {
    print_status "Testing installation..."
    
    # Test web UI
    if curl -s http://127.0.0.1:8999 > /dev/null; then
        print_success "Web UI is accessible at http://127.0.0.1:8999"
    else
        print_warning "Web UI may not be accessible. Check service status."
    fi
    
    # Test AI agent commands
    if command -v ai-chat &> /dev/null; then
        print_success "AI chat command is available"
    else
        print_warning "AI chat command not found in PATH"
    fi
    
    if command -v ai-voice &> /dev/null; then
        print_success "AI voice command is available"
    else
        print_warning "AI voice command not found in PATH"
    fi
}

# Function to show final instructions
show_final_instructions() {
    print_success "Installation completed!"
    echo
    echo "🎉 NixOS AI Hyprland is now installed and ready to use!"
    echo
    echo "📋 Quick Start:"
    echo "  • Press Super+Space to open AI chat"
    echo "  • Press Super+Shift+Space for voice interaction"
    echo "  • Or open http://127.0.0.1:8999 in your browser"
    echo
    echo "🔧 Useful Commands:"
    echo "  • ai-chat          - Open AI chat interface"
    echo "  • ai-voice         - Start voice interaction"
    echo "  • ai-status        - Check AI agent status"
    echo "  • ai-logs          - View AI agent logs"
    echo
    echo "📚 Examples:"
    echo "  • 'Install Firefox' - Install packages"
    echo "  • 'Open Chrome'     - Launch applications"
    echo "  • 'Change wallpaper' - Configure system"
    echo
    echo "🆘 Troubleshooting:"
    echo "  • Check service: systemctl status nixos-agent"
    echo "  • View logs: journalctl -u nixos-agent -f"
    echo "  • Restart service: sudo systemctl restart nixos-agent"
    echo
    echo "Enjoy your AI-powered NixOS desktop! 🚀"
}

# Main installation function
main() {
    echo "🤖 NixOS AI Hyprland Installation Script"
    echo "========================================"
    echo
    
    check_root
    check_requirements
    get_user_input
    create_directories
    setup_git_repo
    create_env_file
    build_system
    start_services
    test_installation
    show_final_instructions
}

# Run main function
main "$@"
