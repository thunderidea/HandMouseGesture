"""
Gesture Processing Module
Advanced gesture analysis and custom gesture recognition
"""

import numpy as np
import json
from typing import Dict, List, Optional, Tuple
from collections import deque
import logging
import math

class GestureProcessor:
    """Process and analyze hand gestures"""
    
    def __init__(self, config: dict):
        self.logger = logging.getLogger('GestureProcessor')
        self.config = config
        
        # Custom gesture templates
        self.custom_gestures = self._load_custom_gestures()
        
        # Gesture analysis parameters
        self.min_confidence = config.get('gesture_confidence', 0.8)
        self.gesture_buffer_size = config.get('gesture_buffer_size', 5)
        
        # Gesture buffers for stability
        self.gesture_buffer = deque(maxlen=self.gesture_buffer_size)
        
        # Pinch detection parameters
        self.pinch_threshold = config.get('pinch_threshold', 30)
        
        # OK sign detection parameters
        self.ok_threshold = config.get('ok_threshold', 40)
        
    def recognize_custom_gesture(self, hand_data: Dict) -> Optional[str]:
        """Recognize custom gestures"""
        landmarks = hand_data['landmarks']
        
        # Check for pinch gesture
        if self._detect_pinch(landmarks):
            return 'PINCH'
        
        # Check for OK sign
        if self._detect_ok_sign(landmarks):
            return 'OK_SIGN'
        
        # Check for custom trained gestures
        for gesture_name, template in self.custom_gestures.items():
            if self._match_custom_gesture(hand_data, template):
                return gesture_name
        
        return None
    
    def _detect_pinch(self, landmarks: List) -> bool:
        """Detect pinch gesture between thumb and index finger"""
        thumb_tip = np.array(landmarks[4][:2])
        index_tip = np.array(landmarks[8][:2])
        
        distance = np.linalg.norm(thumb_tip - index_tip)
        
        return distance < self.pinch_threshold
    
    def _detect_ok_sign(self, landmarks: List) -> bool:
        """Detect OK sign gesture"""
        thumb_tip = np.array(landmarks[4][:2])
        index_tip = np.array(landmarks[8][:2])
        middle_tip = np.array(landmarks[12][:2])
        ring_tip = np.array(landmarks[16][:2])
        pinky_tip = np.array(landmarks[20][:2])
        
        # Check if thumb and index are close (forming circle)
        thumb_index_dist = np.linalg.norm(thumb_tip - index_tip)
        
        # Check if other fingers are extended
        middle_extended = landmarks[12][1] < landmarks[10][1]
        ring_extended = landmarks[16][1] < landmarks[14][1]
        pinky_extended = landmarks[20][1] < landmarks[18][1]
        
        return (thumb_index_dist < self.ok_threshold and 
                middle_extended and ring_extended and pinky_extended)
    
    def _match_custom_gesture(self, hand_data: Dict, template: Dict) -> bool:
        """Match hand data against custom gesture template"""
        if 'finger_pattern' in template:
            if hand_data['finger_states']['pattern'] != template['finger_pattern']:
                return False
        
        if 'orientation' in template:
            angle_diff = abs(hand_data['orientation']['angle'] - template['orientation'])
            if angle_diff > template.get('angle_tolerance', 30):
                return False
        
        if 'landmarks' in template:
            similarity = self._calculate_landmark_similarity(
                hand_data['landmarks'],
                template['landmarks']
            )
            if similarity < template.get('similarity_threshold', 0.85):
                return False
        
        return True
    
    def _calculate_landmark_similarity(self, landmarks1: List, landmarks2: List) -> float:
        """Calculate similarity between two sets of landmarks"""
        # Normalize landmarks
        norm1 = self._normalize_landmarks(landmarks1)
        norm2 = self._normalize_landmarks(landmarks2)
        
        # Calculate cosine similarity
        flat1 = np.array(norm1).flatten()
        flat2 = np.array(norm2).flatten()
        
        similarity = np.dot(flat1, flat2) / (np.linalg.norm(flat1) * np.linalg.norm(flat2))
        
        return similarity
    
    def _normalize_landmarks(self, landmarks: List) -> List:
        """Normalize landmarks relative to wrist and scale"""
        wrist = np.array(landmarks[0])
        normalized = []
        
        # Calculate scale factor (distance from wrist to middle finger base)
        scale = np.linalg.norm(np.array(landmarks[9]) - wrist)
        if scale == 0:
            scale = 1
        
        for point in landmarks:
            norm_point = (np.array(point) - wrist) / scale
            normalized.append(norm_point.tolist())
        
        return normalized
    
    def analyze_gesture_dynamics(self, hand_history: List[Dict]) -> Dict:
        """Analyze gesture dynamics over time"""
        if len(hand_history) < 2:
            return {}
        
        dynamics = {
            'velocity': self._calculate_velocity(hand_history),
            'acceleration': self._calculate_acceleration(hand_history),
            'rotation': self._calculate_rotation(hand_history),
            'stability': self._calculate_stability(hand_history)
        }
        
        return dynamics
    
    def _calculate_velocity(self, hand_history: List[Dict]) -> float:
        """Calculate hand movement velocity"""
        if len(hand_history) < 2:
            return 0
        
        pos1 = np.array(hand_history[-2]['center'])
        pos2 = np.array(hand_history[-1]['center'])
        
        # Assuming 30 FPS
        time_delta = 1/30
        velocity = np.linalg.norm(pos2 - pos1) / time_delta
        
        return velocity
    
    def _calculate_acceleration(self, hand_history: List[Dict]) -> float:
        """Calculate hand movement acceleration"""
        if len(hand_history) < 3:
            return 0
        
        pos1 = np.array(hand_history[-3]['center'])
        pos2 = np.array(hand_history[-2]['center'])
        pos3 = np.array(hand_history[-1]['center'])
        
        v1 = pos2 - pos1
        v2 = pos3 - pos2
        
        time_delta = 1/30
        acceleration = np.linalg.norm(v2 - v1) / time_delta
        
        return acceleration
    
    def _calculate_rotation(self, hand_history: List[Dict]) -> float:
        """Calculate hand rotation speed"""
        if len(hand_history) < 2:
            return 0
        
        angle1 = hand_history[-2]['orientation']['angle']
        angle2 = hand_history[-1]['orientation']['angle']
        
        rotation = abs(angle2 - angle1)
        
        # Handle wrap-around
        if rotation > 180:
            rotation = 360 - rotation
        
        return rotation
    
    def _calculate_stability(self, hand_history: List[Dict]) -> float:
        """Calculate hand stability (inverse of jitter)"""
        if len(hand_history) < 3:
            return 1.0
        
        positions = [h['center'] for h in hand_history[-5:]]
        
        # Calculate variance
        positions_array = np.array(positions)
        variance = np.var(positions_array, axis=0).sum()
        
        # Convert to stability score (0-1)
        stability = 1.0 / (1.0 + variance / 100)
        
        return stability
    
    def add_custom_gesture(self, name: str, template: Dict):
        """Add a new custom gesture"""
        self.custom_gestures[name] = template
        self._save_custom_gestures()
        self.logger.info(f"Added custom gesture: {name}")
    
    def remove_custom_gesture(self, name: str):
        """Remove a custom gesture"""
        if name in self.custom_gestures:
            del self.custom_gestures[name]
            self._save_custom_gestures()
            self.logger.info(f"Removed custom gesture: {name}")
    
    def _load_custom_gestures(self) -> Dict:
        """Load custom gestures from file"""
        try:
            with open('config/custom_gestures.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            self.logger.error(f"Error loading custom gestures: {e}")
            return {}
    
    def _save_custom_gestures(self):
        """Save custom gestures to file"""
        try:
            with open('config/custom_gestures.json', 'w') as f:
                json.dump(self.custom_gestures, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving custom gestures: {e}")
    
    def update_config(self, config: dict):
        """Update processor configuration"""
        self.config.update(config)
        self.min_confidence = config.get('gesture_confidence', 0.8)
        self.pinch_threshold = config.get('pinch_threshold', 30)
        self.ok_threshold = config.get('ok_threshold', 40)
    
    def get_gesture_confidence(self, gesture: str) -> float:
        """Get confidence score for current gesture"""
        # Add gesture to buffer
        self.gesture_buffer.append(gesture)
        
        if len(self.gesture_buffer) < self.gesture_buffer_size:
            return 0.0
        
        # Calculate confidence based on consistency
        most_common = max(set(self.gesture_buffer), key=self.gesture_buffer.count)
        count = self.gesture_buffer.count(most_common)
        confidence = count / len(self.gesture_buffer)
        
        return confidence
    
    def detect_complex_gesture(self, hand_data: Dict, gesture_sequence: List[str]) -> bool:
        """Detect complex multi-step gestures"""
        # This would track gesture sequences over time
        # For example: double-tap, swipe-and-hold, etc.
        pass
    
    def calculate_gesture_features(self, hand_data: Dict) -> np.ndarray:
        """Extract features for machine learning models"""
        features = []
        
        # Landmark features
        landmarks = hand_data['landmarks']
        for point in landmarks:
            features.extend(point[:2])  # x, y coordinates
        
        # Finger state features
        finger_states = hand_data['finger_states']
        features.extend([
            float(finger_states['thumb']),
            float(finger_states['index']),
            float(finger_states['middle']),
            float(finger_states['ring']),
            float(finger_states['pinky'])
        ])
        
        # Orientation features
        features.append(hand_data['orientation']['angle'] / 180.0)
        
        # Distance features
        thumb_index_dist = np.linalg.norm(
            np.array(landmarks[4][:2]) - np.array(landmarks[8][:2])
        )
        features.append(thumb_index_dist / 100.0)
        
        return np.array(features)
