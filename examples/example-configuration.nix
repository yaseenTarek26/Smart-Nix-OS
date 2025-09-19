# Example NixOS configuration with AI Assistant
# Add this to your /etc/nixos/configuration.nix

{ config, pkgs, ... }:

{
  # Import the AI assistant module
  imports = [ ./nixos-ai/nix/ai.nix ];

  # Enable the AI assistant
  services.nixos-ai = {
    enable = true;
    # apiKey = "your-openai-api-key-here";  # Optional
    model = "gpt-4";
    allowedPaths = [ "/etc/nixos/nixos-ai" ];
    enableSystemWideAccess = false;  # Keep this false for safety
  };

  # Example: Add some packages that the AI might manage
  environment.systemPackages = with pkgs; [
    vscode
    git
    docker
    # Add more packages as needed
  ];

  # Example: Enable some services that the AI might manage
  services.docker.enable = true;
  
  # Example: Configure networking
  networking.networkmanager.enable = true;
  
  # Example: Configure users
  users.users.youruser = {
    isNormalUser = true;
    extraGroups = [ "wheel" "docker" ];
  };
}
