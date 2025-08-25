"""
Main GUI window for HeatMapHero application
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import subprocess
import threading
import platform
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
        self.click_enabled = False
        self.analysis_running = False
        
        # Create UI
        self.create_widgets()
        
        # Connect click event to canvas
        self.canvas.mpl_connect('button_press_event', self.on_canvas_click)
        
        # Get available WiFi adapters
        self.get_wifi_adapters()
        
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
        
        # Click analysis controls
        click_frame = ttk.Frame(control_frame)
        click_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0), sticky=(tk.W, tk.E))
        
        self.click_enabled_var = tk.BooleanVar(value=False)
        click_checkbox = ttk.Checkbutton(click_frame, text="Enable Click Analysis", 
                                        variable=self.click_enabled_var,
                                        command=self.toggle_click_analysis)
        click_checkbox.grid(row=0, column=0, sticky=tk.W)
        
        # Add WiFi adapter dropdown
        ttk.Label(click_frame, text="WiFi Adapter:").grid(row=0, column=1, sticky=tk.W, padx=(20, 5))
        self.adapter_var = tk.StringVar()
        self.adapter_combo = ttk.Combobox(click_frame, textvariable=self.adapter_var, 
                                        width=15, state="readonly")
        self.adapter_combo.grid(row=0, column=2, sticky=tk.W)
        ttk.Button(click_frame, text="Refresh", command=self.get_wifi_adapters,
                  width=8).grid(row=0, column=3, padx=(5, 0))
        
        # Add iperf3 controls
        iperf_frame = ttk.Frame(click_frame)
        iperf_frame.grid(row=1, column=0, columnspan=4, pady=(5, 0), sticky=tk.W)
        
        self.iperf_enabled_var = tk.BooleanVar(value=False)
        iperf_checkbox = ttk.Checkbutton(iperf_frame, text="Include iperf3 Testing", 
                                         variable=self.iperf_enabled_var,
                                         command=self.toggle_iperf_options)
        iperf_checkbox.grid(row=0, column=0, sticky=tk.W)
        
        # iperf server input
        ttk.Label(iperf_frame, text="Server:").grid(row=0, column=1, sticky=tk.W, padx=(20, 5))
        self.iperf_server_var = tk.StringVar()
        self.iperf_server_entry = ttk.Entry(iperf_frame, textvariable=self.iperf_server_var, width=15)
        self.iperf_server_entry.grid(row=0, column=2, sticky=tk.W)
        self.iperf_server_entry.config(state=tk.DISABLED)
        
        # Interval input
        ttk.Label(iperf_frame, text="Interval:").grid(row=0, column=3, sticky=tk.W, padx=(10, 5))
        self.iperf_interval_var = tk.StringVar(value="15")
        self.iperf_interval_entry = ttk.Entry(iperf_frame, textvariable=self.iperf_interval_var, width=5)
        self.iperf_interval_entry.grid(row=0, column=4, sticky=tk.W)
        self.iperf_interval_entry.config(state=tk.DISABLED)
        
        # Duration input
        ttk.Label(iperf_frame, text="Duration:").grid(row=0, column=5, sticky=tk.W, padx=(10, 5))
        self.iperf_duration_var = tk.StringVar(value="3600")
        self.iperf_duration_entry = ttk.Entry(iperf_frame, textvariable=self.iperf_duration_var, width=6)
        self.iperf_duration_entry.grid(row=0, column=6, sticky=tk.W)
        self.iperf_duration_entry.config(state=tk.DISABLED)
        
        ttk.Label(click_frame, text="(Click on heatmap to run WiFi analysis at that location)", 
                 foreground=self.theme_manager.colors['gray_fg']).grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=(2, 0))
        
        # Status bar
        self._create_status_bar(control_frame)
    
    def _create_status_bar(self, parent):
        """Create the status bar"""
        self.status_var = tk.StringVar(value="Ready")
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
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
        selected_type = self.heatmap_type_var.get()
        self.status_var.set(f"Generating {selected_type} heat map...")
        self.root.update()
        
        try:
            if not self.data_processor.has_data():
                # Generate empty heatmap with just background and axis bounds
                self.heatmap_generator.generate_empty_heatmap(
                    self.ax, selected_type, self.background_image
                )
                self.canvas.draw()
                self.status_var.set(f"Empty {selected_type} heat map generated (no data points)")
                return
            
            # Get coordinates and values
            x_coords, y_coords, values = self.data_processor.get_coordinates_and_values(selected_type)
            _, label, colormap = self.data_processor.get_heatmap_data(selected_type)
            
            # Filter out zero values for throughput metrics
            if "throughput" in Config.HEATMAP_TYPES[selected_type].lower():
                valid_indices = values > 0
                if not any(valid_indices):
                    # Generate empty heatmap for this specific metric
                    self.heatmap_generator.generate_empty_heatmap(
                        self.ax, selected_type, self.background_image
                    )
                    self.canvas.draw()
                    self.status_var.set(f"Empty {selected_type} heat map - no {selected_type} data available")
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
            self.status_var.set("Error generating heat map")
            print(f"Error generating heat map: {e}")
    
    def toggle_click_analysis(self):
        """Toggle click analysis mode"""
        self.click_enabled = self.click_enabled_var.get()
        if self.click_enabled:
            self.status_var.set("Click analysis enabled - Click on heatmap to analyze")
            # Change cursor to crosshair when over the plot
            self.canvas.get_tk_widget().configure(cursor="crosshair")
        else:
            self.status_var.set("Click analysis disabled")
            self.canvas.get_tk_widget().configure(cursor="")
    
    def on_canvas_click(self, event):
        """Handle click events on the canvas"""
        if not self.click_enabled or self.analysis_running or not event.inaxes:
            return
        
        # Get click coordinates in data space
        x_click = event.xdata
        y_click = event.ydata
        
        if x_click is None or y_click is None:
            return
        
        # Round coordinates to 1 decimal place
        x_click = round(x_click, 1)
        y_click = round(y_click, 1)
        
        self.status_var.set(f"Running WiFi analysis at coordinates ({x_click}, {y_click})...")
        self.root.update()
        
        # Run WiFi analyzer in background thread
        thread = threading.Thread(target=self.run_wifi_analysis, args=(x_click, y_click))
        thread.daemon = True
        thread.start()
    
    def toggle_iperf_options(self):
        """Toggle iperf3 options based on checkbox state"""
        state = tk.NORMAL if self.iperf_enabled_var.get() else tk.DISABLED
        self.iperf_server_entry.config(state=state)
        self.iperf_interval_entry.config(state=state)
        self.iperf_duration_entry.config(state=state)
    
    def run_wifi_analysis(self, x: float, y: float):
        """Run WiFi analysis at the specified coordinates"""
        self.analysis_running = True
        
        try:
            # Get the path to the WiFi analyzer script
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            analyzer_script = os.path.join(script_dir, "wifianalizer", "wifi_analyzer.py")
            
            if not os.path.exists(analyzer_script):
                self.root.after(0, lambda: self.status_var.set("Error: WiFi analyzer script not found"))
                return
            
            # Get selected WiFi adapter
            adapter = self.adapter_var.get()
            
            # Prepare command
            cmd = [
                sys.executable,  # Use current Python interpreter
                analyzer_script,
                "--once",  # Run analysis once
                "--x", str(x),
                "--y", str(y)
            ]
            
            # Add interface parameter if an adapter is selected
            if adapter:
                cmd.extend(["--interface", adapter])
            
            # Add iperf parameters if enabled
            if self.iperf_enabled_var.get():
                iperf_server = self.iperf_server_var.get().strip()
                if iperf_server:
                    cmd.extend(["--iperf-server", iperf_server])
                    
                    # Add interval and duration if they're valid numbers
                    try:
                        interval = int(self.iperf_interval_var.get())
                        cmd.extend(["--interval", str(interval)])
                    except ValueError:
                        pass
                        
                    try:
                        duration = int(self.iperf_duration_var.get())
                        cmd.extend(["--duration", str(duration)])
                    except ValueError:
                        pass
            
            # Add output file in the JSON folder if one is selected
            if self.data_processor.json_folder:
                timestamp = self.get_timestamp()
                output_file = os.path.join(self.data_processor.json_folder, f"analysis_{timestamp}_{x}_{y}.json")
                cmd.extend(["--output", output_file])
            
            # Run the analyzer
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Analysis successful
                analysis_desc = f"Analysis completed at ({x}, {y}) using {adapter}"
                if self.iperf_enabled_var.get() and self.iperf_server_var.get().strip():
                    analysis_desc += f" with iperf testing"
                self.root.after(0, lambda: self.status_var.set(analysis_desc))
                
                # If we have a JSON folder, reload the data
                if self.data_processor.json_folder:
                    self.root.after(100, self.reload_data)
            else:
                error_msg = result.stderr or "Unknown error"
                self.root.after(0, lambda: self.status_var.set(f"Analysis failed: {error_msg[:50]}..."))
                print(f"WiFi analysis error: {error_msg}")
        
        except subprocess.TimeoutExpired:
            self.root.after(0, lambda: self.status_var.set("Analysis timed out"))
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error running analysis: {str(e)[:30]}..."))
            print(f"Error running WiFi analysis: {e}")
        
        finally:
            self.analysis_running = False
    
    def get_wifi_adapters(self):
        """Get available WiFi adapters based on OS"""
        try:
            self.status_var.set("Getting available WiFi adapters...")
            self.root.update()
            
            os_type = platform.system().lower()
            adapters = []
            
            if os_type == "windows":
                # Get Windows WiFi adapters
                output = subprocess.check_output(
                    ["netsh", "wlan", "show", "interfaces"], 
                    text=True, shell=True
                )
                if "Name" in output:
                    for line in output.split('\n'):
                        if "Name" in line and ":" in line:
                            adapter = line.split(':', 1)[1].strip()
                            adapters.append(adapter)
                
                # If no WiFi adapters found, add default
                if not adapters:
                    adapters = ["Wi-Fi"]
            
            elif os_type == "darwin":  # macOS
                # Common macOS WiFi adapter names
                adapters = ["en0", "en1"]
            
            elif os_type == "linux":
                # Get Linux WiFi adapters
                try:
                    output = subprocess.check_output(
                        ["iwconfig"], text=True
                    )
                    for line in output.split('\n'):
                        if "IEEE 802.11" in line:
                            adapter = line.split()[0]
                            adapters.append(adapter)
                except:
                    # Fallback to common adapter names
                    adapters = ["wlan0", "wlan1"]
            
            # Update the combobox
            self.adapter_combo['values'] = adapters
            if adapters:
                self.adapter_combo.current(0)
            
            self.status_var.set(f"Found {len(adapters)} WiFi adapters")
        except Exception as e:
            print(f"Error getting WiFi adapters: {e}")
            self.adapter_combo['values'] = ["wlan0", "Wi-Fi", "en0"]  # Default values
            self.adapter_combo.current(0)
            self.status_var.set("Could not detect WiFi adapters, using defaults")
    
    def get_timestamp(self):
        """Get current timestamp for filename"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def reload_data(self):
        """Reload data from the JSON folder"""
        if self.data_processor.json_folder:
            self.data_processor.load_json_data(self.data_processor.json_folder)
            self.update_data_summary()
            
            # Regenerate current heatmap if we have data
            if self.data_processor.has_data():
                selected_type = self.heatmap_type_var.get()
                self.status_var.set(f"Data reloaded - Regenerating {selected_type} heatmap...")
                self.root.after(100, self.generate_heatmap)
