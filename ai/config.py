"""
Configuration management for NixOS AI Assistant
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any

class AIConfig:
    """Configuration manager for the AI assistant"""
    
    def __init__(self, config_path: str = None):
        self.ai_dir = os.getenv("NIXOS_AI_DIR", "/etc/nixos/nixos-ai")
        self.config_file = config_path or os.path.join(self.ai_dir, "ai", "config.json")
        
        # Load configuration
        self.config = self._load_config()
        
        # Set up paths
        self.allowed_paths = self.config.get("allowed_paths", [self.ai_dir])
        self.enable_system_wide_access = self.config.get("enable_system_wide_access", False)
        
        # AI settings
        self.ai_models = self.config.get("ai_models", {})
        self.active_provider = self.config.get("active_provider", "openai")
        self.fallback_providers = self.config.get("fallback_providers", [])
        
        # Legacy support
        self.api_key = os.getenv("OPENAI_API_KEY") or self.get_api_key("openai")
        self.model = os.getenv("AI_MODEL") or self.get_default_model("openai")
        
        # Safety settings
        self.auto_commit = self.config.get("auto_commit", True)
        self.auto_rollback = self.config.get("auto_rollback", True)
        self.validation_required = self.config.get("validation_required", True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        config_path = Path(self.config_file)
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file: {e}")
        
        # Return default configuration
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "ai_models": {
                "openai": {
                    "api_key": "",
                    "base_url": "https://api.openai.com/v1",
                    "models": {
                        "gpt-4": {"temperature": 0.7, "max_tokens": 2000, "timeout": 300},
                        "gpt-3.5-turbo": {"temperature": 0.7, "max_tokens": 1000, "timeout": 180}
                    },
                    "default_model": "gpt-4"
                }
            },
            "active_provider": "openai",
            "fallback_providers": [],
            "allowed_paths": [self.ai_dir],
            "enable_system_wide_access": False,
            "auto_commit": True,
            "auto_rollback": True,
            "validation_required": True,
            "log_level": "INFO",
            "max_file_size": 10485760,  # 10MB
            "backup_retention_days": 30,
            "state_directory": f"{self.ai_dir}/state",
            "cache_directory": f"{self.ai_dir}/cache"
        }
    
    def save_config(self):
        """Save current configuration to file"""
        config_path = Path(self.config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration with new values"""
        self.config.update(updates)
        self.save_config()
        
        # Update instance variables
        self.allowed_paths = self.config.get("allowed_paths", [self.ai_dir])
        self.enable_system_wide_access = self.config.get("enable_system_wide_access", False)
        self.ai_models = self.config.get("ai_models", {})
        self.active_provider = self.config.get("active_provider", "openai")
        self.fallback_providers = self.config.get("fallback_providers", [])
        self.api_key = self.get_api_key(self.active_provider)
        self.model = self.get_default_model(self.active_provider)
    
    def get_api_key(self, provider: str) -> str:
        """Get API key for a specific provider"""
        if provider in self.ai_models:
            return self.ai_models[provider].get("api_key", "")
        return ""
    
    def get_base_url(self, provider: str) -> str:
        """Get base URL for a specific provider"""
        if provider in self.ai_models:
            return self.ai_models[provider].get("base_url", "")
        return ""
    
    def get_default_model(self, provider: str) -> str:
        """Get default model for a specific provider"""
        if provider in self.ai_models:
            return self.ai_models[provider].get("default_model", "")
        return ""
    
    def get_model_config(self, provider: str, model: str) -> Dict[str, Any]:
        """Get configuration for a specific model"""
        if provider in self.ai_models and model in self.ai_models[provider].get("models", {}):
            return self.ai_models[provider]["models"][model]
        return {}
    
    def get_available_providers(self) -> List[str]:
        """Get list of available AI providers"""
        return list(self.ai_models.keys())
    
    def get_available_models(self, provider: str) -> List[str]:
        """Get list of available models for a provider"""
        if provider in self.ai_models:
            return list(self.ai_models[provider].get("models", {}).keys())
        return []
    
    def set_active_provider(self, provider: str):
        """Set the active AI provider"""
        if provider in self.ai_models:
            self.active_provider = provider
            self.api_key = self.get_api_key(provider)
            self.model = self.get_default_model(provider)
            self.config["active_provider"] = provider
            self.save_config()
    
    def add_api_key(self, provider: str, api_key: str):
        """Add or update API key for a provider"""
        if provider not in self.ai_models:
            self.ai_models[provider] = {"api_key": api_key, "models": {}, "default_model": ""}
        else:
            self.ai_models[provider]["api_key"] = api_key
        self.config["ai_models"] = self.ai_models
        self.save_config()
