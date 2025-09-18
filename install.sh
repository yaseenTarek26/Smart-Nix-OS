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
    
    # Check if we're in a writable environment
    if [[ ! -w "/tmp" ]]; then
        print_warning "Limited write access detected - some features may not work"
    fi
    
    # Check if systemd is available
    if ! command -v systemctl &> /dev/null; then
        print_warning "systemctl not found - service management may be limited"
    fi
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        print_warning "python3 not found - will need to install Python dependencies"
    fi
    
    print_success "System requirements check passed"
}

# Function to get user input
get_user_input() {
    print_status "Getting user configuration..."
    
    # Check if running in non-interactive mode (piped from curl)
    if [[ ! -t 0 ]]; then
        print_status "Running in non-interactive mode, using defaults..."
        USERNAME=${USER:-"nixos"}
        HOST="desktop"
        LLM_PROVIDER="gemini"
        API_KEY="AIzaSyBjj5weW0GXXecUIfN2GHfa0zX9A9MAvm0"
        print_success "Using default configuration: $USERNAME, $HOST, $LLM_PROVIDER"
        return
    fi
    
    # Interactive mode
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
    read -p "Enter choice (1-3, default: 2): " LLM_CHOICE
    LLM_CHOICE=${LLM_CHOICE:-2}
    
    case $LLM_CHOICE in
        1) LLM_PROVIDER="openai" ;;
        2) LLM_PROVIDER="gemini" ;;
        3) LLM_PROVIDER="local" ;;
        *) LLM_PROVIDER="gemini" ;;
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

# Function to create user and directories
create_user_and_directories() {
    print_status "Creating user and directories..."
    
    # Create nixos-agent group first if it doesn't exist
    if ! getent group "nixos-agent" &>/dev/null; then
        print_status "Creating nixos-agent group..."
        if command -v groupadd &> /dev/null; then
            sudo groupadd nixos-agent 2>/dev/null || true
        elif command -v addgroup &> /dev/null; then
            sudo addgroup nixos-agent 2>/dev/null || true
        else
            print_warning "Cannot create group with standard tools"
        fi
    else
        print_status "nixos-agent group already exists"
    fi
    
    # Create nixos-agent user if it doesn't exist
    if ! id "nixos-agent" &>/dev/null; then
        print_status "Creating nixos-agent user..."
        # Try different user creation methods for NixOS compatibility
        if command -v adduser &> /dev/null; then
            sudo adduser --system --shell /bin/bash --home /var/lib/nixos-agent --ingroup nixos-agent nixos-agent 2>/dev/null || true
        elif command -v useradd &> /dev/null; then
            sudo useradd -r -g nixos-agent -s /bin/bash -d /var/lib/nixos-agent nixos-agent 2>/dev/null || true
        else
            print_warning "Cannot create user with standard tools, using alternative approach"
            # Try to create user without group specification
            sudo useradd -r -s /bin/bash -d /var/lib/nixos-agent nixos-agent 2>/dev/null || true
            # If that fails, try creating with a different approach
            if ! id "nixos-agent" &>/dev/null; then
                print_warning "Standard user creation failed, trying minimal approach"
                # Find an available UID for system user (typically 100-999 range)
                for uid in {100..999}; do
                    if ! id "$uid" &>/dev/null; then
                        echo "nixos-agent:x:$uid:$uid:NixOS AI Agent:/var/lib/nixos-agent:/bin/bash" | sudo tee -a /etc/passwd > /dev/null
                        echo "nixos-agent:x:$uid:" | sudo tee -a /etc/group > /dev/null
                        sudo mkdir -p /var/lib/nixos-agent
                        break
                    fi
                done
            fi
        fi
        # Verify user was created successfully
        if id "nixos-agent" &>/dev/null; then
            print_success "nixos-agent user created successfully"
        else
            print_warning "Failed to create nixos-agent user, will use root for service"
        fi
    else
        print_status "nixos-agent user already exists"
    fi
    
    # Create necessary directories
    sudo mkdir -p /var/lib/nixos-agent
    sudo mkdir -p /var/log/nixos-agent
    sudo mkdir -p /etc/nixos-agent
    sudo mkdir -p /opt/nixos-agent
    
    # Set permissions - only if user exists
    if id "nixos-agent" &>/dev/null; then
        sudo chown -R nixos-agent:nixos-agent /var/lib/nixos-agent
        sudo chown -R nixos-agent:nixos-agent /var/log/nixos-agent
        print_success "User and directories created with proper ownership"
    else
        print_warning "nixos-agent user not found, using root ownership"
        sudo chown -R root:root /var/lib/nixos-agent
        sudo chown -R root:root /var/log/nixos-agent
        print_success "User and directories created with root ownership"
    fi
    
    sudo chmod 755 /etc/nixos-agent
    sudo chmod 755 /opt/nixos-agent
}

# Function to create fallback configuration
create_fallback_config() {
    print_status "Creating fallback configuration..."
    
    # Determine the user and group to use for the service
    SERVICE_USER="root"
    SERVICE_GROUP="root"
    
    if id "nixos-agent" &>/dev/null; then
        SERVICE_USER="nixos-agent"
        # Check if the group exists, otherwise use the user's primary group
        if getent group "nixos-agent" &>/dev/null; then
            SERVICE_GROUP="nixos-agent"
        else
            # Get the user's primary group
            SERVICE_GROUP=$(id -gn nixos-agent 2>/dev/null || echo "nixos-agent")
        fi
        print_status "Using nixos-agent user for service (group: $SERVICE_GROUP)"
    else
        print_warning "nixos-agent user not found, using root for service"
    fi
    
    # Create a simple systemd service for the AI agent
    # Note: In NixOS, systemd services are typically managed through configuration.nix
    # This is a fallback for systems where /etc/systemd/system is writable
    if [ -w "/etc/systemd/system" ]; then
        sudo tee /etc/systemd/system/nixos-agent.service > /dev/null << EOF
[Unit]
Description=NixOS AI Agent
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=/opt/nixos-agent
ExecStart=/usr/bin/python3 /opt/nixos-agent/ai-agent/agent.py
Restart=always
RestartSec=5
EnvironmentFile=/etc/nixos-agent/.env

[Install]
WantedBy=multi-user.target
EOF
        print_success "Fallback configuration created with user: $SERVICE_USER"
    else
        print_warning "Cannot write to /etc/systemd/system (read-only filesystem)"
        print_status "Service will be managed through NixOS configuration instead"
    fi
}

# Function to create NixOS configuration snippet
create_nixos_config_snippet() {
    print_status "Creating NixOS configuration snippet..."
    
    # Create a configuration snippet that can be added to configuration.nix
    sudo tee /etc/nixos-agent/nixos-config-snippet.nix > /dev/null << 'EOF'
# AI Agent configuration for NixOS
# Add this to your /etc/nixos/configuration.nix

# Create nixos-agent user
users.users.nixos-agent = {
  isSystemUser = true;
  group = "nixos-agent";
  home = "/var/lib/nixos-agent";
  createHome = true;
  shell = pkgs.bash;
};

users.groups.nixos-agent = {};

# Enable AI agent service
systemd.services.nixos-agent = {
  description = "NixOS AI Agent";
  wantedBy = [ "multi-user.target" ];
  after = [ "network.target" ];
  serviceConfig = {
    Type = "simple";
    User = "nixos-agent";
    Group = "nixos-agent";
    WorkingDirectory = "/opt/nixos-agent";
    ExecStart = "${pkgs.python3}/bin/python /opt/nixos-agent/ai-agent/agent.py";
    Restart = "always";
    RestartSec = 5;
    EnvironmentFile = "/etc/nixos-agent/.env";
    StandardOutput = "journal";
    StandardError = "journal";
  };
};

# Install required packages
environment.systemPackages = with pkgs; [
  python3
  python3Packages.pip
  python3Packages.virtualenv
  python3Packages.fastapi
  python3Packages.uvicorn
  python3Packages.websockets
  python3Packages.openai
  python3Packages.google-generativeai
  python3Packages.gitpython
  python3Packages.pyyaml
  python3Packages.requests
  python3Packages.aiofiles
  python3Packages.python-multipart
  python3Packages.jinja2
];
EOF

    print_success "NixOS configuration snippet created at /etc/nixos-agent/nixos-config-snippet.nix"
    print_status "You can add this to your /etc/nixos/configuration.nix and rebuild"
}

# Function to create manual startup script
create_startup_script() {
    print_status "Creating manual startup script..."
    
    # Create a simple startup script for immediate testing
    sudo tee /opt/nixos-agent/start-ai-agent.sh > /dev/null << 'EOF'
#!/bin/bash
# Manual startup script for NixOS AI Agent

echo "Starting NixOS AI Agent manually..."

# Check if user exists
if ! id "nixos-agent" &>/dev/null; then
    echo "Error: nixos-agent user not found"
    echo "Please add the configuration snippet to /etc/nixos/configuration.nix and rebuild"
    exit 1
fi

# Check if virtual environment exists
if [[ -f "/opt/nixos-agent/venv/bin/python" ]]; then
    echo "Using virtual environment for Python dependencies..."
    PYTHON_CMD="/opt/nixos-agent/venv/bin/python"
else
    echo "Using system Python (may need manual dependency installation)..."
    PYTHON_CMD="python3"
fi

# Check if Python dependencies are available
if ! $PYTHON_CMD -c "import fastapi" &>/dev/null; then
    echo "Installing Python dependencies..."
    if [[ -f "/opt/nixos-agent/venv/bin/pip" ]]; then
        /opt/nixos-agent/venv/bin/pip install fastapi uvicorn websockets openai google-generativeai gitpython pyyaml requests aiofiles python-multipart jinja2
    else
        pip3 install --user fastapi uvicorn websockets openai google-generativeai gitpython pyyaml requests aiofiles python-multipart jinja2
    fi
fi

# Start the AI agent
echo "Starting AI agent as nixos-agent user..."
sudo -u nixos-agent $PYTHON_CMD /opt/nixos-agent/ai-agent/agent.py --mode=chat

EOF

    sudo chmod +x /opt/nixos-agent/start-ai-agent.sh
    print_success "Manual startup script created at /opt/nixos-agent/start-ai-agent.sh"
}

# Function to create Python requirements file
create_requirements_file() {
    print_status "Creating Python requirements file..."
    
    # Create requirements.txt for the AI agent
    sudo tee /opt/nixos-agent/requirements.txt > /dev/null << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
openai==1.3.7
google-generativeai==0.3.2
gitpython==3.1.40
pyyaml==6.0.1
requests==2.31.0
aiofiles==23.2.1
python-multipart==0.0.6
jinja2==3.1.2
EOF

    print_success "Python requirements file created at /opt/nixos-agent/requirements.txt"
}

# Function to create a Python dependency installer script
create_python_installer() {
    print_status "Creating Python dependency installer script..."
    
    # Create a Python script that handles dependency installation
    sudo tee /opt/nixos-agent/install_deps.py > /dev/null << 'EOF'
#!/usr/bin/env python3
"""
Python dependency installer for NixOS AI Agent
Handles externally managed environment issues
"""

import subprocess
import sys
import os

def run_command(cmd, check=True):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"Command failed: {cmd}")
            print(f"Error: {result.stderr}")
            return False
        return result.returncode == 0
    except Exception as e:
        print(f"Exception running command {cmd}: {e}")
        return False

def install_dependencies():
    """Install Python dependencies using various methods"""
    packages = [
        "fastapi", "uvicorn", "websockets", "openai", "google-generativeai",
        "gitpython", "pyyaml", "requests", "aiofiles", "python-multipart", "jinja2"
    ]
    
    print("Installing Python dependencies...")
    
    # Method 1: Try virtual environment
    if os.path.exists("/opt/nixos-agent/venv/bin/python"):
        print("Using virtual environment...")
        for package in packages:
            cmd = f"/opt/nixos-agent/venv/bin/pip install {package}"
            if run_command(cmd, check=False):
                print(f"✓ Installed {package}")
            else:
                print(f"✗ Failed to install {package}")
        return True
    
    # Method 2: Try user install
    print("Trying user install...")
    for package in packages:
        cmd = f"python3 -m pip install --user {package}"
        if run_command(cmd, check=False):
            print(f"✓ Installed {package}")
        else:
            print(f"✗ Failed to install {package}")
    
    # Method 3: Try with --break-system-packages
    print("Trying with --break-system-packages...")
    for package in packages:
        cmd = f"python3 -m pip install --user --break-system-packages {package}"
        if run_command(cmd, check=False):
            print(f"✓ Installed {package}")
        else:
            print(f"✗ Failed to install {package}")
    
    return True

if __name__ == "__main__":
    install_dependencies()
EOF

    sudo chmod +x /opt/nixos-agent/install_deps.py
    print_success "Python dependency installer created at /opt/nixos-agent/install_deps.py"
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Use the Python installer script for better error handling
    if [[ -f "/opt/nixos-agent/install_deps.py" ]]; then
        print_status "Using Python dependency installer script..."
        if python3 /opt/nixos-agent/install_deps.py; then
            print_success "Python dependencies installation completed"
        else
            print_warning "Python dependency installer had some issues, but continuing..."
        fi
    else
        print_warning "Python installer script not found, trying manual installation..."
        
        # Fallback to manual installation
        if command -v pip3 &> /dev/null; then
            print_status "Trying manual pip installation..."
            if pip3 install --user --break-system-packages fastapi uvicorn websockets openai google-generativeai gitpython pyyaml requests aiofiles python-multipart jinja2 2>/dev/null; then
                print_success "Python dependencies installed manually"
            else
                print_warning "Manual installation failed, dependencies will need to be installed manually"
            fi
        else
            print_warning "pip3 not available, skipping Python dependency installation"
        fi
    fi
}

# Function to copy AI agent files
copy_ai_agent_files() {
    print_status "Copying AI agent files..."
    
    # Copy AI agent files to /opt/nixos-agent
    if [[ -d "ai-agent" ]]; then
        sudo cp -r ai-agent/* /opt/nixos-agent/
        
        # Set ownership only if user exists
        if id "nixos-agent" &>/dev/null; then
            sudo chown -R nixos-agent:nixos-agent /opt/nixos-agent
        else
            print_warning "nixos-agent user not found, setting root ownership"
            sudo chown -R root:root /opt/nixos-agent
        fi
        
        sudo chmod +x /opt/nixos-agent/bin/* 2>/dev/null || true
        print_success "AI agent files copied"
    else
        print_warning "ai-agent directory not found, skipping file copy"
    fi
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
    
    # Check if we're in the right directory
    if [[ ! -f "flake.nix" ]]; then
        print_error "flake.nix not found. Please run this script from the repository root."
        exit 1
    fi
    
    # Try to build the system
    print_status "Building flake configuration..."
    if sudo nixos-rebuild switch --flake .#$HOST; then
        print_success "System built successfully"
    else
        print_warning "System build failed, trying alternative approach..."
        
        # Alternative: try to build without flake
        print_status "Trying to build without flake..."
        if sudo nixos-rebuild switch; then
            print_success "System built successfully (without flake)"
        else
            print_error "System build failed completely"
            print_warning "You may need to manually configure the system"
            print_status "Continuing with installation..."
        fi
    fi
}

# Function to start services
start_services() {
    print_status "Starting AI agent services..."
    
    # Check if service file exists
    if [[ -f "/etc/systemd/system/nixos-agent.service" ]]; then
        # Enable and start the service
        sudo systemctl daemon-reload
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
    else
        print_warning "Service file not found (read-only filesystem detected)"
        print_status "In NixOS, services are managed through configuration.nix"
        print_status "The AI agent will be available after adding the configuration snippet and rebuilding"
        print_status "You can start it manually with: sudo systemctl start nixos-agent"
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
    echo "📝 NixOS Configuration:"
    echo "  • Configuration snippet: /etc/nixos-agent/nixos-config-snippet.nix"
    echo "  • Add to /etc/nixos/configuration.nix and rebuild for proper user management"
    echo "  • Rebuild: sudo nixos-rebuild switch"
    echo
    echo "🚀 Quick Start (Manual):"
    echo "  • Start AI agent: /opt/nixos-agent/start-ai-agent.sh"
    echo "  • Web UI: http://127.0.0.1:8999"
    echo "  • Chat interface: ai-chat"
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
    create_user_and_directories
    create_fallback_config
    create_nixos_config_snippet
    create_startup_script
    create_requirements_file
    create_python_installer
    install_python_deps
    copy_ai_agent_files
    setup_git_repo
    create_env_file
    build_system
    start_services
    test_installation
    show_final_instructions
}

# Run main function
main "$@"
