"""
Command Processor Module
Natural language processing for voice commands
"""

import re
import difflib
from typing import List, Tuple, Optional
import logging

class CommandProcessor:
    """Process and match voice commands"""
    
    def __init__(self):
        self.logger = logging.getLogger('CommandProcessor')
        
        # Action keywords
        self.action_keywords = {
            'open': ['open', 'launch', 'start', 'run'],
            'close': ['close', 'exit', 'quit', 'stop'],
            'minimize': ['minimize', 'min', 'hide'],
            'maximize': ['maximize', 'max', 'fullscreen'],
            'copy': ['copy', 'duplicate'],
            'paste': ['paste', 'insert'],
            'delete': ['delete', 'remove', 'erase'],
            'screenshot': ['screenshot', 'capture', 'snap'],
            'volume': ['volume', 'sound', 'audio'],
            'brightness': ['brightness', 'bright', 'dim'],
            'scroll': ['scroll', 'move'],
            'search': ['search', 'find', 'look']
        }
        
        # Application aliases
        self.app_aliases = {
            'chrome': ['chrome', 'google chrome', 'browser'],
            'firefox': ['firefox', 'mozilla'],
            'edge': ['edge', 'microsoft edge'],
            'notepad': ['notepad', 'notes', 'text editor'],
            'calculator': ['calculator', 'calc'],
            'settings': ['settings', 'preferences', 'options'],
            'explorer': ['explorer', 'file explorer', 'files']
        }
    
    def match_command(self, input_text: str, commands: List[str], threshold: float = 0.6) -> Optional[str]:
        """Find best matching command using fuzzy matching"""
        input_lower = input_text.lower().strip()
        
        # Direct match
        if input_lower in commands:
            return input_lower
        
        # Fuzzy match
        matches = difflib.get_close_matches(input_lower, commands, n=1, cutoff=threshold)
        if matches:
            return matches[0]
        
        # Partial match
        for command in commands:
            if command in input_lower or input_lower in command:
                return command
        
        return None
    
    def extract_action(self, text: str) -> Tuple[Optional[str], List[str]]:
        """Extract action and parameters from natural language"""
        text_lower = text.lower().strip()
        
        # Check for action keywords
        for action, keywords in self.action_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Extract parameters
                    params = self._extract_parameters(text_lower, keyword)
                    return self._map_to_action(action, params), params
        
        return None, []
    
    def _extract_parameters(self, text: str, keyword: str) -> List[str]:
        """Extract parameters from command text"""
        # Remove the keyword and get the rest
        parts = text.split(keyword, 1)
        if len(parts) > 1:
            param_text = parts[1].strip()
            
            # Check for application names
            for app, aliases in self.app_aliases.items():
                for alias in aliases:
                    if alias in param_text:
                        return [app]
            
            # Return raw parameter
            if param_text:
                return [param_text]
        
        return []
    
    def _map_to_action(self, action_type: str, params: List[str]) -> str:
        """Map action type to specific action"""
        if action_type == 'open' and params:
            return 'open_app'
        elif action_type == 'close':
            return 'close_window'
        elif action_type == 'minimize':
            return 'minimize_window'
        elif action_type == 'maximize':
            return 'maximize_window'
        elif action_type == 'copy':
            return 'copy'
        elif action_type == 'paste':
            return 'paste'
        elif action_type == 'delete':
            return 'delete'
        elif action_type == 'screenshot':
            return 'screenshot'
        elif action_type == 'volume':
            if any(word in str(params) for word in ['up', 'increase', 'raise']):
                return 'volume_up'
            elif any(word in str(params) for word in ['down', 'decrease', 'lower']):
                return 'volume_down'
            else:
                return 'mute'
        elif action_type == 'brightness':
            if any(word in str(params) for word in ['up', 'increase', 'raise']):
                return 'brightness_up'
            else:
                return 'brightness_down'
        elif action_type == 'scroll':
            if any(word in str(params) for word in ['up', 'top']):
                return 'scroll_up'
            else:
                return 'scroll_down'
        elif action_type == 'search':
            return 'open_search'
        
        return action_type
    
    def normalize_command(self, text: str) -> str:
        """Normalize command text"""
        # Remove extra spaces
        text = ' '.join(text.split())
        
        # Remove common filler words
        filler_words = ['please', 'could you', 'can you', 'would you', 'the', 'a', 'an']
        for word in filler_words:
            text = text.replace(word, '')
        
        # Clean up
        text = ' '.join(text.split())
        
        return text.lower().strip()
    
    def extract_number(self, text: str) -> Optional[int]:
        """Extract number from text"""
        # Word to number mapping
        word_numbers = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
            'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
            'ten': 10, 'twenty': 20, 'thirty': 30, 'forty': 40,
            'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80,
            'ninety': 90, 'hundred': 100
        }
        
        # Check for word numbers
        for word, num in word_numbers.items():
            if word in text.lower():
                return num
        
        # Check for digit numbers
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        
        return None
