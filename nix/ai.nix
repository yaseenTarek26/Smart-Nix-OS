{ config, lib, pkgs, ... }:

with lib;

let
  cfg = config.services.nixos-ai;
  aiDir = "/etc/nixos/nixos-ai";
in
{
  options.services.nixos-ai = {
    enable = mkEnableOption "NixOS AI Assistant";
    
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
    # Minimal system packages - only essential ones
    environment.systemPackages = with pkgs; [
      python3
      python3Packages.pip
      python3Packages.setuptools
      git
      curl
      jq
    ];

    # Create the AI directory structure
    systemd.tmpfiles.rules = [
      "d ${aiDir} 0755 root root -"
      "d ${aiDir}/logs 0755 root root -"
      "d ${aiDir}/state 0755 root root -"
      "d ${aiDir}/cache 0755 root root -"
    ];

    # Systemd service for the AI assistant
    systemd.services.nixos-ai = {
      description = "NixOS AI Assistant - System-wide smart assistant";
      documentation = [ "https://github.com/yaseenTarek26/Smart-Nix-OS" ];
      
      wantedBy = [ "multi-user.target" ];
      after = [ "network.target" ];
      
      serviceConfig = {
        Type = "simple";
        ExecStart = "${pkgs.python3}/bin/python3 ${aiDir}/ai/agent.py";
        WorkingDirectory = aiDir;
        User = "root";
        Group = "root";
        Restart = "on-failure";
        RestartSec = 5;
        
        # Security settings
        NoNewPrivileges = true;
        PrivateTmp = true;
        ProtectSystem = "strict";
        ProtectHome = true;
        ReadWritePaths = [ aiDir ];
        
        # Resource limits
        MemoryMax = "512M";
        CPUQuota = "50%";
      };
      
      environment = {
        PYTHONPATH = "${aiDir}";
        AI_CONFIG_PATH = "${aiDir}/ai/config.json";
        AI_LOGS_PATH = "${aiDir}/logs";
        AI_STATE_PATH = "${aiDir}/state";
        AI_CACHE_PATH = "${aiDir}/cache";
      };
    };
  };
}