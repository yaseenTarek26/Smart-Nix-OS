{ config, pkgs, lib, ... }:

let
  aiAgentPkg = pkgs.python3Packages.buildPythonApplication {
    pname = "nixos-ai-agent";
    version = "1.0.0";
    src = ./../ai-agent;
        propagatedBuildInputs = with pkgs.python3Packages; [
          fastapi
          uvicorn
          websockets
          openai
          google-generativeai
          gitpython
          pyyaml
          requests
          whisper
          coqui-tts
          pyaudio
          speechrecognition
          aiofiles
          python-multipart
          jinja2
        ];
  };
in
{
  options.services.aiAgent = {
    enable = lib.mkEnableOption "NixOS AI Agent";
    port = lib.mkOption {
      type = lib.types.port;
      default = 8999;
      description = "Port for AI agent web interface";
    };
    llmProvider = lib.mkOption {
      type = lib.types.str;
      default = "openai";
      description = "LLM provider (openai, gemini, local)";
    };
    apiKey = lib.mkOption {
      type = lib.types.str;
      default = "";
      description = "API key for LLM provider";
    };
  };

  config = lib.mkIf config.services.aiAgent.enable {
    # Create nixos-agent user
    users.users.nixos-agent = {
      isSystemUser = true;
      group = "nixos-agent";
      home = "/var/lib/nixos-agent";
      createHome = true;
      shell = pkgs.bash;
    };

    users.groups.nixos-agent = {};

    # Install AI agent
    environment.systemPackages = [ aiAgentPkg ];

    # Create directories
    systemd.tmpfiles.rules = [
      "d /var/lib/nixos-agent 0755 nixos-agent nixos-agent -"
      "d /var/log/nixos-agent 0755 nixos-agent nixos-agent -"
      "d /etc/nixos-agent 0755 root root -"
      "d /opt/nixos-agent 0755 root root -"
    ];

    # Install AI agent files
    system.activationScripts.aiAgentSetup = ''
      # Copy AI agent files
      cp -r ${aiAgentPkg}/* /opt/nixos-agent/
      chown -R nixos-agent:nixos-agent /opt/nixos-agent
      chmod +x /opt/nixos-agent/bin/*

      # Create environment file
      cat > /etc/nixos-agent/.env << EOF
LLM_PROVIDER=${config.services.aiAgent.llmProvider}
OPENAI_API_KEY=${config.services.aiAgent.apiKey}
AI_AGENT_PORT=${toString config.services.aiAgent.port}
NIXOS_CONFIG_PATH=/etc/nixos
CACHE_DIR=/var/lib/nixos-agent/cache
LOG_DIR=/var/log/nixos-agent
EOF

      # Initialize git repo in /etc/nixos if not exists
      if [ ! -d /etc/nixos/.git ]; then
        cd /etc/nixos
        git init
        git config user.name "NixOS AI Agent"
        git config user.email "ai-agent@nixos.local"
        git add .
        git commit -m "Initial NixOS configuration"
      fi
    '';

    # Sudoers rule for nixos-agent
    security.sudo.extraRules = [
      {
        users = [ "nixos-agent" ];
        commands = [
          {
            command = "${pkgs.nixos-rebuild}/bin/nixos-rebuild";
            options = [ "NOPASSWD" ];
          }
          {
            command = "${pkgs.git}/bin/git";
            options = [ "NOPASSWD" ];
          }
          {
            command = "${pkgs.flatpak}/bin/flatpak";
            options = [ "NOPASSWD" ];
          }
          {
            command = "${pkgs.podman}/bin/podman";
            options = [ "NOPASSWD" ];
          }
        ];
      }
    ];

    # Systemd service
    systemd.services.nixos-agent = {
      description = "NixOS AI Agent";
      wantedBy = [ "multi-user.target" ];
      after = [ "network.target" ];
      serviceConfig = {
        Type = "simple";
        User = "nixos-agent";
        Group = "nixos-agent";
        WorkingDirectory = "/opt/nixos-agent";
        ExecStart = "${aiAgentPkg}/bin/ai-agent";
        Restart = "always";
        RestartSec = 5;
        EnvironmentFile = "/etc/nixos-agent/.env";
        StandardOutput = "journal";
        StandardError = "journal";
      };
    };
  };
}
