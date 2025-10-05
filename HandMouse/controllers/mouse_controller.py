"""
Mouse Controller Module
Handles all mouse-related operations with advanced features
"""

import pyautogui
import mouse
import time
import numpy as np
from typing import Tuple, Optional
import logging
from threading import Lock

class MouseController:
    """Advanced mouse control with smoothing and acceleration"""
    
    def __init__(self, config: dict):
        self.logger = logging.getLogger('MouseController')
        
        # Configuration
        self.config = config
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Movement parameters
        self.sensitivity = config.get('mouse_sensitivity', 1.5)
        self.acceleration = config.get('mouse_acceleration', 1.2)
        self.smoothing = config.get('mouse_smoothing', 0.3)
        
        # Click parameters
        self.click_delay = config.get('click_delay', 0.1)
        self.double_click_interval = config.get('double_click_interval', 0.3)
        
        # Scroll parameters
        self.scroll_sensitivity = config.get('scroll_sensitivity', 1.0)
        self.scroll_smooth = config.get('scroll_smooth', True)
        
        # State tracking
        self.last_position = None
        self.last_click_time = 0
        self.is_dragging = False
        
        # Thread safety
        self.lock = Lock()
        
        # Disable pyautogui failsafe for smoother operation
        pyautogui.FAILSAFE = False
        
        # Set pyautogui parameters
        pyautogui.MINIMUM_DURATION = 0
        pyautogui.MINIMUM_SLEEP = 0
        pyautogui.PAUSE = 0
        
    def move_cursor(self, hand_position: Tuple[int, int], relative: bool = False):
        """Move cursor to specified position with smoothing"""
        with self.lock:
            try:
                if relative:
                    # Relative movement
                    x, y = hand_position
                    x = int(x * self.sensitivity)
                    y = int(y * self.sensitivity)
                    
                    # Apply acceleration
                    if abs(x) > 10 or abs(y) > 10:
                        x = int(x * self.acceleration)
                        y = int(y * self.acceleration)
                    
                    mouse.move(x, y, absolute=False)
                else:
                    # Absolute positioning - map hand position to screen
                    x, y = self._map_to_screen(hand_position)
                    
                    # Apply smoothing
                    if self.last_position:
                        x = int(self.smoothing * x + (1 - self.smoothing) * self.last_position[0])
                        y = int(self.smoothing * y + (1 - self.smoothing) * self.last_position[1])
                    
                    # Move cursor
                    mouse.move(x, y, absolute=True)
                    self.last_position = (x, y)
                    
            except Exception as e:
                self.logger.error(f"Error moving cursor: {e}")
    
    def _map_to_screen(self, hand_position: Tuple[int, int]) -> Tuple[int, int]:
        """Map hand position to screen coordinates"""
        # Assuming hand position is from camera frame (640x480)
        camera_width = self.config.get('frame_width', 640)
        camera_height = self.config.get('frame_height', 480)
        
        # Define active zone (central area of camera frame)
        zone_margin = self.config.get('active_zone_margin', 0.1)
        zone_left = camera_width * zone_margin
        zone_right = camera_width * (1 - zone_margin)
        zone_top = camera_height * zone_margin
        zone_bottom = camera_height * (1 - zone_margin)
        
        # Clamp to active zone
        x = np.clip(hand_position[0], zone_left, zone_right)
        y = np.clip(hand_position[1], zone_top, zone_bottom)
        
        # Normalize to 0-1 range
        x_norm = (x - zone_left) / (zone_right - zone_left)
        y_norm = (y - zone_top) / (zone_bottom - zone_top)
        
        # Map to screen coordinates
        screen_x = int(x_norm * self.screen_width)
        screen_y = int(y_norm * self.screen_height)
        
        return (screen_x, screen_y)
    
    def click(self, button: str = 'left', clicks: int = 1):
        """Perform mouse click"""
        with self.lock:
            try:
                current_time = time.time()
                
                # Prevent accidental double clicks
                if current_time - self.last_click_time < self.click_delay:
                    return
                
                if button == 'left':
                    mouse.click('left')
                elif button == 'right':
                    mouse.click('right')
                elif button == 'middle':
                    mouse.click('middle')
                
                self.last_click_time = current_time
                self.logger.debug(f"Clicked {button} button")
                
            except Exception as e:
                self.logger.error(f"Error clicking: {e}")
    
    def double_click(self):
        """Perform double click"""
        with self.lock:
            try:
                mouse.double_click('left')
                self.logger.debug("Double clicked")
            except Exception as e:
                self.logger.error(f"Error double clicking: {e}")
    
    def drag_start(self):
        """Start drag operation"""
        with self.lock:
            if not self.is_dragging:
                try:
                    mouse.press('left')
                    self.is_dragging = True
                    self.logger.debug("Drag started")
                except Exception as e:
                    self.logger.error(f"Error starting drag: {e}")
    
    def drag_end(self):
        """End drag operation"""
        with self.lock:
            if self.is_dragging:
                try:
                    mouse.release('left')
                    self.is_dragging = False
                    self.logger.debug("Drag ended")
                except Exception as e:
                    self.logger.error(f"Error ending drag: {e}")
    
    def drag_to(self, position: Tuple[int, int]):
        """Drag to specified position"""
        if self.is_dragging:
            self.move_cursor(position)
    
    def scroll(self, direction: int, amount: Optional[int] = None):
        """Perform scroll operation"""
        with self.lock:
            try:
                if amount is None:
                    amount = int(3 * self.scroll_sensitivity)
                else:
                    amount = int(amount * self.scroll_sensitivity)
                
                if self.scroll_smooth:
                    # Smooth scrolling
                    for _ in range(abs(amount)):
                        mouse.wheel(1 if direction > 0 else -1)
                        time.sleep(0.01)
                else:
                    # Instant scroll
                    mouse.wheel(direction * amount)
                
                self.logger.debug(f"Scrolled {'up' if direction > 0 else 'down'}")
                
            except Exception as e:
                self.logger.error(f"Error scrolling: {e}")
    
    def get_position(self) -> Tuple[int, int]:
        """Get current cursor position"""
        return mouse.get_position()
    
    def set_position(self, x: int, y: int):
        """Set cursor position directly"""
        with self.lock:
            try:
                mouse.move(x, y, absolute=True)
                self.last_position = (x, y)
            except Exception as e:
                self.logger.error(f"Error setting position: {e}")
    
    def update_config(self, config: dict):
        """Update controller configuration"""
        self.config.update(config)
        self.sensitivity = config.get('mouse_sensitivity', 1.5)
        self.acceleration = config.get('mouse_acceleration', 1.2)
        self.smoothing = config.get('mouse_smoothing', 0.3)
        self.scroll_sensitivity = config.get('scroll_sensitivity', 1.0)
        self.logger.info("Mouse controller configuration updated")
    
    def reset(self):
        """Reset controller state"""
        with self.lock:
            self.last_position = None
            self.last_click_time = 0
            if self.is_dragging:
                self.drag_end()
            self.logger.debug("Mouse controller reset")
