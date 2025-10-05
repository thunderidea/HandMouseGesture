import json
import os
from pathlib import Path

# Path to settings file
settings_path = Path('config/settings.json')

# Read current settings
with open(settings_path, 'r') as f:
    settings = json.load(f)

# Update settings for smooth and stable cursor movement
updates = {
    # Mouse movement settings
    'mouse_sensitivity': 1.7,      # Slightly reduced for better control
    'mouse_smoothing': 0.7,        # Increased for smoother movement
    'cursor_smoothing': 0.6,       # Increased for more stable cursor
    'mouse_acceleration': 1.1,     # Reduced acceleration for more linear movement
    
    # Gesture settings
    'gesture_hold_time': 0.15,     # Slightly faster response
    'smoothing_factor': 0.7,       # Increased for smoother tracking
    'history_size': 8,             # Increased history for better averaging
    'active_zone_margin': 0.15,    # Slightly larger active zone
    
    # Performance
    'fps_limit': 60,               # Increased FPS for smoother updates
    'buffer_size': 15,             # Increased buffer for stability
    
    # Enable camera feed for visual feedback
    'show_camera_feed': True,
    'draw_landmarks': True,
    
    # Debugging
    'debug_mode': True,
    'log_level': 'DEBUG'
}

# Apply updates
settings.update(updates)

# Save updated settings
with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2)

print("Cursor movement settings have been optimized for smooth and stable performance!")
print("Please restart the application for changes to take effect.")
