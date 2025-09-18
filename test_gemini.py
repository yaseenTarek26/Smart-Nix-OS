#!/usr/bin/env python3
"""
Test script for Gemini API integration
"""

import asyncio
import sys
from pathlib import Path

# Add ai-agent to path
sys.path.insert(0, str(Path(__file__).parent / 'ai-agent'))

from llm_adapter import LLMAdapter

async def test_gemini():
    """Test Gemini API integration"""
    print("🧪 Testing Gemini API Integration")
    print("=" * 40)
    
    # Test configuration
    config = {
        'llm_provider': 'gemini',
        'api_key': 'AIzaSyBjj5weW0GXXecUIfN2GHfa0zX9A9MAvm0',
        'cache_enabled': False
    }
    
    try:
        # Initialize adapter
        print("Initializing Gemini adapter...")
        adapter = LLMAdapter(config)
        print("✅ Gemini adapter initialized")
        
        # Test patch generation
        print("\nTesting patch generation...")
        patch = await adapter.generate_patch(
            target_files=['/etc/nixos/configuration.nix'],
            instruction='Add pkgs.firefox to environment.systemPackages'
        )
        
        if patch == "UNABLE_TO_GENERATE_PATCH":
            print("❌ Failed to generate patch")
        else:
            print("✅ Patch generated successfully:")
            print(patch[:200] + "..." if len(patch) > 200 else patch)
        
        # Test general response
        print("\nTesting general response...")
        response = await adapter.generate_response(
            "Hello! Can you help me with NixOS configuration?"
        )
        
        print("✅ Response generated:")
        print(response)
        
        print("\n🎉 Gemini integration test completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Install Gemini dependencies with: pip install google-generativeai")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Check your API key and internet connection")

if __name__ == "__main__":
    asyncio.run(test_gemini())
