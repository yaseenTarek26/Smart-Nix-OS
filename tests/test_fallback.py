#!/usr/bin/env python3
"""
Test suite for the fallback modules
"""

import pytest
from unittest.mock import Mock, patch

from ai_agent.fallback.flatpak_helper import FlatpakHelper
from ai_agent.fallback.appimage_helper import AppImageHelper
from ai_agent.fallback.docker_wrapper import DockerWrapper

class TestFlatpakHelper:
    def setup_method(self):
        """Setup test environment"""
        self.helper = FlatpakHelper()

    @pytest.mark.asyncio
    async def test_search_package_success(self):
        """Test successful package search"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "com.example.app\tExample App\t1.0.0"
            mock_run.return_value.stderr = ""
            
            result = await self.helper.search_package("example")
            assert result['success'] == True
            assert len(result['packages']) > 0

    @pytest.mark.asyncio
    async def test_search_package_failure(self):
        """Test failed package search"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = "No packages found"
            
            result = await self.helper.search_package("nonexistent")
            assert result['success'] == False

    @pytest.mark.asyncio
    async def test_install_package_success(self):
        """Test successful package installation"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Package installed"
            mock_run.return_value.stderr = ""
            
            result = await self.helper.install_package("com.example.app")
            assert result['success'] == True

    @pytest.mark.asyncio
    async def test_install_package_failure(self):
        """Test failed package installation"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = "Installation failed"
            
            result = await self.helper.install_package("com.example.app")
            assert result['success'] == False

    @pytest.mark.asyncio
    async def test_generate_install_patch(self):
        """Test generating install patch"""
        patch_content = await self.helper.generate_install_patch("com.example.app", "Example App")
        assert "services.flatpak.enable = true" in patch_content
        assert "Example App" in patch_content

    @pytest.mark.asyncio
    async def test_generate_launch_script(self):
        """Test generating launch script"""
        script = await self.helper.generate_launch_script("com.example.app", "Example App")
        assert "flatpak run com.example.app" in script
        assert "#!/bin/bash" in script

    @pytest.mark.asyncio
    async def test_generate_desktop_file(self):
        """Test generating desktop file"""
        desktop = await self.helper.generate_desktop_file("com.example.app", "Example App")
        assert "Name=Example App" in desktop
        assert "Exec=flatpak run com.example.app" in desktop

class TestAppImageHelper:
    def setup_method(self):
        """Setup test environment"""
        self.helper = AppImageHelper()

    @pytest.mark.asyncio
    async def test_search_package_success(self):
        """Test successful package search"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'items': [{
                    'name': 'example-app',
                    'full_name': 'user/example-app',
                    'description': 'Example App',
                    'html_url': 'https://github.com/user/example-app'
                }]
            }
            mock_get.return_value = mock_response
            
            result = await self.helper.search_package("example")
            assert result['success'] == True
            assert len(result['packages']) > 0

    @pytest.mark.asyncio
    async def test_search_package_failure(self):
        """Test failed package search"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            result = await self.helper.search_package("nonexistent")
            assert result['success'] == False

    @pytest.mark.asyncio
    async def test_download_appimage_success(self):
        """Test successful AppImage download"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.iter_content.return_value = [b"fake appimage data"]
            mock_get.return_value = mock_response
            
            result = await self.helper.download_appimage("https://example.com/app.AppImage", "example")
            assert result['success'] == True
            assert result['path'].endswith('.AppImage')

    @pytest.mark.asyncio
    async def test_generate_launch_script(self):
        """Test generating launch script"""
        script = await self.helper.generate_launch_script("example", "/path/to/app.AppImage")
        assert "#!/bin/bash" in script
        assert "/path/to/app.AppImage" in script

    @pytest.mark.asyncio
    async def test_generate_desktop_file(self):
        """Test generating desktop file"""
        desktop = await self.helper.generate_desktop_file("example", "/path/to/app.AppImage")
        assert "Name=example" in desktop
        assert "Exec=/path/to/app.AppImage" in desktop

class TestDockerWrapper:
    def setup_method(self):
        """Setup test environment"""
        self.wrapper = DockerWrapper()

    @pytest.mark.asyncio
    async def test_search_package_success(self):
        """Test successful package search"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "example-app\tExample App\t100"
            mock_run.return_value.stderr = ""
            
            result = await self.wrapper.search_package("example")
            assert result['success'] == True
            assert len(result['images']) > 0

    @pytest.mark.asyncio
    async def test_search_package_failure(self):
        """Test failed package search"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = "No images found"
            
            result = await self.wrapper.search_package("nonexistent")
            assert result['success'] == False

    @pytest.mark.asyncio
    async def test_pull_image_success(self):
        """Test successful image pull"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Image pulled"
            mock_run.return_value.stderr = ""
            
            result = await self.wrapper.pull_image("example:latest")
            assert result['success'] == True

    @pytest.mark.asyncio
    async def test_pull_image_failure(self):
        """Test failed image pull"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = "Pull failed"
            
            result = await self.wrapper.pull_image("nonexistent:latest")
            assert result['success'] == False

    @pytest.mark.asyncio
    async def test_generate_run_script(self):
        """Test generating run script"""
        script = await self.wrapper.generate_run_script("example", "example:latest")
        assert "#!/bin/bash" in script
        assert "example:latest" in script

    @pytest.mark.asyncio
    async def test_generate_desktop_file(self):
        """Test generating desktop file"""
        desktop = await self.wrapper.generate_desktop_file("example", "example:latest")
        assert "Name=example" in desktop
        assert "example:latest" in desktop

    @pytest.mark.asyncio
    async def test_generate_install_patch(self):
        """Test generating install patch"""
        patch_content = await self.wrapper.generate_install_patch("example", "example:latest")
        assert "virtualisation.podman.enable = true" in patch_content
        assert "example" in patch_content

if __name__ == "__main__":
    pytest.main([__file__])
