#!/usr/bin/env python3
"""
Test suite for the command executor component
"""

import os
import sys
import asyncio
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

# Add the ai directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai'))

from config import AIConfig
from executor import CommandExecutor

class TestCommandExecutor(unittest.TestCase):
    """Test cases for CommandExecutor"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = Mock()
        self.config.ai_dir = "/tmp/test-ai"
        self.config.allowed_paths = ["/tmp/test-ai"]
        self.config.enable_system_wide_access = False
        self.config.validation_required = True
        self.executor = CommandExecutor(self.config)
    
    def test_dangerous_command_detection(self):
        """Test detection of dangerous commands"""
        dangerous_commands = [
            "rm -rf /",
            "dd if=/dev/zero",
            "mkfs /dev/sda",
            "shutdown -h now",
            "reboot"
        ]
        
        for cmd in dangerous_commands:
            with self.subTest(command=cmd):
                self.assertTrue(self.executor._is_dangerous_command(cmd))
    
    def test_safe_command_detection(self):
        """Test detection of safe commands"""
        safe_commands = [
            "ls -la",
            "cat /etc/hostname",
            "nixos-rebuild test",
            "systemctl status nixos-ai",
            "git status"
        ]
        
        for cmd in safe_commands:
            with self.subTest(command=cmd):
                self.assertFalse(self.executor._is_dangerous_command(cmd))
    
    def test_validation_requirement_detection(self):
        """Test detection of commands requiring validation"""
        validation_commands = [
            "nixos-rebuild switch",
            "nix-env -iA nixos.vscode",
            "systemctl enable docker",
            "systemctl start nixos-ai"
        ]
        
        for cmd in validation_commands:
            with self.subTest(command=cmd):
                self.assertTrue(self.executor._requires_validation(cmd))
    
    def test_simple_command_execution(self):
        """Test execution of simple commands"""
        async def run_test():
            result = await self.executor.run_command("echo 'test'")
            self.assertTrue(result["success"])
            self.assertIn("test", result["stdout"])
        
        asyncio.run(run_test())
    
    def test_command_failure(self):
        """Test handling of command failures"""
        async def run_test():
            result = await self.executor.run_command("nonexistentcommand12345")
            self.assertFalse(result["success"])
            self.assertNotEqual(result["return_code"], 0)
        
        asyncio.run(run_test())
    
    def test_command_timeout(self):
        """Test command timeout handling"""
        async def run_test():
            result = await self.executor.run_command("sleep 10", timeout=1)
            self.assertFalse(result["success"])
            self.assertIn("timeout", result["error"].lower())
        
        asyncio.run(run_test())
    
    @patch('subprocess.run')
    def test_nixos_rebuild_validation(self, mock_run):
        """Test NixOS rebuild validation"""
        # Mock successful test command
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = b"test passed"
        mock_run.return_value.stderr = b""
        
        async def run_test():
            result = await self.executor._validate_nixos_rebuild("nixos-rebuild switch")
            self.assertTrue(result["success"])
        
        asyncio.run(run_test())
    
    def test_command_history(self):
        """Test command history retrieval"""
        # This test would require actual log files, so we'll just test the method exists
        history = self.executor.get_command_history(limit=10)
        self.assertIsInstance(history, list)

if __name__ == "__main__":
    unittest.main()
