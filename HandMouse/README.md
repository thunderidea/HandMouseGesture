# 🖐️ Advanced Hand Gesture & Voice Control System

A powerful, feature-rich hand gesture and voice control system for Windows with extensive customization options.

## ✨ Features

### 🎯 Gesture Controls
- **11+ Pre-configured Gestures** with smooth detection
- **Custom Gesture Mapping** via GUI
- **Gesture Training Module** for personalized controls
- **Real-time Visual Feedback**

### 🎤 Voice Commands
- **30+ Built-in Commands** for system control
- **Custom Voice Command Editor**
- **Multi-language Support** (English default)
- **Wake Word Detection**

### 🔧 Advanced Settings
- **Comprehensive Settings Panel** with tabs
- **Gesture Sensitivity Controls**
- **Smoothing & Filtering Options**
- **Performance Profiles**
- **Theme Customization**

### 💻 System Integration
- **Application Control** (Open, Close, Switch)
- **Media Controls** (Volume, Playback)
- **Brightness Control**
- **Screenshot Capture**
- **Window Management**
- **Clipboard Operations**

## 📁 Project Structure

```
HandMouse/
├── main.py                 # Main application entry
├── requirements.txt        # Dependencies
├── config/
│   ├── settings.json      # User settings
│   ├── gestures.json      # Gesture mappings
│   └── voice_commands.json # Voice commands
├── core/
│   ├── __init__.py
│   ├── gesture_recognizer.py
│   ├── hand_tracker.py
│   └── gesture_processor.py
├── voice/
│   ├── __init__.py
│   ├── voice_controller.py
│   ├── command_processor.py
│   └── speech_engine.py
├── gui/
│   ├── __init__.py
│   ├── main_window.py
│   ├── settings_panel.py
│   ├── gesture_editor.py
│   └── voice_editor.py
├── controllers/
│   ├── __init__.py
│   ├── mouse_controller.py
│   ├── keyboard_controller.py
│   ├── system_controller.py
│   └── media_controller.py
├── utils/
│   ├── __init__.py
│   ├── config_manager.py
│   ├── logger.py
│   └── helpers.py
├── overlay/
│   ├── __init__.py
│   ├── visual_feedback.py
│   └── status_overlay.py
├── training/
│   ├── __init__.py
│   ├── gesture_trainer.py
│   └── data_collector.py
└── assets/
    ├── icons/
    ├── sounds/
    └── themes/
```

## 🚀 Installation

1. Install Python 3.8 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## 🎮 Default Gestures

| Gesture | Action |
|---------|--------|
| ☝️ Index Pointing | Cursor Movement |
| 👆 L-shape (Thumb+Index) | Left Click |
| ✌️ Peace Sign | Right Click |
| 🤟 Rock Sign | Scroll Up |
| 🤙 Call Sign | Scroll Down |
| ✊ Closed Fist | Drag Start |
| ✋ Open Hand | Drag End |
| 🖕 Middle Finger | Alt+Tab |
| 👍 Thumbs Up | Volume Up |
| 👎 Thumbs Down | Volume Down |
| Three Fingers | Voice Command |

## 🎤 Voice Commands

- System: "Open Chrome", "Open Settings", "Take Screenshot"
- Navigation: "Go Back", "Go Forward", "Switch App"
- Media: "Volume Up", "Volume Down", "Mute"
- Window: "Minimize", "Maximize", "Close"
- Edit: "Copy This", "Paste Here", "Delete This"

## ⚙️ Configuration

Access the settings panel to:
- Customize gesture mappings
- Add custom voice commands
- Adjust sensitivity and smoothing
- Configure performance profiles
- Change themes and visual feedback

## 📝 License

MIT License

## 👥 Author

Advanced Hand Control System - 2024
