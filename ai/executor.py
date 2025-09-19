"""
Command executor for NixOS AI Assistant
Provides safe command execution with validation and logging
"""

import os
import subprocess
import asyncio
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import json

class CommandExecutor:
    """Safe command executor with validation and logging"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('nixos-ai.executor')
        self.ai_dir = Path(self.config.ai_dir)
        
        # Commands that require special handling
        self.dangerous_commands = [
            'rm -rf /',
            'dd if=/dev/zero',
            'mkfs',
            'fdisk',
            'parted',
            'wipefs',
            'shutdown',
            'reboot',
            'halt',
            'poweroff'
        ]
        
        # Commands that require validation
        self.validation_commands = [
            'nixos-rebuild',
            'nix-env',
            'systemctl',
            'service',
            'systemd'
        ]
    
    async def run_command(self, command: str, timeout: int = 300) -> Dict[str, Any]:
        """Run a command safely with validation and logging"""
        try:
            self.logger.info(f"Executing command: {command}")
            
            # Check if command is dangerous
            if self._is_dangerous_command(command):
                return {
                    "success": False,
                    "error": "Command is considered dangerous and blocked",
                    "command": command
                }
            
            # Validate command if needed
            if self._requires_validation(command):
                validation_result = await self._validate_command(command)
                if not validation_result["success"]:
                    return validation_result
            
            # Execute command
            result = await self._execute_command(command, timeout)
            
            # Log result
            self._log_command_result(command, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing command '{command}': {e}")
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
    
    def _is_dangerous_command(self, command: str) -> bool:
        """Check if command is potentially dangerous"""
        command_lower = command.lower()
        
        for dangerous in self.dangerous_commands:
            if dangerous in command_lower:
                return True
        
        # Check for patterns that could be dangerous
        dangerous_patterns = [
            'rm -rf',
            'dd if=',
            'mkfs',
            'fdisk',
            'parted',
            'wipefs',
            'shutdown',
            'reboot',
            'halt',
            'poweroff',
            '> /dev/',
            '| sh',
            'curl.*| bash',
            'wget.*| sh'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                return True
        
        return False
    
    def _requires_validation(self, command: str) -> bool:
        """Check if command requires validation"""
        command_lower = command.lower()
        
        for validation_cmd in self.validation_commands:
            if command_lower.startswith(validation_cmd):
                return True
        
        return False
    
    async def _validate_command(self, command: str) -> Dict[str, Any]:
        """Validate a command before execution"""
        command_lower = command.lower()
        
        # Validate NixOS rebuild commands
        if 'nixos-rebuild' in command_lower:
            return await self._validate_nixos_rebuild(command)
        
        # Validate systemctl commands
        elif 'systemctl' in command_lower:
            return await self._validate_systemctl(command)
        
        # Default validation
        return {"success": True}
    
    async def _validate_nixos_rebuild(self, command: str) -> Dict[str, Any]:
        """Validate nixos-rebuild commands"""
        try:
            # Always run test first for switch commands
            if 'switch' in command and 'test' not in command:
                test_command = command.replace('switch', 'test')
                test_result = await self._execute_command(test_command, timeout=600)
                
                if not test_result["success"]:
                    return {
                        "success": False,
                        "error": "NixOS configuration test failed",
                        "test_output": test_result.get("stderr", "")
                    }
            
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": f"Validation error: {e}"}
    
    async def _validate_systemctl(self, command: str) -> Dict[str, Any]:
        """Validate systemctl commands"""
        # Basic validation - could be expanded
        if 'stop' in command and 'nixos-ai' in command:
            return {
                "success": False,
                "error": "Cannot stop the AI assistant service"
            }
        
        return {"success": True}
    
    async def _execute_command(self, command: str, timeout: int) -> Dict[str, Any]:
        """Execute a command and return the result"""
        try:
            # Create log file for command output
            log_file = self.ai_dir / "logs" / f"executor_{int(asyncio.get_event_loop().time())}.log"
            log_file.parent.mkdir(exist_ok=True)
            
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.ai_dir
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            # Decode output
            stdout_text = stdout.decode('utf-8', errors='replace')
            stderr_text = stderr.decode('utf-8', errors='replace')
            
            # Log to file
            with open(log_file, 'w') as f:
                f.write(f"Command: {command}\n")
                f.write(f"Return code: {process.returncode}\n")
                f.write(f"STDOUT:\n{stdout_text}\n")
                f.write(f"STDERR:\n{stderr_text}\n")
            
            return {
                "success": process.returncode == 0,
                "command": command,
                "return_code": process.returncode,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "log_file": str(log_file)
            }
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds",
                "command": command
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
    
    def _log_command_result(self, command: str, result: Dict[str, Any]):
        """Log command result to the main log"""
        if result["success"]:
            self.logger.info(f"Command succeeded: {command}")
        else:
            self.logger.error(f"Command failed: {command} - {result.get('error', 'Unknown error')}")
    
    async def run_commands_sequence(self, commands: List[str]) -> Dict[str, Any]:
        """Run a sequence of commands, stopping on first failure"""
        results = []
        
        for i, command in enumerate(commands):
            result = await self.run_command(command)
            results.append(result)
            
            if not result["success"]:
                return {
                    "success": False,
                    "error": f"Command {i+1} failed: {command}",
                    "results": results
                }
        
        return {
            "success": True,
            "results": results
        }
    
    async def check_system_status(self) -> Dict[str, Any]:
        """Check system status and health"""
        try:
            # Check NixOS configuration
            nixos_result = await self.run_command("nixos-rebuild dry-run")
            
            # Check system services
            services_result = await self.run_command("systemctl list-failed --no-pager")
            
            # Check disk space
            disk_result = await self.run_command("df -h /")
            
            # Check memory
            memory_result = await self.run_command("free -h")
            
            return {
                "success": True,
                "nixos_config": nixos_result,
                "failed_services": services_result,
                "disk_usage": disk_result,
                "memory_usage": memory_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_command_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get command execution history"""
        try:
            log_dir = self.ai_dir / "logs"
            if not log_dir.exists():
                return []
            
            # Get all executor log files
            log_files = sorted(
                log_dir.glob("executor_*.log"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )[:limit]
            
            history = []
            for log_file in log_files:
                try:
                    with open(log_file, 'r') as f:
                        content = f.read()
                    
                    # Parse log file (simple format)
                    lines = content.split('\n')
                    if len(lines) >= 3:
                        history.append({
                            "command": lines[0].replace("Command: ", ""),
                            "return_code": int(lines[1].replace("Return code: ", "")),
                            "timestamp": log_file.stat().st_mtime,
                            "log_file": str(log_file)
                        })
                except Exception as e:
                    self.logger.warning(f"Could not parse log file {log_file}: {e}")
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting command history: {e}")
            return []
