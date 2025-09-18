{ config, pkgs, ... }:

{
  # AI Agent user configuration
  home.packages = with pkgs; [
    # Development tools
    git
    curl
    wget
    jq
    yq-go
    
    # Media tools
    ffmpeg
    imagemagick
    vlc
    
    # System utilities
    htop
    btop
    neofetch
    tree
    unzip
    zip
    
    # Network tools
    nmap
    netcat
    openssh
  ];

  # Environment variables
  home.sessionVariables = {
    AI_AGENT_PORT = "8999";
    NIXOS_CONFIG_PATH = "/etc/nixos";
    CACHE_DIR = "/var/lib/nixos-agent/cache";
    LOG_DIR = "/var/log/nixos-agent";
  };

  # Shell configuration
  programs.bash = {
    enable = true;
    initExtra = ''
      # AI Agent aliases
      alias ai-chat="/opt/nixos-agent/bin/ai-chat"
      alias ai-voice="/opt/nixos-agent/bin/ai-voice"
      alias ai-status="systemctl status nixos-agent"
      alias ai-logs="journalctl -u nixos-agent -f"
    '';
  };

  # Git configuration for AI agent
  programs.git = {
    enable = true;
    userEmail = "ai-agent@nixos.local";
    userName = "NixOS AI Agent";
  };
}
