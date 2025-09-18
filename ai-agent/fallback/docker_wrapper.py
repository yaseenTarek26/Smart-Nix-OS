#!/usr/bin/env python3
"""
Docker Wrapper - Handles fallback installation via Docker/Podman
"""

import subprocess
import logging
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class DockerWrapper:
    def __init__(self):
        self.docker_available = self._check_docker_available()
        self.scripts_dir = Path.home() / 'bin'
        self.scripts_dir.mkdir(exist_ok=True)
        self.desktop_dir = Path.home() / '.local' / 'share' / 'applications'
        self.desktop_dir.mkdir(parents=True, exist_ok=True)

    def _check_docker_available(self) -> bool:
        """Check if Docker or Podman is available"""
        try:
            # Try podman first (preferred on NixOS)
            result = subprocess.run(['podman', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.docker_command = 'podman'
                return True
            
            # Try docker as fallback
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.docker_command = 'docker'
                return True
            
            return False
        except FileNotFoundError:
            return False

    async def search_package(self, package_name: str) -> Dict[str, Any]:
        """Search for Docker images on Docker Hub"""
        try:
            if not self.docker_available:
                return {
                    'success': False,
                    'error': 'Docker/Podman is not available'
                }
            
            logger.info(f"Searching Docker Hub for: {package_name}")
            
            # Search Docker Hub
            result = subprocess.run(
                [self.docker_command, 'search', package_name, '--limit', '10'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                images = self._parse_search_results(result.stdout)
                return {
                    'success': True,
                    'images': images,
                    'message': f'Found {len(images)} Docker images for {package_name}'
                }
            else:
                return {
                    'success': False,
                    'error': f'No Docker images found for {package_name}',
                    'output': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Docker search timed out'
            }
        except Exception as e:
            logger.error(f"Error searching Docker: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _parse_search_results(self, output: str) -> List[Dict[str, str]]:
        """Parse docker search results"""
        images = []
        lines = output.strip().split('\n')
        
        for line in lines[1:]:  # Skip header
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    images.append({
                        'name': parts[0],
                        'description': ' '.join(parts[1:]) if len(parts) > 1 else '',
                        'stars': parts[-1] if parts[-1].isdigit() else '0'
                    })
        
        return images

    async def pull_image(self, image_name: str) -> Dict[str, Any]:
        """Pull a Docker image"""
        try:
            if not self.docker_available:
                return {
                    'success': False,
                    'error': 'Docker/Podman is not available'
                }
            
            logger.info(f"Pulling Docker image: {image_name}")
            
            result = subprocess.run(
                [self.docker_command, 'pull', image_name],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'output': result.stdout,
                    'message': f'Successfully pulled {image_name}'
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
                'error': 'Docker pull timed out'
            }
        except Exception as e:
            logger.error(f"Error pulling Docker image: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def generate_run_script(self, package_name: str, image_name: str) -> str:
        """Generate a run script for the Docker container"""
        script_content = f"""#!/bin/bash
# Run script for {package_name} (Docker)
# This script runs {package_name} in a Docker container with GUI support

# Get display
DISPLAY=${{DISPLAY:-:0}}

# Run container with GUI support
{self.docker_command} run --rm -it \\
  --net=host \\
  -e DISPLAY=$DISPLAY \\
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \\
  -v $HOME:$HOME \\
  -v /dev/dri:/dev/dri \\
  --device /dev/dri \\
  --security-opt seccomp=unconfined \\
  {image_name} "$@"
"""
        return script_content

    async def generate_desktop_file(self, package_name: str, image_name: str) -> str:
        """Generate a desktop file for the Docker container"""
        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={package_name}
Comment=Launch {package_name} via Docker
Exec={self.scripts_dir}/run-{package_name}.sh
Icon=application-x-executable
Terminal=false
Categories=Application;
"""
        return desktop_content

    async def install_package(self, package_name: str, image_name: str) -> Dict[str, Any]:
        """Install a Docker package"""
        try:
            if not self.docker_available:
                return {
                    'success': False,
                    'error': 'Docker/Podman is not available'
                }
            
            # Pull image
            pull_result = await self.pull_image(image_name)
            if not pull_result['success']:
                return pull_result
            
            # Generate run script
            run_script = await self.generate_run_script(package_name, image_name)
            script_path = self.scripts_dir / f"run-{package_name}.sh"
            with open(script_path, 'w') as f:
                f.write(run_script)
            script_path.chmod(0o755)
            
            # Generate desktop file
            desktop_file = await self.generate_desktop_file(package_name, image_name)
            desktop_path = self.desktop_dir / f"{package_name}.desktop"
            with open(desktop_path, 'w') as f:
                f.write(desktop_file)
            
            return {
                'success': True,
                'image_name': image_name,
                'script_path': str(script_path),
                'desktop_path': str(desktop_path),
                'message': f'Successfully installed {package_name} via Docker'
            }
            
        except Exception as e:
            logger.error(f"Error installing Docker package: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def generate_install_patch(self, package_name: str, image_name: str) -> str:
        """Generate a patch to add Docker support to NixOS config"""
        patch = f"""diff --git a/configuration.nix b/configuration.nix
index 1234567..abcdef0 100644
--- a/configuration.nix
+++ b/configuration.nix
@@ -30,6 +30,7 @@
   environment.systemPackages = with pkgs; [
     firefox
     git
+    # Docker support for {package_name}
   ];
 
   # ... rest of config
@@ -40,6 +41,8 @@
   # Docker support
   virtualisation.podman.enable = true;
   virtualisation.podman.dockerCompat = true;
+  
+  # X11 forwarding for Docker GUI apps
+  services.xserver.enable = true;
 }}"""
        
        return patch

    async def is_package_installed(self, package_name: str) -> bool:
        """Check if a Docker package is installed"""
        script_path = self.scripts_dir / f"run-{package_name}.sh"
        return script_path.exists()

    async def uninstall_package(self, package_name: str) -> Dict[str, Any]:
        """Uninstall a Docker package"""
        try:
            # Remove run script
            script_path = self.scripts_dir / f"run-{package_name}.sh"
            if script_path.exists():
                script_path.unlink()
            
            # Remove desktop file
            desktop_path = self.desktop_dir / f"{package_name}.desktop"
            if desktop_path.exists():
                desktop_path.unlink()
            
            return {
                'success': True,
                'message': f'Successfully uninstalled {package_name} Docker wrapper'
            }
            
        except Exception as e:
            logger.error(f"Error uninstalling Docker package: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def run_container(self, image_name: str, command: str = None) -> Dict[str, Any]:
        """Run a Docker container"""
        try:
            if not self.docker_available:
                return {
                    'success': False,
                    'error': 'Docker/Podman is not available'
                }
            
            # Build run command
            run_cmd = [self.docker_command, 'run', '--rm', '-it']
            
            # Add GUI support
            run_cmd.extend([
                '--net=host',
                '-e', f'DISPLAY={os.getenv("DISPLAY", ":0")}',
                '-v', '/tmp/.X11-unix:/tmp/.X11-unix:rw',
                '-v', f'{Path.home()}:{Path.home()}',
                '-v', '/dev/dri:/dev/dri',
                '--device', '/dev/dri',
                '--security-opt', 'seccomp=unconfined'
            ])
            
            # Add image and command
            run_cmd.append(image_name)
            if command:
                run_cmd.append(command)
            
            # Run container
            result = subprocess.run(
                run_cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Container run timed out'
            }
        except Exception as e:
            logger.error(f"Error running container: {e}")
            return {
                'success': False,
                'error': str(e)
            }
