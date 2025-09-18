{ config, pkgs, inputs, ... }:

let
  frost-phoenix = import ./external/frost-phoenix { inherit inputs; };
in
{
  imports = [
    frost-phoenix.hosts.laptop
    ./../modules/ai-agent.nix
  ];

  # Enable AI agent
  services.aiAgent.enable = true;

  # Additional packages for AI agent
  environment.systemPackages = with pkgs; [
    # AI agent dependencies
    python3
    git
    curl
    wget
    jq
    yq-go
    
    # Development tools
    vscode
    flatpak
    zenity
    libnotify
    rofi-wayland
    wl-clipboard
    
    # System utilities
    htop
    btop
    neofetch
    tree
    unzip
    zip
    
    # Media tools
    ffmpeg
    imagemagick
    vlc
    
    # Network tools
    nmap
    netcat
    openssh
  ];

  # Enable flatpak for fallback packages
  services.flatpak.enable = true;
  
  # Enable podman for Docker fallback
  virtualisation.podman.enable = true;
  virtualisation.podman.dockerCompat = true;

  # Add AI agent hotkey to Hyprland config
  wayland.windowManager.hyprland.settings = {
    bind = [
      "SUPER, SPACE, exec, /opt/nixos-agent/bin/ai-chat"
      "SUPER SHIFT, SPACE, exec, /opt/nixos-agent/bin/ai-voice"
    ];
  };

  # Systemd user service for AI agent
  systemd.user.services.ai-agent = {
    description = "NixOS AI Agent";
    wantedBy = [ "graphical-session.target" ];
    serviceConfig = {
      Type = "simple";
      ExecStart = "/opt/nixos-agent/bin/ai-agent";
      Restart = "always";
      RestartSec = 5;
      Environment = "DISPLAY=:0";
      Environment = "WAYLAND_DISPLAY=wayland-0";
    };
  };
}
