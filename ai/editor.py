"""
File editing engine for NixOS AI Assistant
Provides safe file editing with git snapshots and validation
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

class FileEditor:
    """Safe file editor with git snapshots and validation"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('nixos-ai.editor')
        self.ai_dir = Path(self.config.ai_dir)
        
    def apply_changes(self, file_path: str, changes: List[str]) -> Dict[str, Any]:
        """Apply changes to a file with safety checks"""
        try:
            file_path = Path(file_path).resolve()
            
            # Validate file path
            if not self._is_path_allowed(file_path):
                return {"error": f"Path not allowed: {file_path}"}
            
            # Check if file exists
            if not file_path.exists():
                return {"error": f"File does not exist: {file_path}"}
            
            # Create backup
            backup_path = self._create_backup(file_path)
            
            # Apply changes
            result = self._apply_file_changes(file_path, changes)
            
            if result["success"]:
                # Commit changes if auto-commit is enabled
                if self.config.auto_commit:
                    self._commit_changes(file_path, changes)
                
                return {
                    "success": True,
                    "file": str(file_path),
                    "changes": changes,
                    "backup": str(backup_path)
                }
            else:
                # Restore backup on failure
                self._restore_backup(file_path, backup_path)
                return result
                
        except Exception as e:
            self.logger.error(f"Error applying changes to {file_path}: {e}")
            return {"error": str(e)}
    
    def _is_path_allowed(self, file_path: Path) -> bool:
        """Check if a path is allowed for modification"""
        if self.config.enable_system_wide_access:
            return True
        
        for allowed_path in self.config.allowed_paths:
            try:
                if file_path.is_relative_to(Path(allowed_path).resolve()):
                    return True
            except (ValueError, OSError):
                continue
        
        return False
    
    def _create_backup(self, file_path: Path) -> Path:
        """Create a backup of the file"""
        backup_dir = self.ai_dir / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = Path(file_path).stat().st_mtime
        backup_name = f"{file_path.name}.backup.{int(timestamp)}"
        backup_path = backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        self.logger.info(f"Created backup: {backup_path}")
        
        return backup_path
    
    def _restore_backup(self, file_path: Path, backup_path: Path):
        """Restore file from backup"""
        try:
            shutil.copy2(backup_path, file_path)
            self.logger.info(f"Restored file from backup: {backup_path}")
        except Exception as e:
            self.logger.error(f"Failed to restore backup: {e}")
    
    def _apply_file_changes(self, file_path: Path, changes: List[str]) -> Dict[str, Any]:
        """Apply changes to the file"""
        try:
            # Read current content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply changes based on type
            if self._is_nix_file(file_path):
                new_content = self._apply_nix_changes(content, changes)
            else:
                new_content = self._apply_generic_changes(content, changes)
            
            # Validate changes
            if self.config.validation_required:
                validation_result = self._validate_changes(file_path, new_content)
                if not validation_result["success"]:
                    return validation_result
            
            # Write new content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.logger.info(f"Applied changes to {file_path}")
            return {"success": True}
            
        except Exception as e:
            self.logger.error(f"Error applying changes: {e}")
            return {"error": str(e)}
    
    def _is_nix_file(self, file_path: Path) -> bool:
        """Check if file is a Nix configuration file"""
        return file_path.suffix == '.nix' or 'configuration.nix' in str(file_path)
    
    def _apply_nix_changes(self, content: str, changes: List[str]) -> str:
        """Apply changes to a Nix file"""
        lines = content.split('\n')
        new_lines = []
        
        # Process each change
        for change in changes:
            if change.strip().startswith('#'):
                # Comment - add as is
                new_lines.append(change)
            elif '=' in change and not change.strip().startswith('imports'):
                # Configuration line
                new_lines.append(change)
            elif change.strip().startswith('imports'):
                # Handle imports specially
                new_lines = self._handle_imports(new_lines, change)
            else:
                # Generic line
                new_lines.append(change)
        
        # If no changes were applied, append them
        if not any(change in content for change in changes):
            new_lines.extend(changes)
        
        return '\n'.join(new_lines)
    
    def _handle_imports(self, lines: List[str], import_line: str) -> List[str]:
        """Handle imports in Nix files"""
        # Find existing imports section
        imports_start = -1
        imports_end = -1
        
        for i, line in enumerate(lines):
            if 'imports = [' in line:
                imports_start = i
            elif imports_start != -1 and line.strip() == '];':
                imports_end = i
                break
        
        if imports_start != -1 and imports_end != -1:
            # Add to existing imports
            lines.insert(imports_end, f"  {import_line}")
        else:
            # Create new imports section
            lines.insert(0, f"imports = [ {import_line} ];")
        
        return lines
    
    def _apply_generic_changes(self, content: str, changes: List[str]) -> str:
        """Apply changes to a generic file"""
        lines = content.split('\n')
        
        for change in changes:
            if change not in lines:
                lines.append(change)
        
        return '\n'.join(lines)
    
    def _validate_changes(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Validate changes before applying"""
        if self._is_nix_file(file_path):
            return self._validate_nix_file(content)
        else:
            return {"success": True}  # No validation for non-Nix files
    
    def _validate_nix_file(self, content: str) -> Dict[str, Any]:
        """Validate Nix file syntax"""
        try:
            # Write to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.nix', delete=False) as f:
                f.write(content)
                temp_file = f.name
            
            try:
                # Run nix-instantiate to check syntax
                result = subprocess.run(
                    ['nix-instantiate', '--parse', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    return {"success": True}
                else:
                    return {
                        "success": False,
                        "error": f"Nix syntax error: {result.stderr}"
                    }
            finally:
                os.unlink(temp_file)
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Nix validation timeout"}
        except Exception as e:
            return {"success": False, "error": f"Validation error: {e}"}
    
    def _commit_changes(self, file_path: Path, changes: List[str]):
        """Commit changes to git"""
        try:
            # Change to AI directory
            original_cwd = os.getcwd()
            os.chdir(self.ai_dir)
            
            try:
                # Add file to git
                subprocess.run(['git', 'add', str(file_path)], check=True)
                
                # Commit changes
                commit_message = f"AI: Modified {file_path.name}\n\nChanges:\n" + '\n'.join(f"- {change}" for change in changes)
                subprocess.run(['git', 'commit', '-m', commit_message], check=True)
                
                self.logger.info(f"Committed changes to {file_path}")
            finally:
                os.chdir(original_cwd)
                
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Failed to commit changes: {e}")
        except Exception as e:
            self.logger.error(f"Error committing changes: {e}")
    
    def get_file_content(self, file_path: str) -> Dict[str, Any]:
        """Get content of a file"""
        try:
            file_path = Path(file_path).resolve()
            
            if not self._is_path_allowed(file_path):
                return {"error": f"Path not allowed: {file_path}"}
            
            if not file_path.exists():
                return {"error": f"File does not exist: {file_path}"}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "file": str(file_path)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def list_files(self, directory: str = None) -> Dict[str, Any]:
        """List files in a directory"""
        try:
            if directory is None:
                directory = self.config.ai_dir
            else:
                directory = Path(directory).resolve()
                if not self._is_path_allowed(directory):
                    return {"error": f"Directory not allowed: {directory}"}
            
            files = []
            for file_path in Path(directory).rglob('*'):
                if file_path.is_file():
                    files.append({
                        "path": str(file_path),
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "modified": file_path.stat().st_mtime
                    })
            
            return {
                "success": True,
                "files": files,
                "directory": str(directory)
            }
            
        except Exception as e:
            return {"error": str(e)}
