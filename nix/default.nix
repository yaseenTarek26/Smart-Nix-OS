{ pkgs ? import <nixpkgs> {} }:

pkgs.stdenv.mkDerivation {
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
    # AI-specific packages
    python3Packages.openai
    python3Packages.anthropic
    python3Packages.httpx
    python3Packages.aiohttp
    python3Packages.psutil
    python3Packages.watchdog
    python3Packages.structlog
    python3Packages.pydantic
    python3Packages.typer
  ];
  
  installPhase = ''
    mkdir -p $out
    cp -r . $out/
    chmod +x $out/scripts/*.sh
    
    # Create symlinks for easy access
    mkdir -p $out/bin
    ln -s $out/ai/agent.py $out/bin/nixos-ai
    chmod +x $out/bin/nixos-ai
  '';
  
  meta = {
    description = "NixOS AI Assistant - System-wide smart assistant";
    homepage = "https://github.com/YOURNAME/nixos-ai";
    license = pkgs.lib.licenses.mit;
    maintainers = [ ];
    platforms = pkgs.lib.platforms.linux;
  };
}
