#!/usr/bin/env python3
"""
Demo script for NixOS AI Hyprland
"""

import asyncio
import json
from pathlib import Path

# Add ai-agent to path
import sys
sys.path.insert(0, str(Path(__file__).parent / 'ai-agent'))

from agent import NixOSAIAgent

async def demo_chat():
    """Demo chat interaction"""
    print("🤖 NixOS AI Hyprland Demo")
    print("=" * 30)
    print()
    
    # Initialize agent
    print("Initializing AI agent...")
    agent = NixOSAIAgent()
    print("✅ AI agent initialized")
    print()
    
    # Demo commands
    demo_commands = [
        "Install Firefox",
        "Open a terminal",
        "Show system information",
        "Enable flatpak support",
        "Change wallpaper to something dark"
    ]
    
    print("🎯 Demo Commands:")
    for i, cmd in enumerate(demo_commands, 1):
        print(f"  {i}. {cmd}")
    print()
    
    # Process each command
    for cmd in demo_commands:
        print(f"💬 User: {cmd}")
        
        try:
            response = await agent.process_message(cmd, "demo_user")
            
            if response['status'] == 'success':
                print(f"✅ AI: {response.get('message', 'Command processed successfully')}")
                
                if 'patch' in response:
                    print("📝 Generated patch:")
                    print(response['patch'][:200] + "..." if len(response['patch']) > 200 else response['patch'])
            else:
                print(f"❌ AI: Error - {response.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error processing command: {e}")
        
        print()
    
    print("🎉 Demo completed!")
    print()
    print("To try the full system:")
    print("1. Run ./install.sh to install")
    print("2. Reboot your system")
    print("3. Open http://127.0.0.1:8999 in your browser")
    print("4. Or press Super+Space for AI chat")

async def demo_voice():
    """Demo voice interaction"""
    print("🎤 Voice Interaction Demo")
    print("=" * 25)
    print()
    
    try:
        from stt.stt_adapter import STTAdapter
        from tts.tts_adapter import TTSAdapter
        
        # Initialize voice components
        config = {
            'whisper_model': 'base',
            'tts_model': 'tts_models/en/ljspeech/tacotron2-DDC'
        }
        
        stt = STTAdapter(config)
        tts = TTSAdapter(config)
        
        # Check availability
        stt_available = await stt.is_available()
        tts_available = await tts.is_available()
        
        print(f"🎤 Speech-to-Text: {'✅ Available' if stt_available else '❌ Not available'}")
        print(f"🔊 Text-to-Speech: {'✅ Available' if tts_available else '❌ Not available'}")
        
        if stt_available:
            methods = await stt.get_supported_methods()
            print(f"   Supported methods: {', '.join(methods)}")
        
        if tts_available:
            methods = await tts.get_supported_methods()
            print(f"   Supported methods: {', '.join(methods)}")
        
        print()
        print("To test voice interaction:")
        print("1. Install the system with ./install.sh")
        print("2. Press Super+Shift+Space for voice mode")
        print("3. Or run ai-voice command")
        
    except ImportError as e:
        print(f"❌ Voice components not available: {e}")
        print("Install with: pip install whisper coqui-tts pyaudio speechrecognition")

async def demo_fallback():
    """Demo fallback system"""
    print("🔄 Fallback System Demo")
    print("=" * 25)
    print()
    
    try:
        from fallback.flatpak_helper import FlatpakHelper
        from fallback.appimage_helper import AppImageHelper
        from fallback.docker_wrapper import DockerWrapper
        
        # Test Flatpak
        flatpak = FlatpakHelper()
        print("📦 Flatpak Helper:")
        print(f"   Available: {flatpak.flatpak_installed}")
        
        # Test AppImage
        appimage = AppImageHelper()
        print("📦 AppImage Helper:")
        print(f"   Scripts dir: {appimage.scripts_dir}")
        print(f"   Desktop dir: {appimage.desktop_dir}")
        
        # Test Docker
        docker = DockerWrapper()
        print("📦 Docker Wrapper:")
        print(f"   Available: {docker.docker_available}")
        if docker.docker_available:
            print(f"   Command: {docker.docker_command}")
        
        print()
        print("Fallback system will automatically try:")
        print("1. NixOS packages (primary)")
        print("2. Flatpak packages (fallback 1)")
        print("3. AppImage packages (fallback 2)")
        print("4. Docker containers (fallback 3)")
        
    except ImportError as e:
        print(f"❌ Fallback components not available: {e}")

async def main():
    """Main demo function"""
    print("🚀 NixOS AI Hyprland - Complete Demo")
    print("=" * 40)
    print()
    
    # Run demos
    await demo_chat()
    print()
    await demo_voice()
    print()
    await demo_fallback()
    print()
    
    print("🎯 Ready to install? Run: ./install.sh")

if __name__ == "__main__":
    asyncio.run(main())
