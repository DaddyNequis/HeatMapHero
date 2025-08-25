"""
Main GUI window for HeatMapHero application
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.theme import ThemeManager
from core.data_processor import DataProcessor
from core.heatmap_generator import HeatMapGenerator
from core.config import Config

class HeatMapHero:
    def __init__(self, root):
        self.root = root
        self.root.title(Config.APP_NAME)
        self.root.geometry(Config.WINDOW_SIZE)
        
        # Initialize components
        self.theme_manager = ThemeManager(root)
        self.data_processor = DataProcessor()
        self.heatmap_generator = HeatMapGenerator(self.theme_manager)
        
        # Configure dark theme
        self.theme_manager.setup_dark_theme()
        
        # Data storage
        self.background_image = None
        self.background_path = None
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        """Create the main UI components"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Create control panel
        self._create_control_panel(main_frame)
        
        # Create data info panel
        self._create_data_info_panel(main_frame)
        
        # Create plot panel
        self._create_plot_panel(main_frame)
        
    def _create_control_panel(self, parent):
        """Create the control panel"""

        # Create a custom style
        style = ttk.Style()
        style.configure("Custom.TLabelframe", background="#2b2b2b")           # Frame bg
        style.configure("Custom.TLabelframe.Label", background="#2b2b2b")     # Title bg


        control_frame = ttk.LabelFrame(parent, text="Controls", padding="10", style="Custom.TLabelframe")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        


        # Background image controls
        ttk.Label(control_frame, text="Background Image:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.bg_path_var = tk.StringVar(value="No image selected")
        ttk.Label(control_frame, textvariable=self.bg_path_var, 
                 foreground=self.theme_manager.colors['gray_fg']).grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        ttk.Button(control_frame, text="Load Background", 
                  command=self.load_background).grid(row=0, column=2, padx=(0, 10))
        
        # JSON folder controls
        ttk.Label(control_frame, text="JSON Folder:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.folder_path_var = tk.StringVar(value="No folder selected")
        ttk.Label(control_frame, textvariable=self.folder_path_var, 
                 foreground=self.theme_manager.colors['gray_fg']).grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        ttk.Button(control_frame, text="Select Folder", 
                  command=self.select_json_folder).grid(row=1, column=2, padx=(0, 10), pady=(10, 0))
        
        # Heat map type selection
        ttk.Label(control_frame, text="Heat Map Type:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.heatmap_type_var = tk.StringVar(value="RSSI (Signal Strength)")
        heatmap_combo = ttk.Combobox(control_frame, textvariable=self.heatmap_type_var, 
                                   values=list(Config.HEATMAP_TYPES.keys()), 
                                   state="readonly", width=25)
        heatmap_combo.grid(row=2, column=1, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        # Generate button
        ttk.Button(control_frame, text="Generate Heat Map", command=self.generate_heatmap, 
                  style="Accent.TButton").grid(row=3, column=0, columnspan=3, pady=(20, 0))
        
        # Status bar
        self._create_status_bar(control_frame)
    
    def _create_status_bar(self, parent):
        """Create the status bar"""
        self.status_var = tk.StringVar(value="Ready")
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        ttk.Label(status_frame, textvariable=self.status_var, 
                 foreground=self.theme_manager.colors['status_fg']).pack(side=tk.LEFT, padx=(5, 0))
    
    def _create_data_info_panel(self, parent):
        """Create the data information panel"""
        info_frame = ttk.LabelFrame(parent, text="Data Information", padding="10")
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=1)
        
        # Data summary text widget
        text_config = self.theme_manager.get_text_widget_config()
        self.data_summary = tk.Text(info_frame, height=15, width=35, **text_config)
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.data_summary.yview)
        self.data_summary.configure(yscrollcommand=scrollbar.set)
        self.data_summary.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def _create_plot_panel(self, parent):
        """Create the plot panel"""
        self.plot_frame = ttk.LabelFrame(parent, text="Heat Map", padding="5")
        self.plot_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.plot_frame.columnconfigure(0, weight=1)
        self.plot_frame.rowconfigure(0, weight=1)
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(10, 7))
        self.theme_manager.configure_plot_theme(self.fig, self.ax)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().configure(bg=self.theme_manager.colors['dark_bg'])
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initialize with empty plot
        self.ax.set_title("WiFi Analysis Heat Map")
        self.ax.set_xlabel("X Coordinate")
        self.ax.set_ylabel("Y Coordinate")
        self.canvas.draw()
        
    def load_background(self):
        """Load background image"""
        filename = filedialog.askopenfilename(
            title="Select Background Image",
            filetypes=Config.IMAGE_FILETYPES
        )
        
        if filename:
            try:
                self.background_image = Image.open(filename)
                self.background_path = filename
                self.bg_path_var.set(os.path.basename(filename))
                self.status_var.set("Background image loaded successfully")
                self.update_data_summary()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
                self.status_var.set("Error loading background image")
    
    def select_json_folder(self):
        """Select folder containing JSON files"""
        folder = filedialog.askdirectory(title="Select Folder with JSON Files")
        
        if folder:
            self.folder_path_var.set(os.path.basename(folder))
            self.data_processor.load_json_data(folder)
            self.status_var.set("JSON data loaded successfully")
            self.update_data_summary()
    
    def update_data_summary(self):
        """Update the data summary display"""
        self.data_summary.delete(1.0, tk.END)
        
        summary_parts = []
        
        # Background image info
        if self.background_path:
            summary_parts.append(f"Background Image:\n{os.path.basename(self.background_path)}")
            if self.background_image:
                summary_parts.append(f"Size: {self.background_image.size[0]}x{self.background_image.size[1]}")
        
        # Data summary
        data_summary = self.data_processor.get_data_summary()
        if data_summary:
            if summary_parts:
                summary_parts.append("")  # Add blank line
            summary_parts.append(data_summary)
        
        self.data_summary.insert(1.0, '\n'.join(summary_parts))
    
    def generate_heatmap(self):
        """Generate and display the heat map"""
        if not self.data_processor.has_data():
            messagebox.showwarning("Warning", "No WiFi data available. Please select a folder with JSON files.")
            return
        
        selected_type = self.heatmap_type_var.get()
        self.status_var.set(f"Generating {selected_type} heat map...")
        self.root.update()
        
        try:
            # Get coordinates and values
            x_coords, y_coords, values = self.data_processor.get_coordinates_and_values(selected_type)
            _, label, colormap = self.data_processor.get_heatmap_data(selected_type)
            
            # Filter out zero values for throughput metrics
            if "throughput" in Config.HEATMAP_TYPES[selected_type].lower():
                valid_indices = values > 0
                if not any(valid_indices):
                    messagebox.showwarning("Warning", f"No {selected_type} data available in the selected files.")
                    return
                x_coords = x_coords[valid_indices]
                y_coords = y_coords[valid_indices]
                values = values[valid_indices]
            
            # Generate heat map
            self.heatmap_generator.generate_heatmap(
                self.ax, x_coords, y_coords, values, label, colormap, self.background_image
            )
            
            # Update canvas
            self.canvas.draw()
            
            self.status_var.set(f"{selected_type} heat map generated with {len(values)} data points")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate heat map: {str(e)}")
            self.status_var.set("Error generating heat map")
