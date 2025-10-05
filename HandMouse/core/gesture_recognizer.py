"""
Advanced Gesture Recognition System
Recognizes and processes hand gestures with custom mapping support
"""

import cv2
import numpy as np
import time
import threading
from typing import Dict, Optional, Callable, List
import logging
from collections import deque

from .hand_tracker import HandTracker
from .gesture_processor import GestureProcessor
from controllers.mouse_controller import MouseController
from controllers.keyboard_controller import KeyboardController
from controllers.system_controller import SystemController
from utils.config_manager import ConfigManager

class GestureRecognizer:
    """Main gesture recognition and control system"""
    
    # Gesture definitions
    GESTURES = {
        'INDEX_POINTING': {'fingers': '01000', 'action': 'cursor_move'},
        'L_SHAPE': {'fingers': '11000', 'action': 'left_click'},
        'PEACE_SIGN': {'fingers': '01100', 'action': 'right_click'},
        'ROCK_SIGN': {'fingers': '01001', 'action': 'scroll_up'},
        'CALL_SIGN': {'fingers': '10001', 'action': 'scroll_down'},
        'CLOSED_FIST': {'fingers': '00000', 'action': 'drag_start'},
        'OPEN_HAND': {'fingers': '11111', 'action': 'drag_end'},
        'MIDDLE_FINGER': {'fingers': '00100', 'action': 'switch_window'},
        'THUMBS_UP': {'fingers': '10000', 'action': 'volume_up'},
        'THUMBS_DOWN': {'fingers': '10000', 'action': 'volume_down'},  # With orientation
        'THREE_FINGERS': {'fingers': '01110', 'action': 'voice_command'},
        'OK_SIGN': {'custom': True, 'action': 'screenshot'},
        'PINCH': {'custom': True, 'action': 'zoom'},
        'SWIPE_LEFT': {'motion': True, 'action': 'go_back'},
        'SWIPE_RIGHT': {'motion': True, 'action': 'go_forward'},
        'SWIPE_UP': {'motion': True, 'action': 'maximize'},
        'SWIPE_DOWN': {'motion': True, 'action': 'minimize'}
    }
    
    def __init__(self, config: dict):
        self.logger = logging.getLogger('GestureRecognizer')
        self.config = config
        self.config_manager = ConfigManager()
        
        # Load gesture mappings
        self.gesture_mappings = self.config_manager.load_gesture_mappings()
        
        # Initialize components
        self.hand_tracker = HandTracker(config)
        self.gesture_processor = GestureProcessor(config)
        self.mouse_controller = MouseController(config)
        self.keyboard_controller = KeyboardController()
        self.system_controller = SystemController()
        
        # Camera setup
        self.camera_index = config.get('camera_index', 0)
        self.camera = None
        self.frame_width = config.get('frame_width', 640)
        self.frame_height = config.get('frame_height', 480)
        
        # State management
        self.running = False
        self.paused = False
        self.current_gesture = None
        self.last_gesture = None
        self.gesture_start_time = None
        self.gesture_hold_time = config.get('gesture_hold_time', 0.3)
        
        # Gesture history for complex gestures
        self.gesture_history = deque(maxlen=10)
        self.motion_history = deque(maxlen=30)
        
        # Performance
        self.fps = 0
        self.frame_count = 0
        self.last_fps_update = time.time()
        
        # Callbacks
        self.gesture_callbacks = {}
        self.status_callback = None
        
        # Drag state
        self.is_dragging = False
        self.drag_start_pos = None
        
        # Smoothing
        self.cursor_smoother = CursorSmoother(config)
        
    def start(self):
        """Start gesture recognition"""
        self.running = True
        self.logger.info("Starting gesture recognition...")
        
        # Open camera
        self.camera = cv2.VideoCapture(self.camera_index)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        self.camera.set(cv2.CAP_PROP_FPS, 30)
        
        # Main recognition loop
        while self.running:
            if not self.paused:
                self._process_frame()
            else:
                time.sleep(0.1)
        
        # Cleanup
        self.camera.release()
        cv2.destroyAllWindows()
        self.logger.info("Gesture recognition stopped")
    
    def _process_frame(self):
        """Process a single camera frame"""
        ret, frame = self.camera.read()
        if not ret:
            self.logger.warning("Failed to read camera frame")
            return
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Process hand tracking
        hand_data = self.hand_tracker.process_frame(frame)
        
        # Update FPS
        self._update_fps()
        
        # Process gestures if hands detected
        if hand_data['hands']:
            for hand in hand_data['hands']:
                gesture = self._recognize_gesture(hand)
                
                if gesture:
                    self._handle_gesture(gesture, hand)
        else:
            # No hands detected - reset states
            if self.is_dragging:
                self._end_drag()
            self.current_gesture = None
        
        # Display frame if enabled
        if self.config.get('show_camera_feed', False):
            self._display_frame(frame, hand_data)
        
        # Notify status callback
        if self.status_callback:
            self.status_callback(self.get_status())
    
    def _recognize_gesture(self, hand_data: Dict) -> Optional[str]:
        """Recognize gesture from hand data"""
        # Get finger pattern
        finger_pattern = hand_data['finger_states']['pattern']
        
        # Check static gestures
        for gesture_name, gesture_def in self.GESTURES.items():
            if 'fingers' in gesture_def:
                if finger_pattern == gesture_def['fingers']:
                    # Special case for thumbs up/down
                    if gesture_name == 'THUMBS_DOWN':
                        if hand_data['orientation']['direction'] != 'down':
                            continue
                    return gesture_name
        
        # Check custom gestures
        custom_gesture = self.gesture_processor.recognize_custom_gesture(hand_data)
        if custom_gesture:
            return custom_gesture
        
        # Check motion gestures
        motion_gesture = self._detect_motion_gesture(hand_data)
        if motion_gesture:
            return motion_gesture
        
        return None
    
    def _detect_motion_gesture(self, hand_data: Dict) -> Optional[str]:
        """Detect motion-based gestures like swipes"""
        # Add current position to motion history
        center = hand_data['center']
        self.motion_history.append({
            'position': center,
            'time': time.time()
        })
        
        # Need enough history for motion detection
        if len(self.motion_history) < 10:
            return None
        
        # Calculate motion vector
        start_pos = np.array(self.motion_history[0]['position'])
        end_pos = np.array(self.motion_history[-1]['position'])
        motion_vector = end_pos - start_pos
        
        # Calculate speed
        time_diff = self.motion_history[-1]['time'] - self.motion_history[0]['time']
        if time_diff == 0:
            return None
        
        speed = np.linalg.norm(motion_vector) / time_diff
        
        # Detect swipe gestures
        if speed > self.config.get('swipe_speed_threshold', 500):
            angle = np.arctan2(motion_vector[1], motion_vector[0])
            angle_degrees = np.degrees(angle)
            
            if -45 <= angle_degrees <= 45:
                return 'SWIPE_RIGHT'
            elif 135 <= angle_degrees or angle_degrees <= -135:
                return 'SWIPE_LEFT'
            elif 45 < angle_degrees < 135:
                return 'SWIPE_DOWN'
            else:
                return 'SWIPE_UP'
        
        return None
    
    def _handle_gesture(self, gesture: str, hand_data: Dict):
        """Handle recognized gesture"""
        # Update gesture state
        if gesture != self.current_gesture:
            self.last_gesture = self.current_gesture
            self.current_gesture = gesture
            self.gesture_start_time = time.time()
            self.logger.info(f"Gesture detected: {gesture}")
        
        # Check if gesture is held long enough
        if time.time() - self.gesture_start_time < self.gesture_hold_time:
            return
        
        # Get action from mapping
        action = self._get_gesture_action(gesture)
        
        # Execute action
        if action:
            self._execute_action(action, hand_data)
        
        # Call registered callback
        if gesture in self.gesture_callbacks:
            self.gesture_callbacks[gesture](hand_data)
    
    def _get_gesture_action(self, gesture: str) -> Optional[str]:
        """Get action for gesture from mappings"""
        # Check custom mappings first
        if gesture in self.gesture_mappings:
            return self.gesture_mappings[gesture]
        
        # Fall back to default
        if gesture in self.GESTURES:
            return self.GESTURES[gesture].get('action')
        
        return None
    
    def _execute_action(self, action: str, hand_data: Dict):
        """Execute the action associated with a gesture"""
        try:
            if action == 'cursor_move':
                # Smooth cursor movement
                smooth_pos = self.cursor_smoother.smooth(hand_data['center'])
                self.mouse_controller.move_cursor(smooth_pos)
                
            elif action == 'left_click':
                self.mouse_controller.click('left')
                
            elif action == 'right_click':
                self.mouse_controller.click('right')
                
            elif action == 'double_click':
                self.mouse_controller.double_click()
                
            elif action == 'scroll_up':
                self.mouse_controller.scroll(5)
                
            elif action == 'scroll_down':
                self.mouse_controller.scroll(-5)
                
            elif action == 'drag_start':
                if not self.is_dragging:
                    self._start_drag(hand_data['center'])
                    
            elif action == 'drag_end':
                if self.is_dragging:
                    self._end_drag()
                    
            elif action == 'switch_window':
                self.keyboard_controller.alt_tab()
                
            elif action == 'volume_up':
                self.system_controller.adjust_volume(10)
                
            elif action == 'volume_down':
                self.system_controller.adjust_volume(-10)
                
            elif action == 'voice_command':
                self.keyboard_controller.trigger_voice_command()
                
            elif action == 'screenshot':
                self.system_controller.take_screenshot()
                
            elif action == 'go_back':
                self.keyboard_controller.go_back()
                
            elif action == 'go_forward':
                self.keyboard_controller.go_forward()
                
            elif action == 'minimize':
                self.keyboard_controller.minimize_window()
                
            elif action == 'maximize':
                self.keyboard_controller.maximize_window()
                
            elif action == 'close':
                self.keyboard_controller.close_window()
                
            elif action == 'copy':
                self.keyboard_controller.copy()
                
            elif action == 'paste':
                self.keyboard_controller.paste()
                
            elif action == 'delete':
                self.keyboard_controller.delete()
                
            else:
                # Custom action - try to execute as keyboard shortcut
                self.keyboard_controller.execute_shortcut(action)
                
        except Exception as e:
            self.logger.error(f"Error executing action {action}: {e}")
    
    def _start_drag(self, position):
        """Start drag operation"""
        self.is_dragging = True
        self.drag_start_pos = position
        self.mouse_controller.drag_start()
        self.logger.info("Drag started")
    
    def _end_drag(self):
        """End drag operation"""
        self.is_dragging = False
        self.drag_start_pos = None
        self.mouse_controller.drag_end()
        self.logger.info("Drag ended")
    
    def _display_frame(self, frame: np.ndarray, hand_data: Dict):
        """Display the camera frame with overlays"""
        # Add status text
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        if self.current_gesture:
            cv2.putText(frame, f"Gesture: {self.current_gesture}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        # Show frame
        cv2.imshow('Hand Control System', frame)
        
        # Check for exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.stop()
    
    def _update_fps(self):
        """Update FPS calculation"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_update > 1.0:
            self.fps = self.frame_count / (current_time - self.last_fps_update)
            self.frame_count = 0
            self.last_fps_update = current_time
    
    def register_gesture_callback(self, gesture: str, callback: Callable):
        """Register a callback for a specific gesture"""
        self.gesture_callbacks[gesture] = callback
    
    def set_status_callback(self, callback: Callable):
        """Set callback for status updates"""
        self.status_callback = callback
    
    def update_gesture_mapping(self, gesture: str, action: str):
        """Update gesture to action mapping"""
        self.gesture_mappings[gesture] = action
        self.config_manager.save_gesture_mappings(self.gesture_mappings)
    
    def pause(self):
        """Pause gesture recognition"""
        self.paused = True
        self.logger.info("Gesture recognition paused")
    
    def resume(self):
        """Resume gesture recognition"""
        self.paused = False
        self.logger.info("Gesture recognition resumed")
    
    def stop(self):
        """Stop gesture recognition"""
        self.running = False
        self.logger.info("Stopping gesture recognition...")
    
    def is_active(self) -> bool:
        """Check if recognizer is active"""
        return self.running and not self.paused
    
    def get_current_gesture(self) -> Optional[str]:
        """Get current gesture"""
        return self.current_gesture
    
    def get_fps(self) -> float:
        """Get current FPS"""
        return self.fps
    
    def get_status(self) -> Dict:
        """Get current status"""
        return {
            'active': self.is_active(),
            'gesture': self.current_gesture,
            'fps': self.fps,
            'dragging': self.is_dragging
        }
    
    def update_config(self, config: dict):
        """Update configuration"""
        self.config.update(config)
        self.hand_tracker.update_config(config)
        self.gesture_processor.update_config(config)
        self.mouse_controller.update_config(config)
        self.cursor_smoother.update_config(config)


class CursorSmoother:
    """Smooth cursor movement using exponential moving average"""
    
    def __init__(self, config: dict):
        self.smoothing_factor = config.get('cursor_smoothing', 0.3)
        self.prev_position = None
        
    def smooth(self, position: tuple) -> tuple:
        """Apply smoothing to cursor position"""
        if self.prev_position is None:
            self.prev_position = position
            return position
        
        smoothed_x = int(self.smoothing_factor * position[0] + 
                        (1 - self.smoothing_factor) * self.prev_position[0])
        smoothed_y = int(self.smoothing_factor * position[1] + 
                        (1 - self.smoothing_factor) * self.prev_position[1])
        
        self.prev_position = (smoothed_x, smoothed_y)
        return self.prev_position
    
    def update_config(self, config: dict):
        """Update smoothing configuration"""
        self.smoothing_factor = config.get('cursor_smoothing', 0.3)
    
    def reset(self):
        """Reset smoother state"""
        self.prev_position = None
