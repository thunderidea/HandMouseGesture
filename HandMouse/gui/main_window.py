"""
Main GUI Window
Advanced interface with system tray integration
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
import sys
from PIL import Image, ImageTk
import pystray
from pystray import MenuItem as item
import logging
from pathlib import Path

from .settings_panel import SettingsPanel
from .gesture_editor import GestureEditor
from .voice_editor import VoiceEditor

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MainApplication:
    """Main application window with comprehensive controls"""
    
    def __init__(self, system_controller):
        self.system = system_controller
        self.logger = logging.getLogger('MainApplication')
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Advanced Hand & Voice Control System")
        self.root.geometry("900x650")
        
        # Set window icon
        self.root.iconbitmap(default='assets/icons/app.ico') if Path('assets/icons/app.ico').exists() else None
        
        # System tray
        self.tray_icon = None
        self.minimized_to_tray = False
        
        # Initialize UI
        self._create_ui()
        
        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind("<Unmap>", self.on_minimize)
        
        # Start status update thread
        self.update_thread = threading.Thread(target=self._update_status_loop, daemon=True)
        self.update_thread.start()
    
    def _create_ui(self):
        """Create the main UI"""
        # Create header
        self._create_header()
        
        # Create main content area with tabs
        self._create_tabs()
        
        # Create status bar
        self._create_status_bar()
    
    def _create_header(self):
        """Create header with title and main controls"""
        header_frame = ctk.CTkFrame(self.root, height=80)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="🖐️ Advanced Hand & Voice Control",
            font=("Segoe UI", 24, "bold")
        )
        title_label.pack(side="left", padx=20, pady=20)
        
        # Main control buttons
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.pack(side="right", padx=20, pady=20)
        
        # Gesture toggle
        self.gesture_switch = ctk.CTkSwitch(
            controls_frame,
            text="Gesture Control",
            command=self.toggle_gesture,
            width=60,
            button_color="#4CAF50",
            progress_color="#81C784"
        )
        self.gesture_switch.pack(side="left", padx=10)
        if self.system.gesture_enabled:
            self.gesture_switch.select()
        
        # Voice toggle
        self.voice_switch = ctk.CTkSwitch(
            controls_frame,
            text="Voice Control",
            command=self.toggle_voice,
            width=60,
            button_color="#2196F3",
            progress_color="#64B5F6"
        )
        self.voice_switch.pack(side="left", padx=10)
        if self.system.voice_enabled:
            self.voice_switch.select()
    
    def _create_tabs(self):
        """Create tabbed interface"""
        self.tabview = ctk.CTkTabview(self.root, width=880, height=450)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs
        self.tabview.add("📊 Dashboard")
        self.tabview.add("⚙️ Settings")
        self.tabview.add("✋ Gestures")
        self.tabview.add("🎤 Voice Commands")
        self.tabview.add("📈 Performance")
        self.tabview.add("ℹ️ About")
        
        # Dashboard tab
        self._create_dashboard_tab(self.tabview.tab("📊 Dashboard"))
        
        # Settings tab
        self.settings_panel = SettingsPanel(self.tabview.tab("⚙️ Settings"), self.system)
        
        # Gestures tab
        self.gesture_editor = GestureEditor(self.tabview.tab("✋ Gestures"), self.system)
        
        # Voice Commands tab
        self.voice_editor = VoiceEditor(self.tabview.tab("🎤 Voice Commands"), self.system)
        
        # Performance tab
        self._create_performance_tab(self.tabview.tab("📈 Performance"))
        
        # About tab
        self._create_about_tab(self.tabview.tab("ℹ️ About"))
    
    def _create_dashboard_tab(self, parent):
        """Create dashboard with real-time status"""
        # Main container
        container = ctk.CTkFrame(parent)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Status cards row
        cards_frame = ctk.CTkFrame(container)
        cards_frame.pack(fill="x", pady=(0, 20))
        
        # Gesture status card
        gesture_card = ctk.CTkFrame(cards_frame, width=200, height=120)
        gesture_card.pack(side="left", padx=10, pady=10)
        gesture_card.pack_propagate(False)
        
        ctk.CTkLabel(gesture_card, text="Gesture Status", font=("Segoe UI", 14, "bold")).pack(pady=10)
        self.gesture_status_label = ctk.CTkLabel(gesture_card, text="Inactive", font=("Segoe UI", 12))
        self.gesture_status_label.pack()
        self.current_gesture_label = ctk.CTkLabel(gesture_card, text="No gesture", font=("Segoe UI", 10))
        self.current_gesture_label.pack()
        self.fps_label = ctk.CTkLabel(gesture_card, text="FPS: 0", font=("Segoe UI", 10))
        self.fps_label.pack()
        
        # Voice status card
        voice_card = ctk.CTkFrame(cards_frame, width=200, height=120)
        voice_card.pack(side="left", padx=10, pady=10)
        voice_card.pack_propagate(False)
        
        ctk.CTkLabel(voice_card, text="Voice Status", font=("Segoe UI", 14, "bold")).pack(pady=10)
        self.voice_status_label = ctk.CTkLabel(voice_card, text="Inactive", font=("Segoe UI", 12))
        self.voice_status_label.pack()
        self.voice_listening_label = ctk.CTkLabel(voice_card, text="Not listening", font=("Segoe UI", 10))
        self.voice_listening_label.pack()
        
        # System status card
        system_card = ctk.CTkFrame(cards_frame, width=200, height=120)
        system_card.pack(side="left", padx=10, pady=10)
        system_card.pack_propagate(False)
        
        ctk.CTkLabel(system_card, text="System", font=("Segoe UI", 14, "bold")).pack(pady=10)
        self.cpu_label = ctk.CTkLabel(system_card, text="CPU: 0%", font=("Segoe UI", 10))
        self.cpu_label.pack()
        self.memory_label = ctk.CTkLabel(system_card, text="Memory: 0%", font=("Segoe UI", 10))
        self.memory_label.pack()
        
        # Quick actions
        actions_frame = ctk.CTkFrame(container)
        actions_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(actions_frame, text="Quick Actions", font=("Segoe UI", 16, "bold")).pack(pady=10)
        
        buttons_frame = ctk.CTkFrame(actions_frame)
        buttons_frame.pack()
        
        # Quick action buttons
        ctk.CTkButton(
            buttons_frame,
            text="📷 Screenshot",
            command=self.take_screenshot,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="🔊 Test Voice",
            command=self.test_voice,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="📹 Camera View",
            command=self.toggle_camera_view,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="🔄 Calibrate",
            command=self.calibrate_system,
            width=120
        ).pack(side="left", padx=5)
        
        # Activity log
        log_frame = ctk.CTkFrame(container)
        log_frame.pack(fill="both", expand=True, pady=20)
        
        ctk.CTkLabel(log_frame, text="Activity Log", font=("Segoe UI", 14, "bold")).pack(pady=5)
        
        self.log_text = ctk.CTkTextbox(log_frame, height=150)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _create_performance_tab(self, parent):
        """Create performance monitoring tab"""
        container = ctk.CTkFrame(parent)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Performance metrics
        metrics_frame = ctk.CTkFrame(container)
        metrics_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(metrics_frame, text="Performance Metrics", font=("Segoe UI", 16, "bold")).pack(pady=10)
        
        # Metrics display
        self.metrics_labels = {}
        metrics = ['Recognition Rate', 'Response Time', 'CPU Usage', 'Memory Usage', 'Frame Rate']
        
        for metric in metrics:
            row = ctk.CTkFrame(metrics_frame)
            row.pack(fill="x", padx=20, pady=5)
            
            ctk.CTkLabel(row, text=f"{metric}:", width=150, anchor="w").pack(side="left")
            label = ctk.CTkLabel(row, text="N/A", anchor="w")
            label.pack(side="left")
            self.metrics_labels[metric] = label
        
        # Performance profiles
        profiles_frame = ctk.CTkFrame(container)
        profiles_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(profiles_frame, text="Performance Profile", font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        profile_buttons = ctk.CTkFrame(profiles_frame)
        profile_buttons.pack()
        
        profiles = [
            ("🔋 Power Saver", self.set_power_saver),
            ("⚖️ Balanced", self.set_balanced),
            ("🚀 High Performance", self.set_high_performance)
        ]
        
        for text, command in profiles:
            ctk.CTkButton(
                profile_buttons,
                text=text,
                command=command,
                width=140
            ).pack(side="left", padx=5)
    
    def _create_about_tab(self, parent):
        """Create about tab"""
        container = ctk.CTkFrame(parent)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # App info
        info_frame = ctk.CTkFrame(container)
        info_frame.pack(pady=20)
        
        ctk.CTkLabel(
            info_frame,
            text="Advanced Hand & Voice Control System",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text="Version 2.0.0",
            font=("Segoe UI", 14)
        ).pack(pady=5)
        
        ctk.CTkLabel(
            info_frame,
            text="A powerful gesture and voice control system for Windows",
            font=("Segoe UI", 12)
        ).pack(pady=5)
        
        # Features
        features_frame = ctk.CTkFrame(container)
        features_frame.pack(fill="x", padx=50, pady=20)
        
        ctk.CTkLabel(
            features_frame,
            text="Features:",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=10)
        
        features = [
            "✋ 11+ Pre-configured gestures",
            "🎤 30+ Voice commands",
            "⚙️ Extensive customization options",
            "📊 Real-time performance monitoring",
            "🎨 Custom gesture training",
            "🔧 Advanced settings panel",
            "💾 Configuration management",
            "🖼️ Visual feedback system"
        ]
        
        for feature in features:
            ctk.CTkLabel(
                features_frame,
                text=feature,
                font=("Segoe UI", 11),
                anchor="w"
            ).pack(anchor="w", padx=20, pady=2)
        
        # Links
        links_frame = ctk.CTkFrame(container)
        links_frame.pack(pady=20)
        
        ctk.CTkButton(
            links_frame,
            text="📖 Documentation",
            command=lambda: self.open_link("docs"),
            width=140
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            links_frame,
            text="🐛 Report Issue",
            command=lambda: self.open_link("issues"),
            width=140
        ).pack(side="left", padx=5)
    
    def _create_status_bar(self):
        """Create status bar at bottom"""
        self.status_bar = ctk.CTkFrame(self.root, height=30)
        self.status_bar.pack(fill="x", side="bottom", padx=10, pady=(0, 10))
        
        self.status_text = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=("Segoe UI", 10)
        )
        self.status_text.pack(side="left", padx=10)
        
        # Connection status
        self.connection_label = ctk.CTkLabel(
            self.status_bar,
            text="● Connected",
            font=("Segoe UI", 10),
            text_color="green"
        )
        self.connection_label.pack(side="right", padx=10)
    
    def _update_status_loop(self):
        """Update status displays in loop"""
        import time
        while True:
            try:
                if self.root.winfo_exists():
                    self.root.after(0, self._update_status)
                time.sleep(1)
            except:
                break
    
    def _update_status(self):
        """Update status displays"""
        try:
            status = self.system.get_status()
            
            # Update gesture status
            if status.get('gesture_active'):
                self.gesture_status_label.configure(text="Active", text_color="green")
                gesture = status.get('current_gesture', 'None')
                self.current_gesture_label.configure(text=f"Gesture: {gesture}")
                fps = status.get('fps', 0)
                self.fps_label.configure(text=f"FPS: {fps:.1f}")
            else:
                self.gesture_status_label.configure(text="Inactive", text_color="gray")
                self.current_gesture_label.configure(text="No gesture")
                self.fps_label.configure(text="FPS: 0")
            
            # Update voice status
            if status.get('voice_active'):
                self.voice_status_label.configure(text="Active", text_color="green")
                if status.get('listening'):
                    self.voice_listening_label.configure(text="Listening...", text_color="yellow")
                else:
                    self.voice_listening_label.configure(text="Ready", text_color="green")
            else:
                self.voice_status_label.configure(text="Inactive", text_color="gray")
                self.voice_listening_label.configure(text="Not listening")
            
            # Update system info
            if hasattr(self.system, 'system_controller'):
                sys_info = self.system.system_controller.get_system_info()
                self.cpu_label.configure(text=f"CPU: {sys_info.get('cpu_percent', 0):.1f}%")
                self.memory_label.configure(text=f"Memory: {sys_info.get('memory_percent', 0):.1f}%")
        except:
            pass
    
    # Control methods
    def toggle_gesture(self):
        """Toggle gesture control"""
        enabled = self.gesture_switch.get()
        self.system.toggle_gesture(enabled)
        self.log_activity(f"Gesture control {'enabled' if enabled else 'disabled'}")
    
    def toggle_voice(self):
        """Toggle voice control"""
        enabled = self.voice_switch.get()
        self.system.toggle_voice(enabled)
        self.log_activity(f"Voice control {'enabled' if enabled else 'disabled'}")
    
    def take_screenshot(self):
        """Take screenshot"""
        if hasattr(self.system, 'system_controller'):
            self.system.system_controller.take_screenshot()
            self.log_activity("Screenshot captured")
    
    def test_voice(self):
        """Test voice recognition"""
        if hasattr(self.system, 'voice_controller') and self.system.voice_controller:
            self.system.voice_controller.trigger_listen()
            self.log_activity("Voice test triggered")
    
    def toggle_camera_view(self):
        """Toggle camera view"""
        # This would show/hide camera feed
        self.log_activity("Camera view toggled")
    
    def calibrate_system(self):
        """Calibrate system"""
        self.log_activity("System calibration started")
        # Trigger calibration
    
    def set_power_saver(self):
        """Set power saver profile"""
        settings = {
            'detection_confidence': 0.8,
            'tracking_confidence': 0.6,
            'frame_width': 480,
            'frame_height': 360,
            'model_complexity': 0
        }
        self.system.update_settings(settings)
        self.log_activity("Power saver profile activated")
    
    def set_balanced(self):
        """Set balanced profile"""
        settings = {
            'detection_confidence': 0.7,
            'tracking_confidence': 0.5,
            'frame_width': 640,
            'frame_height': 480,
            'model_complexity': 1
        }
        self.system.update_settings(settings)
        self.log_activity("Balanced profile activated")
    
    def set_high_performance(self):
        """Set high performance profile"""
        settings = {
            'detection_confidence': 0.6,
            'tracking_confidence': 0.4,
            'frame_width': 1280,
            'frame_height': 720,
            'model_complexity': 2
        }
        self.system.update_settings(settings)
        self.log_activity("High performance profile activated")
    
    def open_link(self, link_type):
        """Open external link"""
        import webbrowser
        urls = {
            'docs': 'https://github.com/handcontrol/docs',
            'issues': 'https://github.com/handcontrol/issues'
        }
        if link_type in urls:
            webbrowser.open(urls[link_type])
    
    def log_activity(self, message):
        """Log activity to display"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        if hasattr(self, 'log_text'):
            self.log_text.insert("end", log_entry)
            self.log_text.see("end")
    
    def on_minimize(self, event):
        """Handle minimize event"""
        if self.root.state() == 'iconic':
            self.minimize_to_tray()
    
    def minimize_to_tray(self):
        """Minimize to system tray"""
        self.root.withdraw()
        self.minimized_to_tray = True
        
        if not self.tray_icon:
            self.create_tray_icon()
    
    def create_tray_icon(self):
        """Create system tray icon"""
        # Create icon image
        try:
            image = Image.open("assets/icons/tray.png")
        except:
            # Create default icon if not found
            image = Image.new('RGB', (64, 64), color='blue')
        
        menu = pystray.Menu(
            item('Show', self.show_window),
            item('Gesture Control', self.toggle_gesture_tray, checked=lambda item: self.system.gesture_enabled),
            item('Voice Control', self.toggle_voice_tray, checked=lambda item: self.system.voice_enabled),
            item('Exit', self.quit_app)
        )
        
        self.tray_icon = pystray.Icon("HandControl", image, menu=menu)
        
        # Run in separate thread
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
    
    def show_window(self, icon=None, item=None):
        """Show window from tray"""
        self.root.deiconify()
        self.root.state('normal')
        self.minimized_to_tray = False
    
    def toggle_gesture_tray(self, icon, item):
        """Toggle gesture from tray"""
        self.system.toggle_gesture(not self.system.gesture_enabled)
    
    def toggle_voice_tray(self, icon, item):
        """Toggle voice from tray"""
        self.system.toggle_voice(not self.system.voice_enabled)
    
    def quit_app(self, icon=None, item=None):
        """Quit application"""
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()
    
    def on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            self.quit_app()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()
