#!/usr/bin/env python3
"""
Executor - Handles command execution and system operations
"""

import subprocess
import logging
import os
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class Executor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.nixos_config_path = config.get('nixos_config_path', '/etc/nixos')

    async def run_command(self, command: str, user: bool = False) -> Dict[str, Any]:
        """Run a command safely"""
        try:
            logger.info(f"Running command: {command}")
            
            # Determine if command should run as user or system
            if user:
                result = await self._run_user_command(command)
            else:
                result = await self._run_system_command(command)
            
            return result
            
        except Exception as e:
            logger.error(f"Error running command: {e}")
            return {
                'success': False,
                'error': str(e),
                'output': ''
            }

    async def _run_user_command(self, command: str) -> Dict[str, Any]:
        """Run command as regular user"""
        try:
            # Get current user
            user = os.getenv('USER', 'nixos')
            
            # Run command
            result = subprocess.run(
                command,
                shell=True,
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
                'error': 'Command timed out',
                'output': ''
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'output': ''
            }

    async def _run_system_command(self, command: str) -> Dict[str, Any]:
        """Run command with sudo privileges"""
        try:
            # Add sudo to command
            sudo_command = f"sudo {command}"
            
            result = subprocess.run(
                sudo_command,
                shell=True,
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
                'error': 'Command timed out',
                'output': ''
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'output': ''
            }

    async def test_build(self) -> Dict[str, Any]:
        """Test NixOS configuration build"""
        try:
            logger.info("Testing NixOS configuration build")
            
            result = subprocess.run(
                ['nixos-rebuild', 'test', '--flake', f'{self.nixos_config_path}#desktop'],
                cwd=self.nixos_config_path,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            if result.returncode == 0:
                logger.info("Build test successful")
                return {
                    'success': True,
                    'output': result.stdout,
                    'message': 'Configuration build successful'
                }
            else:
                logger.error(f"Build test failed: {result.stderr}")
                return {
                    'success': False,
                    'error': result.stderr,
                    'output': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            logger.error("Build test timed out")
            return {
                'success': False,
                'error': 'Build test timed out after 30 minutes'
            }
        except Exception as e:
            logger.error(f"Error testing build: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def switch_configuration(self) -> Dict[str, Any]:
        """Switch to the new NixOS configuration"""
        try:
            logger.info("Switching NixOS configuration")
            
            result = subprocess.run(
                ['nixos-rebuild', 'switch', '--flake', f'{self.nixos_config_path}#desktop'],
                cwd=self.nixos_config_path,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            if result.returncode == 0:
                logger.info("Configuration switch successful")
                return {
                    'success': True,
                    'output': result.stdout,
                    'message': 'Configuration switched successfully'
                }
            else:
                logger.error(f"Configuration switch failed: {result.stderr}")
                return {
                    'success': False,
                    'error': result.stderr,
                    'output': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            logger.error("Configuration switch timed out")
            return {
                'success': False,
                'error': 'Configuration switch timed out after 30 minutes'
            }
        except Exception as e:
            logger.error(f"Error switching configuration: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def open_app(self, app_name: str) -> Dict[str, Any]:
        """Open an application"""
        try:
            logger.info(f"Opening application: {app_name}")
            
            # Try different methods to find and launch the app
            launch_methods = [
                f"which {app_name} && {app_name}",
                f"flatpak run {app_name}",
                f"flatpak run com.{app_name}",
                f"flatpak run org.{app_name}",
                f"nix run nixpkgs#{app_name}",
                f"nix run nixpkgs#{app_name}-unstable"
            ]
            
            for method in launch_methods:
                result = await self.run_command(method, user=True)
                if result['success']:
                    return {
                        'success': True,
                        'output': result['output'],
                        'message': f'Opened {app_name} successfully'
                    }
            
            # If no method worked, try to find the app
            find_result = await self.run_command(f"find /nix/store -name '*{app_name}*' -type f -executable | head -1", user=True)
            if find_result['success'] and find_result['output'].strip():
                app_path = find_result['output'].strip()
                launch_result = await self.run_command(f"{app_path} &", user=True)
                if launch_result['success']:
                    return {
                        'success': True,
                        'output': launch_result['output'],
                        'message': f'Opened {app_name} from {app_path}'
                    }
            
            return {
                'success': False,
                'error': f'Could not find or launch {app_name}',
                'suggestion': 'Try installing the package first or check if it\'s available via flatpak'
            }
            
        except Exception as e:
            logger.error(f"Error opening app {app_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def search_package(self, package_name: str) -> Dict[str, Any]:
        """Search for a package in NixOS repositories"""
        try:
            logger.info(f"Searching for package: {package_name}")
            
            # Search in nixpkgs
            result = subprocess.run(
                ['nix', 'search', 'nixpkgs', package_name],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'output': result.stdout,
                    'message': f'Found packages matching {package_name}'
                }
            else:
                return {
                    'success': False,
                    'error': f'No packages found matching {package_name}',
                    'output': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Package search timed out'
            }
        except Exception as e:
            logger.error(f"Error searching for package: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            info = {}
            
            # Get NixOS version
            nixos_result = await self.run_command("nixos-version", user=True)
            if nixos_result['success']:
                info['nixos_version'] = nixos_result['output'].strip()
            
            # Get kernel version
            kernel_result = await self.run_command("uname -r", user=True)
            if kernel_result['success']:
                info['kernel_version'] = kernel_result['output'].strip()
            
            # Get available memory
            memory_result = await self.run_command("free -h", user=True)
            if memory_result['success']:
                info['memory'] = memory_result['output'].strip()
            
            # Get disk usage
            disk_result = await self.run_command("df -h", user=True)
            if disk_result['success']:
                info['disk_usage'] = disk_result['output'].strip()
            
            return {
                'success': True,
                'info': info,
                'message': 'System information retrieved'
            }
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def restart_service(self, service_name: str) -> Dict[str, Any]:
        """Restart a systemd service"""
        try:
            logger.info(f"Restarting service: {service_name}")
            
            result = await self.run_command(f"systemctl restart {service_name}")
            
            if result['success']:
                return {
                    'success': True,
                    'output': result['output'],
                    'message': f'Service {service_name} restarted successfully'
                }
            else:
                return {
                    'success': False,
                    'error': result['error'],
                    'output': result['output']
                }
                
        except Exception as e:
            logger.error(f"Error restarting service: {e}")
            return {
                'success': False,
                'error': str(e)
            }
