# NixOS AI Assistant

A system-wide smart assistant that provides natural language interface for system management, configuration editing, and package installation. Works on any Linux system with ultra-simple installation.

## 🚀 Features

- **Natural Language Interface**: Talk to your system in plain English
- **Multi-provider AI Support**: OpenAI, Anthropic, Ollama, Google Gemini
- **Safe File Editing**: AI can edit files with git snapshots and validation
- **Command Execution**: Run system commands with safety checks and logging
- **Real-time Monitoring**: Continuous system health monitoring and log watching
- **Ultra-Simple Installation**: Works in user space, no root required
- **Cross-Platform**: Works on any Linux system, not just NixOS
- **Zero Dependencies**: No systemd, no complex configuration required

## 📋 Requirements

- Any Linux system (not just NixOS!)
- No root access required
- Internet connection for initial download
- Python 3 (usually pre-installed)

## 🛠️ Installation

### One-Command Install (Ultra-Simple!)

```bash
# Ultra-simple installation - works in user space, no root required!
curl -s https://raw.githubusercontent.com/yaseenTarek26/Smart-Nix-OS/main/scripts/bootstrap.sh | sh
```

**That's it!** The AI assistant will be installed to `~/nixos-ai/` and available as `nixos-ai` command.

### What This Does

- ✅ **Installs in user space** - no root permissions needed
- ✅ **No systemd required** - simple background process
- ✅ **No NixOS configuration** - works on any Linux
- ✅ **No Git authentication** - downloads files directly
- ✅ **Zero failure points** - guaranteed to work

## 🎮 Usage

After installation, you can immediately use:

```bash
# Basic interaction
nixos-ai "hello"
nixos-ai "help"

# System management
nixos-ai "check system status"
nixos-ai "install packages"

# File operations
nixos-ai "edit my configuration"
nixos-ai "create a new script"
```

## 📁 Installation Details

- **Files**: `~/nixos-ai/`
- **CLI**: `~/.local/bin/nixos-ai`
- **Logs**: `~/nixos-ai/logs/`
- **Config**: `~/nixos-ai/ai/config.json`

## 🎯 Usage

### Command Line Interface

```bash
# Process a single request
nixos-ai "install docker and enable it"

# Interactive mode
nixos-ai

# Run as daemon
nixos-ai --daemon
```

### Example Commands

```bash
# Install packages
nixos-ai "install vscode and git"

# Enable services
nixos-ai "enable docker service"

# System management
nixos-ai "check system status and show memory usage"

# Configuration changes
nixos-ai "add vscode to system packages"
```

## 🔧 Configuration

The AI assistant can be configured through `/etc/nixos/nixos-ai/ai/config.json`:

```json
{
  "ai_models": {
    "openai": {
      "api_key": "your-openai-api-key",
      "base_url": "https://api.openai.com/v1",
      "models": {
        "gpt-4": {"temperature": 0.7, "max_tokens": 2000, "timeout": 300},
        "gpt-3.5-turbo": {"temperature": 0.7, "max_tokens": 1000, "timeout": 180}
      },
      "default_model": "gpt-4"
    },
    "anthropic": {
      "api_key": "your-anthropic-api-key",
      "base_url": "https://api.anthropic.com",
      "models": {
        "claude-3-opus": {"temperature": 0.7, "max_tokens": 2000, "timeout": 300}
      },
      "default_model": "claude-3-opus"
    },
    "gemini": {
      "api_key": "your-gemini-api-key",
      "base_url": "https://generativelanguage.googleapis.com/v1beta",
      "models": {
        "gemini-pro": {"temperature": 0.7, "max_tokens": 2000, "timeout": 300}
      },
      "default_model": "gemini-pro"
    },
    "ollama": {
      "api_key": "",
      "base_url": "http://localhost:11434",
      "models": {
        "llama2": {"temperature": 0.7, "max_tokens": 2000, "timeout": 300}
      },
      "default_model": "llama2"
    }
  },
  "active_provider": "openai",
  "fallback_providers": ["gemini", "ollama", "anthropic"],
  "allowed_paths": ["/etc/nixos/nixos-ai"],
  "enable_system_wide_access": false,
  "auto_commit": true,
  "auto_rollback": true,
  "validation_required": true
}
```

### Configuration Options

- `ai_models`: Configuration for multiple AI providers (OpenAI, Anthropic, Ollama)
- `active_provider`: Currently active AI provider
- `fallback_providers`: Fallback providers if primary fails
- `allowed_paths`: Paths the AI can modify (default: AI directory only)
- `enable_system_wide_access`: Allow AI to modify any system file (dangerous)
- `auto_commit`: Automatically commit changes to git
- `auto_rollback`: Automatically rollback on failures
- `validation_required`: Validate NixOS configs before applying

### Supported AI Providers

- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Google Gemini**: Gemini Pro, Gemini Pro Vision
- **Anthropic**: Claude-3-opus, Claude-3-sonnet
- **Ollama**: Local models (llama2, codellama)
- **Custom**: Add your own providers

## 🛡️ Safety Features

### Git Snapshots
- All file changes are automatically committed to git
- Easy rollback to any previous state
- Complete change history tracking

### Validation
- NixOS configuration syntax validation
- `nixos-rebuild test` before applying changes
- Command safety checks and filtering

### Rollback Options
```bash
# Interactive rollback
/etc/nixos/nixos-ai/scripts/rollback.sh

# Rollback to specific backup
/etc/nixos/nixos-ai/scripts/rollback.sh --backup /etc/nixos/backup-20231201-120000

# Rollback using NixOS generations
/etc/nixos/nixos-ai/scripts/rollback.sh --generation
```

## 📁 Project Structure

```
nixos-ai/
├── ai/                          # Core AI components
│   ├── agent.py                 # Main AI agent
│   ├── editor.py                # File editing engine
│   ├── executor.py              # Command executor
│   ├── watcher.py               # Log monitoring
│   ├── config.py                # Configuration management
│   └── config.json              # AI settings
├── nix/                         # NixOS integration
│   ├── ai.nix                   # Main NixOS module
│   ├── service.nix              # Systemd service definition
│   └── default.nix              # Non-flake support
├── scripts/                     # Installation & management
│   ├── bootstrap.sh             # One-command installer
│   ├── apply.sh                 # Apply changes safely
│   ├── rollback.sh              # Emergency rollback
│   ├── test.sh                  # Installation verification
│   ├── demo.sh                  # Demonstration script
│   └── setup_dev.sh             # Development setup
├── tests/                       # Test suite
│   ├── test_agent.py            # AI agent tests
│   ├── test_editor.py           # File editor tests
│   ├── test_executor.py         # Command executor tests
│   ├── test_config.py           # Configuration tests
│   └── run_tests.py             # Test runner
├── docs/                        # Documentation
│   ├── ARCHITECTURE.md          # System architecture
│   └── SECURITY.md              # Security documentation
├── state/                       # AI working state
├── cache/                       # AI response cache
├── logs/                        # AI and system logs
├── examples/                    # Example configurations
├── flake.nix                    # Nix flake definition
├── requirements.txt             # Python dependencies
├── permissions.json             # Security permissions
└── README.md                    # This file
```

## 🔍 Monitoring

### Service Status
```bash
# Check AI service status
systemctl status nixos-ai.service

# View service logs
journalctl -u nixos-ai.service -f

# View AI logs
tail -f /etc/nixos/nixos-ai/logs/ai.log
```

### System Health
```bash
# Check system health
nixos-ai "check system status"

# View recent events
nixos-ai "show recent system events"
```

## 🚨 Troubleshooting

### Common Issues

1. **AI service not starting**
   - Check logs: `journalctl -u nixos-ai.service`
   - Verify configuration: `nixos-rebuild test`
   - Check API key if using OpenAI

2. **Permission denied errors**
   - Ensure running as root for installation
   - Check file permissions in AI directory

3. **Configuration validation failures**
   - Use `nixos-rebuild test` to check syntax
   - Check NixOS configuration for errors
   - Use rollback script if needed

### Emergency Recovery

If the system becomes unstable:

1. **Immediate rollback**:
```bash
nixos-rebuild switch --rollback
```

2. **Full system recovery**:
```bash
/etc/nixos/nixos-ai/scripts/rollback.sh --generation
```

3. **Manual recovery**:
   - Boot from previous generation
   - Restore from backup
   - Rebuild configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool provides powerful system management capabilities. Always:
- Test changes in a safe environment first
- Keep backups of important configurations
- Understand what changes the AI is making
- Use the safety features provided

The AI assistant is designed to be safe, but system administration always carries risks. Use responsibly.
