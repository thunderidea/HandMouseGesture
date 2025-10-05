"""
Advanced Hand Gesture & Voice Control System
Main Application Entry Point
"""

import sys
import os
import threading
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from gui.main_window import MainApplication
from core.gesture_recognizer import GestureRecognizer
from voice.voice_controller import VoiceController
from utils.config_manager import ConfigManager
from utils.logger import setup_logger
from overlay.status_overlay import StatusOverlay

class HandControlSystem:
    """Main system controller that manages all components"""
    
    def __init__(self):
        # Setup logging
        self.logger = setup_logger('HandControlSystem')
        self.logger.info("Initializing Hand Control System...")
        
        # Initialize configuration
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        
        # Initialize components
        self.gesture_recognizer = None
        self.voice_controller = None
        self.status_overlay = None
        self.main_window = None
        
        # System state
        self.running = False
        self.gesture_enabled = self.config.get('gesture_enabled', True)
        self.voice_enabled = self.config.get('voice_enabled', False)
        
    def initialize_components(self):
        """Initialize all system components"""
        try:
            # Initialize gesture recognizer
            if self.gesture_enabled:
                self.gesture_recognizer = GestureRecognizer(self.config)
                self.logger.info("Gesture recognizer initialized")
            
            # Initialize voice controller
            if self.voice_enabled:
                self.voice_controller = VoiceController(self.config)
                self.logger.info("Voice controller initialized")
            
            # Initialize status overlay
            if self.config.get('show_overlay', True):
                self.status_overlay = StatusOverlay()
                self.logger.info("Status overlay initialized")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            return False
    
    def start_gesture_recognition(self):
        """Start gesture recognition in a separate thread"""
        if self.gesture_recognizer and self.gesture_enabled:
            self.gesture_thread = threading.Thread(
                target=self.gesture_recognizer.start,
                daemon=True
            )
            self.gesture_thread.start()
            self.logger.info("Gesture recognition started")
    
    def start_voice_control(self):
        """Start voice control in a separate thread"""
        if self.voice_controller and self.voice_enabled:
            self.voice_thread = threading.Thread(
                target=self.voice_controller.start,
                daemon=True
            )
            self.voice_thread.start()
            self.logger.info("Voice control started")
    
    def toggle_gesture(self, enabled):
        """Toggle gesture recognition on/off"""
        self.gesture_enabled = enabled
        if self.gesture_recognizer:
            if enabled:
                self.gesture_recognizer.resume()
            else:
                self.gesture_recognizer.pause()
        self.config_manager.update_setting('gesture_enabled', enabled)
        self.logger.info(f"Gesture recognition {'enabled' if enabled else 'disabled'}")
    
    def toggle_voice(self, enabled):
        """Toggle voice control on/off"""
        self.voice_enabled = enabled
        if self.voice_controller:
            if enabled:
                self.voice_controller.resume()
            else:
                self.voice_controller.pause()
        self.config_manager.update_setting('voice_enabled', enabled)
        self.logger.info(f"Voice control {'enabled' if enabled else 'disabled'}")
    
    def update_settings(self, settings):
        """Update system settings"""
        self.config.update(settings)
        self.config_manager.save_config(self.config)
        
        # Update components with new settings
        if self.gesture_recognizer:
            self.gesture_recognizer.update_config(self.config)
        if self.voice_controller:
            self.voice_controller.update_config(self.config)
        
        self.logger.info("Settings updated")
    
    def run(self):
        """Run the main application"""
        self.running = True
        
        # Initialize components
        if not self.initialize_components():
            self.logger.error("Failed to initialize system")
            return
        
        # Start background services
        self.start_gesture_recognition()
        self.start_voice_control()
        
        # Create and run GUI
        self.main_window = MainApplication(self)
        self.main_window.run()
        
        # Cleanup on exit
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources on exit"""
        self.running = False
        
        if self.gesture_recognizer:
            self.gesture_recognizer.stop()
        if self.voice_controller:
            self.voice_controller.stop()
        if self.status_overlay:
            self.status_overlay.close()
        
        self.logger.info("System shutdown complete")
    
    def get_status(self):
        """Get current system status"""
        return {
            'gesture_enabled': self.gesture_enabled,
            'voice_enabled': self.voice_enabled,
            'gesture_active': self.gesture_recognizer.is_active() if self.gesture_recognizer else False,
            'voice_active': self.voice_controller.is_active() if self.voice_controller else False,
            'current_gesture': self.gesture_recognizer.get_current_gesture() if self.gesture_recognizer else None,
            'fps': self.gesture_recognizer.get_fps() if self.gesture_recognizer else 0
        }

def main():
    """Main entry point"""
    # Create application directory structure
    app_dir = Path(__file__).parent
    (app_dir / 'config').mkdir(exist_ok=True)
    (app_dir / 'logs').mkdir(exist_ok=True)
    (app_dir / 'assets' / 'icons').mkdir(parents=True, exist_ok=True)
    (app_dir / 'assets' / 'sounds').mkdir(parents=True, exist_ok=True)
    (app_dir / 'assets' / 'themes').mkdir(parents=True, exist_ok=True)
    (app_dir / 'data').mkdir(exist_ok=True)
    
    # Run the system
    system = HandControlSystem()
    try:
        system.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
