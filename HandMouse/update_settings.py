import json
import os
from pathlib import Path

# Path to settings file
settings_path = Path('config/settings.json')

# Read current settings
with open(settings_path, 'r') as f:
    settings = json.load(f)

# Update settings
updates = {
    # Enable camera feed for debugging
    'show_camera_feed': True,
    
    # Optimize mouse settings
    'mouse_sensitivity': 2.0,  # Increase sensitivity
    'mouse_smoothing': 0.5,   # Smoother cursor movement
    'cursor_smoothing': 0.4,  # Smoother cursor movement
    
    # Gesture settings
    'gesture_hold_time': 0.2,  # Faster response time
    'detection_confidence': 0.7,
    'tracking_confidence': 0.5,
    
    # Enable debug mode for more logging
    'debug_mode': True,
    'log_level': 'DEBUG'
}

# Apply updates
settings.update(updates)

# Save updated settings
with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2)

print("Settings updated successfully!")
print("Please restart the application for changes to take effect.")
