#!/usr/bin/env python3
"""
NixOS AI Agent - Main daemon for chat, patch generation, and system management
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from decision_engine import DecisionEngine
from llm_adapter import LLMAdapter
from patcher import Patcher
from executor import Executor
from fallback.flatpak_helper import FlatpakHelper
from fallback.appimage_helper import AppImageHelper
from fallback.docker_wrapper import DockerWrapper
from webui import WebUI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/nixos-agent/agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NixOSAIAgent:
    def __init__(self):
        self.config = self._load_config()
        self.decision_engine = DecisionEngine()
        self.llm_adapter = LLMAdapter(self.config)
        self.patcher = Patcher(self.config)
        self.executor = Executor(self.config)
        self.flatpak_helper = FlatpakHelper()
        self.appimage_helper = AppImageHelper()
        self.docker_wrapper = DockerWrapper()
        self.webui = WebUI(self)
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment and files"""
        config = {
            'llm_provider': os.getenv('LLM_PROVIDER', 'openai'),
            'api_key': os.getenv('OPENAI_API_KEY', ''),
            'port': int(os.getenv('AI_AGENT_PORT', '8999')),
            'nixos_config_path': os.getenv('NIXOS_CONFIG_PATH', '/etc/nixos'),
            'cache_dir': os.getenv('CACHE_DIR', '/var/lib/nixos-agent/cache'),
            'log_dir': os.getenv('LOG_DIR', '/var/log/nixos-agent'),
        }
        
        # Load from .env file if exists
        env_file = Path('/etc/nixos-agent/.env')
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key.lower()] = value
        
        return config

    async def process_message(self, message: str, user_id: str = "default") -> Dict[str, Any]:
        """Process a user message and return response"""
        try:
            logger.info(f"Processing message from {user_id}: {message}")
            
            # Classify intent
            intent = await self.decision_engine.classify_intent(message)
            logger.info(f"Classified intent: {intent}")
            
            response = {
                'intent': intent,
                'message': message,
                'user_id': user_id,
                'status': 'success'
            }
            
            if intent['type'] == 'declarative':
                result = await self._handle_declarative(intent, message)
                response.update(result)
            elif intent['type'] == 'imperative':
                result = await self._handle_imperative(intent, message)
                response.update(result)
            elif intent['type'] == 'hybrid':
                result = await self._handle_hybrid(intent, message)
                response.update(result)
            else:
                response['status'] = 'error'
                response['error'] = f"Unknown intent type: {intent['type']}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                'intent': {'type': 'error'},
                'message': message,
                'user_id': user_id,
                'status': 'error',
                'error': str(e)
            }

    async def _handle_declarative(self, intent: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Handle declarative config changes"""
        try:
            # Generate patch
            patch = await self.llm_adapter.generate_patch(
                target_files=intent.get('target_files', []),
                instruction=message,
                context=intent.get('context', {})
            )
            
            if patch == "UNABLE_TO_GENERATE_PATCH":
                return {
                    'status': 'error',
                    'error': 'Unable to generate patch for this request'
                }
            
            # Validate and apply patch
            validation_result = await self.patcher.validate_patch(patch)
            if not validation_result['valid']:
                return {
                    'status': 'error',
                    'error': f"Patch validation failed: {validation_result['error']}"
                }
            
            # Apply patch
            apply_result = await self.patcher.apply_patch(patch, message)
            if not apply_result['success']:
                return {
                    'status': 'error',
                    'error': f"Patch application failed: {apply_result['error']}"
                }
            
            # Test build
            build_result = await self.executor.test_build()
            if not build_result['success']:
                # Revert patch
                await self.patcher.revert_last_commit()
                return {
                    'status': 'error',
                    'error': f"Build failed: {build_result['error']}",
                    'suggestion': 'Consider using fallback installation methods'
                }
            
            return {
                'status': 'success',
                'patch': patch,
                'commit_hash': apply_result['commit_hash'],
                'message': 'Configuration updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error in declarative handling: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    async def _handle_imperative(self, intent: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Handle immediate commands"""
        try:
            command = intent.get('command', message)
            result = await self.executor.run_command(command)
            
            return {
                'status': 'success' if result['success'] else 'error',
                'output': result['output'],
                'error': result.get('error', ''),
                'message': f"Executed: {command}"
            }
            
        except Exception as e:
            logger.error(f"Error in imperative handling: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    async def _handle_hybrid(self, intent: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Handle hybrid declarative + imperative"""
        try:
            # First handle declarative part
            declarative_result = await self._handle_declarative(intent, message)
            
            if declarative_result['status'] != 'success':
                return declarative_result
            
            # Then handle imperative part
            imperative_result = await self._handle_imperative(intent, message)
            
            return {
                'status': 'success',
                'declarative': declarative_result,
                'imperative': imperative_result,
                'message': 'Both declarative and imperative actions completed'
            }
            
        except Exception as e:
            logger.error(f"Error in hybrid handling: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    async def start(self):
        """Start the AI agent"""
        logger.info("Starting NixOS AI Agent...")
        
        # Ensure directories exist
        os.makedirs(self.config['cache_dir'], exist_ok=True)
        os.makedirs(self.config['log_dir'], exist_ok=True)
        
        # Start web UI
        await self.webui.start()
        
        logger.info("NixOS AI Agent started successfully")

    async def stop(self):
        """Stop the AI agent"""
        logger.info("Stopping NixOS AI Agent...")
        await self.webui.stop()
        logger.info("NixOS AI Agent stopped")

async def main():
    """Main entry point"""
    agent = NixOSAIAgent()
    
    try:
        await agent.start()
        # Keep running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
