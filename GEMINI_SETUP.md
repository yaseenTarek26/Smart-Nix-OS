# Gemini API Key Setup Guide

## 🔑 Your Gemini API Key

**API Key**: `AIzaSyBjj5weW0GXXecUIfN2GHfa0zX9A9MAvm0`

This key has been integrated into the project and will be used by default when you select Gemini as your LLM provider.

## 📍 Where the API Key is Configured

### 1. **Installation Script** (`install.sh`)
- **Lines 107-109**: Default API key is set when user selects Gemini
- **Line 167**: API key is written to environment file
- **Location**: User is prompted to enter API key or press Enter for default

### 2. **Environment File** (`/etc/nixos-agent/.env`)
- **Created by**: Installation script
- **Contains**: `GEMINI_API_KEY=AIzaSyBjj5weW0GXXecUIfN2GHfa0zX9A9MAvm0`
- **Location**: `/etc/nixos-agent/.env` (system-wide)

### 3. **LLM Adapter** (`ai-agent/llm_adapter.py`)
- **Lines 89-90**: Reads API key from config
- **Lines 210-230**: Implements Gemini API calls
- **Fallback**: Uses `api_key` or `gemini_api_key` from config

### 4. **NixOS Module** (`modules/ai-agent.nix`)
- **Line 13**: Includes `google-generativeai` dependency
- **Location**: Python package dependencies

## 🚀 Quick Setup Options

### Option 1: Automatic Setup (Recommended)
```bash
# Run the installation script
./install.sh

# When prompted:
# 1. Choose "2" for Gemini
# 2. Press Enter to use default API key
```

### Option 2: Manual Setup
```bash
# Setup Gemini with default key
./setup_gemini.sh

# Test the integration
python3 test_gemini.py
```

### Option 3: Manual Environment File
```bash
# Create environment file manually
sudo mkdir -p /etc/nixos-agent
sudo tee /etc/nixos-agent/.env > /dev/null << EOF
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyBjj5weW0GXXecUIfN2GHfa0zX9A9MAvm0
AI_AGENT_PORT=8999
NIXOS_CONFIG_PATH=/etc/nixos
CACHE_DIR=/var/lib/nixos-agent/cache
LOG_DIR=/var/log/nixos-agent
EOF

sudo chown root:root /etc/nixos-agent/.env
sudo chmod 600 /etc/nixos-agent/.env
```

## 🧪 Testing the Integration

### Test Gemini API
```bash
python3 test_gemini.py
```

### Test Full System
```bash
# After installation
./test_installation.sh

# Test AI agent
ai-chat
# Or open http://127.0.0.1:8999
```

## 🔧 Configuration Details

### Environment Variables
- **`LLM_PROVIDER`**: Set to `gemini`
- **`GEMINI_API_KEY`**: Your API key
- **`AI_AGENT_PORT`**: Web UI port (default: 8999)
- **`NIXOS_CONFIG_PATH`**: NixOS config directory
- **`CACHE_DIR`**: LLM response cache directory
- **`LOG_DIR`**: AI agent log directory

### Dependencies
- **Python**: `google-generativeai==0.3.2`
- **NixOS**: Included in `modules/ai-agent.nix`
- **Requirements**: Listed in `ai-agent/requirements.txt`

## 🎯 Usage Examples

### Chat Commands
```
"Install Firefox using Gemini"
"Add VSCode to my system"
"Change my wallpaper to something dark"
"Show system information"
```

### Voice Commands
- Press `Super+Shift+Space` or run `ai-voice`
- Speak: "Install Discord and open it"
- AI responds with both text and voice

## 🔒 Security Notes

- **API Key**: Stored in `/etc/nixos-agent/.env` with 600 permissions
- **Access**: Only root and nixos-agent user can read
- **Network**: All API calls are made over HTTPS
- **Caching**: Responses are cached locally to reduce API usage

## 🐛 Troubleshooting

### Common Issues

**"Gemini support not implemented yet"**
```bash
# Install missing dependency
pip install google-generativeai
```

**"API key not found"**
```bash
# Check environment file
cat /etc/nixos-agent/.env

# Restart service
sudo systemctl restart nixos-agent
```

**"Import error"**
```bash
# Install Python dependencies
pip install -r ai-agent/requirements.txt
```

### Debug Commands
```bash
# Check service status
sudo systemctl status nixos-agent

# View logs
journalctl -u nixos-agent -f

# Test API key
python3 -c "import google.generativeai as genai; genai.configure(api_key='AIzaSyBjj5weW0GXXecUIfN2GHfa0zX9A9MAvm0'); print('API key works!')"
```

## ✅ Verification

After setup, verify everything works:

1. **API Key**: `python3 test_gemini.py` should succeed
2. **Service**: `systemctl is-active nixos-agent` should return "active"
3. **Web UI**: `curl http://127.0.0.1:8999` should return HTML
4. **Chat**: `ai-chat` should open the interface
5. **Voice**: `ai-voice` should start voice interaction

## 🎉 Ready to Use!

Your Gemini API key is now fully integrated and ready to power your AI-powered NixOS desktop!

---

**API Key**: `AIzaSyBjj5weW0GXXecUIfN2GHfa0zX9A9MAvm0`  
**Status**: ✅ Integrated and ready to use
