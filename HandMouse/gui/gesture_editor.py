"""
Gesture Editor Module
Interface for customizing gesture mappings and training new gestures
"""

import customtkinter as ctk
from tkinter import messagebox
import json
from pathlib import Path
import logging

class GestureEditor:
    """Gesture mapping and training interface"""
    
    def __init__(self, parent, system):
        self.parent = parent
        self.system = system
        self.logger = logging.getLogger('GestureEditor')
        
        # Load gesture mappings
        self.gesture_mappings = self._load_mappings()
        
        # Available actions
        self.available_actions = [
            'cursor_move', 'left_click', 'right_click', 'double_click',
            'scroll_up', 'scroll_down', 'drag_start', 'drag_end',
            'switch_window', 'volume_up', 'volume_down', 'voice_command',
            'screenshot', 'go_back', 'go_forward', 'minimize', 'maximize',
            'close', 'copy', 'paste', 'delete', 'zoom_in', 'zoom_out'
        ]
        
        # Predefined gestures
        self.predefined_gestures = [
            'INDEX_POINTING', 'L_SHAPE', 'PEACE_SIGN', 'ROCK_SIGN',
            'CALL_SIGN', 'CLOSED_FIST', 'OPEN_HAND', 'MIDDLE_FINGER',
            'THUMBS_UP', 'THUMBS_DOWN', 'THREE_FINGERS', 'OK_SIGN',
            'PINCH', 'SWIPE_LEFT', 'SWIPE_RIGHT', 'SWIPE_UP', 'SWIPE_DOWN'
        ]
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create gesture editor UI"""
        # Create main container
        container = ctk.CTkFrame(self.parent)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create left panel for gesture list
        left_panel = ctk.CTkFrame(container, width=300)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Gesture list header
        header_frame = ctk.CTkFrame(left_panel)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="Gesture Mappings",
            font=("Segoe UI", 16, "bold")
        ).pack(side="left", padx=10)
        
        # Add gesture button
        ctk.CTkButton(
            header_frame,
            text="+ Add",
            command=self.add_custom_gesture,
            width=60
        ).pack(side="right", padx=10)
        
        # Gesture list
        self.gesture_listbox = ctk.CTkScrollableFrame(left_panel)
        self.gesture_listbox.pack(fill="both", expand=True)
        
        # Populate gesture list
        self._populate_gesture_list()
        
        # Create right panel for editing
        self.right_panel = ctk.CTkFrame(container)
        self.right_panel.pack(side="right", fill="both", expand=True)
        
        # Show default content
        self._show_welcome()
    
    def _populate_gesture_list(self):
        """Populate the gesture list"""
        # Clear existing items
        for widget in self.gesture_listbox.winfo_children():
            widget.destroy()
        
        # Add predefined gestures
        ctk.CTkLabel(
            self.gesture_listbox,
            text="Predefined Gestures",
            font=("Segoe UI", 12, "bold"),
            text_color="gray"
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        for gesture in self.predefined_gestures:
            self._create_gesture_item(gesture, is_custom=False)
        
        # Add custom gestures
        custom_gestures = [g for g in self.gesture_mappings.keys() 
                          if g not in self.predefined_gestures]
        
        if custom_gestures:
            ctk.CTkLabel(
                self.gesture_listbox,
                text="Custom Gestures",
                font=("Segoe UI", 12, "bold"),
                text_color="gray"
            ).pack(anchor="w", padx=10, pady=(20, 5))
            
            for gesture in custom_gestures:
                self._create_gesture_item(gesture, is_custom=True)
    
    def _create_gesture_item(self, gesture_name, is_custom=False):
        """Create a gesture list item"""
        item_frame = ctk.CTkFrame(self.gesture_listbox)
        item_frame.pack(fill="x", padx=10, pady=2)
        
        # Gesture name
        name_label = ctk.CTkLabel(
            item_frame,
            text=self._format_gesture_name(gesture_name),
            anchor="w"
        )
        name_label.pack(side="left", padx=10, fill="x", expand=True)
        
        # Current action
        action = self.gesture_mappings.get(gesture_name, "Not mapped")
        action_label = ctk.CTkLabel(
            item_frame,
            text=action,
            text_color="green" if action != "Not mapped" else "gray",
            anchor="e"
        )
        action_label.pack(side="right", padx=10)
        
        # Click handler
        item_frame.bind("<Button-1>", lambda e: self._select_gesture(gesture_name, is_custom))
        name_label.bind("<Button-1>", lambda e: self._select_gesture(gesture_name, is_custom))
        action_label.bind("<Button-1>", lambda e: self._select_gesture(gesture_name, is_custom))
    
    def _format_gesture_name(self, name):
        """Format gesture name for display"""
        # Add emoji icons for common gestures
        icons = {
            'INDEX_POINTING': '☝️',
            'L_SHAPE': '👆',
            'PEACE_SIGN': '✌️',
            'ROCK_SIGN': '🤟',
            'CALL_SIGN': '🤙',
            'CLOSED_FIST': '✊',
            'OPEN_HAND': '✋',
            'MIDDLE_FINGER': '🖕',
            'THUMBS_UP': '👍',
            'THUMBS_DOWN': '👎',
            'THREE_FINGERS': '🤟',
            'OK_SIGN': '👌',
            'PINCH': '🤏'
        }
        
        icon = icons.get(name, '✋')
        formatted = name.replace('_', ' ').title()
        return f"{icon} {formatted}"
    
    def _show_welcome(self):
        """Show welcome/help content"""
        # Clear right panel
        for widget in self.right_panel.winfo_children():
            widget.destroy()
        
        welcome_frame = ctk.CTkFrame(self.right_panel)
        welcome_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            welcome_frame,
            text="Gesture Editor",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=20)
        
        ctk.CTkLabel(
            welcome_frame,
            text="Select a gesture from the list to edit its mapping\nor click '+ Add' to create a custom gesture",
            font=("Segoe UI", 12)
        ).pack(pady=10)
        
        # Instructions
        instructions_frame = ctk.CTkFrame(welcome_frame)
        instructions_frame.pack(pady=20)
        
        instructions = [
            "• Click on a gesture to edit its action mapping",
            "• Use '+ Add' to create new custom gestures",
            "• Train gestures for better recognition",
            "• Export/Import gesture configurations",
            "• Test gestures in real-time"
        ]
        
        for instruction in instructions:
            ctk.CTkLabel(
                instructions_frame,
                text=instruction,
                anchor="w",
                font=("Segoe UI", 11)
            ).pack(anchor="w", padx=20, pady=2)
    
    def _select_gesture(self, gesture_name, is_custom):
        """Select a gesture for editing"""
        # Clear right panel
        for widget in self.right_panel.winfo_children():
            widget.destroy()
        
        # Create edit form
        edit_frame = ctk.CTkFrame(self.right_panel)
        edit_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Gesture name header
        header_frame = ctk.CTkFrame(edit_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            header_frame,
            text=self._format_gesture_name(gesture_name),
            font=("Segoe UI", 18, "bold")
        ).pack(side="left")
        
        if is_custom:
            ctk.CTkButton(
                header_frame,
                text="Delete",
                command=lambda: self.delete_gesture(gesture_name),
                fg_color="red",
                width=80
            ).pack(side="right")
        
        # Action mapping
        mapping_frame = ctk.CTkFrame(edit_frame)
        mapping_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            mapping_frame,
            text="Action:",
            font=("Segoe UI", 12)
        ).pack(anchor="w", pady=5)
        
        current_action = self.gesture_mappings.get(gesture_name, "Not mapped")
        self.action_menu = ctk.CTkOptionMenu(
            mapping_frame,
            values=["Not mapped"] + self.available_actions,
            command=lambda v: self.update_mapping(gesture_name, v)
        )
        self.action_menu.set(current_action)
        self.action_menu.pack(fill="x")
        
        # Custom command input
        custom_frame = ctk.CTkFrame(edit_frame)
        custom_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            custom_frame,
            text="Custom Command (optional):",
            font=("Segoe UI", 12)
        ).pack(anchor="w", pady=5)
        
        self.custom_entry = ctk.CTkEntry(
            custom_frame,
            placeholder_text="e.g., ctrl+shift+a"
        )
        self.custom_entry.pack(fill="x")
        
        ctk.CTkButton(
            custom_frame,
            text="Apply Custom Command",
            command=lambda: self.apply_custom_command(gesture_name)
        ).pack(pady=10)
        
        # Training section
        if is_custom or gesture_name in ['OK_SIGN', 'PINCH']:
            training_frame = ctk.CTkFrame(edit_frame)
            training_frame.pack(fill="x", pady=20)
            
            ctk.CTkLabel(
                training_frame,
                text="Gesture Training",
                font=("Segoe UI", 14, "bold")
            ).pack(anchor="w", pady=10)
            
            ctk.CTkLabel(
                training_frame,
                text="Train this gesture for better recognition",
                font=("Segoe UI", 11)
            ).pack(anchor="w", pady=5)
            
            button_frame = ctk.CTkFrame(training_frame)
            button_frame.pack(pady=10)
            
            ctk.CTkButton(
                button_frame,
                text="Start Training",
                command=lambda: self.start_training(gesture_name),
                width=120
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                button_frame,
                text="Test Gesture",
                command=lambda: self.test_gesture(gesture_name),
                width=120
            ).pack(side="left", padx=5)
        
        # Save button
        ctk.CTkButton(
            edit_frame,
            text="Save Changes",
            command=self.save_mappings,
            fg_color="green",
            width=150,
            height=40
        ).pack(pady=20)
    
    def update_mapping(self, gesture_name, action):
        """Update gesture to action mapping"""
        if action == "Not mapped":
            if gesture_name in self.gesture_mappings:
                del self.gesture_mappings[gesture_name]
        else:
            self.gesture_mappings[gesture_name] = action
        
        # Update system
        if hasattr(self.system, 'gesture_recognizer') and self.system.gesture_recognizer:
            self.system.gesture_recognizer.update_gesture_mapping(gesture_name, action)
        
        # Refresh list
        self._populate_gesture_list()
        
        self.logger.info(f"Updated mapping: {gesture_name} -> {action}")
    
    def apply_custom_command(self, gesture_name):
        """Apply custom keyboard command"""
        command = self.custom_entry.get().strip()
        if command:
            self.gesture_mappings[gesture_name] = command
            
            # Update system
            if hasattr(self.system, 'gesture_recognizer') and self.system.gesture_recognizer:
                self.system.gesture_recognizer.update_gesture_mapping(gesture_name, command)
            
            messagebox.showinfo("Custom Command", f"Applied custom command: {command}")
            self._populate_gesture_list()
    
    def add_custom_gesture(self):
        """Add a new custom gesture"""
        dialog = ctk.CTkInputDialog(
            text="Enter name for new gesture:",
            title="Add Custom Gesture"
        )
        gesture_name = dialog.get_input()
        
        if gesture_name:
            gesture_name = gesture_name.upper().replace(' ', '_')
            if gesture_name not in self.gesture_mappings:
                self.gesture_mappings[gesture_name] = "Not mapped"
                self._populate_gesture_list()
                self._select_gesture(gesture_name, is_custom=True)
                self.logger.info(f"Added custom gesture: {gesture_name}")
            else:
                messagebox.showwarning("Duplicate", "This gesture already exists!")
    
    def delete_gesture(self, gesture_name):
        """Delete a custom gesture"""
        if messagebox.askyesno("Delete", f"Delete gesture '{gesture_name}'?"):
            if gesture_name in self.gesture_mappings:
                del self.gesture_mappings[gesture_name]
            
            # Update system
            if hasattr(self.system, 'gesture_processor') and self.system.gesture_processor:
                self.system.gesture_processor.remove_custom_gesture(gesture_name)
            
            self.save_mappings()
            self._populate_gesture_list()
            self._show_welcome()
            self.logger.info(f"Deleted gesture: {gesture_name}")
    
    def start_training(self, gesture_name):
        """Start gesture training"""
        messagebox.showinfo(
            "Training",
            f"Training mode for '{gesture_name}'\n\n"
            "1. Position your hand in view\n"
            "2. Perform the gesture multiple times\n"
            "3. Training will capture samples automatically"
        )
        
        # Start training process
        if hasattr(self.system, 'gesture_trainer'):
            self.system.gesture_trainer.start_training(gesture_name)
    
    def test_gesture(self, gesture_name):
        """Test gesture recognition"""
        messagebox.showinfo(
            "Test Mode",
            f"Testing gesture '{gesture_name}'\n\n"
            "Perform the gesture to test recognition"
        )
        
        # Enable test mode
        if hasattr(self.system, 'gesture_recognizer') and self.system.gesture_recognizer:
            # Set callback to show result
            def on_gesture_detected(detected):
                if detected == gesture_name:
                    messagebox.showinfo("Success", f"Gesture '{gesture_name}' detected!")
                else:
                    messagebox.showinfo("Detection", f"Detected: '{detected}'")
            
            self.system.gesture_recognizer.register_gesture_callback(
                gesture_name, 
                lambda data: on_gesture_detected(gesture_name)
            )
    
    def save_mappings(self):
        """Save gesture mappings to file"""
        try:
            with open('config/gestures.json', 'w') as f:
                json.dump(self.gesture_mappings, f, indent=2)
            
            # Update system
            if hasattr(self.system, 'config_manager'):
                self.system.config_manager.save_gesture_mappings(self.gesture_mappings)
            
            messagebox.showinfo("Saved", "Gesture mappings saved successfully!")
            self.logger.info("Gesture mappings saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save mappings: {e}")
            self.logger.error(f"Failed to save mappings: {e}")
    
    def _load_mappings(self):
        """Load gesture mappings from file"""
        try:
            if Path('config/gestures.json').exists():
                with open('config/gestures.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading gesture mappings: {e}")
        
        # Return default mappings
        return {
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
            'THREE_FINGERS': 'voice_command'
        }
