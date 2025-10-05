"""
Speech Engine Module
Text-to-speech and audio feedback
"""

import pyttsx3
import threading
import queue
import logging
from pathlib import Path
import pygame

class SpeechEngine:
    """Text-to-speech and audio feedback engine"""
    
    def __init__(self, config: dict):
        self.logger = logging.getLogger('SpeechEngine')
        self.config = config
        
        # Initialize TTS engine
        self.engine = pyttsx3.init()
        self._configure_engine()
        
        # Initialize pygame for sound effects
        pygame.mixer.init()
        
        # Speech queue
        self.speech_queue = queue.Queue()
        self.speaking = False
        
        # Start speech thread
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()
        
        # Load sound effects
        self.sounds = self._load_sounds()
    
    def _configure_engine(self):
        """Configure TTS engine settings"""
        # Set voice
        voices = self.engine.getProperty('voices')
        voice_index = self.config.get('voice_index', 0)
        if voices and 0 <= voice_index < len(voices):
            self.engine.setProperty('voice', voices[voice_index].id)
        
        # Set rate
        rate = self.config.get('speech_rate', 150)
        self.engine.setProperty('rate', rate)
        
        # Set volume
        volume = self.config.get('speech_volume', 0.9)
        self.engine.setProperty('volume', volume)
    
    def _load_sounds(self) -> dict:
        """Load sound effect files"""
        sounds = {}
        sound_dir = Path('assets/sounds')
        
        if sound_dir.exists():
            sound_files = {
                'listening': 'listening.wav',
                'command_received': 'command.wav',
                'error': 'error.wav',
                'success': 'success.wav'
            }
            
            for name, filename in sound_files.items():
                filepath = sound_dir / filename
                if filepath.exists():
                    try:
                        sounds[name] = pygame.mixer.Sound(str(filepath))
                        self.logger.debug(f"Loaded sound: {name}")
                    except Exception as e:
                        self.logger.error(f"Error loading sound {name}: {e}")
        
        return sounds
    
    def speak(self, text: str, priority: bool = False):
        """Add text to speech queue"""
        if priority:
            # Clear queue and add with priority
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                except queue.Empty:
                    break
        
        self.speech_queue.put(text)
    
    def _speech_worker(self):
        """Worker thread for processing speech queue"""
        while True:
            try:
                text = self.speech_queue.get(timeout=1)
                self.speaking = True
                self.engine.say(text)
                self.engine.runAndWait()
                self.speaking = False
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in speech worker: {e}")
                self.speaking = False
    
    def play_sound(self, sound_name: str):
        """Play a sound effect"""
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                self.logger.error(f"Error playing sound {sound_name}: {e}")
    
    def stop_speaking(self):
        """Stop current speech"""
        self.engine.stop()
        # Clear queue
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except queue.Empty:
                break
        self.speaking = False
    
    def is_speaking(self) -> bool:
        """Check if currently speaking"""
        return self.speaking
    
    def get_voices(self) -> list:
        """Get available voices"""
        voices = self.engine.getProperty('voices')
        return [(i, v.name) for i, v in enumerate(voices)]
    
    def set_voice(self, voice_index: int):
        """Set voice by index"""
        voices = self.engine.getProperty('voices')
        if voices and 0 <= voice_index < len(voices):
            self.engine.setProperty('voice', voices[voice_index].id)
            self.config['voice_index'] = voice_index
    
    def set_rate(self, rate: int):
        """Set speech rate"""
        self.engine.setProperty('rate', rate)
        self.config['speech_rate'] = rate
    
    def set_volume(self, volume: float):
        """Set speech volume"""
        self.engine.setProperty('volume', volume)
        self.config['speech_volume'] = volume
    
    def update_config(self, config: dict):
        """Update engine configuration"""
        self.config.update(config)
        self._configure_engine()
