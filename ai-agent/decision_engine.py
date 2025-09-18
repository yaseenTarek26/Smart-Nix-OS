#!/usr/bin/env python3
"""
Decision Engine - Classifies user intents and determines action types
"""

import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DecisionEngine:
    def __init__(self):
        self.declarative_keywords = [
            'install', 'add', 'remove', 'uninstall', 'configure', 'setup',
            'change', 'modify', 'update', 'enable', 'disable', 'set',
            'create', 'delete', 'edit', 'customize', 'theme', 'wallpaper'
        ]
        
        self.imperative_keywords = [
            'open', 'launch', 'start', 'run', 'execute', 'show', 'display',
            'play', 'stop', 'close', 'quit', 'exit', 'restart', 'reload',
            'screenshot', 'record', 'capture', 'search', 'find', 'look'
        ]
        
        self.hybrid_keywords = [
            'install and open', 'add and launch', 'setup and start',
            'configure and run', 'install then open'
        ]

    async def classify_intent(self, message: str) -> Dict[str, Any]:
        """Classify user intent and determine action type"""
        message_lower = message.lower()
        
        # Check for hybrid patterns first
        for pattern in self.hybrid_keywords:
            if pattern in message_lower:
                return await self._classify_hybrid(message)
        
        # Check for imperative patterns
        imperative_score = self._calculate_score(message_lower, self.imperative_keywords)
        declarative_score = self._calculate_score(message_lower, self.declarative_keywords)
        
        if imperative_score > declarative_score and imperative_score > 0:
            return await self._classify_imperative(message)
        elif declarative_score > 0:
            return await self._classify_declarative(message)
        else:
            return await self._classify_unknown(message)

    def _calculate_score(self, message: str, keywords: List[str]) -> int:
        """Calculate score based on keyword matches"""
        score = 0
        for keyword in keywords:
            if keyword in message:
                score += 1
        return score

    async def _classify_declarative(self, message: str) -> Dict[str, Any]:
        """Classify as declarative intent"""
        target_files = self._extract_target_files(message)
        context = self._extract_context(message)
        
        return {
            'type': 'declarative',
            'target_files': target_files,
            'context': context,
            'confidence': 0.8
        }

    async def _classify_imperative(self, message: str) -> Dict[str, Any]:
        """Classify as imperative intent"""
        command = self._extract_command(message)
        
        return {
            'type': 'imperative',
            'command': command,
            'confidence': 0.8
        }

    async def _classify_hybrid(self, message: str) -> Dict[str, Any]:
        """Classify as hybrid intent"""
        # Split message into declarative and imperative parts
        parts = self._split_hybrid_message(message)
        
        return {
            'type': 'hybrid',
            'declarative_part': parts.get('declarative', ''),
            'imperative_part': parts.get('imperative', ''),
            'confidence': 0.7
        }

    async def _classify_unknown(self, message: str) -> Dict[str, Any]:
        """Classify as unknown intent"""
        return {
            'type': 'unknown',
            'confidence': 0.1,
            'message': 'I\'m not sure what you want me to do. Please be more specific.'
        }

    def _extract_target_files(self, message: str) -> List[str]:
        """Extract target files from message"""
        files = []
        
        # Common NixOS config files
        config_files = [
            'configuration.nix',
            'hardware-configuration.nix',
            'home.nix',
            'desktop.nix',
            'laptop.nix'
        ]
        
        for file in config_files:
            if file in message.lower():
                files.append(f"/etc/nixos/{file}")
        
        # If no specific files mentioned, default to main config
        if not files:
            files = ["/etc/nixos/configuration.nix"]
        
        return files

    def _extract_context(self, message: str) -> Dict[str, Any]:
        """Extract context information from message"""
        context = {}
        
        # Extract package names
        package_pattern = r'\b([a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9])\b'
        packages = re.findall(package_pattern, message)
        if packages:
            context['packages'] = packages
        
        # Extract system components
        components = []
        if 'hyprland' in message.lower():
            components.append('hyprland')
        if 'waybar' in message.lower():
            components.append('waybar')
        if 'rofi' in message.lower():
            components.append('rofi')
        if 'theme' in message.lower():
            components.append('theming')
        
        if components:
            context['components'] = components
        
        return context

    def _extract_command(self, message: str) -> str:
        """Extract command from message"""
        # Remove common prefixes
        prefixes = ['please', 'can you', 'could you', 'would you', 'i want to']
        command = message.lower()
        
        for prefix in prefixes:
            if command.startswith(prefix):
                command = command[len(prefix):].strip()
                break
        
        return command

    def _split_hybrid_message(self, message: str) -> Dict[str, str]:
        """Split hybrid message into declarative and imperative parts"""
        # Simple splitting based on conjunctions
        conjunctions = [' and ', ' then ', ' after ', ' followed by ']
        
        for conj in conjunctions:
            if conj in message.lower():
                parts = message.lower().split(conj, 1)
                return {
                    'declarative': parts[0].strip(),
                    'imperative': parts[1].strip()
                }
        
        # Default split
        return {
            'declarative': message,
            'imperative': message
        }
