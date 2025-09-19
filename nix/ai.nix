{ config, lib, pkgs, ... }:

with lib;

let
  cfg = config.services.nixos-ai;
  aiDir = "/etc/nixos/nixos-ai";
in
{
  options.services.nixos-ai = {
    enable = mkEnableOption "NixOS AI Assistant";
  };

  config = mkIf cfg.enable {
    # Only essential packages that are guaranteed to exist
    environment.systemPackages = with pkgs; [
      python3
      git
      curl
    ];

    # Create the AI directory structure
    systemd.tmpfiles.rules = [
      "d ${aiDir} 0755 root root -"
      "d ${aiDir}/logs 0755 root root -"
      "d ${aiDir}/state 0755 root root -"
      "d ${aiDir}/cache 0755 root root -"
    ];

    # Minimal systemd service
    systemd.services.nixos-ai = {
      description = "NixOS AI Assistant";
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