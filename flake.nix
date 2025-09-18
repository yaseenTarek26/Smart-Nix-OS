{
  description = "NixOS Hyprland AI-Powered Living Desktop";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    hyprland.url = "github:hyprwm/Hyprland";
    frost-phoenix = {
      url = "github:Frost-Phoenix/nixos-config";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, home-manager, hyprland, frost-phoenix, ... }@inputs:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      nixosConfigurations = {
        desktop = nixpkgs.lib.nixosSystem {
          inherit system;
          modules = [
            ./profiles/desktop.nix
            ./modules/ai-agent.nix
            home-manager.nixosModules.home-manager
            {
              home-manager.useGlobalPkgs = true;
              home-manager.useUserPackages = true;
              home-manager.users.nixos-agent = import ./modules/home/ai-agent.nix;
            }
          ];
          specialArgs = { inherit inputs; };
        };
        laptop = nixpkgs.lib.nixosSystem {
          inherit system;
          modules = [
            ./profiles/laptop.nix
            ./modules/ai-agent.nix
            home-manager.nixosModules.home-manager
            {
              home-manager.useGlobalPkgs = true;
              home-manager.useUserPackages = true;
              home-manager.users.nixos-agent = import ./modules/home/ai-agent.nix;
            }
          ];
          specialArgs = { inherit inputs; };
        };
      };

      packages.${system} = {
        ai-agent = pkgs.python3Packages.buildPythonApplication {
          pname = "nixos-ai-agent";
          version = "1.0.0";
          src = ./ai-agent;
          propagatedBuildInputs = with pkgs.python3Packages; [
            fastapi
            uvicorn
            websockets
            openai
            gitpython
            pyyaml
            requests
            whisper
            coqui-tts
            pyaudio
            speechrecognition
          ];
        };
      };

      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          nix
          git
          python3
          python3Packages.pip
          python3Packages.virtualenv
        ];
      };
    };
}
