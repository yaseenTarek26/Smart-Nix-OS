#!/usr/bin/env python3
"""
Flatpak Helper - Handles fallback installation via Flatpak
"""

import subprocess
import logging
import json
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class FlatpakHelper:
    def __init__(self):
        self.flatpak_installed = self._check_flatpak_installed()

    def _check_flatpak_installed(self) -> bool:
        """Check if flatpak is installed and available"""
        try:
            result = subprocess.run(['flatpak', '--version'], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    async def search_package(self, package_name: str) -> Dict[str, Any]:
        """Search for a package in Flathub"""
        try:
            if not self.flatpak_installed:
                return {
                    'success': False,
                    'error': 'Flatpak is not installed'
                }
            
            logger.info(f"Searching Flatpak for: {package_name}")
            
            # Search in Flathub
            result = subprocess.run(
                ['flatpak', 'search', package_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                packages = self._parse_search_results(result.stdout)
                return {
                    'success': True,
                    'packages': packages,
                    'message': f'Found {len(packages)} packages matching {package_name}'
                }
            else:
                return {
                    'success': False,
                    'error': f'No Flatpak packages found for {package_name}',
                    'output': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Flatpak search timed out'
            }
        except Exception as e:
            logger.error(f"Error searching Flatpak: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _parse_search_results(self, output: str) -> List[Dict[str, str]]:
        """Parse flatpak search results"""
        packages = []
        lines = output.strip().split('\n')
        
        for line in lines[1:]:  # Skip header
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 3:
                    packages.append({
                        'name': parts[0].strip(),
                        'description': parts[1].strip(),
                        'version': parts[2].strip()
                    })
        
        return packages

    async def install_package(self, package_id: str) -> Dict[str, Any]:
        """Install a Flatpak package"""
        try:
            if not self.flatpak_installed:
                return {
                    'success': False,
                    'error': 'Flatpak is not installed'
                }
            
            logger.info(f"Installing Flatpak package: {package_id}")
            
            # Install package
            result = subprocess.run(
                ['flatpak', 'install', '--noninteractive', '--yes', 'flathub', package_id],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'output': result.stdout,
                    'message': f'Successfully installed {package_id} via Flatpak'
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr,
                    'output': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Flatpak installation timed out'
            }
        except Exception as e:
            logger.error(f"Error installing Flatpak package: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def generate_install_patch(self, package_id: str, package_name: str) -> str:
        """Generate a patch to install Flatpak package declaratively"""
        patch = f"""diff --git a/configuration.nix b/configuration.nix
index 1234567..abcdef0 100644
--- a/configuration.nix
+++ b/configuration.nix
@@ -20,6 +20,8 @@
   services.xserver.enable = true;
 
+  # Enable Flatpak for {package_name}
+  services.flatpak.enable = true;
+
   # ... rest of config
 }}
 
@@ -30,6 +32,7 @@
   environment.systemPackages = with pkgs; [
     firefox
     git
+    flatpak
   ];
 }}"""
        
        return patch

    async def generate_launch_script(self, package_id: str, package_name: str) -> str:
        """Generate a launch script for the Flatpak package"""
        script_content = f"""#!/bin/bash
# Launch script for {package_name} (Flatpak)
flatpak run {package_id} "$@"
"""
        return script_content

    async def generate_desktop_file(self, package_id: str, package_name: str) -> str:
        """Generate a desktop file for the Flatpak package"""
        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={package_name}
Comment=Launch {package_name} via Flatpak
Exec=flatpak run {package_id}
Icon=application-x-executable
Terminal=false
Categories=Application;
"""
        return desktop_content

    async def is_package_installed(self, package_id: str) -> bool:
        """Check if a Flatpak package is installed"""
        try:
            result = subprocess.run(
                ['flatpak', 'list', '--app', '--columns=application'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return package_id in result.stdout
            return False
            
        except Exception as e:
            logger.error(f"Error checking if package is installed: {e}")
            return False

    async def uninstall_package(self, package_id: str) -> Dict[str, Any]:
        """Uninstall a Flatpak package"""
        try:
            if not self.flatpak_installed:
                return {
                    'success': False,
                    'error': 'Flatpak is not installed'
                }
            
            logger.info(f"Uninstalling Flatpak package: {package_id}")
            
            result = subprocess.run(
                ['flatpak', 'uninstall', '--noninteractive', '--yes', package_id],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'output': result.stdout,
                    'message': f'Successfully uninstalled {package_id}'
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr,
                    'output': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Flatpak uninstallation timed out'
            }
        except Exception as e:
            logger.error(f"Error uninstalling Flatpak package: {e}")
            return {
                'success': False,
                'error': str(e)
            }
