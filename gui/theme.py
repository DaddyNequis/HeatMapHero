"""
Theme management for HeatMapHero application
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt

class ThemeManager:
    """Manages dark theme configuration for the application"""
    
    def __init__(self, root):
        self.root = root
        self.colors = {
            'dark_bg': '#2b2b2b',
            'dark_fg': '#ffffff',
            'accent_bg': '#404040',
            'button_bg': '#505050',
            'entry_bg': '#404040',
            'selected_bg': '#0078d4',
            'text_bg': '#404040',
            'text_fg': '#ffffff',
            'status_fg': '#00aaff',
            'gray_fg': '#888888'
        }
        
    def setup_dark_theme(self):
        """Configure dark theme for the application"""
        # Configure matplotlib dark theme
        plt.style.use('dark_background')
        
        # Configure root window
        self.root.configure(bg=self.colors['dark_bg'])
        
        # Configure ttk styles for dark theme
        style = ttk.Style()
        
        # Try to use a modern dark theme if available
        try:
            style.theme_use('clam')  # Use clam as base theme
        except:
            pass
        
        # Configure styles
        style.configure('TFrame', background=self.colors['dark_bg'])
        style.configure('TLabelFrame', 
                       background=self.colors['dark_bg'], 
                       foreground=self.colors['dark_fg'], 
                       borderwidth=1)
        style.configure('TLabelFrame.Label', 
                       background=self.colors['dark_bg'], 
                       foreground=self.colors['dark_fg'])
        style.configure('TLabel', 
                       background=self.colors['dark_bg'], 
                       foreground=self.colors['dark_fg'])
        style.configure('TButton', 
                       background=self.colors['button_bg'], 
                       foreground=self.colors['dark_fg'], 
                       borderwidth=1)
        style.configure('Accent.TButton', 
                       background=self.colors['selected_bg'], 
                       foreground=self.colors['dark_fg'], 
                       borderwidth=1)
        style.configure('TCombobox', 
                       fieldbackground=self.colors['entry_bg'], 
                       background=self.colors['button_bg'],
                       foreground=self.colors['dark_fg'], 
                       borderwidth=1)
        
        # Configure button hover effects
        style.map('TButton', 
                 background=[('active', self.colors['accent_bg']), 
                           ('pressed', self.colors['selected_bg'])])
        style.map('Accent.TButton',
                 background=[('active', '#106ebe'), ('pressed', '#005a9e')])
        style.map('TCombobox',
                 fieldbackground=[('readonly', self.colors['entry_bg']), 
                                ('focus', self.colors['entry_bg'])],
                 background=[('active', self.colors['accent_bg'])])
    
    def get_text_widget_config(self):
        """Get configuration for Text widgets"""
        return {
            'bg': self.colors['text_bg'],
            'fg': self.colors['text_fg'],
            'insertbackground': self.colors['text_fg'],
            'selectbackground': self.colors['selected_bg'],
            'selectforeground': self.colors['text_fg']
        }
    
    def configure_plot_theme(self, fig, ax):
        """Configure matplotlib figure and axes for dark theme"""
        fig.patch.set_facecolor(self.colors['dark_bg'])
        ax.set_facecolor(self.colors['dark_bg'])
        ax.tick_params(colors=self.colors['dark_fg'])
        ax.xaxis.label.set_color(self.colors['dark_fg'])
        ax.yaxis.label.set_color(self.colors['dark_fg'])
        ax.title.set_color(self.colors['dark_fg'])
        
        # Configure colorbar if it exists
        for child in ax.get_children():
            if hasattr(child, 'colorbar'):
                child.colorbar.ax.tick_params(colors=self.colors['dark_fg'])
    
    def get_annotation_style(self):
        """Get annotation style for plots"""
        return {
            'bbox': dict(boxstyle="round,pad=0.3", 
                        facecolor=self.colors['dark_bg'], 
                        edgecolor=self.colors['dark_fg'], 
                        alpha=0.8),
            'color': self.colors['dark_fg']
        }
