"""
Configuration Manager Module
Handles all configuration loading, saving, and management
"""

import json
import os
from pathlib import Path
import logging
from typing import Dict, Any

class ConfigManager:
    """Manage application configuration"""
    
    def __init__(self):
        self.logger = logging.getLogger('ConfigManager')
        
        # Configuration paths
        self.config_dir = Path('config')
        self.config_dir.mkdir(exist_ok=True)
        
        self.settings_file = self.config_dir / 'settings.json'
        self.gestures_file = self.config_dir / 'gestures.json'
        self.voice_commands_file = self.config_dir / 'voice_commands.json'
        self.custom_gestures_file = self.config_dir / 'custom_gestures.json'
        
        # Load configurations
        self.config = self.load_config()
        self.gesture_mappings = self.load_gesture_mappings()
        self.voice_commands = self.load_voice_commands()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            # General settings
            'auto_start': False,
            'minimize_to_tray': True,
            'show_notifications': True,
            'language': 'English',
            'theme': 'Dark',
            'color_scheme': 'Blue',
            
            # Gesture settings
            'gesture_enabled': True,
            'detection_confidence': 0.7,
            'tracking_confidence': 0.5,
            'model_complexity': 1,
            'max_hands': 1,
            'gesture_hold_time': 300,
            'smoothing_enabled': True,
            'smoothing_factor': 0.5,
            'draw_landmarks': True,
            'history_size': 5,
            'pinch_threshold': 30,
            'ok_threshold': 40,
            'gesture_confidence': 0.8,
            'gesture_buffer_size': 5,
            'swipe_speed_threshold': 500,
            
            # Voice settings
            'voice_enabled': False,
            'voice_language': 'en-US',
            'continuous_listening': True,
            'voice_feedback': True,
            'voice_confidence': 0.5,
            'wake_word': None,
            'energy_threshold': 4000,
            'dynamic_energy': True,
            'pause_threshold': 0.8,
            'phrase_threshold': 0.3,
            'listen_timeout': 5,
            'phrase_limit': 5,
            'speech_rate': 150,
            'speech_volume': 0.9,
            'voice_index': 0,
            
            # Mouse settings
            'mouse_sensitivity': 1.5,
            'mouse_acceleration': 1.2,
            'mouse_smoothing': 0.3,
            'cursor_smoothing': 0.3,
            'scroll_sensitivity': 1.0,
            'scroll_smooth': True,
            'click_delay': 0.1,
            'double_click_interval': 0.3,
            'active_zone_margin': 0.1,
            
            # Camera settings
            'camera_index': 0,
            'frame_width': 640,
            'frame_height': 480,
            'show_camera_feed': False,
            
            # Performance settings
            'fps_limit': 30,
            'buffer_size': 10,
            
            # Appearance settings
            'show_overlay': True,
            'window_transparency': 1.0,
            
            # Advanced settings
            'debug_mode': False,
            'log_level': 'INFO'
        }
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    default_config = self.get_default_config()
                    default_config.update(config)
                    return default_config
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
        
        # Return default config
        return self.get_default_config()
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.logger.info("Configuration saved")
            return True
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            return False
    
    def update_setting(self, key: str, value: Any):
        """Update a single setting"""
        self.config[key] = value
        self.save_config(self.config)
    
    def load_gesture_mappings(self) -> Dict[str, str]:
        """Load gesture to action mappings"""
        default_mappings = {
            'INDEX_POINTING': 'cursor_move',
            'L_SHAPE': 'left_click',
            'PEACE_SIGN': 'right_click',
            'ROCK_SIGN': 'scroll_up',
            'CALL_SIGN': 'scroll_down',
            'CLOSED_FIST': 'drag_start',
            'OPEN_HAND': 'drag_end',
            'MIDDLE_FINGER': 'switch_window',
            'THUMBS_UP': 'volume_up',
            'THUMBS_DOWN': 'volume_down',
            'THREE_FINGERS': 'voice_command',
            'OK_SIGN': 'screenshot',
            'PINCH': 'zoom'
        }
        
        if self.gestures_file.exists():
            try:
                with open(self.gestures_file, 'r') as f:
                    mappings = json.load(f)
                    default_mappings.update(mappings)
            except Exception as e:
                self.logger.error(f"Error loading gesture mappings: {e}")
        
        return default_mappings
    
    def save_gesture_mappings(self, mappings: Dict[str, str]):
        """Save gesture mappings"""
        try:
            with open(self.gestures_file, 'w') as f:
                json.dump(mappings, f, indent=2)
            self.logger.info("Gesture mappings saved")
            return True
        except Exception as e:
            self.logger.error(f"Error saving gesture mappings: {e}")
            return False
    
    def load_voice_commands(self) -> Dict[str, Dict]:
        """Load voice commands"""
        commands = {}
        
        if self.voice_commands_file.exists():
            try:
                with open(self.voice_commands_file, 'r') as f:
                    commands = json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading voice commands: {e}")
        
        return commands
    
    def save_voice_commands(self, commands: Dict[str, Dict]):
        """Save voice commands"""
        try:
            with open(self.voice_commands_file, 'w') as f:
                json.dump(commands, f, indent=2)
            self.logger.info("Voice commands saved")
            return True
        except Exception as e:
            self.logger.error(f"Error saving voice commands: {e}")
            return False
    
    def load_custom_gestures(self) -> Dict[str, Dict]:
        """Load custom gesture templates"""
        if self.custom_gestures_file.exists():
            try:
                with open(self.custom_gestures_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading custom gestures: {e}")
        
        return {}
    
    def save_custom_gestures(self, gestures: Dict[str, Dict]):
        """Save custom gesture templates"""
        try:
            with open(self.custom_gestures_file, 'w') as f:
                json.dump(gestures, f, indent=2)
            self.logger.info("Custom gestures saved")
            return True
        except Exception as e:
            self.logger.error(f"Error saving custom gestures: {e}")
            return False
    
    def export_config(self, filepath: str):
        """Export all configuration to a file"""
        try:
            export_data = {
                'settings': self.config,
                'gesture_mappings': self.gesture_mappings,
                'voice_commands': self.voice_commands,
                'custom_gestures': self.load_custom_gestures()
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.logger.info(f"Configuration exported to {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting config: {e}")
            return False
    
    def import_config(self, filepath: str):
        """Import configuration from a file"""
        try:
            with open(filepath, 'r') as f:
                import_data = json.load(f)
            
            # Import settings
            if 'settings' in import_data:
                self.config.update(import_data['settings'])
                self.save_config(self.config)
            
            # Import gesture mappings
            if 'gesture_mappings' in import_data:
                self.gesture_mappings.update(import_data['gesture_mappings'])
                self.save_gesture_mappings(self.gesture_mappings)
            
            # Import voice commands
            if 'voice_commands' in import_data:
                self.voice_commands.update(import_data['voice_commands'])
                self.save_voice_commands(self.voice_commands)
            
            # Import custom gestures
            if 'custom_gestures' in import_data:
                self.save_custom_gestures(import_data['custom_gestures'])
            
            self.logger.info(f"Configuration imported from {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Error importing config: {e}")
            return False
    
    def reset_to_defaults(self):
        """Reset all configuration to defaults"""
        self.config = self.get_default_config()
        self.save_config(self.config)
        
        # Reset gesture mappings
        self.gesture_mappings = self.load_gesture_mappings()
        
        # Clear custom voice commands
        self.voice_commands = {}
        self.save_voice_commands(self.voice_commands)
        
        self.logger.info("Configuration reset to defaults")
    
    def get_profile(self, profile_name: str) -> Dict[str, Any]:
        """Get a performance profile configuration"""
        profiles = {
            'power_saver': {
                'detection_confidence': 0.8,
                'tracking_confidence': 0.6,
                'frame_width': 480,
                'frame_height': 360,
                'model_complexity': 0,
                'fps_limit': 20
            },
            'balanced': {
                'detection_confidence': 0.7,
                'tracking_confidence': 0.5,
                'frame_width': 640,
                'frame_height': 480,
                'model_complexity': 1,
                'fps_limit': 30
            },
            'high_performance': {
                'detection_confidence': 0.6,
                'tracking_confidence': 0.4,
                'frame_width': 1280,
                'frame_height': 720,
                'model_complexity': 2,
                'fps_limit': 60
            }
        }
        
        return profiles.get(profile_name, profiles['balanced'])
    
    def apply_profile(self, profile_name: str):
        """Apply a performance profile"""
        profile = self.get_profile(profile_name)
        self.config.update(profile)
        self.save_config(self.config)
        self.logger.info(f"Applied profile: {profile_name}")
