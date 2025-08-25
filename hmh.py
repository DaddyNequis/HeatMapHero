#!/usr/bin/env python3
"""
HeatMapHero - WiFi Signal Strength Heat Map Generator
Cross-platform GUI application for visualizing WiFi signal strength data
"""

import tkinter as tk
import platform
from gui import HeatMapHero

def main():
    """Main function to run the application"""
    # Create the main window
    root = tk.Tk()
    
    # Set application icon (if available)
    try:
        if platform.system() == "Windows":
            root.iconbitmap(default="icon.ico")
    except:
        pass
    
    # Create and run the application
    app = HeatMapHero(root)
    
    # Center the window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main()
