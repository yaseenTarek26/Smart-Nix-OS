#!/bin/bash

# NixOS AI Assistant - Development Setup Script
# Sets up a development environment for the project

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
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
PYTHON_VERSION="python3"

log "Setting up NixOS AI Assistant development environment..."

# Check if we're in the right directory
if [[ ! -f "$PROJECT_DIR/ai/agent.py" ]]; then
    error "Please run this script from the project root directory"
fi

# Check Python version
if ! command -v python3 &> /dev/null; then
    error "Python 3 is required but not installed"
fi

PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
log "Found Python $PYTHON_VER"

# Create virtual environment
log "Creating virtual environment..."
if [[ -d "$VENV_DIR" ]]; then
    warn "Virtual environment already exists, removing..."
    rm -rf "$VENV_DIR"
fi

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Upgrade pip
log "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
log "Installing Python dependencies..."
pip install -r "$PROJECT_DIR/requirements.txt"

# Install development dependencies
log "Installing development dependencies..."
pip install pytest pytest-asyncio pytest-cov black flake8 mypy

# Create necessary directories
log "Creating project directories..."
mkdir -p "$PROJECT_DIR/state"
mkdir -p "$PROJECT_DIR/cache"
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/backups"

# Set up git hooks (if in a git repository)
if [[ -d "$PROJECT_DIR/.git" ]]; then
    log "Setting up git hooks..."
    
    # Pre-commit hook
    cat > "$PROJECT_DIR/.git/hooks/pre-commit" << 'EOF'
#!/bin/bash
# Run tests before commit
cd "$(git rev-parse --show-toplevel)"
python3 tests/run_tests.py
EOF
    chmod +x "$PROJECT_DIR/.git/hooks/pre-commit"
    
    success "Git hooks installed"
fi

# Create development configuration
log "Creating development configuration..."
cat > "$PROJECT_DIR/ai/config.dev.json" << 'EOF'
{
  "ai_models": {
    "openai": {
      "api_key": "",
      "base_url": "https://api.openai.com/v1",
      "models": {
        "gpt-4": {
          "temperature": 0.7,
          "max_tokens": 2000,
          "timeout": 300
        }
      },
      "default_model": "gpt-4"
    }
  },
  "active_provider": "openai",
  "allowed_paths": ["/tmp/nixos-ai-dev"],
  "enable_system_wide_access": false,
  "auto_commit": true,
  "auto_rollback": true,
  "validation_required": true,
  "log_level": "DEBUG",
  "state_directory": "/tmp/nixos-ai-dev/state",
  "cache_directory": "/tmp/nixos-ai-dev/cache"
}
EOF

# Create development environment file
log "Creating development environment file..."
cat > "$PROJECT_DIR/.env.dev" << 'EOF'
# Development environment variables
NIXOS_AI_DIR=/tmp/nixos-ai-dev
AI_ACTIVE_PROVIDER=openai
ALLOWED_PATHS=/tmp/nixos-ai-dev
SYSTEM_WIDE_ACCESS=false
PYTHONPATH=/tmp/nixos-ai-dev/ai
EOF

# Create development test directory
log "Creating development test directory..."
mkdir -p /tmp/nixos-ai-dev
mkdir -p /tmp/nixos-ai-dev/state
mkdir -p /tmp/nixos-ai-dev/cache
mkdir -p /tmp/nixos-ai-dev/logs

# Run tests
log "Running initial tests..."
cd "$PROJECT_DIR"
if python3 tests/run_tests.py; then
    success "All tests passed"
else
    warn "Some tests failed, but development environment is ready"
fi

# Create development scripts
log "Creating development scripts..."

# Test script
cat > "$PROJECT_DIR/dev_test.sh" << 'EOF'
#!/bin/bash
# Development test script
cd "$(dirname "$0")"
source venv/bin/activate
python3 tests/run_tests.py
EOF
chmod +x "$PROJECT_DIR/dev_test.sh"

# Run script
cat > "$PROJECT_DIR/dev_run.sh" << 'EOF'
#!/bin/bash
# Development run script
cd "$(dirname "$0")"
source venv/bin/activate
export NIXOS_AI_DIR=/tmp/nixos-ai-dev
export AI_ACTIVE_PROVIDER=openai
export ALLOWED_PATHS=/tmp/nixos-ai-dev
export SYSTEM_WIDE_ACCESS=false
export PYTHONPATH=/tmp/nixos-ai-dev/ai
python3 ai/agent.py "$@"
EOF
chmod +x "$PROJECT_DIR/dev_run.sh"

# Lint script
cat > "$PROJECT_DIR/dev_lint.sh" << 'EOF'
#!/bin/bash
# Development lint script
cd "$(dirname "$0")"
source venv/bin/activate
flake8 ai/ tests/ --max-line-length=100 --ignore=E203,W503
mypy ai/ --ignore-missing-imports --no-strict-optional
EOF
chmod +x "$PROJECT_DIR/dev_lint.sh"

success "Development environment setup complete!"
echo ""
echo "Development commands:"
echo "  ./dev_test.sh     - Run all tests"
echo "  ./dev_run.sh      - Run AI assistant in development mode"
echo "  ./dev_lint.sh     - Run linting and type checking"
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run tests:"
echo "  python3 tests/run_tests.py"
echo ""
echo "To run the AI assistant:"
echo "  python3 ai/agent.py 'your command here'"
echo ""
echo "Development configuration:"
echo "  Config: ai/config.dev.json"
echo "  Environment: .env.dev"
echo "  Test directory: /tmp/nixos-ai-dev"
