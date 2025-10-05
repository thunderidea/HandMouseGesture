"""
Keyboard Controller Module
Handles keyboard shortcuts and text input
"""

import keyboard
import pyautogui
import time
import logging
from typing import List, Optional

class KeyboardController:
    """Control keyboard input and shortcuts"""
    
    def __init__(self):
        self.logger = logging.getLogger('KeyboardController')
        
        # Shortcut definitions
        self.shortcuts = {
            'copy': 'ctrl+c',
            'paste': 'ctrl+v',
            'cut': 'ctrl+x',
            'undo': 'ctrl+z',
            'redo': 'ctrl+y',
            'select_all': 'ctrl+a',
            'save': 'ctrl+s',
            'open': 'ctrl+o',
            'new': 'ctrl+n',
            'close_tab': 'ctrl+w',
            'new_tab': 'ctrl+t',
            'switch_tab': 'ctrl+tab',
            'find': 'ctrl+f',
            'print': 'ctrl+p'
        }
        
    def press_key(self, key: str):
        """Press a single key"""
        try:
            keyboard.press_and_release(key)
            self.logger.debug(f"Pressed key: {key}")
        except Exception as e:
            self.logger.error(f"Error pressing key {key}: {e}")
    
    def press_keys(self, keys: List[str]):
        """Press multiple keys simultaneously"""
        try:
            keyboard.press_and_release('+'.join(keys))
            self.logger.debug(f"Pressed keys: {keys}")
        except Exception as e:
            self.logger.error(f"Error pressing keys {keys}: {e}")
    
    def type_text(self, text: str):
        """Type text"""
        try:
            keyboard.write(text)
            self.logger.debug(f"Typed text: {text[:20]}...")
        except Exception as e:
            self.logger.error(f"Error typing text: {e}")
    
    def execute_shortcut(self, shortcut_name: str):
        """Execute a predefined shortcut"""
        if shortcut_name in self.shortcuts:
            shortcut = self.shortcuts[shortcut_name]
            try:
                keyboard.press_and_release(shortcut)
                self.logger.debug(f"Executed shortcut: {shortcut_name}")
            except Exception as e:
                self.logger.error(f"Error executing shortcut {shortcut_name}: {e}")
        else:
            # Try to execute as raw shortcut
            try:
                keyboard.press_and_release(shortcut_name)
                self.logger.debug(f"Executed raw shortcut: {shortcut_name}")
            except Exception as e:
                self.logger.error(f"Unknown shortcut: {shortcut_name}")
    
    # Common operations
    def copy(self):
        """Copy selected content"""
        self.execute_shortcut('copy')
    
    def paste(self):
        """Paste clipboard content"""
        self.execute_shortcut('paste')
    
    def cut(self):
        """Cut selected content"""
        self.execute_shortcut('cut')
    
    def undo(self):
        """Undo last action"""
        self.execute_shortcut('undo')
    
    def redo(self):
        """Redo last undone action"""
        self.execute_shortcut('redo')
    
    def select_all(self):
        """Select all content"""
        self.execute_shortcut('select_all')
    
    def delete(self):
        """Delete selected content"""
        self.press_key('delete')
    
    def backspace(self):
        """Backspace key"""
        self.press_key('backspace')
    
    def enter(self):
        """Enter key"""
        self.press_key('enter')
    
    def escape(self):
        """Escape key"""
        self.press_key('escape')
    
    def tab(self):
        """Tab key"""
        self.press_key('tab')
    
    # Window management
    def alt_tab(self):
        """Switch between windows"""
        try:
            keyboard.press_and_release('alt+tab')
            self.logger.debug("Alt+Tab executed")
        except Exception as e:
            self.logger.error(f"Error executing Alt+Tab: {e}")
    
    def minimize_window(self):
        """Minimize current window"""
        try:
            keyboard.press_and_release('win+down')
            self.logger.debug("Window minimized")
        except Exception as e:
            self.logger.error(f"Error minimizing window: {e}")
    
    def maximize_window(self):
        """Maximize current window"""
        try:
            keyboard.press_and_release('win+up')
            self.logger.debug("Window maximized")
        except Exception as e:
            self.logger.error(f"Error maximizing window: {e}")
    
    def close_window(self):
        """Close current window"""
        try:
            keyboard.press_and_release('alt+f4')
            self.logger.debug("Window closed")
        except Exception as e:
            self.logger.error(f"Error closing window: {e}")
    
    def show_desktop(self):
        """Show desktop"""
        try:
            keyboard.press_and_release('win+d')
            self.logger.debug("Showing desktop")
        except Exception as e:
            self.logger.error(f"Error showing desktop: {e}")
    
    # Navigation
    def go_back(self):
        """Navigate back (browser/explorer)"""
        try:
            keyboard.press_and_release('alt+left')
            self.logger.debug("Navigated back")
        except Exception as e:
            self.logger.error(f"Error navigating back: {e}")
    
    def go_forward(self):
        """Navigate forward (browser/explorer)"""
        try:
            keyboard.press_and_release('alt+right')
            self.logger.debug("Navigated forward")
        except Exception as e:
            self.logger.error(f"Error navigating forward: {e}")
    
    def refresh(self):
        """Refresh current page/window"""
        try:
            keyboard.press_and_release('f5')
            self.logger.debug("Refreshed")
        except Exception as e:
            self.logger.error(f"Error refreshing: {e}")
    
    # Special functions
    def trigger_voice_command(self):
        """Trigger Windows voice command (Win+H)"""
        try:
            keyboard.press_and_release('win+h')
            self.logger.debug("Voice command triggered")
        except Exception as e:
            self.logger.error(f"Error triggering voice command: {e}")
    
    def open_search(self):
        """Open Windows search"""
        try:
            keyboard.press_and_release('win+s')
            self.logger.debug("Search opened")
        except Exception as e:
            self.logger.error(f"Error opening search: {e}")
    
    def open_run(self):
        """Open Run dialog"""
        try:
            keyboard.press_and_release('win+r')
            self.logger.debug("Run dialog opened")
        except Exception as e:
            self.logger.error(f"Error opening Run dialog: {e}")
    
    def lock_screen(self):
        """Lock the screen"""
        try:
            keyboard.press_and_release('win+l')
            self.logger.debug("Screen locked")
        except Exception as e:
            self.logger.error(f"Error locking screen: {e}")
    
    def take_screenshot(self):
        """Take screenshot using Windows shortcut"""
        try:
            keyboard.press_and_release('win+shift+s')
            self.logger.debug("Screenshot tool opened")
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
    
    # Media controls
    def play_pause(self):
        """Play/pause media"""
        try:
            keyboard.press_and_release('play_pause_media')
            self.logger.debug("Play/pause toggled")
        except Exception as e:
            self.logger.error(f"Error toggling play/pause: {e}")
    
    def next_track(self):
        """Next media track"""
        try:
            keyboard.press_and_release('next_track')
            self.logger.debug("Next track")
        except Exception as e:
            self.logger.error(f"Error skipping to next track: {e}")
    
    def previous_track(self):
        """Previous media track"""
        try:
            keyboard.press_and_release('previous_track')
            self.logger.debug("Previous track")
        except Exception as e:
            self.logger.error(f"Error going to previous track: {e}")
    
    def volume_mute(self):
        """Mute/unmute volume"""
        try:
            keyboard.press_and_release('volume_mute')
            self.logger.debug("Volume mute toggled")
        except Exception as e:
            self.logger.error(f"Error toggling mute: {e}")
    
    def add_custom_shortcut(self, name: str, keys: str):
        """Add a custom shortcut"""
        self.shortcuts[name] = keys
        self.logger.info(f"Added custom shortcut: {name} -> {keys}")
    
    def remove_custom_shortcut(self, name: str):
        """Remove a custom shortcut"""
        if name in self.shortcuts:
            del self.shortcuts[name]
            self.logger.info(f"Removed custom shortcut: {name}")
