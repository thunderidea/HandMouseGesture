"""
Hand Tracking Module using MediaPipe
Provides real-time hand detection and landmark tracking
"""

import cv2
import mediapipe as mp
import numpy as np
import time
from typing import List, Tuple, Optional, Dict
import logging

class HandTracker:
    """Advanced hand tracking with MediaPipe"""
    
    def __init__(self, config: dict):
        self.logger = logging.getLogger('HandTracker')
        
        # MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Configuration
        self.max_hands = config.get('max_hands', 1)
        self.detection_confidence = config.get('detection_confidence', 0.7)
        self.tracking_confidence = config.get('tracking_confidence', 0.5)
        self.model_complexity = config.get('model_complexity', 1)
        
        # Initialize hand detector
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=self.max_hands,
            model_complexity=self.model_complexity,
            min_detection_confidence=self.detection_confidence,
            min_tracking_confidence=self.tracking_confidence
        )
        
        # Tracking data
        self.prev_landmarks = None
        self.landmark_history = []
        self.history_size = config.get('history_size', 5)
        
        # Smoothing parameters
        self.smoothing_enabled = config.get('smoothing_enabled', True)
        self.smoothing_factor = config.get('smoothing_factor', 0.5)
        
        # Performance tracking
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        
        # Drawing control
        self.should_draw = config.get('draw_landmarks', True)
        
    def process_frame(self, frame: np.ndarray) -> Dict:
        """Process a single frame and extract hand landmarks"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        
        # Process the frame
        results = self.hands.process(rgb_frame)
        
        # Update FPS
        self._update_fps()
        
        # Prepare output
        output = {
            'frame': frame,
            'hands': [],
            'fps': self.fps,
            'timestamp': time.time()
        }
        
        if results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Get hand info
                hand_info = self._process_hand(
                    hand_landmarks,
                    results.multi_handedness[hand_idx],
                    frame.shape
                )
                output['hands'].append(hand_info)
                
                # Draw landmarks if enabled
                if self.should_draw:
                    self._draw_landmarks(frame, hand_landmarks)
        
        # Update history
        self._update_history(output['hands'])
        
        return output
    
    def _process_hand(self, landmarks, handedness, frame_shape) -> Dict:
        """Process individual hand data"""
        h, w, _ = frame_shape
        
        # Extract landmark positions
        landmark_points = []
        for landmark in landmarks.landmark:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            z = landmark.z
            landmark_points.append([x, y, z])
        
        # Apply smoothing if enabled
        if self.smoothing_enabled and self.prev_landmarks is not None:
            landmark_points = self._smooth_landmarks(landmark_points)
        
        self.prev_landmarks = landmark_points
        
        # Calculate hand metrics
        hand_data = {
            'landmarks': landmark_points,
            'handedness': handedness.classification[0].label,
            'confidence': handedness.classification[0].score,
            'bounding_box': self._calculate_bounding_box(landmark_points),
            'center': self._calculate_center(landmark_points),
            'palm_size': self._calculate_palm_size(landmark_points),
            'finger_states': self._analyze_fingers(landmark_points),
            'orientation': self._calculate_orientation(landmark_points)
        }
        
        return hand_data
    
    def _smooth_landmarks(self, current_landmarks: List) -> List:
        """Apply exponential smoothing to landmarks"""
        if self.prev_landmarks is None:
            return current_landmarks
        
        smoothed = []
        alpha = self.smoothing_factor
        
        for i, (curr, prev) in enumerate(zip(current_landmarks, self.prev_landmarks)):
            smoothed_point = [
                alpha * curr[0] + (1 - alpha) * prev[0],
                alpha * curr[1] + (1 - alpha) * prev[1],
                alpha * curr[2] + (1 - alpha) * prev[2]
            ]
            smoothed.append(smoothed_point)
        
        return smoothed
    
    def _calculate_bounding_box(self, landmarks: List) -> Tuple[int, int, int, int]:
        """Calculate bounding box for hand"""
        x_coords = [p[0] for p in landmarks]
        y_coords = [p[1] for p in landmarks]
        
        return (
            min(x_coords),
            min(y_coords),
            max(x_coords),
            max(y_coords)
        )
    
    def _calculate_center(self, landmarks: List) -> Tuple[int, int]:
        """Calculate hand center point"""
        # Use wrist and middle finger base
        wrist = landmarks[0]
        middle_base = landmarks[9]
        
        center_x = int((wrist[0] + middle_base[0]) / 2)
        center_y = int((wrist[1] + middle_base[1]) / 2)
        
        return (center_x, center_y)
    
    def _calculate_palm_size(self, landmarks: List) -> float:
        """Calculate palm size for gesture scaling"""
        # Distance between wrist and middle finger base
        wrist = np.array(landmarks[0][:2])
        middle_base = np.array(landmarks[9][:2])
        
        return np.linalg.norm(middle_base - wrist)
    
    def _analyze_fingers(self, landmarks: List) -> Dict:
        """Analyze finger positions and states"""
        fingers = {
            'thumb': self._is_finger_up(landmarks, [1, 2, 3, 4], is_thumb=True),
            'index': self._is_finger_up(landmarks, [5, 6, 7, 8]),
            'middle': self._is_finger_up(landmarks, [9, 10, 11, 12]),
            'ring': self._is_finger_up(landmarks, [13, 14, 15, 16]),
            'pinky': self._is_finger_up(landmarks, [17, 18, 19, 20])
        }
        
        # Calculate additional metrics
        fingers['count'] = sum(fingers.values())
        fingers['pattern'] = self._encode_finger_pattern(fingers)
        
        return fingers
    
    def _is_finger_up(self, landmarks: List, indices: List[int], is_thumb: bool = False) -> bool:
        """Check if a finger is extended"""
        if is_thumb:
            # Special logic for thumb (horizontal comparison)
            return landmarks[indices[3]][0] > landmarks[indices[2]][0]  # For right hand
        else:
            # Vertical comparison for other fingers
            return landmarks[indices[3]][1] < landmarks[indices[1]][1]
    
    def _encode_finger_pattern(self, fingers: Dict) -> str:
        """Encode finger pattern as binary string"""
        pattern = ''
        for finger in ['thumb', 'index', 'middle', 'ring', 'pinky']:
            pattern += '1' if fingers[finger] else '0'
        return pattern
    
    def _calculate_orientation(self, landmarks: List) -> Dict:
        """Calculate hand orientation angles"""
        # Calculate vectors
        wrist = np.array(landmarks[0][:2])
        index_base = np.array(landmarks[5][:2])
        pinky_base = np.array(landmarks[17][:2])
        
        # Palm vector
        palm_vector = index_base - pinky_base
        
        # Calculate angle
        angle = np.arctan2(palm_vector[1], palm_vector[0])
        angle_degrees = np.degrees(angle)
        
        return {
            'angle': angle_degrees,
            'direction': self._get_direction(angle_degrees)
        }
    
    def _get_direction(self, angle: float) -> str:
        """Get hand direction from angle"""
        if -45 <= angle <= 45:
            return 'right'
        elif 45 < angle <= 135:
            return 'down'
        elif -135 <= angle < -45:
            return 'up'
        else:
            return 'left'
    
    def _draw_landmarks(self, frame: np.ndarray, landmarks):
        """Draw hand landmarks on frame"""
        self.mp_drawing.draw_landmarks(
            frame,
            landmarks,
            self.mp_hands.HAND_CONNECTIONS,
            self.mp_drawing_styles.get_default_hand_landmarks_style(),
            self.mp_drawing_styles.get_default_hand_connections_style()
        )
    
    def _update_history(self, hands: List[Dict]):
        """Update landmark history for temporal analysis"""
        self.landmark_history.append(hands)
        if len(self.landmark_history) > self.history_size:
            self.landmark_history.pop(0)
    
    def _update_fps(self):
        """Update FPS calculation"""
        self.frame_count += 1
        elapsed = time.time() - self.start_time
        
        if elapsed > 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.start_time = time.time()
    
    def get_gesture_features(self, hand_data: Dict) -> np.ndarray:
        """Extract features for gesture recognition"""
        features = []
        landmarks = hand_data['landmarks']
        
        # Normalize landmarks relative to wrist
        wrist = np.array(landmarks[0])
        normalized = []
        
        for point in landmarks:
            normalized_point = (np.array(point) - wrist) / hand_data['palm_size']
            normalized.extend(normalized_point[:2])  # Use only x, y
        
        features.extend(normalized)
        
        # Add finger states
        finger_states = hand_data['finger_states']
        features.extend([
            float(finger_states['thumb']),
            float(finger_states['index']),
            float(finger_states['middle']),
            float(finger_states['ring']),
            float(finger_states['pinky'])
        ])
        
        # Add orientation
        features.append(hand_data['orientation']['angle'] / 180.0)
        
        return np.array(features)
    
    def update_config(self, config: dict):
        """Update tracker configuration"""
        self.detection_confidence = config.get('detection_confidence', 0.7)
        self.tracking_confidence = config.get('tracking_confidence', 0.5)
        self.smoothing_enabled = config.get('smoothing_enabled', True)
        self.smoothing_factor = config.get('smoothing_factor', 0.5)
        self.should_draw = config.get('draw_landmarks', True)
        
        # Reinitialize hands with new config
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=self.max_hands,
            model_complexity=self.model_complexity,
            min_detection_confidence=self.detection_confidence,
            min_tracking_confidence=self.tracking_confidence
        )
    
    def release(self):
        """Release resources"""
        self.hands.close()
        self.logger.info("Hand tracker released")
