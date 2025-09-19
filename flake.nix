{
  description = "NixOS AI Assistant - System-wide smart assistant for NixOS";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        packages = {
          nixos-ai = pkgs.stdenv.mkDerivation {
            name = "nixos-ai";
            version = "1.0.0";
            src = ./.;
            
            buildInputs = with pkgs; [
              python3
              python3Packages.pip
              python3Packages.setuptools
              git
              curl
              jq
              inotify-tools
            ];
            
            installPhase = ''
              mkdir -p $out
              cp -r . $out/
              chmod +x $out/scripts/*.sh
            '';
          };
        };
        
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python3
            python3Packages.pip
            python3Packages.setuptools
            git
            curl
            jq
            inotify-tools
            nixos-rebuild
          ];
        };
      }
    ) // {
      nixosModules.default = { config, lib, pkgs, ... }:
        with lib;
        let
          cfg = config.services.nixos-ai;
          aiDir = "/etc/nixos/nixos-ai";
        in
        {
          options.services.nixos-ai = {
            enable = mkEnableOption "NixOS AI Assistant";
            
            apiKey = mkOption {
              type = types.str;
              default = "";
              description = "OpenAI API key for the AI assistant";
            };
            
            model = mkOption {
              type = types.str;
              default = "gpt-4";
              description = "AI model to use";
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
            ];

            # Systemd service for the AI assistant
            systemd.services.nixos-ai = {
              description = "NixOS AI Assistant";
              after = [ "network.target" ];
              wantedBy = [ "multi-user.target" ];
              
              serviceConfig = {
                Type = "simple";
                User = "root";
                WorkingDirectory = aiDir;
                ExecStart = "${pkgs.python3}/bin/python3 ${aiDir}/ai/agent.py --daemon";
                Restart = "always";
                RestartSec = 5;
                
                # Security settings
                NoNewPrivileges = false; # AI needs to modify system files
                PrivateTmp = false; # AI needs access to system files
                ProtectSystem = "strict";
                ProtectHome = "read-only";
                ReadWritePaths = [ aiDir "/etc/nixos" "/var/log" ];
                
                # Environment variables
                Environment = [
                  "PYTHONPATH=${aiDir}/ai"
                  "NIXOS_AI_DIR=${aiDir}"
                  "OPENAI_API_KEY=${cfg.apiKey}"
                  "AI_MODEL=${cfg.model}"
                  "ALLOWED_PATHS=${concatStringsSep ":" cfg.allowedPaths}"
                  "SYSTEM_WIDE_ACCESS=${toString cfg.enableSystemWideAccess}"
                ];
              };
            };

            # Create the AI directory structure
            systemd.tmpfiles.rules = [
              "d ${aiDir} 0755 root root -"
              "d ${aiDir}/logs 0755 root root -"
              "d ${aiDir}/backups 0755 root root -"
            ];
          };
        };
    };
}
