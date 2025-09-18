# Quick Start Guide

This guide will help you get up and running with NixOS AI Hyprland in just a few minutes.

## Prerequisites

- NixOS system (any recent version)
- Internet connection
- Root access (for installation)
- At least 4GB RAM and 20GB free disk space

## Installation

### Option 1: One-Command Installation (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/your-repo/nixos-ai-hyperland/main/install.sh | bash
```

### Option 2: Manual Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo/nixos-ai-hyperland.git
   cd nixos-ai-hyperland
   ```

2. **Run the installation script:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. **Follow the prompts:**
   - Enter your username
   - Choose desktop or laptop configuration
   - Select LLM provider (OpenAI, Gemini, or Local)
   - Enter API key if needed

4. **Reboot your system:**
   ```bash
   sudo reboot
   ```

## First Boot

After rebooting, you'll be greeted by the beautiful Hyprland desktop with AI agent integration.

### Accessing the AI Agent

- **Web Interface**: Open http://127.0.0.1:8999 in your browser
- **Hotkey**: Press `Super+Space` to open AI chat
- **Terminal**: Run `ai-chat` command
- **Voice**: Press `Super+Shift+Space` or run `ai-voice`

## Basic Usage

### Installing Packages

```
"Install Firefox"
"Add VSCode to my system"
"Install a music player"
```

### Opening Applications

```
"Open Firefox"
"Launch VSCode"
"Start a terminal"
```

### System Configuration

```
"Change my wallpaper"
"Enable flatpak support"
"Show system information"
"Install a development environment"
```

### Voice Commands

1. Press `Super+Shift+Space` or run `ai-voice`
2. Wait for the "Listening..." prompt
3. Speak your command clearly
4. The AI will respond with both text and voice

## Configuration

### LLM Provider Setup

Edit `/etc/nixos-agent/.env`:

```bash
# For OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# For Gemini
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-key-here

# For Local (experimental)
LLM_PROVIDER=local
```

### Customizing Hyprland

Edit the configuration files:
- `profiles/desktop.nix` - Desktop configuration
- `profiles/laptop.nix` - Laptop configuration

### AI Agent Settings

- **Prompts**: Edit `ai-agent/prompts.json`
- **Voice**: Configure in `ai-agent/stt/` and `ai-agent/tts/`
- **Fallback**: Modify `ai-agent/fallback/` modules

## Troubleshooting

### AI Agent Not Starting

```bash
# Check service status
sudo systemctl status nixos-agent

# View logs
journalctl -u nixos-agent -f

# Restart service
sudo systemctl restart nixos-agent
```

### Web UI Not Accessible

```bash
# Check if port is open
netstat -tlnp | grep 8999

# Check firewall
sudo ufw status

# Test connection
curl http://127.0.0.1:8999
```

### Build Failures

```bash
# Test configuration
nixos-rebuild test --flake .#desktop

# Check for errors
nixos-rebuild switch --flake .#desktop --show-trace

# Revert changes
git -C /etc/nixos revert HEAD
```

### Voice Not Working

```bash
# Check audio devices
arecord -l
aplay -l

# Test microphone
arecord -d 5 test.wav
aplay test.wav

# Check permissions
ls -la /dev/snd/
```

## Advanced Usage

### Custom Commands

You can create custom commands by modifying the decision engine:

```python
# In ai-agent/decision_engine.py
def _extract_command(self, message: str) -> str:
    # Add your custom command parsing logic
    pass
```

### Adding New Fallback Methods

Create a new helper in `ai-agent/fallback/`:

```python
class CustomHelper:
    async def install_package(self, package_name: str):
        # Your custom installation logic
        pass
```

### Extending the Web UI

Modify `ai-agent/webui.py` to add new features:

```python
@app.get("/api/custom-endpoint")
async def custom_endpoint():
    return {"message": "Custom response"}
```

## Getting Help

- **Documentation**: Check the `docs/` directory
- **Issues**: [GitHub Issues](https://github.com/your-repo/nixos-ai-hyperland/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/nixos-ai-hyperland/discussions)
- **Discord**: [Join our Discord](https://discord.gg/your-discord)

## Next Steps

- Explore the [API Reference](api.md)
- Learn about [Prompt Engineering](prompts.md)
- Check out [Advanced Configuration](advanced.md)
- Contribute to the project!

---

**Happy computing with your AI-powered NixOS desktop! 🚀**
