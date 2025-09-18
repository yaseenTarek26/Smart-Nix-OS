#!/usr/bin/env python3
"""
Test suite for the executor module
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from ai_agent.executor import Executor

class TestExecutor:
    def setup_method(self):
        """Setup test environment"""
        self.config = {
            'nixos_config_path': '/etc/nixos'
        }
        self.executor = Executor(self.config)

    @pytest.mark.asyncio
    async def test_run_command_success(self):
        """Test running a successful command"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Success"
            mock_run.return_value.stderr = ""
            
            result = await self.executor.run_command("echo 'test'")
            assert result['success'] == True
            assert result['output'] == "Success"

    @pytest.mark.asyncio
    async def test_run_command_failure(self):
        """Test running a failed command"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = "Error"
            
            result = await self.executor.run_command("invalid-command")
            assert result['success'] == False
            assert result['error'] == "Error"

    @pytest.mark.asyncio
    async def test_run_command_timeout(self):
        """Test command timeout"""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("test", 1)
            
            result = await self.executor.run_command("sleep 10")
            assert result['success'] == False
            assert 'timed out' in result['error']

    @pytest.mark.asyncio
    async def test_test_build_success(self):
        """Test successful build"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Build successful"
            mock_run.return_value.stderr = ""
            
            result = await self.executor.test_build()
            assert result['success'] == True
            assert "Build successful" in result['output']

    @pytest.mark.asyncio
    async def test_test_build_failure(self):
        """Test failed build"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = "Build failed"
            
            result = await self.executor.test_build()
            assert result['success'] == False
            assert "Build failed" in result['error']

    @pytest.mark.asyncio
    async def test_switch_configuration_success(self):
        """Test successful configuration switch"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Switch successful"
            mock_run.return_value.stderr = ""
            
            result = await self.executor.switch_configuration()
            assert result['success'] == True
            assert "Switch successful" in result['output']

    @pytest.mark.asyncio
    async def test_open_app_success(self):
        """Test successful app opening"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "App opened"
            mock_run.return_value.stderr = ""
            
            result = await self.executor.open_app("firefox")
            assert result['success'] == True

    @pytest.mark.asyncio
    async def test_open_app_failure(self):
        """Test failed app opening"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = "App not found"
            
            result = await self.executor.open_app("nonexistent-app")
            assert result['success'] == False

    @pytest.mark.asyncio
    async def test_search_package_success(self):
        """Test successful package search"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "firefox firefox-123.0"
            mock_run.return_value.stderr = ""
            
            result = await self.executor.search_package("firefox")
            assert result['success'] == True
            assert "firefox" in result['output']

    @pytest.mark.asyncio
    async def test_search_package_failure(self):
        """Test failed package search"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = "No packages found"
            
            result = await self.executor.search_package("nonexistent-package")
            assert result['success'] == False

    @pytest.mark.asyncio
    async def test_get_system_info(self):
        """Test getting system information"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "NixOS 23.11"
            mock_run.return_value.stderr = ""
            
            result = await self.executor.get_system_info()
            assert result['success'] == True
            assert 'info' in result

    @pytest.mark.asyncio
    async def test_restart_service_success(self):
        """Test successful service restart"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Service restarted"
            mock_run.return_value.stderr = ""
            
            result = await self.executor.restart_service("nixos-agent")
            assert result['success'] == True

    @pytest.mark.asyncio
    async def test_restart_service_failure(self):
        """Test failed service restart"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = "Service not found"
            
            result = await self.executor.restart_service("nonexistent-service")
            assert result['success'] == False

if __name__ == "__main__":
    pytest.main([__file__])
