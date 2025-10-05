import json
from pathlib import Path

# Path to settings file
settings_path = Path('config/settings.json')

# Read current settings
with open(settings_path, 'r') as f:
    settings = json.load(f)

# Update settings for better finger movement detection
updates = {
    # Make tracking more sensitive to small movements
    'tracking_confidence': 0.4,     # Reduced to detect smaller movements
    'detection_confidence': 0.6,    # Slightly reduced for better responsiveness
    
    # Adjust movement sensitivity for fingers
    'mouse_sensitivity': 2.2,       # Increased to detect smaller movements
    'cursor_smoothing': 0.5,        # Balanced smoothing
    'mouse_smoothing': 0.5,         # Balanced smoothing
    'smoothing_factor': 0.6,        # Slightly reduced for more responsiveness
    
    # Enable detailed logging for debugging
    'debug_mode': True,
    'log_level': 'DEBUG',
    
    # Ensure visual feedback is enabled
    'show_camera_feed': True,
    'draw_landmarks': True
}

# Apply updates
settings.update(updates)

# Save updated settings
with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2)

print("Settings updated for better finger movement detection!")
print("Please restart the application for changes to take effect.")
