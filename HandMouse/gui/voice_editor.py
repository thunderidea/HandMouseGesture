"""
Voice Editor Module
Interface for customizing voice commands
"""

import customtkinter as ctk
from tkinter import messagebox
import json
from pathlib import Path
import logging

class VoiceEditor:
    """Voice command customization interface"""
    
    def __init__(self, parent, system):
        self.parent = parent
        self.system = system
        self.logger = logging.getLogger('VoiceEditor')
        
        # Load voice commands
        self.voice_commands = self._load_commands()
        
        # Available actions
        self.available_actions = [
            'open_app', 'close_window', 'minimize_window', 'maximize_window',
            'switch_window', 'show_desktop', 'go_back', 'go_forward', 'refresh',
            'scroll_up', 'scroll_down', 'copy', 'paste', 'cut', 'delete',
            'select_all', 'undo', 'redo', 'screenshot', 'volume_up', 'volume_down',
            'mute', 'brightness_up', 'brightness_down', 'lock_screen', 'open_search',
            'play_pause', 'next_track', 'previous_track', 'voice_typing'
        ]
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create voice editor UI"""
        # Main container
        container = ctk.CTkFrame(self.parent)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ctk.CTkFrame(container)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="Voice Commands",
            font=("Segoe UI", 18, "bold")
        ).pack(side="left", padx=10)
        
        # Add command button
        ctk.CTkButton(
            header_frame,
            text="+ Add Command",
            command=self.add_command,
            width=120
        ).pack(side="right", padx=10)
        
        # Search bar
        search_frame = ctk.CTkFrame(container)
        search_frame.pack(fill="x", pady=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search commands..."
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(10, 5))
        self.search_entry.bind("<KeyRelease>", self.search_commands)
        
        ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.search_commands,
            width=80
        ).pack(side="right", padx=(5, 10))
        
        # Commands list
        self.commands_frame = ctk.CTkScrollableFrame(container)
        self.commands_frame.pack(fill="both", expand=True, pady=10)
        
        # Populate commands
        self._populate_commands()
        
        # Bottom controls
        bottom_frame = ctk.CTkFrame(container)
        bottom_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(
            bottom_frame,
            text="Test Voice",
            command=self.test_voice,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            bottom_frame,
            text="Import",
            command=self.import_commands,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            bottom_frame,
            text="Export",
            command=self.export_commands,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            bottom_frame,
            text="Save All",
            command=self.save_commands,
            fg_color="green",
            width=120
        ).pack(side="right", padx=5)
    
    def _populate_commands(self, filter_text=""):
        """Populate the commands list"""
        # Clear existing items
        for widget in self.commands_frame.winfo_children():
            widget.destroy()
        
        # Group commands by category
        categories = {
            'Applications': [],
            'Window Control': [],
            'Navigation': [],
            'Edit Operations': [],
            'System Control': [],
            'Media Control': [],
            'Custom': []
        }
        
        # Categorize commands
        for command, data in self.voice_commands.items():
            if filter_text and filter_text.lower() not in command.lower():
                continue
            
            action = data.get('action', '')
            
            if 'open' in command or 'app' in action:
                categories['Applications'].append(command)
            elif any(x in action for x in ['window', 'minimize', 'maximize', 'close']):
                categories['Window Control'].append(command)
            elif any(x in action for x in ['back', 'forward', 'scroll', 'refresh']):
                categories['Navigation'].append(command)
            elif any(x in action for x in ['copy', 'paste', 'cut', 'delete', 'undo']):
                categories['Edit Operations'].append(command)
            elif any(x in action for x in ['screenshot', 'volume', 'brightness', 'lock']):
                categories['System Control'].append(command)
            elif any(x in action for x in ['play', 'pause', 'track']):
                categories['Media Control'].append(command)
            else:
                categories['Custom'].append(command)
        
        # Display categories
        for category, commands in categories.items():
            if commands:
                # Category header
                ctk.CTkLabel(
                    self.commands_frame,
                    text=category,
                    font=("Segoe UI", 14, "bold"),
                    text_color="gray"
                ).pack(anchor="w", padx=10, pady=(15, 5))
                
                # Commands in category
                for command in sorted(commands):
                    self._create_command_item(command)
    
    def _create_command_item(self, command):
        """Create a command list item"""
        item_frame = ctk.CTkFrame(self.commands_frame)
        item_frame.pack(fill="x", padx=10, pady=2)
        
        # Command text
        command_label = ctk.CTkLabel(
            item_frame,
            text=f'"{command}"',
            font=("Segoe UI", 11, "bold"),
            anchor="w",
            width=200
        )
        command_label.pack(side="left", padx=10)
        
        # Arrow
        ctk.CTkLabel(
            item_frame,
            text="→",
            font=("Segoe UI", 11),
            text_color="gray"
        ).pack(side="left", padx=5)
        
        # Action
        action_data = self.voice_commands[command]
        action_text = action_data.get('action', 'Not set')
        params = action_data.get('params', [])
        if params:
            action_text += f" ({', '.join(params)})"
        
        action_label = ctk.CTkLabel(
            item_frame,
            text=action_text,
            font=("Segoe UI", 11),
            anchor="w",
            text_color="green" if action_text != 'Not set' else "gray"
        )
        action_label.pack(side="left", padx=10, fill="x", expand=True)
        
        # Edit button
        ctk.CTkButton(
            item_frame,
            text="Edit",
            command=lambda: self.edit_command(command),
            width=60,
            height=28
        ).pack(side="right", padx=5)
        
        # Delete button
        ctk.CTkButton(
            item_frame,
            text="Delete",
            command=lambda: self.delete_command(command),
            fg_color="red",
            width=60,
            height=28
        ).pack(side="right", padx=5)
    
    def add_command(self):
        """Add a new voice command"""
        dialog = AddCommandDialog(self.parent, self.available_actions)
        self.parent.wait_window(dialog.top)
        
        if dialog.result:
            command = dialog.result['command']
            action = dialog.result['action']
            params = dialog.result['params']
            
            self.voice_commands[command] = {
                'action': action,
                'params': params
            }
            
            # Update system
            if hasattr(self.system, 'voice_controller') and self.system.voice_controller:
                self.system.voice_controller.add_custom_command(command, action, params)
            
            self._populate_commands()
            self.logger.info(f"Added command: {command}")
    
    def edit_command(self, command):
        """Edit an existing command"""
        current_data = self.voice_commands[command]
        
        dialog = AddCommandDialog(
            self.parent,
            self.available_actions,
            command,
            current_data.get('action'),
            current_data.get('params', [])
        )
        self.parent.wait_window(dialog.top)
        
        if dialog.result:
            # Remove old command if name changed
            if dialog.result['command'] != command:
                del self.voice_commands[command]
            
            # Add updated command
            self.voice_commands[dialog.result['command']] = {
                'action': dialog.result['action'],
                'params': dialog.result['params']
            }
            
            # Update system
            if hasattr(self.system, 'voice_controller') and self.system.voice_controller:
                if dialog.result['command'] != command:
                    self.system.voice_controller.remove_custom_command(command)
                self.system.voice_controller.add_custom_command(
                    dialog.result['command'],
                    dialog.result['action'],
                    dialog.result['params']
                )
            
            self._populate_commands()
            self.logger.info(f"Updated command: {dialog.result['command']}")
    
    def delete_command(self, command):
        """Delete a voice command"""
        if messagebox.askyesno("Delete", f"Delete command '{command}'?"):
            del self.voice_commands[command]
            
            # Update system
            if hasattr(self.system, 'voice_controller') and self.system.voice_controller:
                self.system.voice_controller.remove_custom_command(command)
            
            self._populate_commands()
            self.logger.info(f"Deleted command: {command}")
    
    def search_commands(self, event=None):
        """Search/filter commands"""
        search_text = self.search_entry.get()
        self._populate_commands(search_text)
    
    def test_voice(self):
        """Test voice recognition"""
        if hasattr(self.system, 'voice_controller') and self.system.voice_controller:
            self.system.voice_controller.trigger_listen()
            messagebox.showinfo("Voice Test", "Listening... Speak a command now!")
        else:
            messagebox.showwarning("Voice Test", "Voice control is not active")
    
    def import_commands(self):
        """Import commands from file"""
        from tkinter import filedialog
        
        filename = filedialog.askopenfilename(
            title="Import Commands",
            filetypes=[("JSON files", "*.json")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    imported = json.load(f)
                
                # Merge with existing
                self.voice_commands.update(imported)
                
                # Update system
                if hasattr(self.system, 'voice_controller') and self.system.voice_controller:
                    for command, data in imported.items():
                        self.system.voice_controller.add_custom_command(
                            command,
                            data.get('action'),
                            data.get('params', [])
                        )
                
                self._populate_commands()
                messagebox.showinfo("Import", f"Imported {len(imported)} commands")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import: {e}")
    
    def export_commands(self):
        """Export commands to file"""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            title="Export Commands",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if filename:
            try:
                # Export only custom commands
                custom_commands = {}
                for command, data in self.voice_commands.items():
                    if not self._is_default_command(command):
                        custom_commands[command] = data
                
                with open(filename, 'w') as f:
                    json.dump(custom_commands, f, indent=2)
                
                messagebox.showinfo("Export", f"Exported {len(custom_commands)} commands")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    def save_commands(self):
        """Save all commands"""
        try:
            # Save custom commands only
            custom_commands = {}
            for command, data in self.voice_commands.items():
                if not self._is_default_command(command):
                    custom_commands[command] = data
            
            with open('config/voice_commands.json', 'w') as f:
                json.dump(custom_commands, f, indent=2)
            
            messagebox.showinfo("Save", "Commands saved successfully!")
            self.logger.info("Voice commands saved")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")
            self.logger.error(f"Failed to save commands: {e}")
    
    def _is_default_command(self, command):
        """Check if command is a default command"""
        # This would check against default commands list
        defaults = [
            'open chrome', 'close', 'minimize', 'maximize', 'copy this',
            'paste here', 'take screenshot', 'volume up', 'volume down'
        ]
        return command.lower() in defaults
    
    def _load_commands(self):
        """Load voice commands"""
        commands = {}
        
        # Load defaults (would come from voice controller)
        if hasattr(self.system, 'voice_controller') and self.system.voice_controller:
            commands = self.system.voice_controller.commands.copy()
        
        # Load custom commands
        try:
            if Path('config/voice_commands.json').exists():
                with open('config/voice_commands.json', 'r') as f:
                    custom = json.load(f)
                    commands.update(custom)
        except Exception as e:
            self.logger.error(f"Error loading custom commands: {e}")
        
        return commands


class AddCommandDialog:
    """Dialog for adding/editing voice commands"""
    
    def __init__(self, parent, actions, command="", action="", params=None):
        self.result = None
        
        # Create dialog window
        self.top = ctk.CTkToplevel(parent)
        self.top.title("Add Voice Command" if not command else "Edit Voice Command")
        self.top.geometry("400x350")
        self.top.transient(parent)
        self.top.grab_set()
        
        # Command input
        ctk.CTkLabel(self.top, text="Voice Command:").pack(anchor="w", padx=20, pady=(20, 5))
        self.command_entry = ctk.CTkEntry(self.top)
        self.command_entry.pack(fill="x", padx=20, pady=(0, 10))
        if command:
            self.command_entry.insert(0, command)
        
        # Action selection
        ctk.CTkLabel(self.top, text="Action:").pack(anchor="w", padx=20, pady=(10, 5))
        self.action_menu = ctk.CTkOptionMenu(self.top, values=actions)
        self.action_menu.pack(fill="x", padx=20, pady=(0, 10))
        if action:
            self.action_menu.set(action)
        
        # Parameters input
        ctk.CTkLabel(self.top, text="Parameters (optional):").pack(anchor="w", padx=20, pady=(10, 5))
        self.params_entry = ctk.CTkEntry(self.top, placeholder_text="e.g., chrome, settings")
        self.params_entry.pack(fill="x", padx=20, pady=(0, 10))
        if params:
            self.params_entry.insert(0, ', '.join(params))
        
        # Buttons
        button_frame = ctk.CTkFrame(self.top)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel,
            width=100
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save,
            fg_color="green",
            width=100
        ).pack(side="right", padx=5)
    
    def save(self):
        """Save the command"""
        command = self.command_entry.get().strip().lower()
        action = self.action_menu.get()
        params_text = self.params_entry.get().strip()
        
        if not command:
            messagebox.showwarning("Error", "Please enter a command")
            return
        
        params = []
        if params_text:
            params = [p.strip() for p in params_text.split(',')]
        
        self.result = {
            'command': command,
            'action': action,
            'params': params
        }
        
        self.top.destroy()
    
    def cancel(self):
        """Cancel the dialog"""
        self.top.destroy()
