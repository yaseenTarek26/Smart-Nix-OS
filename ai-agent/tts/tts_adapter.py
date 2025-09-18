#!/usr/bin/env python3
"""
Text-to-Speech Adapter - Handles voice output processing
"""

import logging
import asyncio
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from TTS.api import TTS
    COQUI_TTS_AVAILABLE = True
except ImportError:
    COQUI_TTS_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

logger = logging.getLogger(__name__)

class TTSAdapter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.coqui_tts = None
        self.pyttsx3_engine = None
        self._init_components()

    def _init_components(self):
        """Initialize TTS components"""
        if COQUI_TTS_AVAILABLE:
            try:
                # Load Coqui TTS model
                model_name = self.config.get('tts_model', 'tts_models/en/ljspeech/tacotron2-DDC')
                self.coqui_tts = TTS(model_name)
                logger.info(f"Coqui TTS model '{model_name}' loaded")
            except Exception as e:
                logger.error(f"Error loading Coqui TTS model: {e}")
                self.coqui_tts = None

        if PYTTSX3_AVAILABLE:
            try:
                self.pyttsx3_engine = pyttsx3.init()
                # Configure voice properties
                voices = self.pyttsx3_engine.getProperty('voices')
                if voices:
                    self.pyttsx3_engine.setProperty('voice', voices[0].id)
                self.pyttsx3_engine.setProperty('rate', 150)  # Speed of speech
                self.pyttsx3_engine.setProperty('volume', 0.8)  # Volume level
                logger.info("PyTTSx3 engine initialized")
            except Exception as e:
                logger.error(f"Error initializing PyTTSx3: {e}")
                self.pyttsx3_engine = None

    async def synthesize_speech(self, text: str, method: str = "coqui") -> Dict[str, Any]:
        """Synthesize speech from text"""
        try:
            if method == "coqui" and self.coqui_tts:
                return await self._synthesize_with_coqui(text)
            elif method == "pyttsx3" and self.pyttsx3_engine:
                return await self._synthesize_with_pyttsx3(text)
            else:
                return {
                    'success': False,
                    'error': f'TTS method {method} not available'
                }
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _synthesize_with_coqui(self, text: str) -> Dict[str, Any]:
        """Synthesize using Coqui TTS"""
        try:
            # Generate audio
            audio_data = self.coqui_tts.tts(text)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            return {
                'success': True,
                'audio_file': temp_file_path,
                'text': text,
                'method': 'coqui'
            }
            
        except Exception as e:
            logger.error(f"Error with Coqui TTS: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _synthesize_with_pyttsx3(self, text: str) -> Dict[str, Any]:
        """Synthesize using PyTTSx3"""
        try:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file_path = temp_file.name
            
            # Configure engine to save to file
            self.pyttsx3_engine.save_to_file(text, temp_file_path)
            self.pyttsx3_engine.runAndWait()
            
            return {
                'success': True,
                'audio_file': temp_file_path,
                'text': text,
                'method': 'pyttsx3'
            }
            
        except Exception as e:
            logger.error(f"Error with PyTTSx3: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def speak_text(self, text: str, method: str = "coqui") -> Dict[str, Any]:
        """Speak text directly"""
        try:
            if method == "coqui" and self.coqui_tts:
                return await self._speak_with_coqui(text)
            elif method == "pyttsx3" and self.pyttsx3_engine:
                return await self._speak_with_pyttsx3(text)
            else:
                return {
                    'success': False,
                    'error': f'TTS method {method} not available'
                }
        except Exception as e:
            logger.error(f"Error speaking text: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _speak_with_coqui(self, text: str) -> Dict[str, Any]:
        """Speak using Coqui TTS"""
        try:
            # Generate audio
            audio_data = self.coqui_tts.tts(text)
            
            # Play audio
            await self._play_audio_data(audio_data)
            
            return {
                'success': True,
                'text': text,
                'method': 'coqui'
            }
            
        except Exception as e:
            logger.error(f"Error speaking with Coqui: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _speak_with_pyttsx3(self, text: str) -> Dict[str, Any]:
        """Speak using PyTTSx3"""
        try:
            # Speak text
            self.pyttsx3_engine.say(text)
            self.pyttsx3_engine.runAndWait()
            
            return {
                'success': True,
                'text': text,
                'method': 'pyttsx3'
            }
            
        except Exception as e:
            logger.error(f"Error speaking with PyTTSx3: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _play_audio_data(self, audio_data: bytes):
        """Play audio data"""
        try:
            import pyaudio
            import wave
            import io
            
            # Create audio stream
            p = pyaudio.PyAudio()
            
            # Open stream
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=22050,
                output=True
            )
            
            # Play audio
            stream.write(audio_data)
            
            # Clean up
            stream.stop_stream()
            stream.close()
            p.terminate()
            
        except Exception as e:
            logger.error(f"Error playing audio: {e}")

    async def is_available(self) -> bool:
        """Check if TTS is available"""
        return (self.coqui_tts is not None or self.pyttsx3_engine is not None)

    async def get_supported_methods(self) -> list:
        """Get list of supported TTS methods"""
        methods = []
        
        if self.coqui_tts:
            methods.append('coqui')
        
        if self.pyttsx3_engine:
            methods.append('pyttsx3')
        
        return methods

    async def get_available_voices(self) -> Dict[str, Any]:
        """Get available voices"""
        try:
            voices = []
            
            if self.pyttsx3_engine:
                pyttsx3_voices = self.pyttsx3_engine.getProperty('voices')
                for voice in pyttsx3_voices:
                    voices.append({
                        'id': voice.id,
                        'name': voice.name,
                        'languages': voice.languages,
                        'method': 'pyttsx3'
                    })
            
            return {
                'success': True,
                'voices': voices
            }
            
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def set_voice(self, voice_id: str) -> Dict[str, Any]:
        """Set voice for TTS"""
        try:
            if self.pyttsx3_engine:
                self.pyttsx3_engine.setProperty('voice', voice_id)
                return {
                    'success': True,
                    'message': f'Voice set to {voice_id}'
                }
            else:
                return {
                    'success': False,
                    'error': 'PyTTSx3 not available'
                }
                
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
            return {
                'success': False,
                'error': str(e)
            }
