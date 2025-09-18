#!/usr/bin/env python3
"""
AppImage Helper - Handles fallback installation via AppImage
"""

import subprocess
import logging
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class AppImageHelper:
    def __init__(self):
        self.appimage_dir = Path.home() / 'bin'
        self.appimage_dir.mkdir(exist_ok=True)
        self.desktop_dir = Path.home() / '.local' / 'share' / 'applications'
        self.desktop_dir.mkdir(parents=True, exist_ok=True)

    async def search_package(self, package_name: str) -> Dict[str, Any]:
        """Search for AppImage releases on GitHub"""
        try:
            logger.info(f"Searching for AppImage: {package_name}")
            
            # Search GitHub releases
            search_url = f"https://api.github.com/search/repositories?q={package_name}+AppImage"
            response = requests.get(search_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                repositories = []
                
                for repo in data.get('items', [])[:10]:  # Limit to 10 results
                    # Check if repo has releases
                    releases_url = f"https://api.github.com/repos/{repo['full_name']}/releases"
                    releases_response = requests.get(releases_url, timeout=30)
                    
                    if releases_response.status_code == 200:
                        releases = releases_response.json()
                        for release in releases:
                            for asset in release.get('assets', []):
                                if asset['name'].endswith('.AppImage'):
                                    repositories.append({
                                        'name': repo['name'],
                                        'full_name': repo['full_name'],
                                        'description': repo['description'],
                                        'download_url': asset['browser_download_url'],
                                        'size': asset['size'],
                                        'release_tag': release['tag_name']
                                    })
                                    break
                
                return {
                    'success': True,
                    'packages': repositories,
                    'message': f'Found {len(repositories)} AppImage packages for {package_name}'
                }
            else:
                return {
                    'success': False,
                    'error': f'GitHub API error: {response.status_code}',
                    'output': response.text
                }
                
        except requests.RequestException as e:
            logger.error(f"Error searching for AppImage: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Error searching for AppImage: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def download_appimage(self, download_url: str, package_name: str) -> Dict[str, Any]:
        """Download an AppImage"""
        try:
            logger.info(f"Downloading AppImage: {package_name}")
            
            # Download the AppImage
            response = requests.get(download_url, stream=True, timeout=300)
            response.raise_for_status()
            
            appimage_path = self.appimage_dir / f"{package_name}.AppImage"
            
            with open(appimage_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Make executable
            appimage_path.chmod(0o755)
            
            return {
                'success': True,
                'path': str(appimage_path),
                'message': f'Successfully downloaded {package_name}.AppImage'
            }
            
        except requests.RequestException as e:
            logger.error(f"Error downloading AppImage: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Error downloading AppImage: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def generate_launch_script(self, package_name: str, appimage_path: str) -> str:
        """Generate a launch script for the AppImage"""
        script_content = f"""#!/bin/bash
# Launch script for {package_name} (AppImage)
export APPIMAGE_EXTRACT_AND_RUN=1
exec "{appimage_path}" "$@"
"""
        return script_content

    async def generate_desktop_file(self, package_name: str, appimage_path: str) -> str:
        """Generate a desktop file for the AppImage"""
        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={package_name}
Comment=Launch {package_name} via AppImage
Exec={appimage_path}
Icon=application-x-executable
Terminal=false
Categories=Application;
"""
        return desktop_content

    async def install_package(self, package_name: str, download_url: str) -> Dict[str, Any]:
        """Install an AppImage package"""
        try:
            # Download AppImage
            download_result = await self.download_appimage(download_url, package_name)
            if not download_result['success']:
                return download_result
            
            appimage_path = download_result['path']
            
            # Generate launch script
            launch_script = await self.generate_launch_script(package_name, appimage_path)
            script_path = self.appimage_dir / f"launch-{package_name}.sh"
            with open(script_path, 'w') as f:
                f.write(launch_script)
            script_path.chmod(0o755)
            
            # Generate desktop file
            desktop_file = await self.generate_desktop_file(package_name, appimage_path)
            desktop_path = self.desktop_dir / f"{package_name}.desktop"
            with open(desktop_path, 'w') as f:
                f.write(desktop_file)
            
            return {
                'success': True,
                'appimage_path': appimage_path,
                'script_path': str(script_path),
                'desktop_path': str(desktop_path),
                'message': f'Successfully installed {package_name} as AppImage'
            }
            
        except Exception as e:
            logger.error(f"Error installing AppImage package: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def generate_install_patch(self, package_name: str, appimage_path: str) -> str:
        """Generate a patch to add AppImage support to NixOS config"""
        patch = f"""diff --git a/configuration.nix b/configuration.nix
index 1234567..abcdef0 100644
--- a/configuration.nix
+++ b/configuration.nix
@@ -30,6 +30,7 @@
   environment.systemPackages = with pkgs; [
     firefox
     git
+    # AppImage support for {package_name}
   ];
 
   # ... rest of config
@@ -40,6 +41,12 @@
   # AppImage support
   boot.binfmt.registrations = {{
     appimage = {{
       recognitionType = "magic";
       magicOrExtension = "\\x7fELF\\x02\\x01\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x02\\x00\\x3e\\x00\\x01\\x00\\x00\\x00";
       interpreter = "${{pkgs.appimage-run}}/bin/appimage-run";
     }};
   }};
 }}"""
        
        return patch

    async def is_package_installed(self, package_name: str) -> bool:
        """Check if an AppImage package is installed"""
        appimage_path = self.appimage_dir / f"{package_name}.AppImage"
        return appimage_path.exists()

    async def uninstall_package(self, package_name: str) -> Dict[str, Any]:
        """Uninstall an AppImage package"""
        try:
            # Remove AppImage
            appimage_path = self.appimage_dir / f"{package_name}.AppImage"
            if appimage_path.exists():
                appimage_path.unlink()
            
            # Remove launch script
            script_path = self.appimage_dir / f"launch-{package_name}.sh"
            if script_path.exists():
                script_path.unlink()
            
            # Remove desktop file
            desktop_path = self.desktop_dir / f"{package_name}.desktop"
            if desktop_path.exists():
                desktop_path.unlink()
            
            return {
                'success': True,
                'message': f'Successfully uninstalled {package_name} AppImage'
            }
            
        except Exception as e:
            logger.error(f"Error uninstalling AppImage package: {e}")
            return {
                'success': False,
                'error': str(e)
            }
