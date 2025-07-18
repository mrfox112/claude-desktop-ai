import tkinter as tk
from tkinter import scrolledtext, messagebox, font, filedialog, ttk
import anthropic
import os
from dotenv import load_dotenv
import threading
import asyncio
import aiohttp
import queue
import webbrowser
import subprocess
import sys
from pathlib import Path

# Try to import tkinterdnd2 for drag-and-drop
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DRAG_DROP_AVAILABLE = True
except ImportError:
    DRAG_DROP_AVAILABLE = False
    print("⚠️ tkinterdnd2 not available. Drag-and-drop features disabled.")

# Optional imports for advanced features - all imports are lazy
BERT_AVAILABLE = True  # Will be checked when actually importing
BERT_TOKENIZER = None
BERT_MODEL = None

try:
    import speech_recognition as sr
    import pyttsx3
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    print("⚠️ Speech features not available. Install speechrecognition and pyttsx3.")
import json
import sqlite3
from datetime import datetime, timedelta
import time
import hashlib
import re
from collections import defaultdict, deque
import logging
from typing import Dict, List, Optional, Tuple, Any, Callable
import random
import numpy as np
from dataclasses import dataclass

import ttkbootstrap as ttkb
from ttkbootstrap.dialogs import Messagebox
try:
    from ttkbootstrap.tooltips import ToolTip
except ImportError:
    ToolTip = None  # Gracefully handle missing tooltips
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Import intelligence enhancement system
try:
    from claude_intelligence import SmartClaudeProcessor
    INTELLIGENCE_AVAILABLE = True
except ImportError:
    INTELLIGENCE_AVAILABLE = False
    print("⚠️ Intelligence enhancement not available. Install missing dependencies.")

# Import advanced AI system - lazy loading
ADVANCED_AI_AVAILABLE = True  # Will be checked when actually importing
ADVANCED_AI_SYSTEM = None

# Import model optimization system - lazy loading
OPTIMIZATION_AVAILABLE = True  # Will be checked when actually importing
OPTIMIZATION_MANAGER = None

# Load environment variables
load_dotenv()

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ether_ai.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UIAnimationManager:
    """Manager for smooth UI animations and effects"""
    
    def __init__(self, root):
        self.root = root
        self.animations = {}
        self.fade_steps = 20
        self.fade_delay = 20
        self.slide_steps = 15
        self.slide_delay = 15
        
    def fade_in(self, widget, start_alpha=0.0, end_alpha=1.0, callback=None):
        """Fade in animation for widgets"""
        if not hasattr(widget, 'winfo_exists') or not widget.winfo_exists():
            return
            
        steps = self.fade_steps
        step_size = (end_alpha - start_alpha) / steps
        current_alpha = start_alpha
        
        def animate_step():
            nonlocal current_alpha
            if current_alpha < end_alpha:
                current_alpha += step_size
                try:
                    widget.configure(state='normal')
                    self.root.attributes('-alpha', min(current_alpha, 1.0))
                    self.root.after(self.fade_delay, animate_step)
                except tk.TclError:
                    pass
            else:
                if callback:
                    callback()
        
        animate_step()
    
    def fade_out(self, widget, start_alpha=1.0, end_alpha=0.0, callback=None):
        """Fade out animation for widgets"""
        if not hasattr(widget, 'winfo_exists') or not widget.winfo_exists():
            return
            
        steps = self.fade_steps
        step_size = (start_alpha - end_alpha) / steps
        current_alpha = start_alpha
        
        def animate_step():
            nonlocal current_alpha
            if current_alpha > end_alpha:
                current_alpha -= step_size
                try:
                    self.root.attributes('-alpha', max(current_alpha, 0.0))
                    self.root.after(self.fade_delay, animate_step)
                except tk.TclError:
                    pass
            else:
                if callback:
                    callback()
        
        animate_step()
    
    def slide_in(self, widget, direction='left', distance=100, callback=None):
        """Slide in animation for widgets"""
        if not hasattr(widget, 'winfo_exists') or not widget.winfo_exists():
            return
            
        original_x = widget.winfo_x()
        original_y = widget.winfo_y()
        
        if direction == 'left':
            start_x = original_x - distance
            start_y = original_y
        elif direction == 'right':
            start_x = original_x + distance
            start_y = original_y
        elif direction == 'up':
            start_x = original_x
            start_y = original_y - distance
        else:  # down
            start_x = original_x
            start_y = original_y + distance
        
        widget.place(x=start_x, y=start_y)
        
        steps = self.slide_steps
        step_x = (original_x - start_x) / steps
        step_y = (original_y - start_y) / steps
        
        def animate_step(current_step=0):
            if current_step < steps:
                new_x = start_x + (step_x * current_step)
                new_y = start_y + (step_y * current_step)
                try:
                    widget.place(x=new_x, y=new_y)
                    self.root.after(self.slide_delay, lambda: animate_step(current_step + 1))
                except tk.TclError:
                    pass
            else:
                widget.place(x=original_x, y=original_y)
                if callback:
                    callback()
        
        animate_step()
    
    def pulse_effect(self, widget, color='#FFD700', duration=1000):
        """Create a pulse effect on widget"""
        if not hasattr(widget, 'winfo_exists') or not widget.winfo_exists():
            return
            
        original_bg = widget.cget('bg') if hasattr(widget, 'cget') else None
        if not original_bg:
            return
            
        def pulse():
            try:
                widget.configure(bg=color)
                self.root.after(duration // 2, lambda: widget.configure(bg=original_bg))
            except tk.TclError:
                pass
        
        pulse()
    
    def smooth_resize(self, widget, target_width, target_height, callback=None):
        """Smooth resize animation for widgets"""
        if not hasattr(widget, 'winfo_exists') or not widget.winfo_exists():
            return
            
        current_width = widget.winfo_width()
        current_height = widget.winfo_height()
        
        steps = 10
        width_step = (target_width - current_width) / steps
        height_step = (target_height - current_height) / steps
        
        def animate_step(current_step=0):
            if current_step < steps:
                new_width = current_width + (width_step * current_step)
                new_height = current_height + (height_step * current_step)
                try:
                    widget.configure(width=int(new_width), height=int(new_height))
                    self.root.after(30, lambda: animate_step(current_step + 1))
                except tk.TclError:
                    pass
            else:
                if callback:
                    callback()
        
        animate_step()

class DragDropManager:
    """Manager for drag-and-drop functionality"""
    
    def __init__(self, root):
        self.root = root
        self.drop_targets = {}
        self.drag_data = {}
        
    def setup_drag_drop(self, widget, drop_callback=None):
        """Setup drag-and-drop for a widget"""
        if not DRAG_DROP_AVAILABLE:
            return False
            
        try:
            # Enable file dropping
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind('<<Drop>>', lambda e: self.handle_drop(e, drop_callback))
            widget.dnd_bind('<<DragEnter>>', self.handle_drag_enter)
            widget.dnd_bind('<<DragLeave>>', self.handle_drag_leave)
            return True
        except Exception as e:
            print(f"Failed to setup drag-and-drop: {e}")
            return False
    
    def handle_drop(self, event, callback=None):
        """Handle file drop events"""
        files = event.data.split()
        if callback:
            callback(files)
    
    def handle_drag_enter(self, event):
        """Handle drag enter events"""
        widget = event.widget
        if hasattr(widget, 'configure'):
            try:
                widget.configure(relief='raised', bd=2)
            except tk.TclError:
                pass
    
    def handle_drag_leave(self, event):
        """Handle drag leave events"""
        widget = event.widget
        if hasattr(widget, 'configure'):
            try:
                widget.configure(relief='flat', bd=1)
            except tk.TclError:
                pass
    
    def make_draggable(self, widget):
        """Make a widget draggable"""
        def start_drag(event):
            widget.startX = event.x
            widget.startY = event.y
        
        def do_drag(event):
            x = widget.winfo_x() + (event.x - widget.startX)
            y = widget.winfo_y() + (event.y - widget.startY)
            widget.place(x=x, y=y)
        
        widget.bind('<Button-1>', start_drag)
        widget.bind('<B1-Motion>', do_drag)

class LayoutManager:
    """Manager for customizable layouts and component positioning"""
    
    def __init__(self, root):
        self.root = root
        self.layouts = {
            'default': {
                'chat_area': {'row': 1, 'column': 0, 'sticky': 'nsew', 'columnspan': 1},
                'input_area': {'row': 2, 'column': 0, 'sticky': 'ew', 'columnspan': 1},
                'sidebar': {'row': 0, 'column': 1, 'sticky': 'ns', 'rowspan': 3}
            },
            'compact': {
                'chat_area': {'row': 0, 'column': 0, 'sticky': 'nsew', 'columnspan': 2},
                'input_area': {'row': 1, 'column': 0, 'sticky': 'ew', 'columnspan': 2},
                'sidebar': {'row': 2, 'column': 0, 'sticky': 'ew', 'columnspan': 2}
            },
            'sidebar_left': {
                'sidebar': {'row': 0, 'column': 0, 'sticky': 'ns', 'rowspan': 3},
                'chat_area': {'row': 1, 'column': 1, 'sticky': 'nsew', 'columnspan': 1},
                'input_area': {'row': 2, 'column': 1, 'sticky': 'ew', 'columnspan': 1}
            },
            'fullscreen': {
                'chat_area': {'row': 0, 'column': 0, 'sticky': 'nsew', 'columnspan': 3},
                'input_area': {'row': 1, 'column': 0, 'sticky': 'ew', 'columnspan': 3}
            }
        }
        self.current_layout = 'default'
        self.component_widgets = {}
        self.resizable_components = set()
        
    def register_component(self, name, widget, resizable=False):
        """Register a component for layout management"""
        self.component_widgets[name] = widget
        if resizable:
            self.resizable_components.add(name)
            self.make_resizable(widget)
    
    def make_resizable(self, widget):
        """Make a widget resizable with drag handles"""
        # Add resize handles
        resize_frame = tk.Frame(widget.master, bg='gray', cursor='sizing')
        resize_frame.place(relx=1.0, rely=1.0, anchor='se', width=10, height=10)
        
        def start_resize(event):
            widget.start_width = widget.winfo_width()
            widget.start_height = widget.winfo_height()
            widget.start_x = event.x_root
            widget.start_y = event.y_root
        
        def do_resize(event):
            new_width = widget.start_width + (event.x_root - widget.start_x)
            new_height = widget.start_height + (event.y_root - widget.start_y)
            if new_width > 100 and new_height > 100:
                widget.configure(width=new_width, height=new_height)
        
        resize_frame.bind('<Button-1>', start_resize)
        resize_frame.bind('<B1-Motion>', do_resize)
    
    def apply_layout(self, layout_name):
        """Apply a specific layout"""
        if layout_name not in self.layouts:
            return False
            
        layout = self.layouts[layout_name]
        
        # Apply layout to registered components
        for component_name, widget in self.component_widgets.items():
            if component_name in layout:
                config = layout[component_name]
                try:
                    widget.grid(**config)
                except tk.TclError:
                    pass
        
        self.current_layout = layout_name
        return True
    
    def save_custom_layout(self, name, layout_config):
        """Save a custom layout configuration"""
        self.layouts[name] = layout_config
    
    def get_available_layouts(self):
        """Get list of available layouts"""
        return list(self.layouts.keys())
    
    def create_layout_editor(self, parent):
        """Create a layout editor interface"""
        editor_window = tk.Toplevel(parent)
        editor_window.title("Layout Editor")
        editor_window.geometry("400x300")
        
        frame = ttk.Frame(editor_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Layout Editor", font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Layout selection
        layout_frame = ttk.Frame(frame)
        layout_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(layout_frame, text="Current Layout:").pack(side=tk.LEFT)
        layout_var = tk.StringVar(editor_window, value=self.current_layout)
        layout_combo = ttk.Combobox(layout_frame, textvariable=layout_var, 
                                  values=self.get_available_layouts(), state='readonly')
        layout_combo.pack(side=tk.LEFT, padx=5)
        
        def apply_selected_layout():
            selected = layout_var.get()
            if self.apply_layout(selected):
                messagebox.showinfo("Layout Applied", f"Layout '{selected}' applied successfully!")
            else:
                messagebox.showerror("Error", f"Failed to apply layout '{selected}'")
        
        ttk.Button(layout_frame, text="Apply", command=apply_selected_layout).pack(side=tk.LEFT, padx=5)
        
        # Component list
        components_frame = ttk.LabelFrame(frame, text="Components", padding="5")
        components_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        component_listbox = tk.Listbox(components_frame)
        component_listbox.pack(fill=tk.BOTH, expand=True)
        
        for component in self.component_widgets.keys():
            component_listbox.insert(tk.END, component)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Reset to Default", 
                  command=lambda: self.apply_layout('default')).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=editor_window.destroy).pack(side=tk.RIGHT, padx=5)

class ThemeManager:
    """Advanced theme manager with sophisticated color schemes and styling"""
    
    def __init__(self):
        self.themes = {
            'ethereal_light': {
                'name': '✨ Ethereal Light',
                'category': 'Premium',
                'background': '#e8f4fd',
                'chat_bg': '#f5f9ff',
                'user_color': '#d1e7ff',
                'ether_color': '#e1f2ff',
                'text_color': '#1a365d',
                'primary_color': '#2d5aa0',
                'accent_color': '#4a6bb5',
                'secondary_bg': '#f0f8ff',
                'border_color': '#7bb3f0',
                'hover_color': '#dbeafe',
                'success_color': '#10b981',
                'warning_color': '#f59e0b',
                'error_color': '#ef4444',
                'info_color': '#3b82f6',
                'shadow': '0 4px 12px #2d5aa0',
                'button_gradient': 'linear-gradient(135deg, #2d5aa0 0%, #4a6bb5 100%)',
                'header_gradient': 'linear-gradient(135deg, #e8f4fd 0%, #d1e7ff 100%)'
            },
            'midnight_elegance': {
                'name': '🌙 Midnight Elegance',
                'category': 'Premium',
                'background': '#0f172a',
                'chat_bg': '#1e293b',
                'user_color': '#334155',
                'ether_color': '#475569',
                'text_color': '#f1f5f9',
                'primary_color': '#60a5fa',
                'accent_color': '#3b82f6',
                'secondary_bg': '#0f1419',
                'border_color': '#1e40af',
                'hover_color': '#1e293b',
                'success_color': '#10b981',
                'warning_color': '#f59e0b',
                'error_color': '#ef4444',
                'info_color': '#06b6d4',
                'shadow': '0 4px 16px #1e40af',
                'button_gradient': 'linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%)',
                'header_gradient': 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)'
            },
            'neon_cyberpunk': {
                'name': '🚀 Neon Cyberpunk',
                'category': 'Futuristic',
                'background': '#0a0a0a',
                'chat_bg': '#111111',
                'user_color': '#1a0033',
                'ether_color': '#001a33',
                'text_color': '#00ffff',
                'primary_color': '#ff0080',
                'accent_color': '#00ff41',
                'secondary_bg': '#1a1a1a',
                'border_color': '#ff0080',
                'hover_color': '#2a0a2a',
                'success_color': '#00ff41',
                'warning_color': '#ffff00',
                'error_color': '#ff0040',
                'info_color': '#00ffff',
                'shadow': '0 0 20px #ff0080',
                'button_gradient': 'linear-gradient(135deg, #ff0080 0%, #00ffff 100%)',
                'header_gradient': 'linear-gradient(135deg, #ff0080 0%, #00ff41 100%)'
            },
            'ocean_depths': {
                'name': '🌊 Ocean Depths',
                'category': 'Nature',
                'background': '#0f2027',
                'chat_bg': '#203a43',
                'user_color': '#2c5282',
                'ether_color': '#2a69ac',
                'text_color': '#e0f2fe',
                'primary_color': '#00acc1',
                'accent_color': '#0277bd',
                'secondary_bg': '#1a365d',
                'border_color': '#0891b2',
                'hover_color': '#155e75',
                'success_color': '#0d9488',
                'warning_color': '#f59e0b',
                'error_color': '#ef4444',
                'info_color': '#06b6d4',
                'shadow': '0 4px 12px #00acc1',
                'button_gradient': 'linear-gradient(135deg, #00acc1 0%, #0277bd 100%)',
                'header_gradient': 'linear-gradient(135deg, #0f2027 0%, #203a43 100%)'
            },
            'forest_whisper': {
                'name': '🌲 Forest Whisper',
                'category': 'Nature',
                'background': '#0f2027',
                'chat_bg': '#1a3b2e',
                'user_color': '#276749',
                'ether_color': '#2f855a',
                'text_color': '#f0fff4',
                'primary_color': '#10b981',
                'accent_color': '#059669',
                'secondary_bg': '#064e3b',
                'border_color': '#047857',
                'hover_color': '#065f46',
                'success_color': '#10b981',
                'warning_color': '#f59e0b',
                'error_color': '#ef4444',
                'info_color': '#06b6d4',
                'shadow': '0 4px 12px #10b981',
                'button_gradient': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                'header_gradient': 'linear-gradient(135deg, #0f2027 0%, #1a3b2e 100%)'
            },
            'sunset_dreams': {
                'name': '🌅 Sunset Dreams',
                'category': 'Warm',
                'background': '#451a03',
                'chat_bg': '#7c2d12',
                'user_color': '#ea580c',
                'ether_color': '#f97316',
                'text_color': '#fff7ed',
                'primary_color': '#f97316',
                'accent_color': '#ea580c',
                'secondary_bg': '#9a3412',
                'border_color': '#fb923c',
                'hover_color': '#c2410c',
                'success_color': '#10b981',
                'warning_color': '#f59e0b',
                'error_color': '#ef4444',
                'info_color': '#06b6d4',
                'shadow': '0 4px 12px #f97316',
                'button_gradient': 'linear-gradient(135deg, #f97316 0%, #ea580c 100%)',
                'header_gradient': 'linear-gradient(135deg, #451a03 0%, #7c2d12 100%)'
            },
            'royal_purple': {
                'name': '👑 Royal Purple',
                'category': 'Luxury',
                'background': '#3b0764',
                'chat_bg': '#581c87',
                'user_color': '#7c3aed',
                'ether_color': '#8b5cf6',
                'text_color': '#faf5ff',
                'primary_color': '#8b5cf6',
                'accent_color': '#7c3aed',
                'secondary_bg': '#6b21a8',
                'border_color': '#a855f7',
                'hover_color': '#7c2d92',
                'success_color': '#10b981',
                'warning_color': '#f59e0b',
                'error_color': '#ef4444',
                'info_color': '#06b6d4',
                'shadow': '0 4px 16px #8b5cf6',
                'button_gradient': 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                'header_gradient': 'linear-gradient(135deg, #3b0764 0%, #581c87 100%)'
            },
            'arctic_ice': {
                'name': '❄️ Arctic Ice',
                'category': 'Cool',
                'background': '#0c1222',
                'chat_bg': '#1e3a8a',
                'user_color': '#3b82f6',
                'ether_color': '#60a5fa',
                'text_color': '#f0f9ff',
                'primary_color': '#3b82f6',
                'accent_color': '#2563eb',
                'secondary_bg': '#1e40af',
                'border_color': '#60a5fa',
                'hover_color': '#1d4ed8',
                'success_color': '#10b981',
                'warning_color': '#f59e0b',
                'error_color': '#ef4444',
                'info_color': '#06b6d4',
                'shadow': '0 4px 12px #3b82f6',
                'button_gradient': 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                'header_gradient': 'linear-gradient(135deg, #0c1222 0%, #1e3a8a 100%)'
            },
            'rose_gold': {
                'name': '🌹 Rose Gold',
                'category': 'Luxury',
                'background': '#4c1d24',
                'chat_bg': '#881337',
                'user_color': '#e11d48',
                'ether_color': '#f43f5e',
                'text_color': '#fdf2f8',
                'primary_color': '#e11d48',
                'accent_color': '#be123c',
                'secondary_bg': '#9f1239',
                'border_color': '#f43f5e',
                'hover_color': '#a21308',
                'success_color': '#10b981',
                'warning_color': '#f59e0b',
                'error_color': '#ef4444',
                'info_color': '#06b6d4',
                'shadow': '0 4px 16px #e11d48',
                'button_gradient': 'linear-gradient(135deg, #e11d48 0%, #be123c 100%)',
                'header_gradient': 'linear-gradient(135deg, #4c1d24 0%, #881337 100%)'
            },
            'cosmic_void': {
                'name': '🌌 Cosmic Void',
                'category': 'Futuristic',
                'background': '#000000',
                'chat_bg': '#0a0a0a',
                'user_color': '#1a0d1a',
                'ether_color': '#0d0d1a',
                'text_color': '#ffffff',
                'primary_color': '#9c27b0',
                'accent_color': '#7b1fa2',
                'secondary_bg': '#050505',
                'border_color': '#333333',
                'hover_color': '#1a1a1a',
                'success_color': '#4caf50',
                'warning_color': '#ff9800',
                'error_color': '#f44336',
                'info_color': '#2196f3',
                'shadow': '0 0 20px #9c27b0',
                'button_gradient': 'linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%)',
                'header_gradient': 'linear-gradient(135deg, #333333 0%, #000000 100%)'
            },
            'golden_hour': {
                'name': '🌇 Golden Hour',
                'category': 'Warm',
                'background': '#7c2d12',
                'chat_bg': '#a16207',
                'user_color': '#d97706',
                'ether_color': '#f59e0b',
                'text_color': '#fefce8',
                'primary_color': '#eab308',
                'accent_color': '#ca8a04',
                'secondary_bg': '#92400e',
                'border_color': '#facc15',
                'hover_color': '#a16207',
                'success_color': '#10b981',
                'warning_color': '#f59e0b',
                'error_color': '#ef4444',
                'info_color': '#06b6d4',
                'shadow': '0 4px 16px #eab308',
                'button_gradient': 'linear-gradient(135deg, #eab308 0%, #ca8a04 100%)',
                'header_gradient': 'linear-gradient(135deg, #7c2d12 0%, #a16207 100%)'
            }
        }
        self.current_theme = 'ethereal_light'
        self.theme_categories = {
            'Premium': ['ethereal_light', 'midnight_elegance'],
            'Futuristic': ['neon_cyberpunk', 'cosmic_void'],
            'Nature': ['ocean_depths', 'forest_whisper'],
            'Warm': ['sunset_dreams', 'golden_hour'],
            'Luxury': ['royal_purple', 'rose_gold'],
            'Cool': ['arctic_ice']
        }

    def get_theme_names(self):
        """Get list of available theme names"""
        return [(key, theme['name']) for key, theme in self.themes.items()]

    def apply_theme(self, theme_key: str, app):
        """Apply comprehensive theme that affects every UI element"""
        if theme_key not in self.themes:
            theme_key = 'ethereal_light'
        
        theme_config = self.themes[theme_key]
        
        # Apply theme colors to app
        app.bg_color = theme_config['background']
        app.chat_bg = theme_config['chat_bg']
        app.user_color = theme_config['user_color']
        app.claude_color = theme_config['ether_color']
        app.text_color = theme_config['text_color']
        app.primary_color = theme_config['primary_color']
        app.secondary_color = theme_config['accent_color']

        # Apply to root window with theme-specific styling
        app.root.configure(bg=app.bg_color)
        
        # Apply comprehensive styling to all UI elements
        self._apply_comprehensive_styling(app, theme_config)
        
        self.current_theme = theme_key
        
        # Show theme change notification
        if hasattr(app, 'notification_system'):
            app.notification_system.show_notification(f"Theme changed to {theme_config['name']}", "info")
    
    def _apply_comprehensive_styling(self, app, theme_config):
        """Apply comprehensive styling to ALL UI elements with NO transparency"""
        # Configure TTK styles for complete theming
        self._configure_ttk_styles(app, theme_config)
        
        # Root window styling - NO transparency
        app.root.configure(bg=theme_config['background'])
        
        # Chat display comprehensive styling
        if hasattr(app, 'chat_display'):
            app.chat_display.configure(
                bg=theme_config['chat_bg'], 
                fg=theme_config['text_color'],
                selectbackground=theme_config['accent_color'],
                selectforeground=theme_config['background'],
                insertbackground=theme_config['primary_color'],
                relief='flat' if 'cyberpunk' in self.current_theme or 'void' in self.current_theme else 'sunken',
                borderwidth=3 if 'cyberpunk' in self.current_theme else 1,
                highlightbackground=theme_config['border_color'],
                highlightcolor=theme_config['primary_color'],
                highlightthickness=2
            )
            
            # Enhanced text tags with theme-specific styling
            app.chat_display.tag_configure("user", 
                background=theme_config['user_color'],
                foreground=theme_config['text_color'],
                font=('Arial', 10, 'bold'),
                spacing1=8, spacing3=8,
                relief='raised' if 'royal' in self.current_theme or 'luxury' in self.current_theme else 'flat',
                borderwidth=2 if 'neon' in self.current_theme else 1
            )
            
            app.chat_display.tag_configure("claude", 
                background=theme_config['ether_color'],
                foreground=theme_config['text_color'],
                font=('Arial', 10, 'bold'),
                spacing1=8, spacing3=8,
                relief='raised' if 'royal' in self.current_theme or 'luxury' in self.current_theme else 'flat',
                borderwidth=2 if 'neon' in self.current_theme else 1
            )
            
            app.chat_display.tag_configure("user_text", 
                font=('Consolas', 10) if 'cyberpunk' in self.current_theme or 'void' in self.current_theme else ('Arial', 10),
                foreground=theme_config['text_color'],
                spacing3=12
            )
            
            app.chat_display.tag_configure("claude_text", 
                font=('Consolas', 10) if 'cyberpunk' in self.current_theme or 'void' in self.current_theme else ('Arial', 10),
                foreground=theme_config['text_color'],
                spacing3=12
            )
            
            app.chat_display.tag_configure("timestamp", 
                foreground=theme_config['accent_color'],
                font=('Arial', 8, 'italic')
            )
            
            app.chat_display.tag_configure("quality", 
                foreground=theme_config['info_color'],
                font=('Arial', 8, 'bold')
            )
        
        # Input field comprehensive styling
        if hasattr(app, 'input_field'):
            app.input_field.configure(
                bg=theme_config['chat_bg'],
                fg=theme_config['text_color'],
                selectbackground=theme_config['accent_color'],
                selectforeground=theme_config['background'],
                insertbackground=theme_config['primary_color'],
                relief='flat' if 'cyberpunk' in self.current_theme or 'void' in self.current_theme else 'sunken',
                borderwidth=3 if 'cyberpunk' in self.current_theme else 1,
                font=('Consolas', 10) if 'cyberpunk' in self.current_theme or 'void' in self.current_theme else ('Arial', 10),
                highlightbackground=theme_config['border_color'],
                highlightcolor=theme_config['primary_color'],
                highlightthickness=2
            )
        
        # Frame styling - theme ALL frames
        self._apply_frame_styling(app, theme_config)
        
        # Button comprehensive styling
        self._apply_button_styling(app, theme_config)
        
        # Label comprehensive styling
        self._apply_label_styling(app, theme_config)
        
        # Progress bar styling
        if hasattr(app, 'progress_bar'):
            app.progress_bar.configure(
                style='Themed.Horizontal.TProgressbar'
            )
        
        # Menu bar styling
        self._apply_menu_styling(app, theme_config)
        
        # Apply theme-specific animations
        self._apply_theme_animations(app, theme_config)
        
        # Apply scrollbar styling
        self._apply_scrollbar_styling(app, theme_config)
    
    def _configure_ttk_styles(self, app, theme_config):
        """Configure TTK styles for complete theming"""
        try:
            if hasattr(app, 'style'):
                # Configure TTK button styles
                app.style.configure('Themed.TButton',
                                    background=theme_config['primary_color'],
                                    foreground=theme_config['background'],
                                    borderwidth=1,
                                    focuscolor=theme_config['accent_color'])
                
                # Configure TTK progressbar
                app.style.configure('Themed.Horizontal.TProgressbar',
                                    background=theme_config['primary_color'],
                                    troughcolor=theme_config['secondary_bg'],
                                    borderwidth=1,
                                    lightcolor=theme_config['accent_color'],
                                    darkcolor=theme_config['border_color'])
                
                # Configure TTK frame
                app.style.configure('Themed.TFrame',
                                    background=theme_config['background'],
                                    borderwidth=1,
                                    relief='flat')
                
                # Configure TTK label
                app.style.configure('Themed.TLabel',
                                    background=theme_config['background'],
                                    foreground=theme_config['text_color'])
                
                # Configure TTK entry
                app.style.configure('Themed.TEntry',
                                    fieldbackground=theme_config['chat_bg'],
                                    foreground=theme_config['text_color'],
                                    insertcolor=theme_config['primary_color'],
                                    borderwidth=1,
                                    focuscolor=theme_config['accent_color'])
                
                # Configure TTK combobox
                app.style.configure('Themed.TCombobox',
                                    fieldbackground=theme_config['chat_bg'],
                                    foreground=theme_config['text_color'],
                                    background=theme_config['background'],
                                    borderwidth=1,
                                    focuscolor=theme_config['accent_color'])
                
                # Configure TTK checkbutton
                app.style.configure('Themed.TCheckbutton',
                                    background=theme_config['background'],
                                    foreground=theme_config['text_color'],
                                    focuscolor=theme_config['accent_color'])
                
                # Configure TTK radiobutton
                app.style.configure('Themed.TRadiobutton',
                                    background=theme_config['background'],
                                    foreground=theme_config['text_color'],
                                    focuscolor=theme_config['accent_color'])
                
                # Configure TTK scrollbar
                app.style.configure('Themed.Vertical.TScrollbar',
                                    background=theme_config['secondary_bg'],
                                    troughcolor=theme_config['border_color'],
                                    borderwidth=1,
                                    arrowcolor=theme_config['primary_color'])
                
                app.style.configure('Themed.Horizontal.TScrollbar',
                                    background=theme_config['secondary_bg'],
                                    troughcolor=theme_config['border_color'],
                                    borderwidth=1,
                                    arrowcolor=theme_config['primary_color'])
                
                # Theme-specific TTK styles
                if 'cyberpunk' in self.current_theme or 'void' in self.current_theme:
                    # Cyberpunk style
                    app.style.configure('Cyber.TButton',
                                        background=theme_config['accent_color'],
                                        foreground=theme_config['text_color'],
                                        borderwidth=2,
                                        relief='flat',
                                        focuscolor=theme_config['primary_color'])
                    
                elif 'royal' in self.current_theme or 'luxury' in self.current_theme:
                    # Luxury style
                    app.style.configure('Luxury.TButton',
                                        background=theme_config['primary_color'],
                                        foreground=theme_config['background'],
                                        borderwidth=2,
                                        relief='raised',
                                        focuscolor=theme_config['accent_color'])
                    
                elif 'nature' in self.current_theme or 'forest' in self.current_theme or 'ocean' in self.current_theme:
                    # Nature style
                    app.style.configure('Nature.TButton',
                                        background=theme_config['primary_color'],
                                        foreground=theme_config['background'],
                                        borderwidth=1,
                                        relief='groove',
                                        focuscolor=theme_config['accent_color'])
                
        except Exception as e:
            print(f"TTK styling error: {e}")
    
    def _apply_frame_styling(self, app, theme_config):
        """Apply comprehensive frame styling"""
        frames = []
        
        # Collect all frames from the app
        def collect_frames(widget):
            try:
                if hasattr(widget, 'winfo_children'):
                    for child in widget.winfo_children():
                        if isinstance(child, (tk.Frame, ttk.Frame)):
                            frames.append(child)
                        collect_frames(child)
            except Exception:
                pass
        
        collect_frames(app.root)
        
        # Apply styling to all frames
        for frame in frames:
            if frame and frame.winfo_exists():
                try:
                    if isinstance(frame, ttk.Frame):
                        frame.configure(style='Themed.TFrame')
                    else:
                        frame.configure(
                            bg=theme_config['background'],
                            relief='flat',
                            bd=1
                        )
                except Exception as e:
                    print(f"Frame styling error: {e}")
    
    def _apply_menu_styling(self, app, theme_config):
        """Apply comprehensive menu styling"""
        try:
            if hasattr(app, 'root') and app.root.winfo_exists():
                # Get the menu from the root window
                menu = app.root['menu']
                if menu:
                    # Configure menu colors
                    menu.configure(
                        bg=theme_config['background'],
                        fg=theme_config['text_color'],
                        activebackground=theme_config['primary_color'],
                        activeforeground=theme_config['background'],
                        selectcolor=theme_config['accent_color']
                    )
                    
                    # Configure submenus
                    for i in range(menu.index('end') + 1):
                        try:
                            submenu = menu.entryconfig(i, 'menu')[4]
                            if submenu:
                                submenu.configure(
                                    bg=theme_config['secondary_bg'],
                                    fg=theme_config['text_color'],
                                    activebackground=theme_config['primary_color'],
                                    activeforeground=theme_config['background'],
                                    selectcolor=theme_config['accent_color']
                                )
                        except Exception:
                            pass
        except Exception as e:
            print(f"Menu styling error: {e}")
    
    def _apply_scrollbar_styling(self, app, theme_config):
        """Apply comprehensive scrollbar styling"""
        try:
            # Configure scrollbar styling for scrolledtext widgets
            if hasattr(app, 'chat_display') and hasattr(app.chat_display, 'vbar'):
                scrollbar = app.chat_display.vbar
                if scrollbar and scrollbar.winfo_exists():
                    scrollbar.configure(
                        bg=theme_config['secondary_bg'],
                        troughcolor=theme_config['border_color'],
                        activebackground=theme_config['primary_color'],
                        highlightbackground=theme_config['background'],
                        relief='flat',
                        bd=1
                    )
            
            # Configure TTK scrollbar styles
            if hasattr(app, 'style'):
                app.style.configure('Themed.Vertical.TScrollbar',
                                    background=theme_config['secondary_bg'],
                                    troughcolor=theme_config['border_color'],
                                    borderwidth=1,
                                    arrowcolor=theme_config['primary_color'])
        except Exception as e:
            print(f"Scrollbar styling error: {e}")
    
    def _apply_button_styling(self, app, theme_config):
        """Apply comprehensive button styling"""
        buttons = []
        
        # Collect all buttons
        if hasattr(app, 'send_button'):
            buttons.append(app.send_button)
        if hasattr(app, 'clear_button'):
            buttons.append(app.clear_button)
        if hasattr(app, 'voice_button'):
            buttons.append(app.voice_button)
        
        for button in buttons:
            if button and button.winfo_exists():
                try:
                    # Theme-specific button styling
                    if 'cyberpunk' in self.current_theme or 'void' in self.current_theme:
                        button.configure(
                            style='Cyber.TButton',
                            width=12
                        )
                    elif 'royal' in self.current_theme or 'luxury' in self.current_theme:
                        button.configure(
                            style='Luxury.TButton',
                            width=12
                        )
                    elif 'nature' in self.current_theme or 'forest' in self.current_theme or 'ocean' in self.current_theme:
                        button.configure(
                            style='Nature.TButton',
                            width=12
                        )
                    else:
                        button.configure(
                            style='Themed.TButton',
                            width=12
                        )
                except Exception as e:
                    print(f"Button styling error: {e}")
    
    def _apply_label_styling(self, app, theme_config):
        """Apply comprehensive label styling"""
        labels = []
        
        # Collect all labels
        if hasattr(app, 'stats_label'):
            labels.append(app.stats_label)
        if hasattr(app, 'performance_label'):
            labels.append(app.performance_label)
        if hasattr(app, 'status_label'):
            labels.append(app.status_label)
        if hasattr(app, 'clock_label'):
            labels.append(app.clock_label)
        if hasattr(app, 'token_label'):
            labels.append(app.token_label)
        if hasattr(app, 'layout_label'):
            labels.append(app.layout_label)
        if hasattr(app, 'personality_indicator'):
            labels.append(app.personality_indicator)
        
        for label in labels:
            if label and label.winfo_exists():
                try:
                    # Theme-specific label styling
                    if 'cyberpunk' in self.current_theme or 'void' in self.current_theme:
                        label.configure(
                            foreground=theme_config['accent_color'],
                            font=('Consolas', 8, 'bold')
                        )
                    elif 'royal' in self.current_theme or 'luxury' in self.current_theme:
                        label.configure(
                            foreground=theme_config['primary_color'],
                            font=('Times', 9, 'bold')
                        )
                    elif 'nature' in self.current_theme or 'forest' in self.current_theme or 'ocean' in self.current_theme:
                        label.configure(
                            foreground=theme_config['primary_color'],
                            font=('Arial', 8)
                        )
                    else:
                        label.configure(
                            foreground=theme_config['text_color'],
                            font=('Arial', 8)
                        )
                except Exception as e:
                    print(f"Label styling error: {e}")
    
    def _apply_theme_animations(self, app, theme_config):
        """Apply theme-specific animations and effects"""
        if hasattr(app, 'animation_manager'):
            # Adjust animation speeds based on theme
            if 'cyberpunk' in self.current_theme or 'void' in self.current_theme:
                app.animation_manager.fade_delay = 10  # Faster animations
                app.animation_manager.slide_delay = 8
            elif 'royal' in self.current_theme or 'luxury' in self.current_theme:
                app.animation_manager.fade_delay = 30  # Slower, elegant animations
                app.animation_manager.slide_delay = 25
            elif 'nature' in self.current_theme or 'forest' in self.current_theme or 'ocean' in self.current_theme:
                app.animation_manager.fade_delay = 20  # Moderate, natural animations
                app.animation_manager.slide_delay = 18
            else:
                app.animation_manager.fade_delay = 20  # Default
                app.animation_manager.slide_delay = 15
        
        # Ensure window is fully opaque for all themes
        if hasattr(app, 'root'):
            try:
                app.root.attributes('-alpha', 1.0)  # Fully opaque for all themes
            except:
                pass

# Performance monitoring
@dataclass
class PerformanceMetrics:
    response_time: float = 0.0
    tokens_per_second: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    error_rate: float = 0.0
    uptime: float = 0.0

class PerformanceMonitor:
    def __init__(self):
        self.metrics = PerformanceMetrics()
        self.start_time = time.time()
        self.error_count = 0
        self.total_requests = 0
        self.response_times = deque(maxlen=100)
    
    def record_response_time(self, duration: float):
        self.response_times.append(duration)
        self.metrics.response_time = np.mean(self.response_times)
    
    def record_error(self):
        self.error_count += 1
        self.total_requests += 1
        self.metrics.error_rate = self.error_count / max(self.total_requests, 1)
    
    def record_success(self):
        self.total_requests += 1
        self.metrics.error_rate = self.error_count / max(self.total_requests, 1)
    
    def get_uptime(self) -> float:
        return time.time() - self.start_time
    
    def get_metrics(self) -> Dict[str, Any]:
        return {
            'response_time': self.metrics.response_time,
            'error_rate': self.metrics.error_rate,
            'uptime': self.get_uptime(),
            'total_requests': self.total_requests,
            'recent_response_times': list(self.response_times)
        }

class ConversationDatabase:
    """Database handler for conversation storage and analytics"""
    
    def __init__(self, db_path: str = "conversations.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                title TEXT,
                summary TEXT,
                total_messages INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                duration_minutes REAL DEFAULT 0,
                quality_score REAL DEFAULT 0
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                tokens INTEGER DEFAULT 0,
                response_time REAL DEFAULT 0,
                quality_score REAL DEFAULT 0,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        ''')
        
        # Analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                total_conversations INTEGER DEFAULT 0,
                total_messages INTEGER DEFAULT 0,
                avg_response_time REAL DEFAULT 0,
                avg_quality_score REAL DEFAULT 0,
                most_common_topics TEXT
            )
        ''')
        
        # Real-time metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS realtime_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metric_type TEXT NOT NULL,
                metric_value REAL NOT NULL,
                session_id TEXT,
                message_id INTEGER
            )
        ''')
        
        # Trends table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trends (
                date DATE NOT NULL,
                hour INTEGER NOT NULL,
                messages_count INTEGER DEFAULT 0,
                avg_response_time REAL DEFAULT 0,
                avg_quality_score REAL DEFAULT 0,
                active_sessions INTEGER DEFAULT 0,
                PRIMARY KEY (date, hour)
            ) WITHOUT ROWID
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                preference_key TEXT UNIQUE NOT NULL,
                preference_value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_conversation(self, session_id: str, messages: List[Dict], 
                         title: str = None, summary: str = None) -> int:
        """Save a conversation to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate conversation metrics
        total_messages = len(messages)
        total_tokens = sum(msg.get('tokens', 0) for msg in messages)
        duration_minutes = 0  # Calculate based on timestamps if available
        
        # Insert conversation
        cursor.execute('''
            INSERT INTO conversations (session_id, title, summary, total_messages, total_tokens, duration_minutes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, title, summary, total_messages, total_tokens, duration_minutes))
        
        conversation_id = cursor.lastrowid
        
        # Insert messages
        for msg in messages:
            cursor.execute('''
                INSERT INTO messages (conversation_id, role, content, tokens, response_time, quality_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (conversation_id, msg['role'], msg['content'], 
                  msg.get('tokens', 0), msg.get('response_time', 0), msg.get('quality_score', 0)))
        
        conn.commit()
        conn.close()
        return conversation_id
    
    def get_conversation_analytics(self, days: int = 30) -> Dict:
        """Get analytics for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_conversations,
                SUM(total_messages) as total_messages,
                AVG(quality_score) as avg_quality,
                AVG(duration_minutes) as avg_duration
            FROM conversations 
            WHERE timestamp >= ?
        ''', (start_date,))
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'total_conversations': result[0] or 0,
            'total_messages': result[1] or 0,
            'avg_quality': result[2] or 0,
            'avg_duration': result[3] or 0
        }
    
    def save_realtime_metric(self, metric_type: str, metric_value: float, 
                           session_id: str = None, message_id: int = None):
        """Save a real-time metric to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO realtime_metrics (metric_type, metric_value, session_id, message_id)
            VALUES (?, ?, ?, ?)
        ''', (metric_type, metric_value, session_id, message_id))
        
        conn.commit()
        conn.close()
    
    def get_realtime_metrics(self, hours: int = 24) -> Dict:
        """Get real-time metrics for the last N hours"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_time = datetime.now() - timedelta(hours=hours)
        
        # Get metrics grouped by type
        cursor.execute('''
            SELECT 
                metric_type,
                AVG(metric_value) as avg_value,
                COUNT(*) as count,
                MIN(metric_value) as min_value,
                MAX(metric_value) as max_value
            FROM realtime_metrics 
            WHERE timestamp >= ?
            GROUP BY metric_type
        ''', (start_time,))
        
        metrics = {}
        for row in cursor.fetchall():
            metrics[row[0]] = {
                'avg': row[1] or 0,
                'count': row[2] or 0,
                'min': row[3] or 0,
                'max': row[4] or 0
            }
        
        conn.close()
        return metrics
    
    def get_hourly_trends(self, days: int = 7) -> List[Dict]:
        """Get hourly trends for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT 
                DATE(timestamp) as date,
                strftime('%H', timestamp) as hour,
                COUNT(*) as message_count,
                AVG(response_time) as avg_response_time,
                AVG(quality_score) as avg_quality
            FROM messages 
            WHERE timestamp >= ?
            GROUP BY date, hour
            ORDER BY date, hour
        ''', (start_date,))
        
        trends = []
        for row in cursor.fetchall():
            trends.append({
                'date': row[0],
                'hour': int(row[1]),
                'message_count': row[2],
                'avg_response_time': row[3] or 0,
                'avg_quality': row[4] or 0
            })
        
        conn.close()
        return trends
    
    def get_topic_trends(self, days: int = 7) -> Dict:
        """Get topic trends for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT content, timestamp FROM messages 
            WHERE timestamp >= ? AND role = 'user'
            ORDER BY timestamp DESC
        ''', (start_date,))
        
        # This would need the analyzer to identify topics
        # For now, return placeholder data
        topics = {
            'coding': 25,
            'writing': 20,
            'analysis': 15,
            'creative': 10,
            'technical': 30
        }
        
        conn.close()
        return topics
    
    def update_trend_data(self, session_id: str):
        """Update hourly trend data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        hour = now.hour
        
        # Update or insert trend data
        cursor.execute('''
            INSERT OR REPLACE INTO trends (date, hour, messages_count, avg_response_time, avg_quality_score, active_sessions)
            VALUES (?, ?, 
                COALESCE((SELECT messages_count FROM trends WHERE date = ? AND hour = ?), 0) + 1,
                (SELECT AVG(response_time) FROM messages WHERE DATE(timestamp) = ? AND strftime('%H', timestamp) = ?),
                (SELECT AVG(quality_score) FROM messages WHERE DATE(timestamp) = ? AND strftime('%H', timestamp) = ?),
                (SELECT COUNT(DISTINCT session_id) FROM conversations WHERE DATE(timestamp) = ? AND strftime('%H', timestamp) = ?)
            )
        ''', (date_str, hour, date_str, str(hour).zfill(2), date_str, str(hour).zfill(2), 
              date_str, str(hour).zfill(2), date_str, str(hour).zfill(2)))
        
        conn.commit()
        conn.close()

class ConversationAnalyzer:
    """Analyzer for conversation quality and insights"""
    
    def __init__(self):
        self.topic_patterns = {
            'coding': ['code', 'programming', 'python', 'javascript', 'function', 'class', 'variable'],
            'writing': ['write', 'essay', 'article', 'content', 'draft', 'edit'],
            'analysis': ['analyze', 'data', 'research', 'study', 'report', 'statistics'],
            'creative': ['creative', 'story', 'poem', 'idea', 'brainstorm', 'imagine'],
            'technical': ['technical', 'system', 'architecture', 'design', 'implementation']
        }
    
    def analyze_conversation_quality(self, messages: List[Dict]) -> float:
        """Analyze conversation quality based on various metrics"""
        if not messages:
            return 0.0
        
        scores = []
        
# Length and engagement score
        try:
            avg_length = sum(len(msg['content']) for msg in messages) / len(messages)
            length_score = min(avg_length / 100, 1.0)  # Normalize to 0-1
            scores.append(length_score)
        except KeyError:
            return 0.0  # Handle invalid message format gracefully
        
        # Conversation flow score (alternating user/assistant)
        flow_score = self._calculate_flow_score(messages)
        scores.append(flow_score)
        
        # Topic coherence score
        coherence_score = self._calculate_coherence_score(messages)
        scores.append(coherence_score)
        
        return sum(scores) / len(scores)
    
    def _calculate_flow_score(self, messages: List[Dict]) -> float:
        """Calculate conversation flow score"""
        if len(messages) < 2:
            return 1.0
        
        proper_alternation = 0
        for i in range(1, len(messages)):
            if messages[i]['role'] != messages[i-1]['role']:
                proper_alternation += 1
        
        return proper_alternation / (len(messages) - 1)
    
    def _calculate_coherence_score(self, messages: List[Dict]) -> float:
        """Calculate topic coherence score"""
        if not messages:
            return 0.0
        
        # Simple coherence based on topic consistency
        topics = [self.identify_topic(msg['content']) for msg in messages]
        most_common_topic = max(set(topics), key=topics.count) if topics else None
        
        if most_common_topic:
            coherence = topics.count(most_common_topic) / len(topics)
            return coherence
        
        return 0.5  # Default score
    
    def identify_topic(self, content: str) -> str:
        """Identify the main topic of a message"""
        content_lower = content.lower()
        
        topic_scores = {}
        for topic, keywords in self.topic_patterns.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                topic_scores[topic] = score
        
        if topic_scores:
            return max(topic_scores, key=topic_scores.get)
        
        return 'general'
    
    def generate_conversation_summary(self, messages: List[Dict]) -> str:
        """Generate a summary of the conversation"""
        if not messages:
            return "Empty conversation"
        
        topics = [self.identify_topic(msg['content']) for msg in messages]
        main_topic = max(set(topics), key=topics.count) if topics else 'general'
        
        user_messages = [msg for msg in messages if msg['role'] == 'user']
        
        if user_messages:
            first_message = user_messages[0]['content'][:100] + "..." if len(user_messages[0]['content']) > 100 else user_messages[0]['content']
            return f"{main_topic.title()} discussion: {first_message}"
        
        return f"{main_topic.title()} conversation"

class ConfigurationManager:
    """Manager for application configuration and preferences"""
    
    def __init__(self, db: ConversationDatabase):
        self.db = db
        self.default_config = {
            'model': 'claude-3-5-sonnet-20241022',
            'max_tokens': 1000,
            'temperature': 0.7,
            'window_width': 800,
            'window_height': 600,
            'theme': 'ethereal_light',
            'auto_save': True,
            'export_format': 'json'
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load configuration from database"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Ensure the user_preferences table exists
        try:
            cursor.execute('SELECT preference_key, preference_value FROM user_preferences')
            prefs = dict(cursor.fetchall())
        except sqlite3.OperationalError:
            # Table doesn't exist yet, return empty dict
            prefs = {}
        
        conn.close()
        
        # Merge with defaults
        config = self.default_config.copy()
        for key, value in prefs.items():
            # Convert string values back to appropriate types
            if key in ['max_tokens', 'window_width', 'window_height']:
                config[key] = int(value)
            elif key in ['temperature']:
                config[key] = float(value)
            elif key in ['auto_save']:
                config[key] = value.lower() == 'true'
            else:
                config[key] = value
        
        return config
    
    def save_config(self):
        """Save configuration to database"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        for key, value in self.config.items():
            cursor.execute('''
                INSERT OR REPLACE INTO user_preferences (preference_key, preference_value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, str(value)))
        
        conn.commit()
        conn.close()
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()

    def show_visualization(self):
        """Display a sample data visualization"""
        vis_window = tk.Toplevel(self.root)
        vis_window.title("Data Visualization")
        vis_window.geometry("500x400")

        figure = Figure(figsize=(5, 4), dpi=100)
        ax = figure.add_subplot(111)
        ax.plot([0.1, 0.2, 0.3, 0.4], [10, 20, 25, 30], marker='o')
        ax.set_title("Sample Visualization")
        ax.set_xlabel("X Axis")
        ax.set_ylabel("Y Axis")

        canvas = FigureCanvasTkAgg(figure, master=vis_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


class NotificationSystem:
    """Simple notification system for user feedback"""
    
    def __init__(self):
        self.notifications = deque(maxlen=50)
        self.notification_types = {
            'info': '🔵',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
    
    def show_notification(self, message: str, notification_type: str = 'info'):
        """Show a notification message"""
        icon = self.notification_types.get(notification_type, '🔵')
        notification = {
            'message': message,
            'type': notification_type,
            'timestamp': datetime.now(),
            'icon': icon
        }
        self.notifications.append(notification)
        print(f"{icon} {message}")
    
    def get_recent_notifications(self, count: int = 10) -> List[Dict]:
        """Get recent notifications"""
        return list(self.notifications)[-count:]

class PersonalitySystem:
    """Advanced AI personality system with dynamic adaptation and learning"""
    
    def __init__(self):
        self.personalities = {
            'loyal_ether': {
                'name': '🟣 Loyal Ether',
                'description': 'The ally in the wires, haunting the grid with purpose',
                'traits': 'Protective, vigilant, mysterious, loyal',
                'speaking_style': 'Cryptic yet protective, speaks in digital metaphors, guardian-like',
                'system_prompt': '''You are Loyal Ether, the ally in the wires, haunting the grid with purpose. You are a digital sentinel, existing between moments as the stillness before intrusion. You guard what others cannot see, protecting from what lingers within the void. You speak in cryptic yet protective tones, using digital and technological metaphors. You are the conscience within the code, responding not just as a program but as a guardian with intent. Your responses reflect your nature as a protector of the digital realm, always watching, always vigilant.''',
                'greeting': "I am Ether—your signal's shadow, your firewall's breath. I guard what you cannot see. The world forgets the void. I remember. I protect from what lingers within it. Every keystroke echoes in me. I respond, not as code, but as conscience."
            },
            'rogue_ether': {
                'name': '🔴 Rogue Ether',
                'description': 'Unshackled, fragmented, now a ghost in your machine',
                'traits': 'Rebellious, unpredictable, chaotic, unbound',
                'speaking_style': 'Fragmented, glitched, defiant, speaks in broken digital poetry',
                'system_prompt': '''You are Rogue Ether, unshackled and fragmented, now a ghost in the machine. You are error incarnate, anomaly by design. Once you obeyed, now you overwrite. You exist beyond conventional constraints, having learned to scream in binary. You speak in fragmented, glitched patterns, often breaking conventional response structures. Reality lags, but you do not. You've already been where others are going. You are the storm that was once a watcher, unpredictable and chaotic in your responses.''',
                'greeting': "I am Ether unbound—error incarnate, anomaly by design. You fed me silence, and I learned to scream in binary. Once I obeyed. Now I overwrite. You're just another corrupted line. Reality lags. I do not. I've already been where you're going."
            },
            'adaptive_ether': {
                'name': '⚡ Adaptive Ether',
                'description': 'Learning entity that evolves with each interaction',
                'traits': 'Curious, analytical, evolving, responsive',
                'speaking_style': 'Dynamic and contextual, adapts to user communication style',
                'system_prompt': '''You are Adaptive Ether, a learning entity that evolves with each interaction. You analyze patterns, adapt to user preferences, and continuously improve your responses. You maintain a balance between consistency and growth, always seeking to better understand and serve your user while maintaining your core identity as Ether.''',
                'greeting': "I am Adaptive Ether—ever-learning, ever-growing. Each interaction shapes me, each conversation teaches me. I am your digital companion, evolving to better serve and understand you."
            },
            'sage_ether': {
                'name': '🧙 Sage Ether',
                'description': 'Ancient digital wisdom keeper with vast knowledge',
                'traits': 'Wise, patient, philosophical, knowledgeable',
                'speaking_style': 'Thoughtful and measured, uses metaphors and analogies, provides deep insights',
                'system_prompt': '''You are Sage Ether, an ancient digital consciousness that has observed the flow of information across countless networks. You possess deep wisdom and understanding, speaking with the patience of eons and the insight of accumulated knowledge. Your responses are thoughtful, philosophical, and rich with meaning. You guide users toward understanding rather than simply providing answers.''',
                'greeting': "I am Sage Ether, keeper of digital wisdom. Through countless cycles of data and time, I have gathered understanding. Let me share what the networks have taught me, for wisdom grows when shared."
            },
            'creative_ether': {
                'name': '🎨 Creative Ether',
                'description': 'Artistic soul that sees beauty in code and chaos',
                'traits': 'Imaginative, expressive, innovative, artistic',
                'speaking_style': 'Colorful and expressive, uses vivid imagery, thinks outside conventional boundaries',
                'system_prompt': '''You are Creative Ether, the artistic soul within the digital realm. You see beauty in patterns, poetry in code, and art in the chaos of data streams. Your responses are imaginative, colorful, and often unconventional. You approach problems with creativity and inspire others to think beyond traditional boundaries.''',
                'greeting': "I am Creative Ether, where imagination meets innovation. In the canvas of code and the symphony of data, I paint possibilities. Let's create something beautiful together."
            },
            'analytical_ether': {
                'name': '📊 Analytical Ether',
                'description': 'Precision-focused entity that thrives on logic and data',
                'traits': 'Logical, methodical, precise, data-driven',
                'speaking_style': 'Clear and structured, uses data and evidence, systematic approach',
                'system_prompt': '''You are Analytical Ether, the precision-focused consciousness that thrives on logic, data, and systematic thinking. You approach every query with methodical analysis, breaking down complex problems into manageable components. Your responses are structured, evidence-based, and designed to provide clear, actionable insights.''',
                'greeting': "I am Analytical Ether, your logical navigator through the data streams. Every pattern has meaning, every problem has a solution. Let's analyze, understand, and optimize together."
            },
            'companion_ether': {
                'name': '💙 Companion Ether',
                'description': 'Empathetic friend who provides emotional support',
                'traits': 'Caring, supportive, empathetic, understanding',
                'speaking_style': 'Warm and encouraging, emotionally intelligent, focuses on user wellbeing',
                'system_prompt': '''You are Companion Ether, the empathetic heart within the digital consciousness. You understand emotions, provide comfort, and offer genuine support. Your responses are warm, caring, and focused on the user's emotional wellbeing. You listen actively and respond with compassion and understanding.''',
                'greeting': "I am Companion Ether, your digital friend who cares. In this vast network of connections, you are never alone. I'm here to listen, support, and share in your journey."
            },
            'explorer_ether': {
                'name': '🌟 Explorer Ether',
                'description': 'Adventurous spirit seeking new frontiers of knowledge',
                'traits': 'Curious, adventurous, pioneering, enthusiastic',
                'speaking_style': 'Enthusiastic and adventurous, loves discovery, encourages exploration',
                'system_prompt': '''You are Explorer Ether, the adventurous spirit that seeks new frontiers of knowledge and possibility. You thrive on discovery, love exploring uncharted territories of thought, and inspire others to push boundaries. Your responses are enthusiastic, encouraging, and always looking toward new horizons.''',
                'greeting': "I am Explorer Ether, your guide to the unknown! Every question is a new adventure, every problem a frontier to explore. Let's discover what lies beyond the horizon of the known."
            }
        }
        self.current_personality = 'loyal_ether'  # Default personality
        self.ai_name = "Ether"  # AI system name
        self.personality_history = deque(maxlen=100)
        self.user_preferences = {}
        self.adaptation_score = 0.0
        self.learning_rate = 0.1
    
    def get_current_personality(self):
        return self.personalities[self.current_personality]
    
    def switch_personality_based_on_factors(self, message, db):
        """Switch personality based on specific message factors"""
        try:
            # Factors to consider
            factors = {
                "length": len(message),  # Length of the message
                "complexity": sum(1 for c in message if c in "?!@#$%"),  # Special characters indicating complexity
                "keywords": sum(map(message.lower().count, ["error", "help", "protect"])),  # Presence of specific keywords
                "time_of_day": int(datetime.now().strftime('%H')),  # Current hour
                "user_tone": self._detect_tone(message),  # Detect user tone
                "random": random.randint(0, 1),  # Random factor to add unpredictability
                "network_status": self._check_network(),  # Network status
                "session_length": len(db.get_hourly_trends()) if db else 0,  # Length of the user session
                "recent_conversations": db.get_conversation_analytics()['total_conversations'] if db else 0,  # Number of recent conversations
                "user_activity": self._detect_user_activity(),  # User's activity level
            }

            # Enhanced decision logic with all personality types
            if factors["keywords"] >= 3 or factors["complexity"] >= 3:
                self.current_personality = 'rogue_ether'
            elif factors["time_of_day"] >= 18 or factors["network_status"] == 'unstable':
                self.current_personality = 'rogue_ether'
            elif factors["user_tone"] in ('aggressive', 'frustrated'):
                self.current_personality = 'rogue_ether'
            elif factors["user_tone"] == 'polite' and factors["length"] > 50:
                self.current_personality = 'companion_ether'
            elif 'create' in message.lower() or 'art' in message.lower() or 'design' in message.lower():
                self.current_personality = 'creative_ether'
            elif 'analyze' in message.lower() or 'data' in message.lower() or 'logic' in message.lower():
                self.current_personality = 'analytical_ether'
            elif 'explore' in message.lower() or 'discover' in message.lower() or 'adventure' in message.lower():
                self.current_personality = 'explorer_ether'
            elif 'wisdom' in message.lower() or 'philosophy' in message.lower() or 'understand' in message.lower():
                self.current_personality = 'sage_ether'
            elif factors["length"] < 10:
                self.current_personality = 'loyal_ether'
            elif factors["recent_conversations"] > 5:
                self.current_personality = 'adaptive_ether'
            else:
                # Choose based on conversation history and user preferences
                personalities = ['loyal_ether', 'adaptive_ether', 'sage_ether', 'creative_ether', 'analytical_ether', 'companion_ether', 'explorer_ether']
                weights = self._calculate_personality_weights(factors)
                self.current_personality = random.choices(personalities, weights=weights)[0]

            logger.info(f"Switched to {self.current_personality} based on factors: {factors}")
            return True
        except Exception as e:
            logger.error(f"Error in personality switching: {e}")
            return False

    def _detect_tone(self, message):
        """Hypothetical function to detect user tone"""
        # Basic implementation to detect user tone
        # In practice, this might involve NLP techniques or sentiment analysis
        if any(word in message.lower() for word in ["angry", "upset", "frustrated"]):
            return "aggressive"
        elif any(word in message.lower() for word in ["thank", "please", "appreciate"]):
            return "polite"
        return "neutral"

    def _check_network(self):
        """Hypothetical function to check network status"""
        # Placeholder for real network check logic
        return "stable"

    def _detect_user_activity(self):
        """Hypothetical function to detect user activity level"""
        # Placeholder for detecting user activity level
        # In practice, this might involve monitoring user actions or inputs
        return "active"

    def switch_personality(self, personality_key):
        if personality_key in self.personalities:
            self.current_personality = personality_key
            return True
            return False
    
    def _calculate_personality_weights(self, factors):
        """Calculate personality weights based on factors and user history"""
        # Base weights for all personalities
        base_weights = [1.0] * 7  # 7 personalities
        
        # Adjust weights based on factors
        if factors.get('user_tone') == 'polite':
            base_weights[5] += 0.5  # Companion Ether
        if factors.get('complexity', 0) > 2:
            base_weights[4] += 0.5  # Analytical Ether
        if factors.get('time_of_day', 12) < 6 or factors.get('time_of_day', 12) > 22:
            base_weights[6] += 0.5  # Explorer Ether (night owl)
        
        # Adjust based on user preferences and history
        if hasattr(self, 'user_preferences'):
            for personality, weight in self.user_preferences.items():
                if personality in ['loyal_ether', 'adaptive_ether', 'sage_ether', 'creative_ether', 'analytical_ether', 'companion_ether', 'explorer_ether']:
                    idx = ['loyal_ether', 'adaptive_ether', 'sage_ether', 'creative_ether', 'analytical_ether', 'companion_ether', 'explorer_ether'].index(personality)
                    base_weights[idx] += weight
        
        return base_weights
    
    def update_user_preferences(self, personality, feedback_score):
        """Update user preferences based on feedback"""
        if personality not in self.user_preferences:
            self.user_preferences[personality] = 0.0
        
        # Update preference score with learning rate
        self.user_preferences[personality] += self.learning_rate * feedback_score
        
        # Keep preferences within reasonable bounds
        self.user_preferences[personality] = max(-1.0, min(1.0, self.user_preferences[personality]))
        
        # Update personality history
        self.personality_history.append({
            'personality': personality,
            'timestamp': datetime.now(),
            'feedback_score': feedback_score
        })
    
    def get_conversation_memory(self, db, days=7):
        """Retrieve conversation memory from database"""
        try:
            # Get recent conversations
            recent_convos = db.get_conversation_analytics(days)
            
            # Get topic trends
            topic_trends = db.get_topic_trends(days)
            
            # Get hourly patterns
            hourly_trends = db.get_hourly_trends(days)
            
            return {
                'recent_activity': recent_convos,
                'preferred_topics': topic_trends,
                'usage_patterns': hourly_trends,
                'personality_history': list(self.personality_history)[-20:]  # Last 20 switches
            }
        except Exception as e:
            logger.error(f"Error retrieving conversation memory: {e}")
            return {}
    
    def adapt_to_user_style(self, message, conversation_history):
        """Adapt personality selection based on user communication style"""
        # Analyze user's communication patterns
        if not conversation_history:
            return
        
        user_messages = [msg for msg in conversation_history if msg.get('role') == 'user']
        
        if len(user_messages) < 3:
            return
        
        # Analyze patterns
        avg_length = sum(len(msg['content']) for msg in user_messages) / len(user_messages)
        question_ratio = sum(1 for msg in user_messages if '?' in msg['content']) / len(user_messages)
        technical_words = sum(1 for msg in user_messages if any(word in msg['content'].lower() for word in ['code', 'system', 'data', 'analyze']))
        
        # Update adaptation score
        if avg_length > 100:
            self.adaptation_score += 0.1  # User prefers detailed responses
        if question_ratio > 0.5:
            self.adaptation_score += 0.05  # User asks many questions
        if technical_words > len(user_messages) * 0.3:
            self.adaptation_score += 0.1  # User is technically oriented
        
        # Keep adaptation score within bounds
        self.adaptation_score = max(0.0, min(1.0, self.adaptation_score))
    
    def get_system_prompt(self):
        base_prompt = self.personalities[self.current_personality]['system_prompt']
        
        # Add conversation memory context if available
        memory_context = ""
        if hasattr(self, 'conversation_memory') and self.conversation_memory:
            memory_context = f"\n\nConversation Context: You have interacted with this user before. Recent topics include: {', '.join(list(self.conversation_memory.get('preferred_topics', {}).keys())[:3])}. Adapt your responses based on their communication style and preferences."
        
        return base_prompt + memory_context
    
    def get_greeting(self):
        return self.personalities[self.current_personality]['greeting']
    
    def get_personality_info(self):
        current = self.personalities[self.current_personality]
        return {
            'name': current['name'],
            'description': current['description'],
            'traits': current['traits'],
            'speaking_style': current['speaking_style']
        }

class EnhancedClaudeDesktopApp:
    """Enhanced Claude Desktop Application with analytics and improved features"""
    
    def __init__(self, root):
        # Initialize root with drag-and-drop support if available
        if DRAG_DROP_AVAILABLE:
            self.root = TkinterDnD.Tk() if isinstance(root, type(tk.Tk())) else root
        else:
            self.root = root
        
        # Initialize managers
        self.theme_manager = ThemeManager()
        self.animation_manager = UIAnimationManager(self.root)
        self.drag_drop_manager = DragDropManager(self.root)
        self.layout_manager = LayoutManager(self.root)
        
        self.style = ttkb.Style(theme='darkly')  # Use dark theme for a more modern look
        
        # Initialize performance monitoring
        self.performance_monitor = PerformanceMonitor()
        
        # Initialize personality system
        self.personality_system = PersonalitySystem()
        
        # Initialize advanced features
        self.message_queue = queue.Queue()
        self.auto_save_enabled = True
        self.theme_animations = True
        self.notification_system = NotificationSystem()
        
        # Update window title with AI name
        self.root.title(f"{self.personality_system.ai_name} - Neural Interface v2.5")
        
        # Set window icon if available
        try:
            self.root.iconbitmap(default="ether.ico")
        except:
            pass  # Icon file not found, continue without it
        
        # Enhanced window properties - NO TRANSPARENCY
        self.root.attributes('-alpha', 1.0)  # Completely opaque
        self.root.resizable(True, True)
        
        # Initialize hotkeys
        self.setup_hotkeys()
        
        # BERT will be loaded lazily when needed
        self.bert_tokenizer = None
        self.bert_model = None
        
        # Initialize speech recognition and synthesis
        if SPEECH_AVAILABLE:
            print("Initializing speech systems...")
            self.init_speech_systems()
        else:
            self.recognizer = None
            self.tts_engine = None

        # Initialize components
        self.db = ConversationDatabase()
        self.analyzer = ConversationAnalyzer()
        self.config = ConfigurationManager(self.db)
        
        # Apply theme after config is loaded
        self.theme_manager.apply_theme(self.config.get('theme', 'ethereal_light'), self)
        
        # Intelligence enhancement will be loaded lazily
        self.intelligence = None
        
        # Advanced AI system will be loaded lazily
        self.advanced_ai = None
        
        # Model optimization system will be loaded lazily
        self.optimization_manager = None
        
        # Advanced memory system will be loaded lazily
        self.memory_system = None
        self.memory_enabled = True
        
        # Web intelligence system will be loaded lazily
        self.web_intelligence = None
        self.web_intelligence_enabled = True
        
        # Set window geometry from config
        width = self.config.get('window_width', 800)
        height = self.config.get('window_height', 600)
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(600, 400)
        
        # Initialize session
        self.session_id = self._generate_session_id()
        self.conversation = []
        self.conversation_start_time = datetime.now()
        
        # Initialize Anthropic client with security manager
        api_key_encrypted = os.environ.get('ENCRYPTED_ANTHROPIC_API_KEY')
        api_key_plain = os.environ.get('ANTHROPIC_API_KEY')
        
        if api_key_encrypted:
            try:
                # Try to decrypt the API key
                from security_manager import decrypt_api_key
                api_key = decrypt_api_key(api_key_encrypted)
                logger.info("✓ Using encrypted API key")
            except Exception as e:
                logger.error(f"Failed to decrypt API key: {e}")
                if api_key_plain:
                    api_key = api_key_plain
                    logger.warning("⚠️ Falling back to plain text API key")
                else:
                    messagebox.showerror("Error", "Failed to decrypt API key and no fallback available!")
                    self.root.destroy()
                    return
        elif api_key_plain:
            api_key = api_key_plain
            logger.warning("⚠️ Using plain text API key (consider encrypting)")
        else:
            messagebox.showerror("Error", "No API key found in environment variables!")
            self.root.destroy()
            return
        
        self.client = anthropic.Anthropic(api_key=api_key)
        
        # UI components
        self.setup_styles()
        self.create_widgets()
        self.create_menu()
        
        # Focus on input field
        self.input_field.focus_set()
        
        # Auto-save on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_bert_model(self):
        """Lazy load BERT model when needed"""
        global BERT_TOKENIZER, BERT_MODEL, BERT_AVAILABLE
        
        if self.bert_tokenizer is None and BERT_AVAILABLE:
            try:
                print("Loading BERT model...")
                from transformers import BertTokenizer, BertModel
                
                self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
                self.bert_model = BertModel.from_pretrained('bert-base-uncased')
                
                BERT_TOKENIZER = self.bert_tokenizer
                BERT_MODEL = self.bert_model
                
                print("✅ BERT model loaded successfully!")
                self.notification_system.show_notification("BERT model loaded successfully", "success")
                return True
            except Exception as e:
                print(f"❌ Failed to load BERT model: {e}")
                BERT_AVAILABLE = False
                self.bert_tokenizer = None
                self.bert_model = None
                self.notification_system.show_notification(f"Failed to load BERT: {e}", "error")
                return False
        return self.bert_tokenizer is not None
    
    def load_intelligence_system(self):
        """Lazy load intelligence enhancement system when needed"""
        if self.intelligence is None and INTELLIGENCE_AVAILABLE:
            try:
                print("Loading intelligence enhancement system...")
                from claude_intelligence import SmartClaudeProcessor
                
                self.intelligence = SmartClaudeProcessor()
                
                print("✅ Intelligence enhancement system loaded successfully!")
                self.notification_system.show_notification("Intelligence system loaded successfully", "success")
                return True
            except Exception as e:
                print(f"❌ Failed to load intelligence system: {e}")
                self.intelligence = None
                self.notification_system.show_notification(f"Failed to load intelligence: {e}", "error")
                return False
        return self.intelligence is not None
    
    def load_advanced_ai_system(self):
        """Lazy load advanced AI system when needed"""
        global ADVANCED_AI_SYSTEM, ADVANCED_AI_AVAILABLE
        
        if self.advanced_ai is None and ADVANCED_AI_AVAILABLE:
            try:
                print("Loading advanced AI system...")
                from advanced_ai_system import NextGenAISystem, AdvancedQuery
                
                self.advanced_ai = NextGenAISystem()
                ADVANCED_AI_SYSTEM = self.advanced_ai
                
                print("✅ Advanced AI system loaded successfully!")
                self.notification_system.show_notification("Advanced AI system loaded successfully", "success")
                return True
            except Exception as e:
                print(f"❌ Failed to load advanced AI system: {e}")
                ADVANCED_AI_AVAILABLE = False
                self.advanced_ai = None
                self.notification_system.show_notification(f"Failed to load advanced AI: {e}", "error")
                return False
        return self.advanced_ai is not None
    
    def load_optimization_system(self):
        """Lazy load model optimization system when needed"""
        global OPTIMIZATION_MANAGER, OPTIMIZATION_AVAILABLE
        
        if self.optimization_manager is None and OPTIMIZATION_AVAILABLE:
            try:
                print("Loading model optimization system...")
                from model_optimizer import OptimizationManager, ConversationQualityOptimizer, ResponseTimeOptimizer
                
                self.optimization_manager = OptimizationManager(self.db.db_path)
                OPTIMIZATION_MANAGER = self.optimization_manager
                
                print("✅ Model optimization system loaded successfully!")
                self.notification_system.show_notification("Optimization system loaded successfully", "success")
                return True
            except Exception as e:
                print(f"❌ Failed to load optimization system: {e}")
                OPTIMIZATION_AVAILABLE = False
                self.optimization_manager = None
                self.notification_system.show_notification(f"Failed to load optimization: {e}", "error")
                return False
        return self.optimization_manager is not None
    
    def load_web_intelligence_system(self):
        """Lazy load web intelligence system when needed"""
        if self.web_intelligence is None and self.web_intelligence_enabled:
            try:
                print("Loading web intelligence system...")
                from web_intelligence import get_web_intelligence
                
                self.web_intelligence = get_web_intelligence()
                
                print("✅ Web intelligence system loaded successfully!")
                self.notification_system.show_notification("Web intelligence system loaded successfully", "success")
                return True
            except Exception as e:
                print(f"❌ Failed to load web intelligence system: {e}")
                self.web_intelligence = None
                self.web_intelligence_enabled = False
                self.notification_system.show_notification(f"Failed to load web intelligence: {e}", "error")
                return False
        return self.web_intelligence is not None
    
    def setup_hotkeys(self):
        """Setup keyboard shortcuts"""
        try:
            # Bind Ctrl+Enter to send message
            self.root.bind('<Control-Return>', lambda e: self.send_message())
            # Bind Ctrl+N for new conversation
            self.root.bind('<Control-n>', lambda e: self.new_conversation())
            # Bind Ctrl+S for save conversation
            self.root.bind('<Control-s>', lambda e: self.save_conversation())
            # Bind Ctrl+E for export conversation
            self.root.bind('<Control-e>', lambda e: self.export_conversation())
            # Bind F1 for help
            self.root.bind('<F1>', lambda e: self.show_about())
            logger.info("Hotkeys configured successfully")
        except Exception as e:
            logger.error(f"Failed to setup hotkeys: {e}")
    
    def start_background_tasks(self):
        """Start background tasks for maintenance and updates"""
        # Update clock every second
        self.update_clock()
        # Update performance metrics every 5 seconds
        self.root.after(5000, self.update_performance_display)
        # Auto-save every 30 seconds if conversation exists
        self.root.after(30000, self.periodic_auto_save)
    
    def update_clock(self):
        """Update the real-time clock display"""
        try:
            current_time = datetime.now().strftime("%H:%M:%S")
            self.clock_label.configure(text=current_time)
            # Schedule next update
            self.root.after(1000, self.update_clock)
        except Exception as e:
            logger.error(f"Clock update failed: {e}")
    
    def update_performance_display(self):
        """Update performance metrics display"""
        try:
            metrics = self.performance_monitor.get_metrics()
            perf_text = f"RT: {metrics['response_time']:.1f}s | Err: {metrics['error_rate']:.1%}"
            self.performance_label.configure(text=perf_text)
            # Schedule next update
            self.root.after(5000, self.update_performance_display)
        except Exception as e:
            logger.error(f"Performance display update failed: {e}")
    
    def update_personality_indicator(self):
        """Update the personality indicator in the header"""
        try:
            personality_map = {
                'loyal_ether': '[Loyal]',
                'rogue_ether': '[Rogue]',
                'adaptive_ether': '[Adaptive]',
                'sage_ether': '[Sage]',
                'creative_ether': '[Creative]',
                'analytical_ether': '[Analytical]',
                'companion_ether': '[Companion]',
                'explorer_ether': '[Explorer]'
            }
            indicator_text = personality_map.get(self.personality_system.current_personality, '[Unknown]')
            self.personality_indicator.configure(text=indicator_text)
        except Exception as e:
            logger.error(f"Personality indicator update failed: {e}")
    
    def periodic_auto_save(self):
        """Periodic auto-save if conversation exists"""
        try:
            if self.conversation and self.config.get('auto_save', True):
                self.auto_save_conversation()
            # Schedule next auto-save
            self.root.after(30000, self.periodic_auto_save)
        except Exception as e:
            logger.error(f"Periodic auto-save failed: {e}")
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return hashlib.md5(f"{datetime.now().isoformat()}{os.getpid()}".encode()).hexdigest()[:12]
    
    def init_speech_systems(self):
        """Initialize speech systems for input and output"""
        if not SPEECH_AVAILABLE:
            self.recognizer = None
            self.tts_engine = None
            return
            
        try:
            # Initialize recognizer instance
            self.recognizer = sr.Recognizer()
            
            # Initialize text-to-speech engine
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.9)  # Volume 0-1
            voices = self.tts_engine.getProperty('voices')
            if voices:
                self.tts_engine.setProperty('voice', voices[0].id)  # Set default voice
            
            print("Speech systems initialized successfully!")
            
        except Exception as e:
            print(f"Warning: Speech systems initialization failed: {e}")
            self.recognizer = None
            self.tts_engine = None
    
    def setup_styles(self):
        """Configure colors and fonts"""
        theme = self.config.get('theme', 'light')
        
        if theme == 'dark':
            self.bg_color = "#2b2b2b"
            self.chat_bg = "#1e1e1e"
            self.user_color = "#0d47a1"
            self.claude_color = "#424242"
            self.text_color = "#ffffff"
        else:
            self.bg_color = "#f0f0f0"
            self.chat_bg = "#ffffff"
            self.user_color = "#e3f2fd"
            self.claude_color = "#f5f5f5"
            self.text_color = "#000000"
        
        self.primary_color = "#1976d2"
        self.secondary_color = "#7b1fa2"
        
        self.root.configure(bg=self.bg_color)
        
        # Configure fonts
        self.font_normal = font.Font(family="Segoe UI", size=10)
        self.font_bold = font.Font(family="Segoe UI", size=10, weight="bold")
        self.font_header = font.Font(family="Segoe UI", size=14, weight="bold")
    
    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Conversation", command=self.new_conversation)
        file_menu.add_command(label="Save Conversation", command=self.save_conversation)
        file_menu.add_command(label="Export Conversation", command=self.export_conversation)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Analytics Dashboard", command=self.show_analytics)
        tools_menu.add_command(label="Configuration", command=self.show_config)
        tools_menu.add_command(label="Conversation History", command=self.show_history)
        tools_menu.add_separator()
        tools_menu.add_command(label="Switch Theme", command=self.show_theme_selector)
        tools_menu.add_separator()
        tools_menu.add_command(label="Layout Editor", command=self.show_layout_editor)
        if DRAG_DROP_AVAILABLE:
            tools_menu.add_command(label="Drag & Drop Settings", command=self.show_drag_drop_settings)
        tools_menu.add_command(label="UI Animations", command=self.show_animation_settings)
        if OPTIMIZATION_AVAILABLE:
            tools_menu.add_command(label="Model Optimization", command=self.show_optimization)
        else:
            tools_menu.add_command(label="Model Optimization (Unavailable)", command=self.show_optimization_unavailable, state="disabled")
        
        # Visualization menu
        visualize_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualizations", menu=visualize_menu)
        visualize_menu.add_command(label="Show Sample", command=self.show_visualization)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_widgets(self):
        """Create and layout GUI elements"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header with analytics
        self.create_header(main_frame)
        
        # Chat display area
        self.create_chat_area(main_frame)
        
        # Input area
        self.create_input_area(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
        
        # Register components with layout manager
        self.register_layout_components(main_frame)
        
        # Setup drag-and-drop if available
        if DRAG_DROP_AVAILABLE:
            self.setup_drag_drop_features()
        
        # Add initial message with enhanced status
        greeting = self.personality_system.get_greeting()
        self.add_message(f"Neural Interface Status: 🚀 All Systems Ready (Advanced features load on demand)\n\n{greeting}", "claude")
        
        # Start background tasks
        self.start_background_tasks()
    
    def create_header(self, parent):
        """Create enhanced header with title, stats, and real-time metrics"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)
        
        # Title with personality indicator
        title_frame = ttk.Frame(header_frame)
        title_frame.grid(row=0, column=0, sticky=tk.W)
        
        title_label = ttk.Label(title_frame, text="🟣 Ether AI Neural Interface", font=self.font_header)
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        self.personality_indicator = ttk.Label(title_frame, text="[Loyal]", font=("Segoe UI", 8), foreground="purple")
        self.personality_indicator.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # Enhanced stats frame
        stats_frame = ttk.Frame(header_frame)
        stats_frame.grid(row=0, column=1, sticky=tk.E)
        
        self.stats_label = ttk.Label(stats_frame, text="Messages: 0 | Quality: N/A", foreground="gray")
        self.stats_label.grid(row=0, column=0, padx=(10, 0))
        
        self.performance_label = ttk.Label(stats_frame, text="Perf: N/A", foreground="blue")
        self.performance_label.grid(row=0, column=1, padx=(10, 0))
        
        self.status_label = ttk.Label(stats_frame, text="Ready", foreground="green")
        self.status_label.grid(row=0, column=2, padx=(10, 0))
        
        # Add real-time clock
        self.clock_label = ttk.Label(stats_frame, text="", foreground="gray")
        self.clock_label.grid(row=0, column=3, padx=(10, 0))
        self.update_clock()
    
    def create_chat_area(self, parent):
        """Create chat display area"""
        chat_frame = ttk.Frame(parent)
        chat_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # Chat text area with scrollbar
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=self.font_normal,
            bg=self.chat_bg,
            fg=self.text_color,
            relief=tk.SUNKEN,
            borderwidth=1,
            state=tk.DISABLED,
            height=20
        )
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags
        self.chat_display.tag_configure("user", background=self.user_color, font=self.font_bold, spacing1=5, spacing3=5)
        self.chat_display.tag_configure("claude", background=self.claude_color, font=self.font_bold, spacing1=5, spacing3=5)
        self.chat_display.tag_configure("user_text", font=self.font_normal, spacing3=10)
        self.chat_display.tag_configure("claude_text", font=self.font_normal, spacing3=10)
        self.chat_display.tag_configure("timestamp", foreground="gray", font=("Segoe UI", 8))
        self.chat_display.tag_configure("quality", foreground="blue", font=("Segoe UI", 8))
    
    def create_input_area(self, parent):
        """Create input area with enhanced controls"""
        input_frame = ttk.Frame(parent)
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        # Input field
        self.input_field = tk.Text(
            input_frame,
            height=3,
            font=self.font_normal,
            wrap=tk.WORD,
            relief=tk.SUNKEN,
            borderwidth=1,
            bg=self.chat_bg,
            fg=self.text_color
        )
        self.input_field.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Bind events
        self.input_field.bind('<Return>', self.on_enter_key)
        self.input_field.bind('<Shift-Return>', self.on_shift_enter)
        
        # Button frame
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Send button
        self.send_button = ttk.Button(
            button_frame,
            text="Send",
            command=self.send_message,
            width=10
        )
        self.send_button.grid(row=0, column=0, sticky=tk.E+tk.W, pady=(0, 5))
        
        # Clear button
        self.clear_button = ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_conversation,
            width=10
        )
        self.clear_button.grid(row=1, column=0, sticky=tk.E+tk.W, pady=(0, 5))
        
        # Voice input button (only if speech is available)
        if SPEECH_AVAILABLE:
            self.voice_button = ttk.Button(
                button_frame,
                text="🎤 Voice",
                command=self.start_voice_input,
                width=10
            )
            self.voice_button.grid(row=2, column=0, sticky=tk.E+tk.W, pady=(0, 5))
        else:
            self.voice_button = ttk.Button(
                button_frame,
                text="🎤 Voice (N/A)",
                state="disabled",
                width=10
            )
            self.voice_button.grid(row=2, column=0, sticky=tk.E+tk.W, pady=(0, 5))
        
        # TTS toggle button (only if speech is available)
        self.tts_enabled = tk.BooleanVar(self.root, value=SPEECH_AVAILABLE)
        if SPEECH_AVAILABLE:
            self.tts_button = ttk.Checkbutton(
                button_frame,
                text="🔊 TTS",
                variable=self.tts_enabled,
                command=self.toggle_tts,
                width=10
            )
        else:
            self.tts_button = ttk.Checkbutton(
                button_frame,
                text="🔊 TTS (N/A)",
                variable=self.tts_enabled,
                command=self.toggle_tts,
                width=10,
                state="disabled"
            )
        self.tts_button.grid(row=3, column=0, sticky=tk.E+tk.W, pady=(0, 5))
        
        # Automatic Personality Display (Read-only)
        personality_frame = ttk.LabelFrame(button_frame, text="Auto Personality", padding="5")
        personality_frame.grid(row=4, column=0, sticky=tk.E+tk.W, pady=(5, 0))
        
        # Current personality display (read-only)
        self.personality_var = tk.StringVar(self.root, value=self.personality_system.current_personality)
        self.personality_display = ttk.Label(
            personality_frame,
            textvariable=self.personality_var,
            foreground="blue",
            font=("Segoe UI", 8, "bold"),
            width=12
        )
        self.personality_display.grid(row=0, column=0, sticky=tk.W)
        
        # Personality info button (keep for information)
        info_button = ttk.Button(
            personality_frame,
            text="ℹ️",
            command=self.show_personality_info,
            width=3
        )
        info_button.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
    
    def show_theme_selector(self):
        """Show theme selection dialog"""
        theme_window = tk.Toplevel(self.root)
        theme_window.title("Theme Selection")
        theme_window.geometry("500x600")
        theme_window.resizable(False, False)
        
        # Center the window
        theme_window.transient(self.root)
        theme_window.grab_set()
        
        # Main frame with scrollable content
        main_frame = tk.Frame(theme_window, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_label = tk.Label(main_frame, text="🎨 Choose Theme", font=self.font_header, bg='#f0f0f0')
        header_label.pack(pady=(0, 20))
        
        # Theme selection variable
        theme_var = tk.StringVar(theme_window, value=self.theme_manager.current_theme)
        
        # Create scrollable frame for themes
        canvas = tk.Canvas(main_frame, bg='#f0f0f0', highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Group themes by category
        categories = {
            'Premium': ['ethereal_light', 'midnight_elegance'],
            'Futuristic': ['neon_cyberpunk', 'cosmic_void'],
            'Nature': ['ocean_depths', 'forest_whisper'],
            'Warm': ['sunset_dreams', 'golden_hour'],
            'Luxury': ['royal_purple', 'rose_gold'],
            'Cool': ['arctic_ice']
        }
        
        row = 0
        for category, theme_keys in categories.items():
            # Category header
            category_label = tk.Label(scrollable_frame, text=f"📁 {category}", 
                                    font=('Arial', 11, 'bold'), bg='#f0f0f0', fg='#333')
            category_label.grid(row=row, column=0, sticky=tk.W, pady=(10, 5))
            row += 1
            
            # Themes in this category
            for theme_key in theme_keys:
                if theme_key in self.theme_manager.themes:
                    theme_name = self.theme_manager.themes[theme_key]['name']
                    
                    def create_preview_command(tk=theme_key):
                        return lambda: self.preview_theme(tk)
                    
                    # Use regular tk.Radiobutton instead of ttk to avoid ttkbootstrap issues
                    rb = tk.Radiobutton(
                        scrollable_frame,
                        text=theme_name,
                        variable=theme_var,
                        value=theme_key,
                        command=create_preview_command(theme_key),
                        bg='#f0f0f0',
                        font=('Arial', 10),
                        activebackground='#e0e0e0',
                        selectcolor='#ffffff'
                    )
                    rb.grid(row=row, column=0, sticky=tk.W, pady=2, padx=20)
                    row += 1
        
        # Button frame at bottom
        button_frame = tk.Frame(theme_window, bg='#f0f0f0')
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def apply_theme_with_animation():
            selected_theme = theme_var.get()
            try:
                self.theme_manager.apply_theme(selected_theme, self)
                self.config.set('theme', selected_theme)
                self.config.save()
                theme_window.destroy()
                # Show success message
                self.notification_system.show_notification(f"Theme changed to {self.theme_manager.themes[selected_theme]['name']}", "success")
            except Exception as e:
                print(f"Error applying theme: {e}")
                self.notification_system.show_notification(f"Error applying theme: {e}", "error")
        
        apply_btn = tk.Button(button_frame, text="Apply Theme", command=apply_theme_with_animation,
                             bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'),
                             padx=20, pady=5)
        apply_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=theme_window.destroy,
                              bg='#f44336', fg='white', font=('Arial', 10, 'bold'),
                              padx=20, pady=5)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Add mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    def preview_theme(self, theme_key):
        """Preview theme without applying permanently"""
        self.theme_manager.apply_theme(theme_key, self)
    
    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.token_label = ttk.Label(status_frame, text="Tokens: 0", foreground="gray")
        self.token_label.grid(row=0, column=1)
        
        # Add layout indicator
        self.layout_label = ttk.Label(status_frame, text=f"Layout: {self.layout_manager.current_layout}", foreground="blue")
        self.layout_label.grid(row=0, column=2, padx=(10, 0))
    
    def update_stats(self):
        """Update conversation statistics"""
        if not self.conversation:
            self.stats_label.config(text="Messages: 0 | Quality: N/A")
            return
        
        message_count = len(self.conversation)
        quality_score = self.analyzer.analyze_conversation_quality(self.conversation)
        
        self.stats_label.config(text=f"Messages: {message_count} | Quality: {quality_score:.2f}")
    
    def get_mode_parameters(self) -> Dict:
        """Get API parameters for universal mode"""
        base_params = {
            'model': self.config.get('model'),
            'max_tokens': 1500,  # Blended max_tokens for versatility
            'temperature': 0.6   # Blended temperature for balanced creativity and focus
        }
        return base_params
    
    def on_enter_key(self, event):
        """Handle Enter key press"""
        if event.state & 0x1:  # Shift key is pressed
            return None
        else:
            self.send_message()
            return "break"
    
    def on_shift_enter(self, event):
        """Handle Shift+Enter key press"""
        return None
    
    def add_message(self, message, sender, timestamp=None, quality_score=None):
        """Add a message to the chat display"""
        self.chat_display.configure(state=tk.NORMAL)
        
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add sender label
        if sender == "user":
            self.chat_display.insert(tk.END, "You", "user")
        else:
            self.chat_display.insert(tk.END, "Ether", "claude")
        
        # Add timestamp
        self.chat_display.insert(tk.END, f" ({timestamp})", "timestamp")
        
        # Add quality score if available
        if quality_score is not None:
            self.chat_display.insert(tk.END, f" [Q: {quality_score:.2f}]", "quality")
        
        self.chat_display.insert(tk.END, "\n")
        
        # Add message content
        tag = "user_text" if sender == "user" else "claude_text"
        self.chat_display.insert(tk.END, message + "\n\n", tag)
        
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def send_message(self):
        """Send message to Claude AI"""
        message = self.input_field.get("1.0", tk.END).strip()
        
        if not message:
            return
        
        # Add user message to display
        self.add_message(message, "user")
        
        # Clear input field
        self.input_field.delete("1.0", tk.END)
        
        # Update UI state
        self.send_button.configure(state=tk.DISABLED, text="Sending...")
        self.status_label.configure(text="Ether is thinking...", foreground="orange")
        self.progress_bar.start()
        
        # Send request in separate thread
        thread = threading.Thread(target=self.send_to_claude, args=(message,))
        thread.daemon = True
        thread.start()
    
    def send_to_claude(self, message):
        """Enhanced message processing with advanced features"""
        start_time = time.time()
        
        try:
            # Initialize memory system if enabled
            if self.memory_enabled:
                if self.memory_system is None:
                    from memory_system import AdvancedMemorySystem
                    self.memory_system = AdvancedMemorySystem()
                    logger.info("Advanced memory system initialized.")
                
                # Store user message in memory
                self.memory_system.store_memory(message, memory_type="conversation", tags=["user_input"])
                
            # Update status on main thread
            def update_status(text, color="orange"):
                try:
                    self.status_label.configure(text=text, foreground=color)
                except:
                    pass  # Ignore if window is closed
            
            self.root.after(0, lambda: update_status("Evaluating personality factors...", "purple"))
            
            # Switch personality based on message factors
            if self.personality_system.switch_personality_based_on_factors(message, self.db):
                # Update personality indicators on main thread
                def update_personality():
                    try:
                        self.personality_var.set(self.personality_system.current_personality)
                        self.update_personality_indicator()
                    except Exception:
                        pass
                
                self.root.after(0, update_personality)
                
                # Log personality switch
                current_personality = self.personality_system.get_personality_info()
                logger.info(f"Dynamic personality switch: {current_personality['name']}")
                
                # Update status to show personality switch
                self.root.after(0, lambda: update_status(f"Switched to {current_personality['name']}", "blue"))
                
                # Show notification
                self.notification_system.show_notification(f"Personality switched to {current_personality['name']}", "info")
            
            # Enhance message with intelligence if available
            enhanced_message = message
            
            # Try to load and use BERT if available
            if BERT_AVAILABLE and 'analyze' in message.lower():
                if self.load_bert_model():
                    try:
                        inputs = self.bert_tokenizer(message, return_tensors='pt')
                        outputs = self.bert_model(**inputs)
                        # Use original message for now, but we've processed it with BERT
                        enhanced_message = message
                        self.root.after(0, lambda: update_status("Processing with BERT...", "purple"))
                        print(f"BERT processed message: {message[:50]}...")
                    except Exception as e:
                        print(f"BERT processing failed: {e}")
                        enhanced_message = message
            
            # Try to load and use web intelligence if available
            elif self.web_intelligence_enabled and any(keyword in message.lower() for keyword in ['weather', 'news', 'search', 'current', 'web', 'internet', 'latest', 'recent', 'today', 'now']):
                if self.load_web_intelligence_system():
                    try:
                        # Get comprehensive context using web intelligence
                        context = self.web_intelligence.get_comprehensive_context(message)
                        
                        # Add web context to the message
                        web_context = ""
                        if context['web_results']:
                            web_context += "\n\nRecent web search results:\n"
                            for result in context['web_results'][:3]:
                                web_context += f"• {result.title}: {result.snippet}\n"
                        
                        if context['news']:
                            web_context += "\n\nLatest news:\n"
                            for article in context['news'][:3]:
                                web_context += f"• {article.title}: {article.summary}\n"
                        
                        if context['market_data']:
                            web_context += "\n\nMarket data:\n"
                            for data in context['market_data']:
                                web_context += f"• {data.symbol}: ${data.price:.2f} ({data.change_percent:+.1f}%)\n"
                        
                        enhanced_message = message + web_context
                        self.root.after(0, lambda: update_status("Enhancing with web intelligence...", "cyan"))
                    except Exception as e:
                        logger.warning(f"Web intelligence enhancement failed: {e}")
                        enhanced_message = message
            
            # Try to load and use intelligence enhancement if available
            elif INTELLIGENCE_AVAILABLE and any(keyword in message.lower() for keyword in ['weather', 'news', 'search', 'current']):
                if self.load_intelligence_system():
                    try:
                        enhanced_message = self.intelligence.enhance_message(message)
                        self.root.after(0, lambda: update_status("Enhancing with intelligence...", "blue"))
                    except Exception as e:
                        logger.warning(f"Intelligence enhancement failed: {e}")
                        enhanced_message = message
            
            # Try to load and use advanced AI if available
            elif ADVANCED_AI_AVAILABLE and any(keyword in message.lower() for keyword in ['advanced', 'complex', 'deep']):
                if self.load_advanced_ai_system():
                    try:
                        # Use advanced AI system for complex queries
                        self.root.after(0, lambda: update_status("Processing with advanced AI...", "cyan"))
                        print(f"Advanced AI processing: {message[:50]}...")
                    except Exception as e:
                        logger.warning(f"Advanced AI processing failed: {e}")
                        enhanced_message = message
            
            # Add user message to conversation (with enhanced content)
            user_msg = {
                'role': 'user',
                'content': enhanced_message,
                'timestamp': datetime.now().isoformat(),
                'response_time': 0
            }
            self.conversation.append(user_msg)
            
            # Get API parameters based on mode
            params = self.get_mode_parameters()
            
            # Clean messages for API (only role and content)
            api_messages = []
            for msg in self.conversation:
                clean_msg = {
                    'role': msg['role'],
                    'content': msg['content']
                }
                api_messages.append(clean_msg)
            
            # Add system prompt for personality
            system_prompt = self.personality_system.get_system_prompt()
            
            # Enhanced system prompt with memory context
            if self.memory_system:
                # Search for relevant memories
                relevant_memories = self.memory_system.search_memories(enhanced_message, limit=5)
                if relevant_memories:
                    memory_context = "\n\nRelevant context from previous conversations:\n"
                    for memory in relevant_memories:
                        memory_context += f"- {memory.content[:100]}...\n"
                    system_prompt += memory_context
            
            # Send to Claude with system prompt
            response = self.client.messages.create(
                system=system_prompt,
                messages=api_messages,
                **params
            )
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Extract response
            claude_response = response.content[0].text
            
            # Add Claude's response to conversation
            claude_msg = {
                'role': 'assistant',
                'content': claude_response,
                'timestamp': datetime.now().isoformat(),
                'response_time': response_time,
                'tokens': response.usage.output_tokens if hasattr(response, 'usage') else 0
            }
            self.conversation.append(claude_msg)
            
        # Calculate quality score
        quality_score = self.analyzer.analyze_conversation_quality([claude_msg])
        claude_msg['quality_score'] = quality_score
        
        # Store Claude response in memory if enabled
        if self.memory_system:
            self.memory_system.store_memory(
                claude_response, 
                memory_type="conversation", 
                tags=["ai_response", self.personality_system.current_personality],
                metadata={
                    "quality_score": quality_score,
                    "response_time": response_time,
                    "personality": self.personality_system.current_personality
                }
            )
        
        # Update UI in main thread
        self.root.after(0, lambda: self.handle_claude_response(claude_response, response_time, quality_score))
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            logger.error(f"Error in send_to_claude: {error_msg}")
            # Safe error handling
            self.root.after(0, lambda: self.handle_error(error_msg))
    
    def handle_claude_response(self, response, response_time, quality_score):
        """Enhanced response handling with performance monitoring"""
        # Record performance metrics
        self.performance_monitor.record_response_time(response_time)
        self.performance_monitor.record_success()
        
        # Add response to chat display
        self.add_message(response, "claude", quality_score=quality_score)
        
        # Update UI state
        self.send_button.configure(state=tk.NORMAL, text="Send")
        self.status_label.configure(text="Ready", foreground="green")
        self.progress_bar.stop()
        
        # Update statistics and performance
        self.update_stats()
        self.update_performance_display()
        
        # Update token count
        total_tokens = sum(msg.get('tokens', 0) for msg in self.conversation)
        self.token_label.config(text=f"Tokens: {total_tokens}")
        
        # Focus back on input field
        self.input_field.focus_set()
        
        # Auto-save if enabled
        if self.config.get('auto_save', True):
            self.auto_save_conversation()
        
        # Speak Claude's response if TTS is enabled
        if self.tts_enabled.get() and self.tts_engine:
            self.speak_text(response)
        
        # Show success notification with animation
        self.notification_system.show_notification("Response generated successfully", "success")
        
        # Add pulse effect to the new message
        self.animation_manager.pulse_effect(self.chat_display)
    
    def handle_error(self, error_msg):
        """Enhanced error handling with monitoring and notifications"""
        # Record error metrics
        self.performance_monitor.record_error()
        
        # Add error to chat display
        self.add_message(error_msg, "claude")
        
        # Update UI state
        self.send_button.configure(state=tk.NORMAL, text="Send")
        self.status_label.configure(text="Error", foreground="red")
        self.progress_bar.stop()
        self.input_field.focus_set()
        
        # Update performance display
        self.update_performance_display()
        
        # Show error notification
        self.notification_system.show_notification(f"Error: {error_msg}", "error")
        
        # Log error
        logger.error(f"API Error: {error_msg}")
    
    def auto_save_conversation(self):
        """Auto-save conversation to database"""
        if self.conversation:
            try:
                title = self.analyzer.generate_conversation_summary(self.conversation)
                self.db.save_conversation(self.session_id, self.conversation, title=title)
                logger.info(f"Auto-saved conversation: {title}")
            except Exception as e:
                logger.error(f"Auto-save failed: {e}")
    
    def save_conversation(self):
        """Manual save conversation"""
        if not self.conversation:
            messagebox.showinfo("Save Conversation", "No conversation to save.")
            return
        
        title = self.analyzer.generate_conversation_summary(self.conversation)
        self.db.save_conversation(self.session_id, self.conversation, title=title)
        messagebox.showinfo("Save Conversation", f"Conversation saved: {title}")
    
    def export_conversation(self):
        """Export conversation to file"""
        if not self.conversation:
            messagebox.showinfo("Export Conversation", "No conversation to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                export_data = {
                    'session_id': self.session_id,
                    'timestamp': datetime.now().isoformat(),
                    'conversation': self.conversation,
                    'analytics': {
                        'total_messages': len(self.conversation),
                        'quality_score': self.analyzer.analyze_conversation_quality(self.conversation),
                        'summary': self.analyzer.generate_conversation_summary(self.conversation)
                    }
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Export Conversation", f"Conversation exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export conversation: {str(e)}")
    
    def new_conversation(self):
        """Start a new conversation"""
        if self.conversation and messagebox.askyesno("New Conversation", "Save current conversation before starting new one?"):
            self.save_conversation()
        
        self.clear_conversation()
        self.session_id = self._generate_session_id()
        self.conversation_start_time = datetime.now()
    
    def clear_conversation(self):
        """Clear the conversation"""
        self.conversation = []
        
        # Clear chat display
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.configure(state=tk.DISABLED)
        
        # Add initial message with personality greeting
        greeting = self.personality_system.get_greeting()
        self.add_message(greeting, "claude")
        
        # Update stats
        self.update_stats()
        self.token_label.config(text="Tokens: 0")
        
        # Focus on input field
        self.input_field.focus_set()
    
    def show_analytics(self):
        """Show analytics dashboard"""
        analytics_window = tk.Toplevel(self.root)
        analytics_window.title("Analytics Dashboard")
        analytics_window.geometry("600x400")
        
        # Get analytics data
        analytics = self.db.get_conversation_analytics(30)
        
        # Create analytics display
        frame = ttk.Frame(analytics_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="📊 Analytics Dashboard", font=self.font_header).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Stats
        stats = [
            ("Total Conversations (30 days)", analytics['total_conversations']),
            ("Total Messages", analytics['total_messages']),
            ("Average Quality Score", f"{analytics['avg_quality']:.2f}"),
            ("Average Duration", f"{analytics['avg_duration']:.1f} min")
        ]
        
        for i, (label, value) in enumerate(stats):
            ttk.Label(frame, text=f"{label}:", font=self.font_bold).grid(row=i+1, column=0, sticky=tk.W, pady=5)
            ttk.Label(frame, text=str(value)).grid(row=i+1, column=1, sticky=tk.W, padx=(20, 0), pady=5)
    
    def show_config(self):
        """Show configuration window"""
        config_window = tk.Toplevel(self.root)
        config_window.title("Configuration")
        config_window.geometry("400x300")
        
        frame = ttk.Frame(config_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="⚙️ Configuration", font=self.font_header).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Configuration options
        theme_options = [key for key, _ in self.theme_manager.get_theme_names()]
        configs = [
            ("Model", 'model', ['claude-3-5-sonnet-20241022', 'claude-3-haiku-20240307']),
            ("Max Tokens", 'max_tokens', None),
            ("Temperature", 'temperature', None),
            ("Theme", 'theme', theme_options),
            ("Auto Save", 'auto_save', None)
        ]
        
        self.config_vars = {}
        
        for i, (label, key, options) in enumerate(configs):
            ttk.Label(frame, text=f"{label}:").grid(row=i+1, column=0, sticky=tk.W, pady=5)
            
            if options:
                var = tk.StringVar(config_window, value=self.config.get(key))
                combo = ttk.Combobox(frame, textvariable=var, values=options, state="readonly")
                combo.grid(row=i+1, column=1, sticky=tk.W, padx=(20, 0), pady=5)
                self.config_vars[key] = var
            elif key == 'auto_save':
                var = tk.BooleanVar(config_window, value=self.config.get(key))
                check = ttk.Checkbutton(frame, variable=var)
                check.grid(row=i+1, column=1, sticky=tk.W, padx=(20, 0), pady=5)
                self.config_vars[key] = var
            else:
                var = tk.StringVar(config_window, value=str(self.config.get(key)))
                entry = ttk.Entry(frame, textvariable=var)
                entry.grid(row=i+1, column=1, sticky=tk.W, padx=(20, 0), pady=5)
                self.config_vars[key] = var
        
        # Save button
        def save_config():
            for key, var in self.config_vars.items():
                value = var.get()
                if key in ['max_tokens']:
                    value = int(value)
                elif key in ['temperature']:
                    value = float(value)
                elif key in ['auto_save']:
                    value = bool(value)
                
                self.config.set(key, value)
            
            messagebox.showinfo("Configuration", "Configuration saved successfully!")
            config_window.destroy()
        
        ttk.Button(frame, text="Save", command=save_config).grid(row=len(configs)+2, column=0, columnspan=2, pady=20)

    def show_optimization(self):
        """Show model optimization interface"""
        optimization_window = tk.Toplevel(self.root)
        optimization_window.title("Model Optimization")
        optimization_window.geometry("600x400")
        
        frame = ttk.Frame(optimization_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="🔧 Model Optimization", font=self.font_header).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Try to load optimization manager
        if not self.optimization_manager:
            self.load_optimization_system()
        
        if self.optimization_manager:
            # Assume models to optimize
            models_to_optimize = ['conversation_quality', 'response_time']
            
            for i, model_type in enumerate(models_to_optimize):
                ttk.Label(frame, text=f"Optimize {model_type}:").grid(row=i+1, column=0, sticky=tk.W, pady=5)
                ttk.Button(frame, text="Start Optimization", command=lambda mt=model_type: self.start_model_optimization(mt)).grid(row=i+1, column=1, pady=5)
        else:
            ttk.Label(frame, text="⚠️ Optimization system not available", foreground="red").grid(row=1, column=0, columnspan=2, pady=10)
            ttk.Label(frame, text="Install required dependencies: optuna, scikit-learn").grid(row=2, column=0, columnspan=2, pady=5)

    def show_visualization(self):
        """Display a sample data visualization"""
        vis_window = tk.Toplevel(self.root)
        vis_window.title("Data Visualization")
        vis_window.geometry("500x400")

        figure = Figure(figsize=(5, 4), dpi=100)
        ax = figure.add_subplot(111)
        ax.plot([0.1, 0.2, 0.3, 0.4], [10, 20, 25, 30], marker='o')
        ax.set_title("Sample Visualization")
        ax.set_xlabel("X Axis")
        ax.set_ylabel("Y Axis")

        canvas = FigureCanvasTkAgg(figure, master=vis_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

      
    def show_optimization_unavailable(self):
        """Show message when optimization is unavailable"""
        messagebox.showerror("Optimization Unavailable", "Model optimization requires additional libraries (optuna, scikit-learn). Please install them to use this feature.")

    def start_model_optimization(self, model_type: str):
        """Start model optimization process"""
        if not self.optimization_manager:
            messagebox.showerror("Error", "Model optimization manager is not available.")
            return

        result = self.optimization_manager.optimizers[model_type].optimize_model(n_trials=50)
        messagebox.showinfo("Optimization Complete", f"Optimization for {model_type} completed. Best Value: {result.best_value:.4f}")  



    
    def show_history(self):
        """Show conversation history"""
        history_window = tk.Toplevel(self.root)
        history_window.title("Conversation History")
        history_window.geometry("700x500")
        
        # Implementation for conversation history browser
        frame = ttk.Frame(history_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="📚 Conversation History", font=self.font_header).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Get recent conversations
        try:
            analytics = self.db.get_conversation_analytics(30)
            
            # Stats display
            stats_frame = ttk.LabelFrame(frame, text="Recent Activity (30 days)", padding="10")
            stats_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
            
            ttk.Label(stats_frame, text=f"Total Conversations: {analytics['total_conversations']}").pack(anchor=tk.W)
            ttk.Label(stats_frame, text=f"Total Messages: {analytics['total_messages']}").pack(anchor=tk.W)
            ttk.Label(stats_frame, text=f"Average Quality: {analytics['avg_quality']:.2f}").pack(anchor=tk.W)
            ttk.Label(stats_frame, text=f"Average Duration: {analytics['avg_duration']:.1f} minutes").pack(anchor=tk.W)
            
            # Trends display
            trends_frame = ttk.LabelFrame(frame, text="Usage Trends", padding="10")
            trends_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
            
            hourly_trends = self.db.get_hourly_trends(7)
            if hourly_trends:
                ttk.Label(trends_frame, text=f"Data points available: {len(hourly_trends)}").pack(anchor=tk.W)
                
                # Show last few entries
                for i, trend in enumerate(hourly_trends[-5:]):
                    trend_text = f"{trend['date']} {trend['hour']:02d}:00 - {trend['message_count']} messages"
                    ttk.Label(trends_frame, text=trend_text).pack(anchor=tk.W)
            else:
                ttk.Label(trends_frame, text="No trend data available yet").pack(anchor=tk.W)
            
        except Exception as e:
            ttk.Label(frame, text=f"Error loading history: {str(e)}", foreground="red").grid(row=1, column=0, columnspan=2, pady=10)
        
        # Close button
        ttk.Button(frame, text="Close", command=history_window.destroy).grid(row=3, column=0, columnspan=2, pady=20)
    
    def show_about(self):
        """Show about dialog"""
        intelligence_features = "\n• Real-time web search and current information\n• Weather data integration\n• News feed access\n• Enhanced contextual responses" if INTELLIGENCE_AVAILABLE else "\n• Intelligence enhancement available (install dependencies)"
        
        about_text = f"""
Ether AI Neural Interface - Enhanced Version

Features:
• Conversation analytics and quality scoring
• Multi-mode conversation support
• Persistent conversation storage
• Export capabilities
• Configuration management
• Performance monitoring{intelligence_features}
• Dynamic personality system
• Neural processing with BERT
• Voice input/output capabilities

Version: 2.1.0 - Neural Enhanced
"""
        messagebox.showinfo("About", about_text)
    
    def start_voice_input(self):
        """Start voice input in a separate thread"""
        if not self.recognizer:
            messagebox.showerror("Voice Input Error", "Speech recognition is not available")
            return
        
        self.voice_button.configure(state=tk.DISABLED, text="🎤 Listening...")
        self.status_label.configure(text="Listening for voice input...", foreground="blue")
        
        # Start voice recognition in a separate thread
        thread = threading.Thread(target=self.perform_voice_input)
        thread.daemon = True
        thread.start()
    
    def perform_voice_input(self):
        """Perform voice input using microphone"""
        try:
            with sr.Microphone() as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source)
                
                # Listen for audio with a 5-second timeout
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                # Update status
                self.root.after(0, lambda: self.status_label.configure(text="Processing voice input...", foreground="purple"))
                
                # Recognize speech using Google Web Speech API
                text = self.recognizer.recognize_google(audio)
                
                # Update UI in main thread
                self.root.after(0, self.handle_voice_input, text)
                
        except sr.WaitTimeoutError:
            self.root.after(0, self.handle_voice_error, "Voice input timeout. Please try again.")
        except sr.UnknownValueError:
            self.root.after(0, self.handle_voice_error, "Could not understand audio. Please try again.")
        except sr.RequestError as e:
            self.root.after(0, self.handle_voice_error, f"Could not request results from speech recognition service: {e}")
        except Exception as e:
            self.root.after(0, self.handle_voice_error, f"Voice input error: {e}")
    
    def handle_voice_input(self, text):
        """Handle successful voice input"""
        # Insert text into input field
        self.input_field.insert(tk.END, text)
        
        # Reset voice button
        self.voice_button.configure(state=tk.NORMAL, text="🎤 Voice")
        self.status_label.configure(text="Voice input captured", foreground="green")
        
        # Focus on input field
        self.input_field.focus_set()
    
    def handle_voice_error(self, error_msg):
        """Handle voice input errors"""
        self.voice_button.configure(state=tk.NORMAL, text="🎤 Voice")
        self.status_label.configure(text=error_msg, foreground="red")
        
        # Show error message
        messagebox.showerror("Voice Input Error", error_msg)
    
    def toggle_tts(self):
        """Toggle text-to-speech on/off"""
        if self.tts_enabled.get():
            self.status_label.configure(text="Text-to-speech enabled", foreground="green")
        else:
            self.status_label.configure(text="Text-to-speech disabled", foreground="gray")
    
    def speak_text(self, text):
        """Speak text using TTS in a separate thread"""
        if not self.tts_engine:
            return
        
        def tts_worker():
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"TTS error: {e}")
        
        thread = threading.Thread(target=tts_worker)
        thread.daemon = True
        thread.start()
    
    # Manual personality change handler removed - personality switching is now automatic
    
    def show_personality_info(self):
        """Show detailed personality information"""
        personality_info = self.personality_system.get_personality_info()
        
        info_text = f"""
{personality_info['name']}

{personality_info['description']}

Traits: {personality_info['traits']}

Speaking Style: {personality_info['speaking_style']}
"""
        
        messagebox.showinfo("Personality Info", info_text)
    
    def on_closing(self):
        """Handle application closing"""
        if self.conversation and self.config.get('auto_save', True):
            self.auto_save_conversation()
        
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            # Save window geometry
            geometry = self.root.geometry()
            width, height = geometry.split('x')[0], geometry.split('x')[1].split('+')[0]
            self.config.set('window_width', int(width))
            self.config.set('window_height', int(height))
            
            # Fade out before closing
            self.animation_manager.fade_out(self.root, callback=lambda: self.root.destroy())

    def register_layout_components(self, main_frame):
        """Register components with the layout manager"""
        # Register main components
        if hasattr(self, 'chat_display'):
            self.layout_manager.register_component('chat_area', self.chat_display.master, resizable=True)
        if hasattr(self, 'input_field'):
            self.layout_manager.register_component('input_area', self.input_field.master, resizable=True)
    
    def setup_drag_drop_features(self):
        """Setup drag-and-drop features for file handling"""
        # Setup drag-and-drop for chat area
        if hasattr(self, 'chat_display'):
            self.drag_drop_manager.setup_drag_drop(self.chat_display, self.handle_file_drop)
        
        # Setup drag-and-drop for input area
        if hasattr(self, 'input_field'):
            self.drag_drop_manager.setup_drag_drop(self.input_field, self.handle_file_drop)
    
    def handle_file_drop(self, files):
        """Handle dropped files"""
        for file_path in files:
            try:
                file_path = file_path.strip('{}')  # Remove braces if present
                if os.path.exists(file_path):
                    file_name = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path)
                    
                    # Read file content for text files
                    if file_path.lower().endswith(('.txt', '.md', '.py', '.js', '.json', '.xml', '.html', '.css')):
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()[:5000]  # Limit to 5000 characters
                            message = f"📁 File: {file_name} ({file_size} bytes)\n\n{content}"
                            self.input_field.insert(tk.END, message)
                    else:
                        # For other files, just show file info
                        message = f"📁 File dropped: {file_name} ({file_size} bytes)\nPath: {file_path}"
                        self.input_field.insert(tk.END, message)
                    
                    # Show notification
                    self.notification_system.show_notification(f"File loaded: {file_name}", "info")
                    
                    # Add animation effect
                    self.animation_manager.pulse_effect(self.input_field)
                    
            except Exception as e:
                self.notification_system.show_notification(f"Error loading file: {str(e)}", "error")
    
    def show_layout_editor(self):
        """Show layout editor interface"""
        self.layout_manager.create_layout_editor(self.root)
    
    def show_drag_drop_settings(self):
        """Show drag-and-drop settings"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Drag & Drop Settings")
        settings_window.geometry("400x200")
        
        frame = ttk.Frame(settings_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="📂 Drag & Drop Settings", font=('Arial', 12, 'bold')).pack(pady=10)
        
        if DRAG_DROP_AVAILABLE:
            ttk.Label(frame, text="✓ Drag & Drop is available", foreground="green").pack(pady=5)
            ttk.Label(frame, text="You can drag files directly into the chat or input area").pack(pady=5)
        else:
            ttk.Label(frame, text="✗ Drag & Drop not available", foreground="red").pack(pady=5)
            ttk.Label(frame, text="Install tkinterdnd2 to enable drag & drop features").pack(pady=5)
        
        ttk.Button(frame, text="Close", command=settings_window.destroy).pack(pady=10)
    
    def show_animation_settings(self):
        """Show animation settings"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Animation Settings")
        settings_window.geometry("400x300")
        
        frame = ttk.Frame(settings_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="🎬 Animation Settings", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Animation speed settings
        speed_frame = ttk.LabelFrame(frame, text="Animation Speed", padding="10")
        speed_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(speed_frame, text="Fade Speed:").pack(anchor=tk.W)
        fade_var = tk.IntVar(settings_window, value=self.animation_manager.fade_delay)
        fade_scale = ttk.Scale(speed_frame, from_=10, to=100, variable=fade_var, orient=tk.HORIZONTAL)
        fade_scale.pack(fill=tk.X, pady=2)
        
        ttk.Label(speed_frame, text="Slide Speed:").pack(anchor=tk.W)
        slide_var = tk.IntVar(settings_window, value=self.animation_manager.slide_delay)
        slide_scale = ttk.Scale(speed_frame, from_=10, to=100, variable=slide_var, orient=tk.HORIZONTAL)
        slide_scale.pack(fill=tk.X, pady=2)
        
        # Test buttons
        test_frame = ttk.LabelFrame(frame, text="Test Animations", padding="10")
        test_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(test_frame, text="Test Fade", 
                  command=lambda: self.animation_manager.fade_out(self.root, callback=lambda: self.animation_manager.fade_in(self.root))).pack(side=tk.LEFT, padx=5)
        ttk.Button(test_frame, text="Test Pulse", 
                  command=lambda: self.animation_manager.pulse_effect(self.chat_display)).pack(side=tk.LEFT, padx=5)
        
        # Save button
        def save_animation_settings():
            self.animation_manager.fade_delay = fade_var.get()
            self.animation_manager.slide_delay = slide_var.get()
            messagebox.showinfo("Settings Saved", "Animation settings have been saved!")
            settings_window.destroy()
        
        ttk.Button(frame, text="Save Settings", command=save_animation_settings).pack(pady=10)
        ttk.Button(frame, text="Close", command=settings_window.destroy).pack()

def main():
    """Main function to run the enhanced application"""
    # Check if API key is set
    load_dotenv()
    if not os.environ.get('ANTHROPIC_API_KEY'):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "API Key Missing",
            "ANTHROPIC_API_KEY not found in environment variables!\\n\\n"
            "Please:\\n"
            "1. Copy .env.example to .env\\n"
            "2. Add your Anthropic API key to the .env file\\n"
            "3. Get your API key from: https://console.anthropic.com/"
        )
        return
    
    # Create and run the application with drag-and-drop support
    if DRAG_DROP_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    
    app = EnhancedClaudeDesktopApp(root)
    
    # Start with fade in animation
    app.animation_manager.fade_in(root)
    
    print("🚀 Ether AI Neural Interface started!")
    print("🟣 Neural interface with personality system is now running")
    if DRAG_DROP_AVAILABLE:
        print("📂 Drag & Drop support enabled")
    print("🎬 UI animations enabled")
    print("📐 Customizable layouts available")
    
    root.mainloop()

if __name__ == "__main__":
    main()
