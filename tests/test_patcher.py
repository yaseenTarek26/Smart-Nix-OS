#!/usr/bin/env python3
"""
Test suite for the patcher module
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import git

from ai_agent.patcher import Patcher

class TestPatcher:
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'nixos_config_path': self.temp_dir
        }
        self.patcher = Patcher(self.config)
        
        # Create a test Nix file
        self.test_nix_file = Path(self.temp_dir) / "test.nix"
        self.test_nix_file.write_text("""
{ config, pkgs, ... }:
{
  environment.systemPackages = with pkgs; [
    firefox
    git
  ];
}
""")

    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir)

    def test_validate_patch_valid(self):
        """Test validating a valid patch"""
        patch = """diff --git a/test.nix b/test.nix
index 1234567..abcdef0 100644
--- a/test.nix
+++ b/test.nix
@@ -2,6 +2,7 @@
   environment.systemPackages = with pkgs; [
     firefox
     git
+    vscode
   ];
 }"""
        
        result = self.patcher.validate_patch(patch)
        assert result['valid'] == True

    def test_validate_patch_invalid(self):
        """Test validating an invalid patch"""
        patch = "invalid patch content"
        
        result = self.patcher.validate_patch(patch)
        assert result['valid'] == False

    def test_validate_patch_unable_to_generate(self):
        """Test validating UNABLE_TO_GENERATE_PATCH"""
        patch = "UNABLE_TO_GENERATE_PATCH"
        
        result = self.patcher.validate_patch(patch)
        assert result['valid'] == False
        assert 'LLM unable to generate patch' in result['error']

    def test_apply_patch(self):
        """Test applying a valid patch"""
        patch = """diff --git a/test.nix b/test.nix
index 1234567..abcdef0 100644
--- a/test.nix
+++ b/test.nix
@@ -2,6 +2,7 @@
   environment.systemPackages = with pkgs; [
     firefox
     git
+    vscode
   ];
 }"""
        
        result = self.patcher.apply_patch(patch, "Add vscode package")
        assert result['success'] == True
        assert 'commit_hash' in result

    def test_revert_last_commit(self):
        """Test reverting the last commit"""
        # First apply a patch
        patch = """diff --git a/test.nix b/test.nix
index 1234567..abcdef0 100644
--- a/test.nix
+++ b/test.nix
@@ -2,6 +2,7 @@
   environment.systemPackages = with pkgs; [
     firefox
     git
+    vscode
   ];
 }"""
        
        apply_result = self.patcher.apply_patch(patch, "Add vscode package")
        assert apply_result['success'] == True
        
        # Then revert it
        revert_result = self.patcher.revert_last_commit()
        assert revert_result['success'] == True

    def test_get_patch_preview(self):
        """Test getting patch preview"""
        patch = """diff --git a/test.nix b/test.nix
index 1234567..abcdef0 100644
--- a/test.nix
+++ b/test.nix
@@ -2,6 +2,7 @@
   environment.systemPackages = with pkgs; [
     firefox
     git
+    vscode
   ];
 }"""
        
        result = self.patcher.get_patch_preview(patch)
        assert result['success'] == True
        assert 'changes' in result
        assert result['changes']['lines_added'] == 1

    def test_get_git_status(self):
        """Test getting git status"""
        result = self.patcher.get_git_status()
        assert result['success'] == True
        assert 'status' in result

    def test_get_commit_history(self):
        """Test getting commit history"""
        result = self.patcher.get_commit_history(5)
        assert result['success'] == True
        assert 'commits' in result
        assert isinstance(result['commits'], list)

if __name__ == "__main__":
    pytest.main([__file__])
