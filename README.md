# NixOS AI Hyprland - Living Desktop

A complete NixOS configuration featuring Hyprland with an integrated AI agent that can manage your system through natural language commands.

## 🌟 Features

- **Beautiful Hyprland Desktop** - Based on the popular Frost-Phoenix configuration
- **AI-Powered System Management** - Chat or speak to install packages, configure settings, and manage your desktop
- **Unified-Diff Patch System** - Safe, reversible configuration changes
- **Fallback Package Installation** - Automatic fallback to Flatpak, AppImage, or Docker when Nix packages aren't available
- **Voice Interaction** - Speech-to-text and text-to-speech support
- **Web UI** - Modern chat interface with patch preview
- **Git Integration** - All changes are tracked and can be reverted

## 🚀 Quick Installation

### One-Command Installation

```bash
curl -fsSL https://raw.githubusercontent.com/yaseenTarek26/Smart-Nix-OS/main/install.sh | bash
```

### Manual Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yaseenTarek26/Smart-Nix-OS.git
   cd Smart-Nix-OS
   ```

2. **Run the installation script:**
   ```bash
   ./install.sh
   ```

3. **Follow the prompts** to configure your system

4. **Reboot** and enjoy your AI-powered desktop!

## 🎯 Usage

### Chat Interface

- **Web UI**: Open http://127.0.0.1:8999 in your browser
- **Hotkey**: Press `Super+Space` to open AI chat
- **Command**: Run `ai-chat` in terminal

### Voice Interaction

- **Hotkey**: Press `Super+Shift+Space` for voice mode
- **Command**: Run `ai-voice` in terminal

### Example Commands

```
"Install Firefox"
"Open Chrome"
"Change wallpaper to something dark"
"Install KiCad and add it to my menu"
"Enable flatpak support"
"Show me system information"
"Install a music player"
```

## 🏗️ Architecture

### Core Components

- **AI Agent** (`ai-agent/`) - Main Python daemon handling LLM calls and system operations
- **Decision Engine** - Classifies user intents (declarative/imperative/hybrid)
- **LLM Adapter** - Handles communication with various LLM providers
- **Patcher** - Validates and applies unified-diff patches
- **Executor** - Runs commands and manages system operations
- **Fallback System** - Handles Flatpak, AppImage, and Docker installations
- **Web UI** - FastAPI server with WebSocket support
- **Voice Support** - STT and TTS adapters

### Configuration Files

- `flake.nix` - Main Nix flake configuration
- `profiles/desktop.nix` - Desktop profile with Hyprland
- `profiles/laptop.nix` - Laptop profile with Hyprland
- `modules/ai-agent.nix` - AI agent NixOS module
- `ai-agent/` - Python AI agent code

## 🔧 Configuration

### LLM Providers

The AI agent supports multiple LLM providers:

- **OpenAI** (default) - Requires API key
- **Gemini** - Requires API key (default key included)
- **Local** - Experimental local models

### Environment Variables

Create `/etc/nixos-agent/.env`:

```bash
# For OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# For Gemini (default key included)
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyBjj5weW0GXXecUIfN2GHfa0zX9A9MAvm0

# Common settings
AI_AGENT_PORT=8999
NIXOS_CONFIG_PATH=/etc/nixos
CACHE_DIR=/var/lib/nixos-agent/cache
LOG_DIR=/var/log/nixos-agent
```

### Quick Gemini Setup

For immediate testing with Gemini:

```bash
# Setup Gemini with default API key
./setup_gemini.sh

# Test Gemini integration
python3 test_gemini.py
```

### Customization

- **Hyprland Config**: Modify `profiles/desktop.nix` or `profiles/laptop.nix`
- **AI Prompts**: Edit `ai-agent/prompts.json`
- **Voice Settings**: Configure in `ai-agent/stt/` and `ai-agent/tts/`

## 🛠️ Development

### Building from Source

```bash
# Build the system
nix build .#nixosConfigurations.desktop.config.system.build.toplevel

# Test in VM
nix run .#nixosConfigurations.desktop.config.system.build.vm
```

### Running Tests

```bash
# Run unit tests
python -m pytest tests/

# Test AI agent
python ai-agent/agent.py --test
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📚 Documentation

- [Quick Start Guide](docs/quickstart.md)
- [Prompt Engineering](docs/prompts.md)
- [API Reference](docs/api.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🐛 Troubleshooting

### Common Issues

**AI agent not starting:**
```bash
sudo systemctl status nixos-agent
journalctl -u nixos-agent -f
```

**Web UI not accessible:**
```bash
# Check if service is running
systemctl is-active nixos-agent

# Check port
netstat -tlnp | grep 8999
```

**Build failures:**
```bash
# Check NixOS configuration
nixos-rebuild test --flake .#desktop

# Check logs
journalctl -u nixos-agent -f
```

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/yaseenTarek26/Smart-Nix-OS/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yaseenTarek26/Smart-Nix-OS/discussions)
- **Discord**: [Join our Discord](https://discord.gg/your-discord)

## 🎨 Screenshots

![Desktop Screenshot](screenshots/desktop.png)
*Beautiful Hyprland desktop with AI agent integration*

![AI Chat Interface](screenshots/chat.png)
*Modern web-based chat interface*

![Voice Interaction](screenshots/voice.png)
*Voice interaction with speech recognition*

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Frost-Phoenix** - For the excellent Hyprland NixOS configuration
- **Hyprland Community** - For the amazing Wayland compositor
- **NixOS Community** - For the incredible package manager and OS
- **OpenAI** - For the powerful language models

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yaseenTarek26/Smart-Nix-OS&type=Date)](https://star-history.com/#yaseenTarek26/Smart-Nix-OS&Date)

---

**Made with ❤️ for the NixOS community**
