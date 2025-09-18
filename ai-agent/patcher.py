#!/usr/bin/env python3
"""
Patcher - Handles patch validation, application, and git operations
"""

import subprocess
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

import git

logger = logging.getLogger(__name__)

class Patcher:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.repo_path = Path(config.get('nixos_config_path', '/etc/nixos'))
        self.repo = self._init_repo()

    def _init_repo(self) -> git.Repo:
        """Initialize git repository"""
        try:
            if not self.repo_path.exists():
                self.repo_path.mkdir(parents=True, exist_ok=True)
            
            if not (self.repo_path / '.git').exists():
                repo = git.Repo.init(self.repo_path)
                # Initial commit
                repo.index.add(['.'])
                repo.index.commit("Initial NixOS configuration")
            else:
                repo = git.Repo(self.repo_path)
            
            return repo
        except Exception as e:
            logger.error(f"Error initializing git repo: {e}")
            raise

    async def validate_patch(self, patch: str) -> Dict[str, Any]:
        """Validate a patch before applying"""
        try:
            if patch == "UNABLE_TO_GENERATE_PATCH":
                return {
                    'valid': False,
                    'error': 'LLM unable to generate patch'
                }
            
            # Check if patch is empty
            if not patch.strip():
                return {
                    'valid': False,
                    'error': 'Empty patch'
                }
            
            # Validate git apply --check
            result = subprocess.run(
                ['git', 'apply', '--check'],
                input=patch,
                text=True,
                cwd=self.repo_path,
                capture_output=True
            )
            
            if result.returncode != 0:
                return {
                    'valid': False,
                    'error': f"Git apply check failed: {result.stderr}"
                }
            
            # Validate Nix syntax
            nix_validation = await self._validate_nix_syntax(patch)
            if not nix_validation['valid']:
                return nix_validation
            
            return {
                'valid': True,
                'message': 'Patch validation successful'
            }
            
        except Exception as e:
            logger.error(f"Error validating patch: {e}")
            return {
                'valid': False,
                'error': str(e)
            }

    async def _validate_nix_syntax(self, patch: str) -> Dict[str, Any]:
        """Validate Nix syntax of the patch"""
        try:
            # Extract file paths from patch
            file_paths = self._extract_file_paths(patch)
            
            for file_path in file_paths:
                full_path = self.repo_path / file_path
                if full_path.exists():
                    # Check Nix syntax
                    result = subprocess.run(
                        ['nix-instantiate', '--parse', str(full_path)],
                        cwd=self.repo_path,
                        capture_output=True
                    )
                    
                    if result.returncode != 0:
                        return {
                            'valid': False,
                            'error': f"Nix syntax error in {file_path}: {result.stderr.decode()}"
                        }
            
            return {
                'valid': True,
                'message': 'Nix syntax validation successful'
            }
            
        except Exception as e:
            logger.error(f"Error validating Nix syntax: {e}")
            return {
                'valid': False,
                'error': str(e)
            }

    def _extract_file_paths(self, patch: str) -> list:
        """Extract file paths from patch"""
        file_paths = []
        for line in patch.split('\n'):
            if line.startswith('diff --git'):
                # Extract file path from diff header
                parts = line.split()
                if len(parts) >= 4:
                    file_path = parts[3][2:]  # Remove 'b/' prefix
                    file_paths.append(file_path)
        return file_paths

    async def apply_patch(self, patch: str, message: str) -> Dict[str, Any]:
        """Apply a validated patch"""
        try:
            # Apply patch
            result = subprocess.run(
                ['git', 'apply'],
                input=patch,
                text=True,
                cwd=self.repo_path,
                capture_output=True
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f"Failed to apply patch: {result.stderr}"
                }
            
            # Add changes to git
            self.repo.index.add(['.'])
            
            # Commit changes
            commit = self.repo.index.commit(f"ai: {message}")
            
            logger.info(f"Applied patch and committed: {commit.hexsha}")
            
            return {
                'success': True,
                'commit_hash': commit.hexsha,
                'message': 'Patch applied successfully'
            }
            
        except Exception as e:
            logger.error(f"Error applying patch: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def revert_last_commit(self) -> Dict[str, Any]:
        """Revert the last commit"""
        try:
            # Get last commit
            last_commit = self.repo.head.commit
            
            # Revert
            self.repo.git.revert('HEAD', '--no-edit')
            
            logger.info(f"Reverted commit: {last_commit.hexsha}")
            
            return {
                'success': True,
                'message': f'Reverted commit: {last_commit.hexsha}'
            }
            
        except Exception as e:
            logger.error(f"Error reverting commit: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_patch_preview(self, patch: str) -> Dict[str, Any]:
        """Get a preview of what the patch will change"""
        try:
            # Parse patch to extract changes
            changes = self._parse_patch_changes(patch)
            
            return {
                'success': True,
                'changes': changes,
                'message': 'Patch preview generated'
            }
            
        except Exception as e:
            logger.error(f"Error generating patch preview: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _parse_patch_changes(self, patch: str) -> Dict[str, Any]:
        """Parse patch to extract changes"""
        changes = {
            'files_modified': [],
            'lines_added': 0,
            'lines_removed': 0,
            'summary': ''
        }
        
        current_file = None
        for line in patch.split('\n'):
            if line.startswith('diff --git'):
                # Extract filename
                parts = line.split()
                if len(parts) >= 4:
                    current_file = parts[3][2:]  # Remove 'b/' prefix
                    changes['files_modified'].append(current_file)
            elif line.startswith('+') and not line.startswith('+++'):
                changes['lines_added'] += 1
            elif line.startswith('-') and not line.startswith('---'):
                changes['lines_removed'] += 1
        
        # Generate summary
        if changes['files_modified']:
            changes['summary'] = f"Modified {len(changes['files_modified'])} files: {', '.join(changes['files_modified'])}"
        
        return changes

    async def get_git_status(self) -> Dict[str, Any]:
        """Get current git status"""
        try:
            status = self.repo.git.status('--porcelain')
            return {
                'success': True,
                'status': status,
                'message': 'Git status retrieved'
            }
        except Exception as e:
            logger.error(f"Error getting git status: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_commit_history(self, limit: int = 10) -> Dict[str, Any]:
        """Get recent commit history"""
        try:
            commits = list(self.repo.iter_commits(max_count=limit))
            commit_list = []
            
            for commit in commits:
                commit_list.append({
                    'hash': commit.hexsha[:8],
                    'message': commit.message.strip(),
                    'author': commit.author.name,
                    'date': commit.committed_datetime.isoformat()
                })
            
            return {
                'success': True,
                'commits': commit_list,
                'message': 'Commit history retrieved'
            }
            
        except Exception as e:
            logger.error(f"Error getting commit history: {e}")
            return {
                'success': False,
                'error': str(e)
            }
