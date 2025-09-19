#!/bin/bash

# NixOS AI Assistant - Gemini API Test Script
# Tests Gemini API integration

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

log "Testing Gemini API integration..."

# Check if AI directory exists
if [[ ! -d "$AI_DIR" ]]; then
    error "AI directory not found: $AI_DIR"
fi

cd "$AI_DIR"

# Test Python imports
log "Testing Python imports..."
if python3 -c "
import sys
sys.path.insert(0, 'ai')
try:
    from config import AIConfig
    from agent import NixOSAIAgent
    print('Core imports successful')
    
    # Test Gemini import
    try:
        import google.generativeai as genai
        print('Gemini library available')
    except ImportError:
        print('Gemini library not installed - run: pip install google-generativeai')
        sys.exit(1)
        
except ImportError as e:
    print(f'Import error: {e}')
    sys.exit(1)
"; then
    success "Python imports working"
else
    error "Python import test failed"
fi

# Test Gemini configuration
log "Testing Gemini configuration..."
if python3 -c "
import sys
sys.path.insert(0, 'ai')
from config import AIConfig
config = AIConfig()
gemini_config = config.get_model_config('gemini', 'gemini-pro')
print(f'Gemini config: {gemini_config}')
api_key = config.get_api_key('gemini')
print(f'API key present: {bool(api_key)}')
"; then
    success "Gemini configuration loaded"
else
    error "Gemini configuration test failed"
fi

# Test Gemini API connection
log "Testing Gemini API connection..."
if python3 -c "
import sys
sys.path.insert(0, 'ai')
from config import AIConfig
from agent import NixOSAIAgent

config = AIConfig()
agent = NixOSAIAgent(config)

# Test Gemini client setup
gemini_client = agent._setup_gemini_client()
if gemini_client:
    print('Gemini client created successfully')
    
    # Test a simple request
    messages = [
        {'role': 'user', 'content': 'Hello, can you help me with NixOS?'}
    ]
    
    try:
        response = gemini_client.chat_completion(messages)
        print('Gemini API response received')
        print(f'Response: {response}')
    except Exception as e:
        print(f'Gemini API error: {e}')
        sys.exit(1)
else:
    print('Failed to create Gemini client')
    sys.exit(1)
"; then
    success "Gemini API connection working"
else
    error "Gemini API connection test failed"
fi

# Test switching to Gemini provider
log "Testing provider switching to Gemini..."
if python3 -c "
import sys
sys.path.insert(0, 'ai')
from config import AIConfig

config = AIConfig()
config.set_active_provider('gemini')
print(f'Active provider: {config.active_provider}')
print(f'API key: {config.get_api_key(\"gemini\")}')
"; then
    success "Provider switching to Gemini working"
else
    error "Provider switching test failed"
fi

success "All Gemini tests passed!"
echo ""
echo "Gemini API integration is working correctly."
echo ""
echo "To use Gemini as your primary provider:"
echo "1. Edit /etc/nixos/nixos-ai/ai/config.json"
echo "2. Set 'active_provider': 'gemini'"
echo "3. Restart the AI service: systemctl restart nixos-ai.service"
echo ""
echo "Test with: nixos-ai 'hello from Gemini'"
