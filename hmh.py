#!/usr/bin/env python3
"""
HeatMapHero - WiFi Signal Strength Heat Map Generator
Cross-platform GUI application for visualizing WiFi signal strength data
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import glob
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
from scipy.interpolate import griddata
import platform

class HeatMapHero:
    def __init__(self, root):
        self.root = root
        self.root.title("HeatMapHero - WiFi Analysis Heat Map Generator")
        self.root.geometry("1400x900")
        
        # Data storage
        self.background_image = None
        self.background_path = None
        self.wifi_data = []
        self.json_folder = None
        
        # Heat map types
        self.heatmap_types = {
            "RSSI (Signal Strength)": "rssi",
            "Average Latency": "latency",
            "TCP Throughput": "tcp_throughput",
            "UDP Throughput": "udp_throughput",
            "Packet Loss": "packet_loss",
            "Jitter": "jitter"
        }
        
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
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Background image controls
        ttk.Label(control_frame, text="Background Image:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.bg_path_var = tk.StringVar(value="No image selected")
        ttk.Label(control_frame, textvariable=self.bg_path_var, foreground="gray").grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        ttk.Button(control_frame, text="Load Background", command=self.load_background).grid(row=0, column=2, padx=(0, 10))
        
        # JSON folder controls
        ttk.Label(control_frame, text="JSON Folder:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.folder_path_var = tk.StringVar(value="No folder selected")
        ttk.Label(control_frame, textvariable=self.folder_path_var, foreground="gray").grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        ttk.Button(control_frame, text="Select Folder", command=self.select_json_folder).grid(row=1, column=2, padx=(0, 10), pady=(10, 0))
        
        # Heat map type selection
        ttk.Label(control_frame, text="Heat Map Type:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.heatmap_type_var = tk.StringVar(value="RSSI (Signal Strength)")
        heatmap_combo = ttk.Combobox(control_frame, textvariable=self.heatmap_type_var, 
                                   values=list(self.heatmap_types.keys()), state="readonly", width=25)
        heatmap_combo.grid(row=2, column=1, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        # Generate button
        ttk.Button(control_frame, text="Generate Heat Map", command=self.generate_heatmap, 
                  style="Accent.TButton").grid(row=3, column=0, columnspan=3, pady=(20, 0))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_frame = ttk.Frame(control_frame)
        status_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        ttk.Label(status_frame, textvariable=self.status_var, foreground="blue").pack(side=tk.LEFT, padx=(5, 0))
        
        # Data info frame
        info_frame = ttk.LabelFrame(main_frame, text="Data Information", padding="10")
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(1, weight=1)
        
        # Data summary
        self.data_summary = tk.Text(info_frame, height=15, width=35)
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.data_summary.yview)
        self.data_summary.configure(yscrollcommand=scrollbar.set)
        self.data_summary.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Heat map display frame
        self.plot_frame = ttk.LabelFrame(main_frame, text="Heat Map", padding="5")
        self.plot_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.plot_frame.columnconfigure(0, weight=1)
        self.plot_frame.rowconfigure(0, weight=1)
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(10, 7))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initialize with empty plot
        self.ax.set_title("WiFi Analysis Heat Map")
        self.ax.set_xlabel("X Coordinate")
        self.ax.set_ylabel("Y Coordinate")
        self.canvas.draw()
        
    def load_background(self):
        """Load background image"""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Background Image",
            filetypes=filetypes
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
            self.json_folder = folder
            self.folder_path_var.set(os.path.basename(folder))
            self.load_json_data()
            self.status_var.set("JSON data loaded successfully")
            self.update_data_summary()
    
    def load_json_data(self):
        """Load WiFi data from JSON files"""
        self.wifi_data = []
        
        if not self.json_folder:
            return
        
        json_files = glob.glob(os.path.join(self.json_folder, "*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                # Handle both single analysis and multiple results
                if isinstance(data, list):
                    for item in data:
                        self.extract_wifi_data(item)
                else:
                    self.extract_wifi_data(data)
                    
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
    
    def extract_wifi_data(self, data):
        """Extract relevant WiFi data from JSON structure"""
        try:
            coordinates = data.get('coordinates', {})
            x = coordinates.get('x')
            y = coordinates.get('y')
            
            if x is None or y is None:
                return
            
            # Get WiFi info
            wifi_info = data.get('wifi_info', {})
            latency_info = data.get('latency', {})
            throughput_info = data.get('throughput', {})
            
            # Extract all relevant metrics
            rssi = wifi_info.get('rssi')
            if rssi is None:
                return  # Skip if no RSSI data
            
            # Store comprehensive data point
            data_point = {
                'x': float(x),
                'y': float(y),
                'rssi': float(rssi),
                'ssid': wifi_info.get('ssid', 'Unknown'),
                'frequency': wifi_info.get('frequency', 'N/A'),
                'tx_rate': wifi_info.get('tx_rate', 'N/A'),
                'timestamp': data.get('timestamp', 'Unknown'),
                
                # Latency metrics
                'avg_latency_ms': latency_info.get('avg_latency_ms', 0),
                'packet_loss_percent': latency_info.get('packet_loss_percent', 0),
                'jitter_ms': latency_info.get('jitter_ms', 0),
                
                # Throughput metrics
                'tcp_throughput_mbps': throughput_info.get('tcp_throughput_mbps', 0),
                'udp_throughput_mbps': throughput_info.get('udp_throughput_mbps', 0),
                'tcp_retransmits': throughput_info.get('tcp_retransmits', 0)
            }
            self.wifi_data.append(data_point)
                
        except Exception as e:
            print(f"Error extracting data: {e}")
    
    def update_data_summary(self):
        """Update the data summary display"""
        self.data_summary.delete(1.0, tk.END)
        
        summary = []
        
        if self.background_path:
            summary.append(f"Background Image:\n{os.path.basename(self.background_path)}")
            if self.background_image:
                summary.append(f"Size: {self.background_image.size[0]}x{self.background_image.size[1]}")
        
        if self.json_folder:
            json_count = len(glob.glob(os.path.join(self.json_folder, "*.json")))
            summary.append(f"\nJSON Files: {json_count}")
        
        if self.wifi_data:
            summary.append(f"Data Points: {len(self.wifi_data)}")
            
            # RSSI statistics
            rssi_values = [d['rssi'] for d in self.wifi_data if d['rssi'] != 0]
            if rssi_values:
                summary.append(f"\nRSSI (dBm):")
                summary.append(f"  Min: {min(rssi_values):.1f}")
                summary.append(f"  Max: {max(rssi_values):.1f}")
                summary.append(f"  Avg: {np.mean(rssi_values):.1f}")
            
            # Latency statistics
            latency_values = [d['avg_latency_ms'] for d in self.wifi_data if d['avg_latency_ms'] > 0]
            if latency_values:
                summary.append(f"\nLatency (ms):")
                summary.append(f"  Min: {min(latency_values):.2f}")
                summary.append(f"  Max: {max(latency_values):.2f}")
                summary.append(f"  Avg: {np.mean(latency_values):.2f}")
            
            # TCP Throughput statistics
            tcp_values = [d['tcp_throughput_mbps'] for d in self.wifi_data if d['tcp_throughput_mbps'] > 0]
            if tcp_values:
                summary.append(f"\nTCP Throughput (Mbps):")
                summary.append(f"  Min: {min(tcp_values):.2f}")
                summary.append(f"  Max: {max(tcp_values):.2f}")
                summary.append(f"  Avg: {np.mean(tcp_values):.2f}")
            
            # UDP Throughput statistics
            udp_values = [d['udp_throughput_mbps'] for d in self.wifi_data if d['udp_throughput_mbps'] > 0]
            if udp_values:
                summary.append(f"\nUDP Throughput (Mbps):")
                summary.append(f"  Min: {min(udp_values):.2f}")
                summary.append(f"  Max: {max(udp_values):.2f}")
                summary.append(f"  Avg: {np.mean(udp_values):.2f}")
            
            # Coordinate ranges
            x_coords = [d['x'] for d in self.wifi_data]
            y_coords = [d['y'] for d in self.wifi_data]
            summary.append(f"\nCoordinate Ranges:")
            summary.append(f"  X: {min(x_coords):.1f} to {max(x_coords):.1f}")
            summary.append(f"  Y: {min(y_coords):.1f} to {max(y_coords):.1f}")
            
            # SSIDs and frequencies
            ssids = list(set(d['ssid'] for d in self.wifi_data))
            frequencies = list(set(d['frequency'] for d in self.wifi_data if d['frequency'] != 'N/A'))
            summary.append(f"\nSSIDs: {', '.join(ssids[:2])}")
            if len(ssids) > 2:
                summary.append(f"  ... and {len(ssids)-2} more")
            if frequencies:
                summary.append(f"Frequencies: {', '.join(frequencies)} MHz")
        
        self.data_summary.insert(1.0, '\n'.join(summary))
    
    def get_heatmap_data(self, heatmap_type):
        """Get data values based on selected heat map type"""
        data_key = self.heatmap_types[heatmap_type]
        
        if data_key == "rssi":
            return [d['rssi'] for d in self.wifi_data], "RSSI (dBm)", 'RdYlGn'
        elif data_key == "latency":
            return [d['avg_latency_ms'] for d in self.wifi_data], "Average Latency (ms)", 'RdYlBu_r'
        elif data_key == "tcp_throughput":
            return [d['tcp_throughput_mbps'] for d in self.wifi_data], "TCP Throughput (Mbps)", 'viridis'
        elif data_key == "udp_throughput":
            return [d['udp_throughput_mbps'] for d in self.wifi_data], "UDP Throughput (Mbps)", 'plasma'
        elif data_key == "packet_loss":
            return [d['packet_loss_percent'] for d in self.wifi_data], "Packet Loss (%)", 'Reds'
        elif data_key == "jitter":
            return [d['jitter_ms'] for d in self.wifi_data], "Jitter (ms)", 'YlOrRd'
        else:
            return [d['rssi'] for d in self.wifi_data], "RSSI (dBm)", 'RdYlGn'
    
    def generate_heatmap(self):
        """Generate and display the heat map"""
        if not self.wifi_data:
            messagebox.showwarning("Warning", "No WiFi data available. Please select a folder with JSON files.")
            return
        
        selected_type = self.heatmap_type_var.get()
        self.status_var.set(f"Generating {selected_type} heat map...")
        self.root.update()
        
        try:
            # Clear previous plot
            self.ax.clear()
            
            # Extract coordinates and selected metric values
            x_coords = np.array([d['x'] for d in self.wifi_data])
            y_coords = np.array([d['y'] for d in self.wifi_data])
            values, label, colormap = self.get_heatmap_data(selected_type)
            values = np.array(values)
            
            # Filter out zero values for throughput metrics
            if "throughput" in self.heatmap_types[selected_type].lower():
                valid_indices = values > 0
                if not any(valid_indices):
                    messagebox.showwarning("Warning", f"No {selected_type} data available in the selected files.")
                    return
                x_coords = x_coords[valid_indices]
                y_coords = y_coords[valid_indices]
                values = values[valid_indices]
            
            # Handle single point case
            if len(values) == 1:
                self.plot_single_point(x_coords[0], y_coords[0], values[0], label, colormap)
                return
            
            # Check for duplicate coordinates and remove them
            unique_coords = {}
            filtered_x, filtered_y, filtered_values = [], [], []
            
            for i, (x, y, val) in enumerate(zip(x_coords, y_coords, values)):
                coord_key = (round(x, 6), round(y, 6))  # Round to avoid floating point issues
                if coord_key not in unique_coords:
                    unique_coords[coord_key] = val
                    filtered_x.append(x)
                    filtered_y.append(y)
                    filtered_values.append(val)
                else:
                    # Average values for duplicate coordinates
                    idx = list(unique_coords.keys()).index(coord_key)
                    filtered_values[idx] = (filtered_values[idx] + val) / 2
            
            x_coords = np.array(filtered_x)
            y_coords = np.array(filtered_y)
            values = np.array(filtered_values)
            
            # Create grid for interpolation
            x_min, x_max = x_coords.min(), x_coords.max()
            y_min, y_max = y_coords.min(), y_coords.max()
            
            # Add padding
            x_range = max(x_max - x_min, 1)  # Minimum range of 1
            y_range = max(y_max - y_min, 1)
            padding = 0.2
            
            x_min -= x_range * padding
            x_max += x_range * padding
            y_min -= y_range * padding
            y_max += y_range * padding
            
            # Create interpolation grid
            grid_x, grid_y = np.mgrid[x_min:x_max:100j, y_min:y_max:100j]
            
            # Try interpolation with fallback methods
            grid_values = self.interpolate_with_fallback(
                x_coords, y_coords, values, grid_x, grid_y
            )
            
            # Display background image if available
            if self.background_image:
                img_array = np.array(self.background_image)
                self.ax.imshow(img_array, extent=[x_min, x_max, y_min, y_max], alpha=0.3, aspect='auto')
            
            # Create heat map
            heatmap = self.ax.imshow(
                grid_values.T, extent=[x_min, x_max, y_min, y_max],
                alpha=0.7, cmap=colormap, aspect='auto', origin='lower'
            )
            
            # Add colorbar
            cbar = plt.colorbar(heatmap, ax=self.ax)
            cbar.set_label(label, rotation=270, labelpad=20)
            
            # Plot data points
            scatter = self.ax.scatter(x_coords, y_coords, c=values, cmap=colormap, 
                                    s=100, edgecolors='black', linewidth=1.5, alpha=0.9)
            
            # Add labels for data points
            for i, (x, y, val) in enumerate(zip(x_coords, y_coords, values)):
                if len(x_coords) <= 10:  # Show all labels if few points
                    format_str = f'{val:.0f}' if "throughput" in label.lower() else f'{val:.1f}'
                    self.ax.annotate(format_str, 
                                   (x, y), 
                                   xytext=(5, 5), textcoords='offset points',
                                   fontsize=9, fontweight='bold', alpha=0.9,
                                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7))
            
            # Set labels and title
            self.ax.set_xlabel('X Coordinate')
            self.ax.set_ylabel('Y Coordinate')
            self.ax.set_title(f'{selected_type} Heat Map ({len(values)} points)')
            
            # Add grid
            self.ax.grid(True, alpha=0.3)
            
            # Update canvas
            self.canvas.draw()
            
            self.status_var.set(f"{selected_type} heat map generated with {len(values)} data points")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate heat map: {str(e)}")
            self.status_var.set("Error generating heat map")

    def interpolate_with_fallback(self, x_coords, y_coords, values, grid_x, grid_y):
        """Try interpolation with fallback methods to avoid QHull errors"""
        methods = ['cubic', 'linear', 'nearest']
        
        for method in methods:
            try:
                # Special handling for cases with few points
                if len(values) < 4 and method == 'cubic':
                    continue  # Skip cubic for less than 4 points
                
                grid_values = griddata(
                    (x_coords, y_coords), values,
                    (grid_x, grid_y), method=method, fill_value=np.mean(values)
                )
                
                # Check if interpolation was successful
                if not np.isnan(grid_values).all():
                    if method != 'cubic':
                        print(f"Using {method} interpolation due to QHull issues")
                    return grid_values
                    
            except Exception as e:
                print(f"Interpolation method '{method}' failed: {e}")
                continue
        
        # Final fallback: create simple radial basis function
        print("All interpolation methods failed, using simple averaging")
        return self.create_simple_interpolation(x_coords, y_coords, values, grid_x, grid_y)
    
    def create_simple_interpolation(self, x_coords, y_coords, values, grid_x, grid_y):
        """Create a simple distance-weighted interpolation as final fallback"""
        grid_values = np.zeros_like(grid_x)
        
        for i in range(grid_x.shape[0]):
            for j in range(grid_x.shape[1]):
                # Calculate distances to all data points
                distances = np.sqrt((grid_x[i,j] - x_coords)**2 + (grid_y[i,j] - y_coords)**2)
                
                # Avoid division by zero
                distances = np.maximum(distances, 1e-10)
                
                # Use inverse distance weighting
                weights = 1.0 / distances**2
                grid_values[i,j] = np.sum(weights * values) / np.sum(weights)
        
        return grid_values
    
    def plot_single_point(self, x, y, value, label, colormap):
        """Handle plotting when only one data point is available"""
        # Create a simple plot with the single point
        if self.background_image:
            img_array = np.array(self.background_image)
            # Use image bounds or create reasonable bounds around the point
            x_min, x_max = x - 5, x + 5
            y_min, y_max = y - 5, y + 5
            self.ax.imshow(img_array, extent=[x_min, x_max, y_min, y_max], alpha=0.3, aspect='auto')
        else:
            x_min, x_max = x - 5, x + 5
            y_min, y_max = y - 5, y + 5
        
        # Plot the single point
        self.ax.scatter([x], [y], c=[value], cmap=colormap, s=200, 
                       edgecolors='black', linewidth=2, alpha=0.9)
        
        # Add label
        format_str = f'{value:.0f}' if "throughput" in label.lower() else f'{value:.1f}'
        self.ax.annotate(format_str, (x, y), xytext=(10, 10), 
                        textcoords='offset points', fontsize=12, fontweight='bold',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        
        # Set bounds and labels
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        self.ax.set_xlabel('X Coordinate')
        self.ax.set_ylabel('Y Coordinate')
        self.ax.set_title(f'{label} - Single Data Point')
        self.ax.grid(True, alpha=0.3)
        
        # Update canvas
        self.canvas.draw()
        
        self.status_var.set(f"Single point plot generated: {format_str} {label}")

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
