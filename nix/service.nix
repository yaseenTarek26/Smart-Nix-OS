{ config, lib, pkgs, ... }:

with lib;

let
  cfg = config.services.nixos-ai;
  aiDir = "/etc/nixos/nixos-ai";
in
{
  options.services.nixos-ai = {
    enable = mkEnableOption "NixOS AI Assistant service";
    
    # AI Configuration
    activeProvider = mkOption {
      type = types.str;
      default = "openai";
      description = "Active AI provider (openai, ollama, anthropic)";
    };
    
    apiKeys = mkOption {
      type = types.attrsOf types.str;
      default = {};
      description = "API keys for different AI providers";
    };
    
    # System Configuration
    allowedPaths = mkOption {
      type = types.listOf types.str;
      default = [ aiDir ];
      description = "Paths the AI is allowed to modify";
    };
    
    enableSystemWideAccess = mkOption {
      type = types.bool;
      default = false;
      description = "Allow AI to modify system-wide files (dangerous)";
    };
    
    # Service Configuration
    user = mkOption {
      type = types.str;
      default = "root";
      description = "User to run the AI service as";
    };
    
    group = mkOption {
      type = types.str;
      default = "root";
      description = "Group to run the AI service as";
    };
    
    # Security Configuration
    restrictNetwork = mkOption {
      type = types.bool;
      default = false;
      description = "Restrict network access for the AI service";
    };
    
    maxMemory = mkOption {
      type = types.str;
      default = "1G";
      description = "Maximum memory usage for the AI service";
    };
    
    maxCpu = mkOption {
      type = types.str;
      default = "50%";
      description = "Maximum CPU usage for the AI service";
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

    # Systemd service for the AI assistant
    systemd.services.nixos-ai = {
      description = "NixOS AI Assistant - System-wide smart assistant";
      documentation = [ "https://github.com/YOURNAME/nixos-ai" ];
      after = [ "network.target" "multi-user.target" ];
      wants = [ "network.target" ];
      wantedBy = [ "multi-user.target" ];
      
      serviceConfig = {
        Type = "notify";
        User = cfg.user;
        Group = cfg.group;
        WorkingDirectory = aiDir;
        ExecStart = "${pkgs.python3}/bin/python3 ${aiDir}/ai/agent.py --daemon";
        ExecReload = "${pkgs.coreutils}/bin/kill -HUP $MAINPID";
        Restart = "always";
        RestartSec = 5;
        TimeoutStartSec = 60;
        TimeoutStopSec = 30;
        
        # Security settings
        NoNewPrivileges = false; # AI needs to modify system files
        PrivateTmp = false; # AI needs access to system files
        ProtectSystem = if cfg.enableSystemWideAccess then "false" else "strict";
        ProtectHome = "read-only";
        ReadWritePaths = [ aiDir "/etc/nixos" "/var/log" ] ++ cfg.allowedPaths;
        
        # Resource limits
        MemoryLimit = cfg.maxMemory;
        CPUQuota = cfg.maxCpu;
        
        # Network restrictions
        PrivateNetwork = cfg.restrictNetwork;
        
        # Environment variables
        Environment = [
          "PYTHONPATH=${aiDir}/ai"
          "NIXOS_AI_DIR=${aiDir}"
          "AI_ACTIVE_PROVIDER=${cfg.activeProvider}"
          "ALLOWED_PATHS=${concatStringsSep ":" cfg.allowedPaths}"
          "SYSTEM_WIDE_ACCESS=${toString cfg.enableSystemWideAccess}"
        ] ++ (mapAttrsToList (name: value: "${toUpper name}_API_KEY=${value}") cfg.apiKeys);
        
        # Logging
        StandardOutput = "journal";
        StandardError = "journal";
        SyslogIdentifier = "nixos-ai";
      };
      
      # Pre-start script to ensure directories exist
      preStart = ''
        mkdir -p ${aiDir}/logs
        mkdir -p ${aiDir}/state
        mkdir -p ${aiDir}/cache
        mkdir -p ${aiDir}/backups
        chown -R ${cfg.user}:${cfg.group} ${aiDir}
        chmod 755 ${aiDir}/logs ${aiDir}/state ${aiDir}/cache ${aiDir}/backups
      '';
    };

    # Create the AI directory structure
    systemd.tmpfiles.rules = [
      "d ${aiDir} 0755 ${cfg.user} ${cfg.group} -"
      "d ${aiDir}/logs 0755 ${cfg.user} ${cfg.group} -"
      "d ${aiDir}/state 0755 ${cfg.user} ${cfg.group} -"
      "d ${aiDir}/cache 0755 ${cfg.user} ${cfg.group} -"
      "d ${aiDir}/backups 0755 ${cfg.user} ${cfg.group} -"
    ];

    # Optional: Create a user for the AI service
    users.users.nixos-ai = mkIf (cfg.user == "nixos-ai") {
      isSystemUser = true;
      group = cfg.group;
      home = aiDir;
      createHome = true;
    };

    users.groups.nixos-ai = mkIf (cfg.group == "nixos-ai") {};

    # Optional: Firewall rules for AI service
    networking.firewall = mkIf (!cfg.restrictNetwork) {
      allowedTCPPorts = [ 11434 ]; # Ollama default port
    };
  };
}
