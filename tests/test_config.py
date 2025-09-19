#!/usr/bin/env python3
"""
Test suite for the configuration component
"""

import os
import sys
import tempfile
import json
from pathlib import Path
import unittest
from unittest.mock import patch

# Add the ai directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai'))

from config import AIConfig

class TestAIConfig(unittest.TestCase):
    """Test cases for AIConfig"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, "test_config.json")
        
        # Create a test configuration
        self.test_config = {
            "ai_models": {
                "openai": {
                    "api_key": "test-key",
                    "base_url": "https://api.openai.com/v1",
                    "models": {
                        "gpt-4": {"temperature": 0.7, "max_tokens": 2000}
                    },
                    "default_model": "gpt-4"
                }
            },
            "active_provider": "openai",
            "allowed_paths": [self.test_dir]
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(self.test_config, f)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_config_loading(self):
        """Test configuration loading"""
        config = AIConfig(self.config_file)
        self.assertEqual(config.active_provider, "openai")
        self.assertIn(self.test_dir, config.allowed_paths)
    
    def test_api_key_retrieval(self):
        """Test API key retrieval"""
        config = AIConfig(self.config_file)
        api_key = config.get_api_key("openai")
        self.assertEqual(api_key, "test-key")
    
    def test_base_url_retrieval(self):
        """Test base URL retrieval"""
        config = AIConfig(self.config_file)
        base_url = config.get_base_url("openai")
        self.assertEqual(base_url, "https://api.openai.com/v1")
    
    def test_default_model_retrieval(self):
        """Test default model retrieval"""
        config = AIConfig(self.config_file)
        model = config.get_default_model("openai")
        self.assertEqual(model, "gpt-4")
    
    def test_model_config_retrieval(self):
        """Test model configuration retrieval"""
        config = AIConfig(self.config_file)
        model_config = config.get_model_config("openai", "gpt-4")
        self.assertEqual(model_config["temperature"], 0.7)
        self.assertEqual(model_config["max_tokens"], 2000)
    
    def test_available_providers(self):
        """Test available providers listing"""
        config = AIConfig(self.config_file)
        providers = config.get_available_providers()
        self.assertIn("openai", providers)
    
    def test_available_models(self):
        """Test available models listing"""
        config = AIConfig(self.config_file)
        models = config.get_available_models("openai")
        self.assertIn("gpt-4", models)
    
    def test_provider_switching(self):
        """Test active provider switching"""
        config = AIConfig(self.config_file)
        config.set_active_provider("openai")
        self.assertEqual(config.active_provider, "openai")
    
    def test_api_key_addition(self):
        """Test API key addition"""
        config = AIConfig(self.config_file)
        config.add_api_key("anthropic", "test-anthropic-key")
        
        # Check if the key was added
        api_key = config.get_api_key("anthropic")
        self.assertEqual(api_key, "test-anthropic-key")
    
    def test_config_saving(self):
        """Test configuration saving"""
        config = AIConfig(self.config_file)
        config.add_api_key("test-provider", "test-key")
        
        # Reload config to verify it was saved
        new_config = AIConfig(self.config_file)
        api_key = new_config.get_api_key("test-provider")
        self.assertEqual(api_key, "test-key")
    
    def test_default_config_creation(self):
        """Test default configuration creation"""
        # Test with non-existent config file
        non_existent_file = os.path.join(self.test_dir, "non_existent.json")
        config = AIConfig(non_existent_file)
        
        # Should have default values
        self.assertEqual(config.active_provider, "openai")
        self.assertIn("openai", config.get_available_providers())

if __name__ == "__main__":
    unittest.main()
