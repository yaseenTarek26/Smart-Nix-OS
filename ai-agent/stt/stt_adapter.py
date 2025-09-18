#!/usr/bin/env python3
"""
Speech-to-Text Adapter - Handles voice input processing
"""

import logging
import asyncio
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import whisper
    import pyaudio
    import wave
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

logger = logging.getLogger(__name__)

class STTAdapter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.whisper_model = None
        self.recognizer = None
        self.microphone = None
        self._init_components()

    def _init_components(self):
        """Initialize STT components"""
        if WHISPER_AVAILABLE:
            try:
                # Load Whisper model
                model_name = self.config.get('whisper_model', 'base')
                self.whisper_model = whisper.load_model(model_name)
                logger.info(f"Whisper model '{model_name}' loaded")
            except Exception as e:
                logger.error(f"Error loading Whisper model: {e}")
                self.whisper_model = None

        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                logger.info("Speech recognition initialized")
            except Exception as e:
                logger.error(f"Error initializing speech recognition: {e}")
                self.recognizer = None
                self.microphone = None

    async def transcribe_audio(self, audio_data: bytes, method: str = "whisper") -> Dict[str, Any]:
        """Transcribe audio data to text"""
        try:
            if method == "whisper" and self.whisper_model:
                return await self._transcribe_with_whisper(audio_data)
            elif method == "speech_recognition" and self.recognizer:
                return await self._transcribe_with_speech_recognition(audio_data)
            else:
                return {
                    'success': False,
                    'error': f'STT method {method} not available'
                }
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _transcribe_with_whisper(self, audio_data: bytes) -> Dict[str, Any]:
        """Transcribe using Whisper"""
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name

            # Transcribe with Whisper
            result = self.whisper_model.transcribe(temp_file_path)
            
            # Clean up temporary file
            Path(temp_file_path).unlink()
            
            return {
                'success': True,
                'text': result['text'].strip(),
                'language': result.get('language', 'unknown'),
                'confidence': 1.0  # Whisper doesn't provide confidence scores
            }
            
        except Exception as e:
            logger.error(f"Error with Whisper transcription: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _transcribe_with_speech_recognition(self, audio_data: bytes) -> Dict[str, Any]:
        """Transcribe using speech_recognition library"""
        try:
            # Convert bytes to AudioData
            audio = sr.AudioData(audio_data, 16000, 2)  # 16kHz, 16-bit
            
            # Try Google Speech Recognition first
            try:
                text = self.recognizer.recognize_google(audio)
                return {
                    'success': True,
                    'text': text,
                    'language': 'en-US',
                    'confidence': 0.8  # Estimated confidence
                }
            except sr.UnknownValueError:
                return {
                    'success': False,
                    'error': 'Could not understand audio'
                }
            except sr.RequestError as e:
                return {
                    'success': False,
                    'error': f'Speech recognition service error: {e}'
                }
                
        except Exception as e:
            logger.error(f"Error with speech recognition: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def record_audio(self, duration: float = 5.0) -> Dict[str, Any]:
        """Record audio from microphone"""
        try:
            if not self.microphone:
                return {
                    'success': False,
                    'error': 'Microphone not available'
                }
            
            # Record audio
            with self.microphone as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Record audio
                audio = self.recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
                
                # Convert to bytes
                audio_data = audio.get_wav_data()
                
                return {
                    'success': True,
                    'audio_data': audio_data,
                    'duration': duration
                }
                
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def is_available(self) -> bool:
        """Check if STT is available"""
        return (self.whisper_model is not None or 
                (self.recognizer is not None and self.microphone is not None))

    async def get_supported_methods(self) -> list:
        """Get list of supported STT methods"""
        methods = []
        
        if self.whisper_model:
            methods.append('whisper')
        
        if self.recognizer and self.microphone:
            methods.append('speech_recognition')
        
        return methods

    async def get_audio_devices(self) -> Dict[str, Any]:
        """Get available audio devices"""
        try:
            if not SPEECH_RECOGNITION_AVAILABLE:
                return {
                    'success': False,
                    'error': 'Speech recognition not available'
                }
            
            devices = []
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                devices.append({
                    'index': index,
                    'name': name
                })
            
            return {
                'success': True,
                'devices': devices
            }
            
        except Exception as e:
            logger.error(f"Error getting audio devices: {e}")
            return {
                'success': False,
                'error': str(e)
            }
