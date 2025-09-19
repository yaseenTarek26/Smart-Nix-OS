#!/usr/bin/env python3
"""
Test suite for the file editor component
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

# Add the ai directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai'))

from config import AIConfig
from editor import FileEditor

class TestFileEditor(unittest.TestCase):
    """Test cases for FileEditor"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.config = Mock()
        self.config.ai_dir = self.test_dir
        self.config.allowed_paths = [self.test_dir]
        self.config.enable_system_wide_access = False
        self.config.auto_commit = False
        self.config.validation_required = True
        self.editor = FileEditor(self.config)
        
        # Create a test file
        self.test_file = Path(self.test_dir) / "test.nix"
        self.test_file.write_text("services.docker.enable = true;\n")
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_file_reading(self):
        """Test reading file content"""
        result = self.editor.get_file_content(str(self.test_file))
        self.assertTrue(result["success"])
        self.assertIn("services.docker.enable = true", result["content"])
    
    def test_file_editing(self):
        """Test editing file content"""
        changes = ["services.vscode.enable = true;"]
        result = self.editor.apply_changes(str(self.test_file), changes)
        self.assertTrue(result["success"])
        
        # Check if changes were applied
        content = self.test_file.read_text()
        self.assertIn("services.vscode.enable = true", content)
    
    def test_path_validation(self):
        """Test path validation"""
        # Test allowed path
        result = self.editor._is_path_allowed(self.test_file)
        self.assertTrue(result)
        
        # Test forbidden path
        forbidden_path = Path("/etc/passwd")
        result = self.editor._is_path_allowed(forbidden_path)
        self.assertFalse(result)
    
    def test_nix_file_detection(self):
        """Test Nix file detection"""
        self.assertTrue(self.editor._is_nix_file(self.test_file))
        
        # Test non-Nix file
        txt_file = Path(self.test_dir) / "test.txt"
        txt_file.write_text("test")
        self.assertFalse(self.editor._is_nix_file(txt_file))
    
    def test_backup_creation(self):
        """Test backup creation"""
        backup_path = self.editor._create_backup(self.test_file)
        self.assertTrue(backup_path.exists())
        self.assertEqual(backup_path.read_text(), self.test_file.read_text())
    
    def test_file_listing(self):
        """Test file listing"""
        result = self.editor.list_files(self.test_dir)
        self.assertTrue(result["success"])
        self.assertGreater(len(result["files"]), 0)
        
        # Check if our test file is in the list
        file_names = [f["name"] for f in result["files"]]
        self.assertIn("test.nix", file_names)

if __name__ == "__main__":
    unittest.main()
