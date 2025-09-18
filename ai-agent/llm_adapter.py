#!/usr/bin/env python3
"""
LLM Adapter - Handles communication with various LLM providers
"""

import json
import hashlib
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

import openai
import requests
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)

class LLMAdapter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cache_dir = Path(config.get('cache_dir', '/var/lib/nixos-agent/cache'))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load prompts
        self.prompts = self._load_prompts()
        
        # Initialize LLM client
        self.client = self._init_client()

    def _load_prompts(self) -> Dict[str, Any]:
        """Load prompts from prompts.json"""
        prompts_file = Path(__file__).parent / 'prompts.json'
        if prompts_file.exists():
            with open(prompts_file) as f:
                return json.load(f)
        else:
            return self._get_default_prompts()

    def _get_default_prompts(self) -> Dict[str, Any]:
        """Get default prompts if prompts.json doesn't exist"""
        return {
            "system_prompt": """You are a NixOS configuration patch generator. Your job is to generate unified diff patches that modify NixOS configuration files.

RULES:
1. Output ONLY a unified diff patch in git format
2. If you cannot generate a safe patch, return exactly: UNABLE_TO_GENERATE_PATCH
3. Preserve existing formatting and style
4. Make minimal, targeted changes
5. Use proper Nix syntax
6. Include proper file paths in the diff header

PATCH FORMAT:
```diff
diff --git a/path/to/file.nix b/path/to/file.nix
index 1234567..abcdef0 100644
--- a/path/to/file.nix
+++ b/path/to/file.nix
@@ -10,7 +10,9 @@
   environment.systemPackages = with pkgs; [
     firefox
+    new-package
   ];
```

EXAMPLES:""",
            "examples": [
                {
                    "input": "TARGET: /etc/nixos/configuration.nix\nINSTRUCTION: Add pkgs.vscode to environment.systemPackages",
                    "output": "diff --git a/configuration.nix b/configuration.nix\nindex 1234567..abcdef0 100644\n--- a/configuration.nix\n+++ b/configuration.nix\n@@ -15,7 +15,8 @@\n   environment.systemPackages = with pkgs; [\n     firefox\n     git\n+    vscode\n   ];"
                }
            ]
        }

    def _init_client(self):
        """Initialize LLM client based on provider"""
        provider = self.config.get('llm_provider', 'openai')
        
        if provider == 'openai':
            openai.api_key = self.config.get('api_key', '')
            return openai
        elif provider == 'gemini':
            if not GEMINI_AVAILABLE:
                raise ImportError("Google Generative AI library not installed. Run: pip install google-generativeai")
            api_key = self.config.get('api_key', '') or self.config.get('gemini_api_key', '')
            genai.configure(api_key=api_key)
            return genai
        elif provider == 'local':
            # TODO: Implement local LLM client
            raise NotImplementedError("Local LLM support not implemented yet")
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

    async def generate_patch(self, target_files: List[str], instruction: str, context: Dict[str, Any] = None) -> str:
        """Generate a unified diff patch for the given instruction"""
        try:
            # Create cache key
            cache_key = self._create_cache_key(target_files, instruction, context)
            
            # Check cache first
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                logger.info("Using cached patch")
                return cached_result
            
            # Generate prompt
            prompt = self._create_prompt(target_files, instruction, context)
            
            # Call LLM
            response = await self._call_llm(prompt)
            
            # Cache result
            self._cache_result(cache_key, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating patch: {e}")
            return "UNABLE_TO_GENERATE_PATCH"

    def _create_cache_key(self, target_files: List[str], instruction: str, context: Dict[str, Any]) -> str:
        """Create cache key for the request"""
        key_data = {
            'target_files': sorted(target_files),
            'instruction': instruction,
            'context': context or {}
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_cached_result(self, cache_key: str) -> Optional[str]:
        """Get cached result if available"""
        if not self.config.get('cache_enabled', True):
            return None
            
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    data = json.load(f)
                    return data.get('response')
            except Exception as e:
                logger.warning(f"Error reading cache file: {e}")
        return None

    def _cache_result(self, cache_key: str, response: str):
        """Cache the result"""
        if not self.config.get('cache_enabled', True):
            return
            
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump({'response': response}, f)
        except Exception as e:
            logger.warning(f"Error caching result: {e}")

    def _create_prompt(self, target_files: List[str], instruction: str, context: Dict[str, Any]) -> str:
        """Create the prompt for the LLM"""
        prompt = self.prompts['system_prompt']
        
        # Add examples
        for example in self.prompts.get('examples', []):
            prompt += f"\n\nINPUT:\n{example['input']}\n\nOUTPUT:\n{example['output']}"
        
        # Add current request
        prompt += f"\n\nINPUT:\nTARGET: {', '.join(target_files)}\nINSTRUCTION: {instruction}"
        
        if context:
            prompt += f"\nCONTEXT: {json.dumps(context)}"
        
        prompt += "\n\nOUTPUT:"
        
        return prompt

    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the prompt"""
        provider = self.config.get('llm_provider', 'openai')
        
        if provider == 'openai':
            return await self._call_openai(prompt)
        elif provider == 'gemini':
            return await self._call_gemini(prompt)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a NixOS configuration expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return "UNABLE_TO_GENERATE_PATCH"

    async def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API"""
        try:
            model = genai.GenerativeModel('gemini-pro')
            
            # Create the full prompt with system message
            full_prompt = f"You are a NixOS configuration expert.\n\n{prompt}"
            
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.0,
                    max_output_tokens=2000,
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return "UNABLE_TO_GENERATE_PATCH"

    async def generate_response(self, message: str, context: Dict[str, Any] = None) -> str:
        """Generate a general response (not a patch)"""
        try:
            prompt = f"""You are a helpful NixOS assistant. Respond to the user's message about NixOS configuration and system management.

User message: {message}

Context: {json.dumps(context or {})}

Provide a helpful response:"""
            
            provider = self.config.get('llm_provider', 'openai')
            
            if provider == 'openai':
                response = await openai.ChatCompletion.acreate(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful NixOS assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                
                return response.choices[0].message.content.strip()
            elif provider == 'gemini':
                model = genai.GenerativeModel('gemini-pro')
                full_prompt = f"You are a helpful NixOS assistant.\n\n{prompt}"
                
                response = model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=500,
                    )
                )
                
                return response.text.strip()
            else:
                return "I'm here to help with NixOS configuration. How can I assist you?"
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm sorry, I encountered an error. Please try again."
