"""
Settings Panel Module
Comprehensive settings interface with multiple categories
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import json
from pathlib import Path
import logging

class SettingsPanel:
    """Advanced settings panel with categorized options"""
    
    def __init__(self, parent, system):
        self.parent = parent
        self.system = system
        self.logger = logging.getLogger('SettingsPanel')
        
        # Load current settings
        self.settings = system.config.copy()
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create settings UI with tabs"""
        # Create scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(self.parent)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Settings categories
        self._create_general_settings()
        self._create_gesture_settings()
        self._create_voice_settings()
        self._create_mouse_settings()
        self._create_performance_settings()
        self._create_appearance_settings()
        self._create_advanced_settings()
        
        # Save/Reset buttons
        self._create_action_buttons()
    
    def _create_section(self, title):
        """Create a settings section"""
        frame = ctk.CTkFrame(self.scroll_frame)
        frame.pack(fill="x", padx=10, pady=10)
        
        header = ctk.CTkLabel(frame, text=title, font=("Segoe UI", 16, "bold"))
        header.pack(anchor="w", padx=10, pady=10)
        
        return frame
    
    def _create_general_settings(self):
        """Create general settings section"""
        frame = self._create_section("🔧 General Settings")
        
        # Auto-start
        self.autostart_var = ctk.BooleanVar(value=self.settings.get('auto_start', False))
        ctk.CTkCheckBox(
            frame,
            text="Start with Windows",
            variable=self.autostart_var,
            command=lambda: self.update_setting('auto_start', self.autostart_var.get())
        ).pack(anchor="w", padx=20, pady=5)
        
        # Minimize to tray
        self.tray_var = ctk.BooleanVar(value=self.settings.get('minimize_to_tray', True))
        ctk.CTkCheckBox(
            frame,
            text="Minimize to system tray",
            variable=self.tray_var,
            command=lambda: self.update_setting('minimize_to_tray', self.tray_var.get())
        ).pack(anchor="w", padx=20, pady=5)
        
        # Show notifications
        self.notif_var = ctk.BooleanVar(value=self.settings.get('show_notifications', True))
        ctk.CTkCheckBox(
            frame,
            text="Show notifications",
            variable=self.notif_var,
            command=lambda: self.update_setting('show_notifications', self.notif_var.get())
        ).pack(anchor="w", padx=20, pady=5)
        
        # Language
        lang_frame = ctk.CTkFrame(frame, fg_color="transparent")
        lang_frame.pack(anchor="w", padx=20, pady=10)
        
        ctk.CTkLabel(lang_frame, text="Language:").pack(side="left", padx=(0, 10))
        self.language_menu = ctk.CTkOptionMenu(
            lang_frame,
            values=["English", "Spanish", "French", "German", "Chinese"],
            command=self.change_language
        )
        self.language_menu.set(self.settings.get('language', 'English'))
        self.language_menu.pack(side="left")
    
    def _create_gesture_settings(self):
        """Create gesture settings section"""
        frame = self._create_section("✋ Gesture Settings")
        
        # Detection confidence
        conf_frame = ctk.CTkFrame(frame, fg_color="transparent")
        conf_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(conf_frame, text="Detection Confidence:").pack(anchor="w")
        self.detection_slider = ctk.CTkSlider(
            conf_frame,
            from_=0.3,
            to=1.0,
            number_of_steps=70,
            command=lambda v: self.update_setting('detection_confidence', round(v, 2))
        )
        self.detection_slider.set(self.settings.get('detection_confidence', 0.7))
        self.detection_slider.pack(fill="x", pady=5)
        self.detection_label = ctk.CTkLabel(conf_frame, text=f"{self.settings.get('detection_confidence', 0.7):.2f}")
        self.detection_label.pack(anchor="w")
        
        # Tracking confidence
        track_frame = ctk.CTkFrame(frame, fg_color="transparent")
        track_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(track_frame, text="Tracking Confidence:").pack(anchor="w")
        self.tracking_slider = ctk.CTkSlider(
            track_frame,
            from_=0.3,
            to=1.0,
            number_of_steps=70,
            command=lambda v: self.update_setting('tracking_confidence', round(v, 2))
        )
        self.tracking_slider.set(self.settings.get('tracking_confidence', 0.5))
        self.tracking_slider.pack(fill="x", pady=5)
        self.tracking_label = ctk.CTkLabel(track_frame, text=f"{self.settings.get('tracking_confidence', 0.5):.2f}")
        self.tracking_label.pack(anchor="w")
        
        # Gesture hold time
        hold_frame = ctk.CTkFrame(frame, fg_color="transparent")
        hold_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(hold_frame, text="Gesture Hold Time (ms):").pack(anchor="w")
        self.hold_slider = ctk.CTkSlider(
            hold_frame,
            from_=100,
            to=1000,
            number_of_steps=90,
            command=lambda v: self.update_setting('gesture_hold_time', int(v))
        )
        self.hold_slider.set(self.settings.get('gesture_hold_time', 300))
        self.hold_slider.pack(fill="x", pady=5)
        self.hold_label = ctk.CTkLabel(hold_frame, text=f"{self.settings.get('gesture_hold_time', 300)} ms")
        self.hold_label.pack(anchor="w")
        
        # Smoothing
        self.smoothing_var = ctk.BooleanVar(value=self.settings.get('smoothing_enabled', True))
        ctk.CTkCheckBox(
            frame,
            text="Enable gesture smoothing",
            variable=self.smoothing_var,
            command=lambda: self.update_setting('smoothing_enabled', self.smoothing_var.get())
        ).pack(anchor="w", padx=20, pady=5)
        
        # Draw landmarks
        self.draw_var = ctk.BooleanVar(value=self.settings.get('draw_landmarks', True))
        ctk.CTkCheckBox(
            frame,
            text="Draw hand landmarks",
            variable=self.draw_var,
            command=lambda: self.update_setting('draw_landmarks', self.draw_var.get())
        ).pack(anchor="w", padx=20, pady=5)
    
    def _create_voice_settings(self):
        """Create voice settings section"""
        frame = self._create_section("🎤 Voice Settings")
        
        # Voice language
        lang_frame = ctk.CTkFrame(frame, fg_color="transparent")
        lang_frame.pack(anchor="w", padx=20, pady=10)
        
        ctk.CTkLabel(lang_frame, text="Voice Language:").pack(side="left", padx=(0, 10))
        self.voice_lang_menu = ctk.CTkOptionMenu(
            lang_frame,
            values=["en-US", "en-GB", "es-ES", "fr-FR", "de-DE", "zh-CN"],
            command=lambda v: self.update_setting('voice_language', v)
        )
        self.voice_lang_menu.set(self.settings.get('voice_language', 'en-US'))
        self.voice_lang_menu.pack(side="left")
        
        # Continuous listening
        self.continuous_var = ctk.BooleanVar(value=self.settings.get('continuous_listening', True))
        ctk.CTkCheckBox(
            frame,
            text="Continuous listening",
            variable=self.continuous_var,
            command=lambda: self.update_setting('continuous_listening', self.continuous_var.get())
        ).pack(anchor="w", padx=20, pady=5)
        
        # Voice feedback
        self.feedback_var = ctk.BooleanVar(value=self.settings.get('voice_feedback', True))
        ctk.CTkCheckBox(
            frame,
            text="Enable voice feedback",
            variable=self.feedback_var,
            command=lambda: self.update_setting('voice_feedback', self.feedback_var.get())
        ).pack(anchor="w", padx=20, pady=5)
        
        # Wake word
        wake_frame = ctk.CTkFrame(frame, fg_color="transparent")
        wake_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(wake_frame, text="Wake Word:").pack(anchor="w")
        self.wake_entry = ctk.CTkEntry(wake_frame, placeholder_text="e.g., Hey Computer")
        self.wake_entry.pack(fill="x", pady=5)
        wake_word = self.settings.get('wake_word', '')
        if wake_word:
            self.wake_entry.insert(0, wake_word)
        
        # Speech rate
        rate_frame = ctk.CTkFrame(frame, fg_color="transparent")
        rate_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(rate_frame, text="Speech Rate:").pack(anchor="w")
        self.rate_slider = ctk.CTkSlider(
            rate_frame,
            from_=50,
            to=300,
            number_of_steps=250,
            command=lambda v: self.update_setting('speech_rate', int(v))
        )
        self.rate_slider.set(self.settings.get('speech_rate', 150))
        self.rate_slider.pack(fill="x", pady=5)
        self.rate_label = ctk.CTkLabel(rate_frame, text=f"{self.settings.get('speech_rate', 150)} wpm")
        self.rate_label.pack(anchor="w")
    
    def _create_mouse_settings(self):
        """Create mouse settings section"""
        frame = self._create_section("🖱️ Mouse Settings")
        
        # Sensitivity
        sens_frame = ctk.CTkFrame(frame, fg_color="transparent")
        sens_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(sens_frame, text="Mouse Sensitivity:").pack(anchor="w")
        self.sens_slider = ctk.CTkSlider(
            sens_frame,
            from_=0.5,
            to=3.0,
            number_of_steps=50,
            command=lambda v: self.update_setting('mouse_sensitivity', round(v, 1))
        )
        self.sens_slider.set(self.settings.get('mouse_sensitivity', 1.5))
        self.sens_slider.pack(fill="x", pady=5)
        self.sens_label = ctk.CTkLabel(sens_frame, text=f"{self.settings.get('mouse_sensitivity', 1.5):.1f}x")
        self.sens_label.pack(anchor="w")
        
        # Acceleration
        accel_frame = ctk.CTkFrame(frame, fg_color="transparent")
        accel_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(accel_frame, text="Mouse Acceleration:").pack(anchor="w")
        self.accel_slider = ctk.CTkSlider(
            accel_frame,
            from_=1.0,
            to=2.0,
            number_of_steps=20,
            command=lambda v: self.update_setting('mouse_acceleration', round(v, 1))
        )
        self.accel_slider.set(self.settings.get('mouse_acceleration', 1.2))
        self.accel_slider.pack(fill="x", pady=5)
        self.accel_label = ctk.CTkLabel(accel_frame, text=f"{self.settings.get('mouse_acceleration', 1.2):.1f}x")
        self.accel_label.pack(anchor="w")
        
        # Scroll sensitivity
        scroll_frame = ctk.CTkFrame(frame, fg_color="transparent")
        scroll_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(scroll_frame, text="Scroll Sensitivity:").pack(anchor="w")
        self.scroll_slider = ctk.CTkSlider(
            scroll_frame,
            from_=0.5,
            to=3.0,
            number_of_steps=50,
            command=lambda v: self.update_setting('scroll_sensitivity', round(v, 1))
        )
        self.scroll_slider.set(self.settings.get('scroll_sensitivity', 1.0))
        self.scroll_slider.pack(fill="x", pady=5)
        self.scroll_label = ctk.CTkLabel(scroll_frame, text=f"{self.settings.get('scroll_sensitivity', 1.0):.1f}x")
        self.scroll_label.pack(anchor="w")
        
        # Click delay
        click_frame = ctk.CTkFrame(frame, fg_color="transparent")
        click_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(click_frame, text="Click Delay (ms):").pack(anchor="w")
        self.click_slider = ctk.CTkSlider(
            click_frame,
            from_=50,
            to=500,
            number_of_steps=45,
            command=lambda v: self.update_setting('click_delay', int(v))
        )
        self.click_slider.set(self.settings.get('click_delay', 100))
        self.click_slider.pack(fill="x", pady=5)
        self.click_label = ctk.CTkLabel(click_frame, text=f"{self.settings.get('click_delay', 100)} ms")
        self.click_label.pack(anchor="w")
    
    def _create_performance_settings(self):
        """Create performance settings section"""
        frame = self._create_section("⚡ Performance Settings")
        
        # Camera settings
        cam_frame = ctk.CTkFrame(frame, fg_color="transparent")
        cam_frame.pack(anchor="w", padx=20, pady=10)
        
        ctk.CTkLabel(cam_frame, text="Camera:").pack(side="left", padx=(0, 10))
        self.camera_menu = ctk.CTkOptionMenu(
            cam_frame,
            values=["Camera 0", "Camera 1", "Camera 2"],
            command=self.change_camera
        )
        self.camera_menu.set(f"Camera {self.settings.get('camera_index', 0)}")
        self.camera_menu.pack(side="left")
        
        # Resolution
        res_frame = ctk.CTkFrame(frame, fg_color="transparent")
        res_frame.pack(anchor="w", padx=20, pady=10)
        
        ctk.CTkLabel(res_frame, text="Resolution:").pack(side="left", padx=(0, 10))
        self.resolution_menu = ctk.CTkOptionMenu(
            res_frame,
            values=["640x480", "1280x720", "1920x1080"],
            command=self.change_resolution
        )
        current_res = f"{self.settings.get('frame_width', 640)}x{self.settings.get('frame_height', 480)}"
        self.resolution_menu.set(current_res)
        self.resolution_menu.pack(side="left")
        
        # Model complexity
        model_frame = ctk.CTkFrame(frame, fg_color="transparent")
        model_frame.pack(anchor="w", padx=20, pady=10)
        
        ctk.CTkLabel(model_frame, text="Model Complexity:").pack(side="left", padx=(0, 10))
        self.model_menu = ctk.CTkOptionMenu(
            model_frame,
            values=["Light (0)", "Medium (1)", "Full (2)"],
            command=self.change_model
        )
        self.model_menu.set(f"Medium ({self.settings.get('model_complexity', 1)})")
        self.model_menu.pack(side="left")
        
        # Max hands
        hands_frame = ctk.CTkFrame(frame, fg_color="transparent")
        hands_frame.pack(anchor="w", padx=20, pady=10)
        
        ctk.CTkLabel(hands_frame, text="Max Hands:").pack(side="left", padx=(0, 10))
        self.hands_menu = ctk.CTkOptionMenu(
            hands_frame,
            values=["1", "2"],
            command=lambda v: self.update_setting('max_hands', int(v))
        )
        self.hands_menu.set(str(self.settings.get('max_hands', 1)))
        self.hands_menu.pack(side="left")
    
    def _create_appearance_settings(self):
        """Create appearance settings section"""
        frame = self._create_section("🎨 Appearance Settings")
        
        # Theme
        theme_frame = ctk.CTkFrame(frame, fg_color="transparent")
        theme_frame.pack(anchor="w", padx=20, pady=10)
        
        ctk.CTkLabel(theme_frame, text="Theme:").pack(side="left", padx=(0, 10))
        self.theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["Dark", "Light", "System"],
            command=self.change_theme
        )
        self.theme_menu.set(self.settings.get('theme', 'Dark'))
        self.theme_menu.pack(side="left")
        
        # Color scheme
        color_frame = ctk.CTkFrame(frame, fg_color="transparent")
        color_frame.pack(anchor="w", padx=20, pady=10)
        
        ctk.CTkLabel(color_frame, text="Color Scheme:").pack(side="left", padx=(0, 10))
        self.color_menu = ctk.CTkOptionMenu(
            color_frame,
            values=["Blue", "Green", "Red", "Purple", "Orange"],
            command=self.change_color
        )
        self.color_menu.set(self.settings.get('color_scheme', 'Blue'))
        self.color_menu.pack(side="left")
        
        # Overlay settings
        self.overlay_var = ctk.BooleanVar(value=self.settings.get('show_overlay', True))
        ctk.CTkCheckBox(
            frame,
            text="Show status overlay",
            variable=self.overlay_var,
            command=lambda: self.update_setting('show_overlay', self.overlay_var.get())
        ).pack(anchor="w", padx=20, pady=5)
        
        # Camera feed
        self.camera_feed_var = ctk.BooleanVar(value=self.settings.get('show_camera_feed', False))
        ctk.CTkCheckBox(
            frame,
            text="Show camera feed",
            variable=self.camera_feed_var,
            command=lambda: self.update_setting('show_camera_feed', self.camera_feed_var.get())
        ).pack(anchor="w", padx=20, pady=5)
        
        # Transparency
        trans_frame = ctk.CTkFrame(frame, fg_color="transparent")
        trans_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(trans_frame, text="Window Transparency:").pack(anchor="w")
        self.trans_slider = ctk.CTkSlider(
            trans_frame,
            from_=0.5,
            to=1.0,
            number_of_steps=50,
            command=lambda v: self.update_setting('window_transparency', round(v, 2))
        )
        self.trans_slider.set(self.settings.get('window_transparency', 1.0))
        self.trans_slider.pack(fill="x", pady=5)
        self.trans_label = ctk.CTkLabel(trans_frame, text=f"{int(self.settings.get('window_transparency', 1.0) * 100)}%")
        self.trans_label.pack(anchor="w")
    
    def _create_advanced_settings(self):
        """Create advanced settings section"""
        frame = self._create_section("🔬 Advanced Settings")
        
        # Debug mode
        self.debug_var = ctk.BooleanVar(value=self.settings.get('debug_mode', False))
        ctk.CTkCheckBox(
            frame,
            text="Enable debug mode",
            variable=self.debug_var,
            command=lambda: self.update_setting('debug_mode', self.debug_var.get())
        ).pack(anchor="w", padx=20, pady=5)
        
        # Log level
        log_frame = ctk.CTkFrame(frame, fg_color="transparent")
        log_frame.pack(anchor="w", padx=20, pady=10)
        
        ctk.CTkLabel(log_frame, text="Log Level:").pack(side="left", padx=(0, 10))
        self.log_menu = ctk.CTkOptionMenu(
            log_frame,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            command=lambda v: self.update_setting('log_level', v)
        )
        self.log_menu.set(self.settings.get('log_level', 'INFO'))
        self.log_menu.pack(side="left")
        
        # Export/Import settings
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(anchor="w", padx=20, pady=10)
        
        ctk.CTkButton(
            button_frame,
            text="Export Settings",
            command=self.export_settings,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Import Settings",
            command=self.import_settings,
            width=120
        ).pack(side="left", padx=5)
        
        # Reset to defaults
        ctk.CTkButton(
            frame,
            text="Reset to Defaults",
            command=self.reset_defaults,
            fg_color="red",
            width=150
        ).pack(anchor="w", padx=20, pady=10)
    
    def _create_action_buttons(self):
        """Create save/cancel buttons"""
        button_frame = ctk.CTkFrame(self.scroll_frame)
        button_frame.pack(fill="x", padx=10, pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="Apply Settings",
            command=self.apply_settings,
            width=150,
            height=40,
            font=("Segoe UI", 14, "bold")
        ).pack(side="right", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="Save & Apply",
            command=self.save_settings,
            width=150,
            height=40,
            font=("Segoe UI", 14, "bold"),
            fg_color="green"
        ).pack(side="right", padx=10)
    
    # Update methods
    def update_setting(self, key, value):
        """Update a setting value"""
        self.settings[key] = value
        
        # Update labels for sliders
        if key == 'detection_confidence':
            self.detection_label.configure(text=f"{value:.2f}")
        elif key == 'tracking_confidence':
            self.tracking_label.configure(text=f"{value:.2f}")
        elif key == 'gesture_hold_time':
            self.hold_label.configure(text=f"{value} ms")
        elif key == 'speech_rate':
            self.rate_label.configure(text=f"{value} wpm")
        elif key == 'mouse_sensitivity':
            self.sens_label.configure(text=f"{value:.1f}x")
        elif key == 'mouse_acceleration':
            self.accel_label.configure(text=f"{value:.1f}x")
        elif key == 'scroll_sensitivity':
            self.scroll_label.configure(text=f"{value:.1f}x")
        elif key == 'click_delay':
            self.click_label.configure(text=f"{value} ms")
        elif key == 'window_transparency':
            self.trans_label.configure(text=f"{int(value * 100)}%")
    
    def change_language(self, value):
        """Change application language"""
        self.update_setting('language', value)
    
    def change_camera(self, value):
        """Change camera index"""
        index = int(value.split()[-1])
        self.update_setting('camera_index', index)
    
    def change_resolution(self, value):
        """Change camera resolution"""
        width, height = map(int, value.split('x'))
        self.update_setting('frame_width', width)
        self.update_setting('frame_height', height)
    
    def change_model(self, value):
        """Change model complexity"""
        complexity = int(value.split('(')[1].split(')')[0])
        self.update_setting('model_complexity', complexity)
    
    def change_theme(self, value):
        """Change application theme"""
        self.update_setting('theme', value)
        ctk.set_appearance_mode(value.lower())
    
    def change_color(self, value):
        """Change color scheme"""
        self.update_setting('color_scheme', value)
        # Apply color scheme
        color_themes = {
            'Blue': 'blue',
            'Green': 'green',
            'Red': 'dark-blue',
            'Purple': 'blue',
            'Orange': 'blue'
        }
        ctk.set_default_color_theme(color_themes.get(value, 'blue'))
    
    def apply_settings(self):
        """Apply settings without saving"""
        # Update wake word
        wake_word = self.wake_entry.get().strip()
        if wake_word:
            self.settings['wake_word'] = wake_word
        
        # Apply to system
        self.system.update_settings(self.settings)
        messagebox.showinfo("Settings", "Settings applied successfully!")
    
    def save_settings(self):
        """Save and apply settings"""
        self.apply_settings()
        
        # Save to file
        try:
            with open('config/settings.json', 'w') as f:
                json.dump(self.settings, f, indent=2)
            messagebox.showinfo("Settings", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def export_settings(self):
        """Export settings to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.settings, f, indent=2)
                messagebox.showinfo("Export", "Settings exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export settings: {e}")
    
    def import_settings(self):
        """Import settings from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    imported = json.load(f)
                self.settings.update(imported)
                self.apply_settings()
                messagebox.showinfo("Import", "Settings imported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import settings: {e}")
    
    def reset_defaults(self):
        """Reset to default settings"""
        if messagebox.askyesno("Reset", "Are you sure you want to reset all settings to defaults?"):
            # Load default settings
            from utils.config_manager import ConfigManager
            config_manager = ConfigManager()
            self.settings = config_manager.get_default_config()
            self.apply_settings()
            messagebox.showinfo("Reset", "Settings reset to defaults!")
