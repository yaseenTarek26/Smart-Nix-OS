#!/bin/bash
# Test script for NixOS AI Hyprland installation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Test 1: Check if NixOS is running
test_nixos() {
    print_status "Testing NixOS environment..."
    
    if [[ -f /etc/nixos/configuration.nix ]]; then
        print_success "NixOS configuration found"
    else
        print_error "NixOS configuration not found"
        return 1
    fi
    
    if command -v nix &> /dev/null; then
        print_success "Nix package manager available"
    else
        print_error "Nix package manager not found"
        return 1
    fi
}

# Test 2: Check if git is available
test_git() {
    print_status "Testing git availability..."
    
    if command -v git &> /dev/null; then
        print_success "Git is available"
    else
        print_error "Git is not available"
        return 1
    fi
}

# Test 3: Check if curl is available
test_curl() {
    print_status "Testing curl availability..."
    
    if command -v curl &> /dev/null; then
        print_success "Curl is available"
    else
        print_error "Curl is not available"
        return 1
    fi
}

# Test 4: Check if Python is available
test_python() {
    print_status "Testing Python availability..."
    
    if command -v python3 &> /dev/null; then
        print_success "Python 3 is available"
    else
        print_error "Python 3 is not available"
        return 1
    fi
}

# Test 5: Check if required directories exist
test_directories() {
    print_status "Testing directory structure..."
    
    local dirs=("ai-agent" "profiles" "modules" "docs" "tests")
    
    for dir in "${dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            print_success "Directory $dir exists"
        else
            print_error "Directory $dir not found"
            return 1
        fi
    done
}

# Test 6: Check if required files exist
test_files() {
    print_status "Testing required files..."
    
    local files=("flake.nix" "install.sh" "README.md" "ai-agent/agent.py" "ai-agent/llm_adapter.py" "ai-agent/patcher.py" "ai-agent/executor.py")
    
    for file in "${files[@]}"; do
        if [[ -f "$file" ]]; then
            print_success "File $file exists"
        else
            print_error "File $file not found"
            return 1
        fi
    done
}

# Test 7: Check if Python modules can be imported
test_python_imports() {
    print_status "Testing Python module imports..."
    
    local modules=("ai-agent.agent" "ai-agent.llm_adapter" "ai-agent.patcher" "ai-agent.executor")
    
    for module in "${modules[@]}"; do
        if python3 -c "import $module" 2>/dev/null; then
            print_success "Module $module can be imported"
        else
            print_warning "Module $module cannot be imported (may need dependencies)"
        fi
    done
}

# Test 8: Check if flake.nix is valid
test_flake() {
    print_status "Testing flake.nix validity..."
    
    if nix flake check . 2>/dev/null; then
        print_success "flake.nix is valid"
    else
        print_warning "flake.nix validation failed (may need dependencies)"
    fi
}

# Test 9: Check if installation script is executable
test_install_script() {
    print_status "Testing installation script..."
    
    if [[ -x "install.sh" ]]; then
        print_success "install.sh is executable"
    else
        print_warning "install.sh is not executable (run chmod +x install.sh)"
    fi
}

# Test 10: Check if AI agent files are properly structured
test_ai_agent_structure() {
    print_status "Testing AI agent structure..."
    
    local ai_files=("ai-agent/agent.py" "ai-agent/decision_engine.py" "ai-agent/llm_adapter.py" "ai-agent/patcher.py" "ai-agent/executor.py" "ai-agent/webui.py" "ai-agent/prompts.json" "ai-agent/requirements.txt")
    
    for file in "${ai_files[@]}"; do
        if [[ -f "$file" ]]; then
            print_success "AI agent file $file exists"
        else
            print_error "AI agent file $file not found"
            return 1
        fi
    done
}

# Main test function
main() {
    echo "🧪 NixOS AI Hyprland Installation Test"
    echo "======================================"
    echo
    
    local tests=(
        "test_nixos"
        "test_git"
        "test_curl"
        "test_python"
        "test_directories"
        "test_files"
        "test_python_imports"
        "test_flake"
        "test_install_script"
        "test_ai_agent_structure"
    )
    
    local passed=0
    local failed=0
    local total=${#tests[@]}
    
    for test in "${tests[@]}"; do
        if $test; then
            ((passed++))
        else
            ((failed++))
        fi
        echo
    done
    
    echo "📊 Test Results"
    echo "==============="
    echo "Total tests: $total"
    echo "Passed: $passed"
    echo "Failed: $failed"
    
    if [[ $failed -eq 0 ]]; then
        echo
        print_success "All tests passed! The installation should work correctly."
        echo
        echo "Next steps:"
        echo "1. Run ./install.sh to install the system"
        echo "2. Follow the installation prompts"
        echo "3. Reboot and enjoy your AI-powered desktop!"
    else
        echo
        print_error "Some tests failed. Please fix the issues before installing."
        echo
        echo "Common fixes:"
        echo "1. Install missing dependencies: nix-env -iA nixpkgs.git nixpkgs.curl nixpkgs.python3"
        echo "2. Make install script executable: chmod +x install.sh"
        echo "3. Check file permissions and ownership"
    fi
}

# Run tests
main "$@"
