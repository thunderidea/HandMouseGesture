"""
Voice Controller Module
Advanced voice command recognition and processing system
"""

import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
import json
import logging
from typing import Dict, List, Optional, Callable
from pathlib import Path

from .command_processor import CommandProcessor
from .speech_engine import SpeechEngine
from controllers.system_controller import SystemController
from controllers.keyboard_controller import KeyboardController
from utils.config_manager import ConfigManager

class VoiceController:
    """Main voice control system with custom command support"""
    
    # Default voice commands
    DEFAULT_COMMANDS = {
        # Application Control
        "open chrome": {"action": "open_app", "params": ["chrome"]},
        "open firefox": {"action": "open_app", "params": ["firefox"]},
        "open edge": {"action": "open_app", "params": ["edge"]},
        "open notepad": {"action": "open_app", "params": ["notepad"]},
        "open calculator": {"action": "open_app", "params": ["calculator"]},
        "open paint": {"action": "open_app", "params": ["paint"]},
        "open settings": {"action": "open_app", "params": ["settings"]},
        "open this pc": {"action": "open_app", "params": ["this pc"]},
        "open control panel": {"action": "open_app", "params": ["control panel"]},
        
        # Window Management
        "close": {"action": "close_window"},
        "close window": {"action": "close_window"},
        "minimize": {"action": "minimize_window"},
        "maximize": {"action": "maximize_window"},
        "switch app": {"action": "switch_window"},
        "switch window": {"action": "switch_window"},
        "show desktop": {"action": "show_desktop"},
        
        # Navigation
        "go back": {"action": "go_back"},
        "go forward": {"action": "go_forward"},
        "refresh": {"action": "refresh"},
        "scroll up": {"action": "scroll", "params": ["up"]},
        "scroll down": {"action": "scroll", "params": ["down"]},
        "page up": {"action": "page_up"},
        "page down": {"action": "page_down"},
        
        # Edit Operations
        "copy this": {"action": "copy"},
        "copy": {"action": "copy"},
        "paste here": {"action": "paste"},
        "paste": {"action": "paste"},
        "cut this": {"action": "cut"},
        "delete this": {"action": "delete"},
        "select all": {"action": "select_all"},
        "undo": {"action": "undo"},
        "redo": {"action": "redo"},
        
        # System Control
        "take screenshot": {"action": "screenshot"},
        "screenshot": {"action": "screenshot"},
        "volume up": {"action": "volume_up"},
        "volume down": {"action": "volume_down"},
        "mute": {"action": "mute"},
        "unmute": {"action": "unmute"},
        "increase brightness": {"action": "brightness_up"},
        "decrease brightness": {"action": "brightness_down"},
        "lock screen": {"action": "lock_screen"},
        "open search": {"action": "open_search"},
        "open search box": {"action": "open_search"},
        
        # Media Control
        "play": {"action": "play_pause"},
        "pause": {"action": "play_pause"},
        "next track": {"action": "next_track"},
        "previous track": {"action": "previous_track"},
        
        # Special Commands
        "typing": {"action": "voice_typing"},
        "start typing": {"action": "voice_typing"},
        "stop listening": {"action": "stop_listening"},
        "pause listening": {"action": "pause_listening"},
        "resume listening": {"action": "resume_listening"}
    }
    
    def __init__(self, config: dict):
        self.logger = logging.getLogger('VoiceController')
        self.config = config
        self.config_manager = ConfigManager()
        
        # Load voice commands
        self.commands = self._load_commands()
        
        # Initialize components
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.command_processor = CommandProcessor()
        self.speech_engine = SpeechEngine(config)
        self.system_controller = SystemController()
        self.keyboard_controller = KeyboardController()
        
        # Configuration
        self.language = config.get('voice_language', 'en-US')
        self.wake_word = config.get('wake_word', None)
        self.continuous_listening = config.get('continuous_listening', True)
        self.feedback_enabled = config.get('voice_feedback', True)
        self.confidence_threshold = config.get('voice_confidence', 0.5)
        
        # State management
        self.running = False
        self.paused = False
        self.listening = False
        self.wake_word_active = False
        
        # Command queue for processing
        self.command_queue = queue.Queue()
        
        # Callbacks
        self.status_callback = None
        self.command_callbacks = {}
        
        # Adjust recognizer settings
        self._configure_recognizer()
        
    def _configure_recognizer(self):
        """Configure speech recognizer settings"""
        self.recognizer.energy_threshold = self.config.get('energy_threshold', 4000)
        self.recognizer.dynamic_energy_threshold = self.config.get('dynamic_energy', True)
        self.recognizer.pause_threshold = self.config.get('pause_threshold', 0.8)
        self.recognizer.phrase_threshold = self.config.get('phrase_threshold', 0.3)
        
    def start(self):
        """Start voice control system"""
        self.running = True
        self.logger.info("Starting voice control...")
        
        # Start command processor thread
        processor_thread = threading.Thread(target=self._process_commands, daemon=True)
        processor_thread.start()
        
        # Calibrate microphone
        self._calibrate_microphone()
        
        # Start listening
        if self.continuous_listening:
            self._continuous_listen()
        else:
            self._manual_listen()
    
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        try:
            with self.microphone as source:
                self.logger.info("Calibrating microphone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                self.logger.info("Microphone calibrated")
        except Exception as e:
            self.logger.error(f"Error calibrating microphone: {e}")
    
    def _continuous_listen(self):
        """Continuous listening mode"""
        self.logger.info("Starting continuous listening...")
        
        while self.running:
            if not self.paused:
                self._listen_once()
            else:
                time.sleep(0.5)
    
    def _manual_listen(self):
        """Manual listening mode (triggered by gesture or hotkey)"""
        while self.running:
            if self.listening and not self.paused:
                self._listen_once()
                self.listening = False
            else:
                time.sleep(0.1)
    
    def _listen_once(self):
        """Listen for a single command"""
        try:
            with self.microphone as source:
                # Notify listening started
                if self.status_callback:
                    self.status_callback({'listening': True})
                
                # Provide audio feedback
                if self.feedback_enabled:
                    self.speech_engine.play_sound('listening')
                
                # Listen for audio
                self.logger.debug("Listening for command...")
                audio = self.recognizer.listen(
                    source,
                    timeout=self.config.get('listen_timeout', 5),
                    phrase_time_limit=self.config.get('phrase_limit', 5)
                )
                
                # Process audio in separate thread
                threading.Thread(
                    target=self._process_audio,
                    args=(audio,),
                    daemon=True
                ).start()
                
        except sr.WaitTimeoutError:
            self.logger.debug("Listening timeout")
        except Exception as e:
            self.logger.error(f"Error listening: {e}")
        finally:
            if self.status_callback:
                self.status_callback({'listening': False})
    
    def _process_audio(self, audio):
        """Process captured audio"""
        try:
            # Recognize speech
            text = self.recognizer.recognize_google(
                audio,
                language=self.language,
                show_all=True
            )
            
            if text:
                # Get best result
                if isinstance(text, dict) and 'alternative' in text:
                    alternatives = text['alternative']
                    if alternatives:
                        best = alternatives[0]
                        transcript = best['transcript'].lower()
                        confidence = best.get('confidence', 1.0)
                        
                        self.logger.info(f"Recognized: '{transcript}' (confidence: {confidence:.2f})")
                        
                        # Check confidence threshold
                        if confidence >= self.confidence_threshold:
                            # Check for wake word if enabled
                            if self.wake_word and not self.wake_word_active:
                                if self.wake_word.lower() in transcript:
                                    self.wake_word_active = True
                                    self.speech_engine.speak("Yes, I'm listening")
                                    return
                            
                            # Process command
                            self._handle_command(transcript)
                        else:
                            self.logger.debug(f"Low confidence: {confidence}")
                
        except sr.UnknownValueError:
            self.logger.debug("Could not understand audio")
        except sr.RequestError as e:
            self.logger.error(f"Recognition error: {e}")
        except Exception as e:
            self.logger.error(f"Error processing audio: {e}")
    
    def _handle_command(self, command: str):
        """Handle recognized command"""
        # Reset wake word state
        self.wake_word_active = False
        
        # Add to command queue
        self.command_queue.put(command)
        
        # Provide feedback
        if self.feedback_enabled:
            self.speech_engine.play_sound('command_received')
    
    def _process_commands(self):
        """Process commands from queue"""
        while self.running:
            try:
                command = self.command_queue.get(timeout=1)
                self._execute_command(command)
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing command: {e}")
    
    def _execute_command(self, command: str):
        """Execute a voice command"""
        # Check for exact match first
        if command in self.commands:
            command_data = self.commands[command]
            action = command_data.get('action')
            params = command_data.get('params', [])
            
            self._perform_action(action, params)
            
            # Call registered callback
            if command in self.command_callbacks:
                self.command_callbacks[command]()
        else:
            # Try fuzzy matching
            matched_command = self.command_processor.match_command(command, self.commands.keys())
            
            if matched_command:
                self.logger.info(f"Matched '{command}' to '{matched_command}'")
                command_data = self.commands[matched_command]
                action = command_data.get('action')
                params = command_data.get('params', [])
                
                self._perform_action(action, params)
            else:
                # Try to extract action from natural language
                action, params = self.command_processor.extract_action(command)
                if action:
                    self._perform_action(action, params)
                else:
                    self.logger.warning(f"Unknown command: {command}")
                    if self.feedback_enabled:
                        self.speech_engine.speak("Sorry, I didn't understand that command")
    
    def _perform_action(self, action: str, params: List = None):
        """Perform the specified action"""
        params = params or []
        
        try:
            # Application control
            if action == 'open_app':
                if params:
                    self.system_controller.open_application(params[0])
                    if self.feedback_enabled:
                        self.speech_engine.speak(f"Opening {params[0]}")
            
            # Window management
            elif action == 'close_window':
                self.keyboard_controller.close_window()
            elif action == 'minimize_window':
                self.keyboard_controller.minimize_window()
            elif action == 'maximize_window':
                self.keyboard_controller.maximize_window()
            elif action == 'switch_window':
                self.keyboard_controller.alt_tab()
            elif action == 'show_desktop':
                self.keyboard_controller.show_desktop()
            
            # Navigation
            elif action == 'go_back':
                self.keyboard_controller.go_back()
            elif action == 'go_forward':
                self.keyboard_controller.go_forward()
            elif action == 'refresh':
                self.keyboard_controller.refresh()
            elif action == 'scroll':
                direction = params[0] if params else 'down'
                from controllers.mouse_controller import MouseController
                mouse = MouseController(self.config)
                mouse.scroll(1 if direction == 'up' else -1)
            
            # Edit operations
            elif action == 'copy':
                self.keyboard_controller.copy()
            elif action == 'paste':
                self.keyboard_controller.paste()
            elif action == 'cut':
                self.keyboard_controller.cut()
            elif action == 'delete':
                self.keyboard_controller.delete()
            elif action == 'select_all':
                self.keyboard_controller.select_all()
            elif action == 'undo':
                self.keyboard_controller.undo()
            elif action == 'redo':
                self.keyboard_controller.redo()
            
            # System control
            elif action == 'screenshot':
                filename = self.system_controller.take_screenshot()
                if self.feedback_enabled and filename:
                    self.speech_engine.speak("Screenshot saved")
            elif action == 'volume_up':
                self.system_controller.adjust_volume(10)
            elif action == 'volume_down':
                self.system_controller.adjust_volume(-10)
            elif action == 'mute':
                self.system_controller.mute_volume()
            elif action == 'brightness_up':
                self.system_controller.adjust_brightness(10)
            elif action == 'brightness_down':
                self.system_controller.adjust_brightness(-10)
            elif action == 'lock_screen':
                self.system_controller.lock_screen()
            elif action == 'open_search':
                self.keyboard_controller.open_search()
            
            # Media control
            elif action == 'play_pause':
                self.keyboard_controller.play_pause()
            elif action == 'next_track':
                self.keyboard_controller.next_track()
            elif action == 'previous_track':
                self.keyboard_controller.previous_track()
            
            # Special commands
            elif action == 'voice_typing':
                self.keyboard_controller.trigger_voice_command()
            elif action == 'stop_listening':
                self.stop()
            elif action == 'pause_listening':
                self.pause()
            elif action == 'resume_listening':
                self.resume()
            
            else:
                self.logger.warning(f"Unknown action: {action}")
                
        except Exception as e:
            self.logger.error(f"Error performing action {action}: {e}")
    
    def add_custom_command(self, command: str, action: str, params: List = None):
        """Add a custom voice command"""
        self.commands[command.lower()] = {
            'action': action,
            'params': params or []
        }
        self._save_commands()
        self.logger.info(f"Added custom command: {command}")
    
    def remove_custom_command(self, command: str):
        """Remove a custom voice command"""
        command_lower = command.lower()
        if command_lower in self.commands:
            del self.commands[command_lower]
            self._save_commands()
            self.logger.info(f"Removed custom command: {command}")
    
    def _load_commands(self) -> Dict:
        """Load voice commands from file"""
        # Start with default commands
        commands = self.DEFAULT_COMMANDS.copy()
        
        # Load custom commands
        try:
            custom_file = Path('config/voice_commands.json')
            if custom_file.exists():
                with open(custom_file, 'r') as f:
                    custom_commands = json.load(f)
                    commands.update(custom_commands)
        except Exception as e:
            self.logger.error(f"Error loading custom commands: {e}")
        
        return commands
    
    def _save_commands(self):
        """Save custom commands to file"""
        try:
            # Extract custom commands (not in defaults)
            custom_commands = {
                k: v for k, v in self.commands.items()
                if k not in self.DEFAULT_COMMANDS
            }
            
            with open('config/voice_commands.json', 'w') as f:
                json.dump(custom_commands, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving commands: {e}")
    
    def register_command_callback(self, command: str, callback: Callable):
        """Register a callback for a specific command"""
        self.command_callbacks[command.lower()] = callback
    
    def set_status_callback(self, callback: Callable):
        """Set callback for status updates"""
        self.status_callback = callback
    
    def trigger_listen(self):
        """Manually trigger listening (for gesture/hotkey activation)"""
        if not self.continuous_listening:
            self.listening = True
    
    def pause(self):
        """Pause voice recognition"""
        self.paused = True
        self.logger.info("Voice control paused")
    
    def resume(self):
        """Resume voice recognition"""
        self.paused = False
        self.logger.info("Voice control resumed")
    
    def stop(self):
        """Stop voice control"""
        self.running = False
        self.logger.info("Voice control stopped")
    
    def is_active(self) -> bool:
        """Check if voice control is active"""
        return self.running and not self.paused
    
    def get_status(self) -> Dict:
        """Get current status"""
        return {
            'active': self.is_active(),
            'listening': self.listening,
            'language': self.language,
            'wake_word': self.wake_word,
            'continuous': self.continuous_listening
        }
    
    def update_config(self, config: dict):
        """Update configuration"""
        self.config.update(config)
        self.language = config.get('voice_language', 'en-US')
        self.wake_word = config.get('wake_word', None)
        self.continuous_listening = config.get('continuous_listening', True)
        self.feedback_enabled = config.get('voice_feedback', True)
        self.confidence_threshold = config.get('voice_confidence', 0.5)
        self._configure_recognizer()
        self.speech_engine.update_config(config)
