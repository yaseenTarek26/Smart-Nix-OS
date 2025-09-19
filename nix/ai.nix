{ config, lib, pkgs, ... }:

with lib;

let
  cfg = config.services.nixos-ai;
  aiDir = "/etc/nixos/nixos-ai";
in
{
  imports = [ ./service.nix ];

  options.services.nixos-ai = {
    enable = mkEnableOption "NixOS AI Assistant";
    
    # Legacy options for backward compatibility
    apiKey = mkOption {
      type = types.str;
      default = "";
      description = "OpenAI API key for the AI assistant (legacy)";
    };
    
    model = mkOption {
      type = types.str;
      default = "gpt-4";
      description = "AI model to use (legacy)";
    };
    
    allowedPaths = mkOption {
      type = types.listOf types.str;
      default = [ "/etc/nixos/nixos-ai" ];
      description = "Paths the AI is allowed to modify";
    };
    
    enableSystemWideAccess = mkOption {
      type = types.bool;
      default = false;
      description = "Allow AI to modify system-wide files (dangerous)";
    };
  };

  config = mkIf cfg.enable {
    # System packages required by the AI assistant
    environment.systemPackages = with pkgs; [
      python3
      python3Packages.pip
      python3Packages.setuptools
      git
      curl
      jq
      inotify-tools
      # AI-specific packages - install via Nix instead of pip
      python3Packages.openai
      python3Packages.anthropic
      python3Packages.google-generativeai
      python3Packages.httpx
      python3Packages.aiohttp
      python3Packages.psutil
      python3Packages.watchdog
      python3Packages.structlog
      python3Packages.pydantic
      python3Packages.typer
      python3Packages.aiofiles
      python3Packages.python-dotenv
    ];

    # Create the AI directory structure
    systemd.tmpfiles.rules = [
      "d ${aiDir} 0755 root root -"
      "d ${aiDir}/logs 0755 root root -"
      "d ${aiDir}/state 0755 root root -"
      "d ${aiDir}/cache 0755 root root -"
      "d ${aiDir}/backups 0755 root root -"
    ];

    # Note: This module should be imported in your configuration.nix
    # The actual service configuration is in service.nix
  };
}
