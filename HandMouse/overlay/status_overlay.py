"""
Status Overlay Module
Provides visual feedback overlay for gesture and voice recognition
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Optional, Dict
import logging

class StatusOverlay:
    """Transparent overlay window for status display"""
    
    def __init__(self):
        self.logger = logging.getLogger('StatusOverlay')
        
        # Create overlay window
        self.root = tk.Tk()
        self.root.title("Hand Control Overlay")
        
        # Make window transparent and always on top
        self.root.attributes('-alpha', 0.8)
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        
        # Position window
        self.root.geometry('300x150+20+20')
        
        # Configure style
        self.root.configure(bg='black')
        
        # Create widgets
        self._create_widgets()
        
        # Status data
        self.gesture_status = "Ready"
        self.voice_status = "Ready"
        self.current_gesture = None
        self.fps = 0
        
        # Animation
        self.animation_active = False
        
        # Start update thread
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
    
    def _create_widgets(self):
        """Create overlay widgets"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='black')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        self.title_label = tk.Label(
            main_frame,
            text="Hand Control",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='black'
        )
        self.title_label.pack(pady=(0, 10))
        
        # Gesture status
        gesture_frame = tk.Frame(main_frame, bg='black')
        gesture_frame.pack(fill='x', pady=5)
        
        tk.Label(
            gesture_frame,
            text="Gesture:",
            font=('Arial', 10),
            fg='gray',
            bg='black',
            width=10,
            anchor='w'
        ).pack(side='left')
        
        self.gesture_label = tk.Label(
            gesture_frame,
            text="Ready",
            font=('Arial', 10, 'bold'),
            fg='green',
            bg='black',
            anchor='w'
        )
        self.gesture_label.pack(side='left', fill='x', expand=True)
        
        # Current gesture
        self.current_gesture_label = tk.Label(
            main_frame,
            text="",
            font=('Arial', 9),
            fg='yellow',
            bg='black'
        )
        self.current_gesture_label.pack(fill='x')
        
        # Voice status
        voice_frame = tk.Frame(main_frame, bg='black')
        voice_frame.pack(fill='x', pady=5)
        
        tk.Label(
            voice_frame,
            text="Voice:",
            font=('Arial', 10),
            fg='gray',
            bg='black',
            width=10,
            anchor='w'
        ).pack(side='left')
        
        self.voice_label = tk.Label(
            voice_frame,
            text="Ready",
            font=('Arial', 10, 'bold'),
            fg='green',
            bg='black',
            anchor='w'
        )
        self.voice_label.pack(side='left', fill='x', expand=True)
        
        # FPS
        fps_frame = tk.Frame(main_frame, bg='black')
        fps_frame.pack(fill='x', pady=5)
        
        tk.Label(
            fps_frame,
            text="FPS:",
            font=('Arial', 10),
            fg='gray',
            bg='black',
            width=10,
            anchor='w'
        ).pack(side='left')
        
        self.fps_label = tk.Label(
            fps_frame,
            text="0",
            font=('Arial', 10),
            fg='white',
            bg='black',
            anchor='w'
        )
        self.fps_label.pack(side='left')
        
        # Close button (small X in corner)
        close_btn = tk.Button(
            self.root,
            text='×',
            font=('Arial', 12),
            fg='white',
            bg='black',
            bd=0,
            command=self.hide
        )
        close_btn.place(x=280, y=5)
        
        # Make window draggable
        self._make_draggable()
    
    def _make_draggable(self):
        """Make the overlay window draggable"""
        def start_move(event):
            self.x = event.x
            self.y = event.y
        
        def on_move(event):
            x = self.root.winfo_x() + event.x - self.x
            y = self.root.winfo_y() + event.y - self.y
            self.root.geometry(f'+{x}+{y}')
        
        self.title_label.bind('<Button-1>', start_move)
        self.title_label.bind('<B1-Motion>', on_move)
    
    def update_gesture_status(self, status: str, gesture: Optional[str] = None, fps: float = 0):
        """Update gesture recognition status"""
        self.gesture_status = status
        self.current_gesture = gesture
        self.fps = fps
    
    def update_voice_status(self, status: str, listening: bool = False):
        """Update voice recognition status"""
        self.voice_status = status
        if listening:
            self.animate_listening()
    
    def show_notification(self, message: str, duration: int = 3):
        """Show a temporary notification"""
        # Create notification window
        notif = tk.Toplevel(self.root)
        notif.overrideredirect(True)
        notif.attributes('-topmost', True)
        notif.attributes('-alpha', 0.9)
        
        # Position at top center
        screen_width = notif.winfo_screenwidth()
        x = (screen_width - 300) // 2
        notif.geometry(f'300x60+{x}+50')
        
        # Style
        notif.configure(bg='#2196F3')
        
        # Message
        msg_label = tk.Label(
            notif,
            text=message,
            font=('Arial', 11),
            fg='white',
            bg='#2196F3'
        )
        msg_label.pack(expand=True)
        
        # Auto close
        notif.after(duration * 1000, notif.destroy)
    
    def animate_listening(self):
        """Animate listening indicator"""
        self.animation_active = True
        
        def pulse():
            colors = ['yellow', 'orange', 'red', 'orange']
            for i in range(len(colors) * 2):
                if not self.animation_active:
                    break
                color = colors[i % len(colors)]
                self.voice_label.configure(fg=color)
                time.sleep(0.2)
            self.voice_label.configure(fg='green')
        
        threading.Thread(target=pulse, daemon=True).start()
    
    def stop_animation(self):
        """Stop listening animation"""
        self.animation_active = False
    
    def _update_loop(self):
        """Update display in loop"""
        while self.running:
            try:
                # Update gesture status
                if self.gesture_status == "Active":
                    self.gesture_label.configure(text="Active", fg='green')
                    if self.current_gesture:
                        self.current_gesture_label.configure(
                            text=f"▶ {self.current_gesture}"
                        )
                    else:
                        self.current_gesture_label.configure(text="")
                else:
                    self.gesture_label.configure(text="Inactive", fg='gray')
                    self.current_gesture_label.configure(text="")
                
                # Update FPS
                self.fps_label.configure(text=f"{self.fps:.1f}")
                
                # Update voice status
                if self.voice_status == "Listening":
                    self.voice_label.configure(text="Listening...", fg='yellow')
                elif self.voice_status == "Active":
                    self.voice_label.configure(text="Active", fg='green')
                else:
                    self.voice_label.configure(text="Inactive", fg='gray')
                
                time.sleep(0.1)
            except:
                break
    
    def show(self):
        """Show the overlay"""
        self.root.deiconify()
    
    def hide(self):
        """Hide the overlay"""
        self.root.withdraw()
    
    def close(self):
        """Close the overlay"""
        self.running = False
        try:
            self.root.destroy()
        except:
            pass
    
    def set_position(self, x: int, y: int):
        """Set overlay position"""
        self.root.geometry(f'+{x}+{y}')
    
    def set_transparency(self, alpha: float):
        """Set overlay transparency (0.0 to 1.0)"""
        self.root.attributes('-alpha', alpha)
