"""
Log watcher for NixOS AI Assistant
Monitors system logs and provides feedback to the AI agent
"""

import os
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
import logging
import json
import time

class LogWatcher:
    """Monitors system logs and provides feedback to the AI agent"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('nixos-ai.watcher')
        self.ai_dir = Path(self.config.ai_dir)
        self.running = False
        self.tasks = []
        
        # Callbacks for different types of events
        self.callbacks = {
            'system_log': [],
            'service_status': [],
            'file_change': [],
            'error': []
        }
    
    async def start(self):
        """Start the log watcher"""
        self.logger.info("Starting log watcher")
        self.running = True
        
        # Start monitoring tasks
        self.tasks = [
            asyncio.create_task(self._watch_system_logs()),
            asyncio.create_task(self._watch_service_status()),
            asyncio.create_task(self._watch_file_changes()),
            asyncio.create_task(self._watch_error_logs())
        ]
        
        # Wait for all tasks
        await asyncio.gather(*self.tasks, return_exceptions=True)
    
    async def stop(self):
        """Stop the log watcher"""
        self.logger.info("Stopping log watcher")
        self.running = False
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)
    
    async def _watch_system_logs(self):
        """Watch system logs for relevant events"""
        try:
            # Use journalctl to follow system logs
            process = await asyncio.create_subprocess_exec(
                'journalctl', '-f', '--no-pager',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            while self.running:
                try:
                    line = await asyncio.wait_for(
                        process.stdout.readline(),
                        timeout=1.0
                    )
                    
                    if line:
                        log_line = line.decode('utf-8', errors='replace').strip()
                        await self._process_system_log(log_line)
                        
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    self.logger.error(f"Error reading system logs: {e}")
                    break
            
        except Exception as e:
            self.logger.error(f"Error starting system log watcher: {e}")
    
    async def _watch_service_status(self):
        """Watch for service status changes"""
        last_status = {}
        
        while self.running:
            try:
                # Get current service status
                result = await asyncio.create_subprocess_exec(
                    'systemctl', 'list-units', '--type=service', '--state=failed',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, _ = await result.communicate()
                current_status = stdout.decode('utf-8', errors='replace')
                
                # Check for changes
                if current_status != last_status.get('content', ''):
                    await self._process_service_status_change(current_status)
                    last_status['content'] = current_status
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error checking service status: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _watch_file_changes(self):
        """Watch for file changes in the AI directory"""
        try:
            # Use inotify to watch for file changes
            process = await asyncio.create_subprocess_exec(
                'inotifywait', '-m', '-r', '-e', 'modify,create,delete',
                str(self.ai_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            while self.running:
                try:
                    line = await asyncio.wait_for(
                        process.stdout.readline(),
                        timeout=1.0
                    )
                    
                    if line:
                        change_line = line.decode('utf-8', errors='replace').strip()
                        await self._process_file_change(change_line)
                        
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    self.logger.error(f"Error reading file changes: {e}")
                    break
            
        except FileNotFoundError:
            # inotifywait not available, use polling instead
            self.logger.warning("inotifywait not available, using polling for file changes")
            await self._watch_file_changes_polling()
        except Exception as e:
            self.logger.error(f"Error starting file change watcher: {e}")
    
    async def _watch_file_changes_polling(self):
        """Fallback file change watcher using polling"""
        last_mtimes = {}
        
        while self.running:
            try:
                current_mtimes = {}
                
                # Check all files in AI directory
                for file_path in self.ai_dir.rglob('*'):
                    if file_path.is_file():
                        current_mtimes[str(file_path)] = file_path.stat().st_mtime
                
                # Check for changes
                for file_path, mtime in current_mtimes.items():
                    if file_path not in last_mtimes or last_mtimes[file_path] != mtime:
                        await self._process_file_change(f"MODIFY {file_path}")
                
                last_mtimes = current_mtimes
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in file change polling: {e}")
                await asyncio.sleep(10)
    
    async def _watch_error_logs(self):
        """Watch for error logs and critical issues"""
        try:
            # Watch for errors in the AI logs
            ai_log_file = self.ai_dir / "logs" / "ai.log"
            
            if ai_log_file.exists():
                process = await asyncio.create_subprocess_exec(
                    'tail', '-f', str(ai_log_file),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                while self.running:
                    try:
                        line = await asyncio.wait_for(
                            process.stdout.readline(),
                            timeout=1.0
                        )
                        
                        if line:
                            log_line = line.decode('utf-8', errors='replace').strip()
                            if 'ERROR' in log_line or 'CRITICAL' in log_line:
                                await self._process_error_log(log_line)
                                
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        self.logger.error(f"Error reading error logs: {e}")
                        break
            
        except Exception as e:
            self.logger.error(f"Error starting error log watcher: {e}")
    
    async def _process_system_log(self, log_line: str):
        """Process a system log line"""
        # Look for relevant events
        if any(keyword in log_line.lower() for keyword in [
            'nixos-rebuild', 'systemctl', 'service', 'docker', 'error', 'failed'
        ]):
            event = {
                'type': 'system_log',
                'content': log_line,
                'timestamp': time.time()
            }
            
            await self._notify_callbacks('system_log', event)
    
    async def _process_service_status_change(self, status: str):
        """Process service status changes"""
        if 'failed' in status.lower():
            event = {
                'type': 'service_status',
                'content': status,
                'timestamp': time.time()
            }
            
            await self._notify_callbacks('service_status', event)
    
    async def _process_file_change(self, change_line: str):
        """Process file change events"""
        event = {
            'type': 'file_change',
            'content': change_line,
            'timestamp': time.time()
        }
        
        await self._notify_callbacks('file_change', event)
    
    async def _process_error_log(self, log_line: str):
        """Process error log events"""
        event = {
            'type': 'error',
            'content': log_line,
            'timestamp': time.time()
        }
        
        await self._notify_callbacks('error', event)
    
    async def _notify_callbacks(self, event_type: str, event: Dict[str, Any]):
        """Notify registered callbacks about an event"""
        for callback in self.callbacks.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                self.logger.error(f"Error in callback: {e}")
    
    def register_callback(self, event_type: str, callback: Callable):
        """Register a callback for a specific event type"""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
        else:
            self.logger.warning(f"Unknown event type: {event_type}")
    
    def unregister_callback(self, event_type: str, callback: Callable):
        """Unregister a callback"""
        if event_type in self.callbacks and callback in self.callbacks[event_type]:
            self.callbacks[event_type].remove(callback)
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get current system health status"""
        try:
            # Check system load
            load_result = await asyncio.create_subprocess_exec(
                'uptime',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            load_stdout, _ = await load_result.communicate()
            
            # Check memory usage
            memory_result = await asyncio.create_subprocess_exec(
                'free', '-h',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            memory_stdout, _ = await memory_result.communicate()
            
            # Check disk usage
            disk_result = await asyncio.create_subprocess_exec(
                'df', '-h', '/',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            disk_stdout, _ = await disk_result.communicate()
            
            return {
                'success': True,
                'load': load_stdout.decode('utf-8', errors='replace').strip(),
                'memory': memory_stdout.decode('utf-8', errors='replace').strip(),
                'disk': disk_stdout.decode('utf-8', errors='replace').strip(),
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': time.time()
            }
    
    async def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent events from all watchers"""
        events = []
        
        try:
            # Get recent system logs
            result = await asyncio.create_subprocess_exec(
                'journalctl', '--no-pager', '-n', str(limit),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            
            for line in stdout.decode('utf-8', errors='replace').split('\n'):
                if line.strip():
                    events.append({
                        'type': 'system_log',
                        'content': line.strip(),
                        'timestamp': time.time()
                    })
            
        except Exception as e:
            self.logger.error(f"Error getting recent events: {e}")
        
        return events[-limit:]  # Return last N events
