"""
System Controller Module
Controls system-level operations like volume, brightness, screenshots, etc.
"""

import os
import subprocess
import pyautogui
import logging
from datetime import datetime
from pathlib import Path
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import win32api
import win32con
import psutil

class SystemController:
    """Control system-level operations"""
    
    def __init__(self):
        self.logger = logging.getLogger('SystemController')
        
        # Initialize audio controller
        self._init_audio()
        
        # Screenshot directory
        self.screenshot_dir = Path.home() / 'Pictures' / 'HandControl_Screenshots'
        self.screenshot_dir.mkdir(exist_ok=True)
        
    def _init_audio(self):
        """Initialize audio controller"""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(interface, POINTER(IAudioEndpointVolume))
            self.logger.info("Audio controller initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize audio: {e}")
            self.volume = None
    
    # Volume Control
    def get_volume(self) -> int:
        """Get current volume level (0-100)"""
        if self.volume:
            try:
                current = self.volume.GetMasterVolumeLevelScalar()
                return int(current * 100)
            except Exception as e:
                self.logger.error(f"Error getting volume: {e}")
        return 0
    
    def set_volume(self, level: int):
        """Set volume level (0-100)"""
        if self.volume:
            try:
                level = max(0, min(100, level))
                self.volume.SetMasterVolumeLevelScalar(level / 100, None)
                self.logger.debug(f"Volume set to {level}%")
            except Exception as e:
                self.logger.error(f"Error setting volume: {e}")
    
    def adjust_volume(self, change: int):
        """Adjust volume by specified amount"""
        current = self.get_volume()
        new_level = current + change
        self.set_volume(new_level)
    
    def mute_volume(self):
        """Toggle mute"""
        if self.volume:
            try:
                is_muted = self.volume.GetMute()
                self.volume.SetMute(not is_muted, None)
                self.logger.debug(f"Mute {'enabled' if not is_muted else 'disabled'}")
            except Exception as e:
                self.logger.error(f"Error toggling mute: {e}")
    
    # Brightness Control
    def get_brightness(self) -> int:
        """Get current brightness level (0-100)"""
        try:
            brightness = sbc.get_brightness()[0]
            return brightness
        except Exception as e:
            self.logger.error(f"Error getting brightness: {e}")
            return 50
    
    def set_brightness(self, level: int):
        """Set brightness level (0-100)"""
        try:
            level = max(0, min(100, level))
            sbc.set_brightness(level)
            self.logger.debug(f"Brightness set to {level}%")
        except Exception as e:
            self.logger.error(f"Error setting brightness: {e}")
    
    def adjust_brightness(self, change: int):
        """Adjust brightness by specified amount"""
        current = self.get_brightness()
        new_level = current + change
        self.set_brightness(new_level)
    
    # Screenshot
    def take_screenshot(self, region=None) -> str:
        """Take a screenshot and save it"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.screenshot_dir / f"screenshot_{timestamp}.png"
            
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
            
            screenshot.save(filename)
            self.logger.info(f"Screenshot saved: {filename}")
            
            # Open the screenshot
            os.startfile(filename)
            
            return str(filename)
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
            return ""
    
    # Application Control
    def open_application(self, app_name: str):
        """Open an application"""
        app_commands = {
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'edge': 'msedge.exe',
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'explorer': 'explorer.exe',
            'cmd': 'cmd.exe',
            'powershell': 'powershell.exe',
            'settings': 'ms-settings:',
            'this pc': 'explorer.exe ::{20D04FE0-3AEA-1069-A2D8-08002B30309D}',
            'control panel': 'control.exe'
        }
        
        app_name_lower = app_name.lower()
        
        if app_name_lower in app_commands:
            try:
                if app_name_lower == 'settings':
                    os.system('start ms-settings:')
                else:
                    subprocess.Popen(app_commands[app_name_lower], shell=True)
                self.logger.info(f"Opened application: {app_name}")
            except Exception as e:
                self.logger.error(f"Error opening {app_name}: {e}")
        else:
            # Try to open as is
            try:
                subprocess.Popen(app_name, shell=True)
                self.logger.info(f"Opened: {app_name}")
            except Exception as e:
                self.logger.error(f"Could not open {app_name}: {e}")
    
    def close_application(self, app_name: str):
        """Close an application by name"""
        try:
            for proc in psutil.process_iter(['name']):
                if app_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    self.logger.info(f"Closed application: {app_name}")
                    return True
            self.logger.warning(f"Application not found: {app_name}")
            return False
        except Exception as e:
            self.logger.error(f"Error closing {app_name}: {e}")
            return False
    
    def list_running_applications(self) -> list:
        """Get list of running applications"""
        apps = []
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] not in ['System', 'Registry']:
                    apps.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name']
                    })
        except Exception as e:
            self.logger.error(f"Error listing applications: {e}")
        return apps
    
    # System Information
    def get_system_info(self) -> dict:
        """Get system information"""
        try:
            info = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'battery': self._get_battery_info()
            }
            return info
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {}
    
    def _get_battery_info(self) -> dict:
        """Get battery information"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': battery.percent,
                    'plugged': battery.power_plugged,
                    'time_left': battery.secsleft if battery.secsleft != -1 else None
                }
        except:
            pass
        return {}
    
    # File Operations
    def open_file_explorer(self, path: str = None):
        """Open file explorer at specified path"""
        try:
            if path:
                subprocess.Popen(f'explorer "{path}"')
            else:
                subprocess.Popen('explorer')
            self.logger.info("File explorer opened")
        except Exception as e:
            self.logger.error(f"Error opening file explorer: {e}")
    
    def open_url(self, url: str):
        """Open URL in default browser"""
        try:
            import webbrowser
            webbrowser.open(url)
            self.logger.info(f"Opened URL: {url}")
        except Exception as e:
            self.logger.error(f"Error opening URL: {e}")
    
    # Power Management
    def lock_screen(self):
        """Lock the screen"""
        try:
            import ctypes
            ctypes.windll.user32.LockWorkStation()
            self.logger.info("Screen locked")
        except Exception as e:
            self.logger.error(f"Error locking screen: {e}")
    
    def sleep_system(self):
        """Put system to sleep"""
        try:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            self.logger.info("System sleeping")
        except Exception as e:
            self.logger.error(f"Error putting system to sleep: {e}")
    
    def shutdown_system(self, restart: bool = False):
        """Shutdown or restart system"""
        try:
            if restart:
                os.system("shutdown /r /t 0")
                self.logger.info("System restarting")
            else:
                os.system("shutdown /s /t 0")
                self.logger.info("System shutting down")
        except Exception as e:
            self.logger.error(f"Error shutting down system: {e}")
    
    # Clipboard Operations
    def get_clipboard(self) -> str:
        """Get clipboard content"""
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            return data
        except Exception as e:
            self.logger.error(f"Error getting clipboard: {e}")
            return ""
    
    def set_clipboard(self, text: str):
        """Set clipboard content"""
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text)
            win32clipboard.CloseClipboard()
            self.logger.debug("Clipboard updated")
        except Exception as e:
            self.logger.error(f"Error setting clipboard: {e}")
