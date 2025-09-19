#!/usr/bin/env python3
"""
NixOS AI Assistant - Main Agent
Natural language interface for managing NixOS systems
"""

import os
import sys
import json
import argparse
import logging
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add the ai directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from editor import FileEditor
from executor import CommandExecutor
from watcher import LogWatcher
from config import AIConfig

class NixOSAIAgent:
    """Main AI agent for NixOS system management"""
    
    def __init__(self, config_path: str = None):
        self.config = AIConfig(config_path)
        self.editor = FileEditor(self.config)
        self.executor = CommandExecutor(self.config)
        self.watcher = LogWatcher(self.config)
        
        # Set up logging
        self.logger = self._setup_logging()
        
        # AI client (will be implemented based on config)
        self.ai_client = self._setup_ai_client()
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the AI agent"""
        logger = logging.getLogger('nixos-ai')
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path(self.config.ai_dir) / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        fh = logging.FileHandler(log_dir / "ai.log")
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def _setup_ai_client(self):
        """Set up AI client based on configuration"""
        active_provider = self.config.active_provider
        
        if active_provider == "openai" and self.config.api_key:
            try:
                import openai
                openai.api_key = self.config.api_key
                return openai
            except ImportError:
                self.logger.warning("OpenAI library not available, trying fallback")
                return self._try_fallback_providers()
        elif active_provider == "gemini":
            gemini_client = self._setup_gemini_client()
            if gemini_client:
                return gemini_client
            else:
                self.logger.warning("Gemini setup failed, trying fallback")
                return self._try_fallback_providers()
        elif active_provider == "anthropic":
            try:
                import anthropic
                api_key = self.config.get_api_key("anthropic")
                if api_key:
                    return anthropic.Anthropic(api_key=api_key)
                else:
                    self.logger.warning("No Anthropic API key provided, trying fallback")
                    return self._try_fallback_providers()
            except ImportError:
                self.logger.warning("Anthropic library not available, trying fallback")
                return self._try_fallback_providers()
        elif active_provider == "ollama":
            # Ollama doesn't need API key, but we need to implement it
            self.logger.warning("Ollama provider not yet implemented, trying fallback")
            return self._try_fallback_providers()
        else:
            self.logger.warning(f"Unknown provider: {active_provider}, using mock AI")
            return self._create_mock_ai()
    
    def _try_fallback_providers(self):
        """Try fallback providers in order"""
        for provider in self.config.fallback_providers:
            if provider == "gemini":
                gemini_client = self._setup_gemini_client()
                if gemini_client:
                    self.logger.info(f"Using fallback provider: {provider}")
                    return gemini_client
            elif provider == "openai" and self.config.api_key:
                try:
                    import openai
                    openai.api_key = self.config.api_key
                    self.logger.info(f"Using fallback provider: {provider}")
                    return openai
                except ImportError:
                    continue
            elif provider == "anthropic":
                try:
                    import anthropic
                    api_key = self.config.get_api_key("anthropic")
                    if api_key:
                        self.logger.info(f"Using fallback provider: {provider}")
                        return anthropic.Anthropic(api_key=api_key)
                except ImportError:
                    continue
        
        self.logger.warning("All providers failed, using mock AI")
        return self._create_mock_ai()
    
    def _create_mock_ai(self):
        """Create a mock AI client for testing"""
        class MockAI:
            def __init__(self):
                self.responses = {
                    "install docker": {
                        "action": "edit_file",
                        "file": "/etc/nixos/nixos-ai/nix/ai.nix",
                        "changes": [
                            "services.docker.enable = true;",
                            "environment.systemPackages = with pkgs; [ docker ];"
                        ],
                        "commands": ["nixos-rebuild test", "nixos-rebuild switch"]
                    },
                    "add vscode": {
                        "action": "edit_file", 
                        "file": "/etc/nixos/nixos-ai/nix/ai.nix",
                        "changes": [
                            "environment.systemPackages = with pkgs; [ vscode ];"
                        ],
                        "commands": ["nixos-rebuild test", "nixos-rebuild switch"]
                    }
                }
            
            def chat_completion(self, messages, model="gpt-4", **kwargs):
                user_message = messages[-1]["content"].lower()
                
                # Find matching response
                for key, response in self.responses.items():
                    if key in user_message:
                        return {
                            "choices": [{
                                "message": {
                                    "content": json.dumps(response)
                                }
                            }]
                        }
                
                # Default response
                return {
                    "choices": [{
                        "message": {
                            "content": json.dumps({
                                "action": "unknown",
                                "message": f"I understand you want to: {user_message}. Please be more specific about what you'd like me to do."
                            })
                        }
                    }]
                }
        
        return MockAI()
    
    def _setup_gemini_client(self):
        """Set up Gemini AI client"""
        try:
            import google.generativeai as genai
            
            # Get Gemini configuration
            gemini_config = self.config.ai_models.get("gemini", {})
            api_key = gemini_config.get("api_key", "")
            base_url = gemini_config.get("base_url", "https://generativelanguage.googleapis.com/v1beta")
            
            if not api_key:
                self.logger.warning("No Gemini API key provided")
                return None
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            
            # Create a wrapper class to match OpenAI interface
            class GeminiClient:
                def __init__(self, config):
                    self.config = config
                    self.model_name = config.get("default_model", "gemini-pro")
                
                def chat_completion(self, messages, model=None, **kwargs):
                    try:
                        # Use specified model or default
                        model_name = model or self.model_name
                        
                        # Convert messages to Gemini format
                        prompt = ""
                        for message in messages:
                            role = message.get("role", "user")
                            content = message.get("content", "")
                            if role == "system":
                                prompt += f"System: {content}\n\n"
                            elif role == "user":
                                prompt += f"User: {content}\n\n"
                            elif role == "assistant":
                                prompt += f"Assistant: {content}\n\n"
                        
                        # Generate response using Gemini
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(prompt)
                        
                        # Convert to OpenAI format
                        return {
                            "choices": [{
                                "message": {
                                    "content": response.text
                                }
                            }]
                        }
                    except Exception as e:
                        self.logger.error(f"Gemini API error: {e}")
                        return {
                            "choices": [{
                                "message": {
                                    "content": json.dumps({
                                        "action": "error",
                                        "message": f"Gemini API error: {str(e)}"
                                    })
                                }
                            }]
                        }
            
            return GeminiClient(gemini_config)
            
        except ImportError:
            self.logger.warning("Google Generative AI library not available. Install with: pip install google-generativeai")
            return None
        except Exception as e:
            self.logger.error(f"Error setting up Gemini client: {e}")
            return None
    
    async def process_request(self, user_input: str) -> Dict[str, Any]:
        """Process a user request and return the result"""
        self.logger.info(f"Processing request: {user_input}")
        
        try:
            # Get AI response
            messages = [
                {
                    "role": "system", 
                    "content": """You are a NixOS AI assistant. You can:
1. Edit NixOS configuration files
2. Run system commands
3. Install packages
4. Enable services

Respond with JSON containing:
- action: "edit_file", "run_command", or "unknown"
- file: path to file (if editing)
- changes: list of changes (if editing)
- commands: list of commands to run
- message: explanation of what you're doing

Be specific and safe. Always validate changes before applying."""
                },
                {"role": "user", "content": user_input}
            ]
            
            response = self.ai_client.chat_completion(
                messages=messages,
                model=self.config.model
            )
            
            ai_response = json.loads(response.choices[0].message.content)
            self.logger.info(f"AI response: {ai_response}")
            
            # Execute the action
            result = await self._execute_action(ai_response)
            
            return {
                "success": True,
                "action": ai_response.get("action"),
                "result": result,
                "message": ai_response.get("message", "Action completed")
            }
            
        except Exception as e:
            self.logger.error(f"Error processing request: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to process request"
            }
    
    async def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the action specified by the AI"""
        action_type = action.get("action")
        
        if action_type == "edit_file":
            return await self._handle_file_edit(action)
        elif action_type == "run_command":
            return await self._handle_command_execution(action)
        else:
            return {"message": action.get("message", "Unknown action")}
    
    async def _handle_file_edit(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file editing actions"""
        file_path = action.get("file")
        changes = action.get("changes", [])
        
        if not file_path:
            return {"error": "No file specified"}
        
        # Validate file path
        if not self._is_path_allowed(file_path):
            return {"error": f"Path not allowed: {file_path}"}
        
        # Apply changes
        result = self.editor.apply_changes(file_path, changes)
        
        # Run any associated commands
        commands = action.get("commands", [])
        if commands:
            for cmd in commands:
                cmd_result = await self.executor.run_command(cmd)
                if not cmd_result["success"]:
                    return {"error": f"Command failed: {cmd}", "details": cmd_result}
        
        return result
    
    async def _handle_command_execution(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle command execution actions"""
        commands = action.get("commands", [])
        results = []
        
        for cmd in commands:
            result = await self.executor.run_command(cmd)
            results.append(result)
            
            if not result["success"]:
                return {"error": f"Command failed: {cmd}", "details": result}
        
        return {"commands": results}
    
    def _is_path_allowed(self, path: str) -> bool:
        """Check if a path is allowed for modification"""
        if self.config.enable_system_wide_access:
            return True
        
        path_obj = Path(path).resolve()
        for allowed_path in self.config.allowed_paths:
            if path_obj.is_relative_to(Path(allowed_path).resolve()):
                return True
        
        return False
    
    async def run_daemon(self):
        """Run the AI agent as a daemon"""
        self.logger.info("Starting NixOS AI Assistant daemon")
        
        # Start the log watcher
        await self.watcher.start()
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Shutting down AI assistant daemon")
            await self.watcher.stop()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="NixOS AI Assistant")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("request", nargs="?", help="User request to process")
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = NixOSAIAgent(args.config)
    
    if args.daemon:
        # Run as daemon
        asyncio.run(agent.run_daemon())
    elif args.request:
        # Process single request
        result = asyncio.run(agent.process_request(args.request))
        print(json.dumps(result, indent=2))
    else:
        # Interactive mode
        print("NixOS AI Assistant - Interactive Mode")
        print("Type 'exit' to quit")
        
        while True:
            try:
                user_input = input("\n> ").strip()
                if user_input.lower() in ['exit', 'quit']:
                    break
                
                if user_input:
                    result = asyncio.run(agent.process_request(user_input))
                    print(json.dumps(result, indent=2))
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()
