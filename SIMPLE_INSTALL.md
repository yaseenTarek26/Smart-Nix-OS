# NixOS AI Assistant - Ultra-Simple Installation

## 🚀 One-Command Install (No Root Required!)

```bash
curl -s https://raw.githubusercontent.com/yaseenTarek26/Smart-Nix-OS/main/scripts/bootstrap.sh | sh
```

## ✨ What This Does

- **Installs in user space** - no root required, no systemd, no NixOS configuration
- **Works on any Linux** - not just NixOS
- **Simple background process** - no complex service management
- **User-friendly** - just works out of the box

## 🎯 Features

- ✅ Multi-provider AI support (OpenAI, Anthropic, Ollama, Gemini)
- ✅ Safe file editing with git snapshots
- ✅ Command execution with validation
- ✅ Real-time system monitoring
- ✅ Comprehensive safety mechanisms
- ✅ Ultra-simple installation

## 📁 Installation Location

- **Files**: `~/nixos-ai/`
- **CLI**: `~/.local/bin/nixos-ai`
- **Logs**: `~/nixos-ai/logs/`
- **Config**: `~/nixos-ai/ai/config.json`

## 🎮 Usage

```bash
# Basic usage
nixos-ai "hello, can you help me?"

# System management
nixos-ai "install docker and enable it"
nixos-ai "add vscode to system packages"
nixos-ai "check system status"

# File operations
nixos-ai "edit my configuration file"
nixos-ai "create a new script"
```

## 🔧 Configuration

Edit `~/nixos-ai/ai/config.json` to add your API keys:

```json
{
  "ai_models": {
    "openai": {
      "api_key": "your-openai-key",
      "models": ["gpt-4", "gpt-3.5-turbo"]
    },
    "gemini": {
      "api_key": "your-gemini-key",
      "models": ["gemini-pro"]
    }
  }
}
```

## 🚀 Why This Approach?

- **No systemd complexity** - simple background process
- **No NixOS configuration** - works on any Linux
- **No root permissions** - user-space installation
- **No read-only filesystem issues** - only writes to user directories
- **No service management** - just run when needed
- **Ultra-reliable** - minimal failure points

## 🛠️ Manual Management

```bash
# Start manually
cd ~/nixos-ai && ./start-ai.sh

# Check if running
ps aux | grep nixos-ai

# View logs
tail -f ~/nixos-ai/logs/ai.log

# Update
cd ~/nixos-ai && git pull origin main
```

This approach eliminates all the complexity and just works! 🎉
