"""
Heat map generation module
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from typing import Tuple, Optional
from PIL import Image
from .config import Config

class HeatMapGenerator:
    """Generates heat maps from WiFi data"""
    
    def __init__(self, theme_manager=None):
        self.theme_manager = theme_manager
        self.current_colorbar = None
    
    def generate_heatmap(self, ax, x_coords: np.ndarray, y_coords: np.ndarray, 
                        values: np.ndarray, label: str, colormap: str, 
                        background_image: Optional[Image.Image] = None) -> None:
        """Generate and display heat map on the given axes"""
        
        # Clear previous plot and colorbar
        ax.clear()
        if self.current_colorbar:
            try:
                if hasattr(self.current_colorbar, 'remove'):
                    self.current_colorbar.remove()
                elif hasattr(self.current_colorbar, 'ax') and self.current_colorbar.ax:
                    self.current_colorbar.ax.remove()
            except (AttributeError, ValueError):
                pass  # Ignore errors if colorbar is already removed or invalid
            finally:
                self.current_colorbar = None
            
        if self.theme_manager:
            self.theme_manager.configure_plot_theme(ax.figure, ax)
        
        # Handle single point case
        if len(values) == 1:
            self._plot_single_point(ax, x_coords[0], y_coords[0], values[0], 
                                   label, colormap, background_image)
            return
        
        # Remove duplicates
        x_coords, y_coords, values = self._remove_duplicates(x_coords, y_coords, values)
        
        # Calculate bounds with padding
        x_min, x_max, y_min, y_max = self._calculate_bounds(x_coords, y_coords)
        
        # Create interpolation grid
        grid_x, grid_y = np.mgrid[x_min:x_max:Config.INTERPOLATION_GRID_SIZE*1j, 
                                  y_min:y_max:Config.INTERPOLATION_GRID_SIZE*1j]
        
        # Interpolate values
        grid_values = self._interpolate_with_fallback(x_coords, y_coords, values, grid_x, grid_y)
        
        # Display background image if available
        if background_image:
            img_array = np.array(background_image)
            ax.imshow(img_array, extent=[x_min, x_max, y_min, y_max], 
                     alpha=1, aspect='auto')
        
        # Create heat map
        heatmap = ax.imshow(grid_values.T, extent=[x_min, x_max, y_min, y_max],
                           alpha=0.5, cmap=colormap, aspect='auto', origin='lower')
        
        # Add colorbar
        # try:
        #     self.current_colorbar = plt.colorbar(heatmap, ax=ax)
        #     self.current_colorbar.set_label(label, rotation=270, labelpad=20)
            
        #     if self.theme_manager:
        #         self.current_colorbar.set_label(label, rotation=270, labelpad=20, 
        #                       color=self.theme_manager.colors['dark_fg'])
        #         self.current_colorbar.ax.tick_params(colors=self.theme_manager.colors['dark_fg'])
        # except Exception as e:
        #     print(f"Warning: Could not create colorbar: {e}")
        #     self.current_colorbar = None
        
        # Plot data points
        edge_color = 'white' if self.theme_manager else 'black'
        ax.scatter(x_coords, y_coords, c=values, cmap=colormap, 
                  s=Config.SCATTER_POINT_SIZE, edgecolors=edge_color, 
                  linewidth=1.5, alpha=0.9)
        
        # Add labels for data points
        self._add_point_labels(ax, x_coords, y_coords, values, label)
        
        # Set labels and title
        title_color = self.theme_manager.colors['dark_fg'] if self.theme_manager else 'black'
        ax.set_title(f'{label.split(" (")[0]} Heat Map ({len(values)} points)', color=title_color)
        
        # Hide x and y axis
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
    
    def generate_empty_heatmap(self, ax, heatmap_type: str, 
                              background_image: Optional[Image.Image] = None) -> None:
        """Generate an empty heatmap with just background and axis setup"""
        
        # Clear previous plot and colorbar
        ax.clear()
        if self.current_colorbar:
            try:
                if hasattr(self.current_colorbar, 'remove'):
                    self.current_colorbar.remove()
                elif hasattr(self.current_colorbar, 'ax') and self.current_colorbar.ax:
                    self.current_colorbar.ax.remove()
            except (AttributeError, ValueError):
                pass
            finally:
                self.current_colorbar = None
                
        if self.theme_manager:
            self.theme_manager.configure_plot_theme(ax.figure, ax)
        
        # Always use full axis range
        x_min, x_max = 0, 200
        y_min, y_max = 0, 100
        
        # Display background image if available
        if background_image:
            img_array = np.array(background_image)
            ax.imshow(img_array, extent=[x_min, x_max, y_min, y_max], 
                     alpha=0.8, aspect='auto')
        
        # Set bounds to full axis range
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        
        # Set title
        title_color = self.theme_manager.colors['dark_fg'] if self.theme_manager else 'black'
        ax.set_title(f'{heatmap_type} Heat Map (No Data)', color=title_color)
        
        # Hide x and y axis
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
    
    def _remove_duplicates(self, x_coords: np.ndarray, y_coords: np.ndarray, 
                          values: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Remove duplicate coordinates and average their values"""
        unique_coords = {}
        filtered_x, filtered_y, filtered_values = [], [], []
        
        for x, y, val in zip(x_coords, y_coords, values):
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
        
        return np.array(filtered_x), np.array(filtered_y), np.array(filtered_values)
    
    def _calculate_bounds(self, x_coords: np.ndarray, y_coords: np.ndarray) -> Tuple[float, float, float, float]:
        """Calculate bounds with padding, enforcing maximum axis limits"""
        # Always use full axis range regardless of data point locations
        x_min, x_max = 0, 200
        y_min, y_max = 0, 100
        
        return x_min, x_max, y_min, y_max
    
    def _interpolate_with_fallback(self, x_coords: np.ndarray, y_coords: np.ndarray, 
                                  values: np.ndarray, grid_x: np.ndarray, 
                                  grid_y: np.ndarray) -> np.ndarray:
        """Try interpolation with fallback methods"""
        for method in Config.INTERPOLATION_METHODS:
            try:
                # Special handling for cases with few points
                if len(values) < 4 and method == 'cubic':
                    continue  # Skip cubic for less than 4 points
                
                grid_values = griddata((x_coords, y_coords), values,
                                     (grid_x, grid_y), method=method, 
                                     fill_value=np.mean(values))
                
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
        return self._create_simple_interpolation(x_coords, y_coords, values, grid_x, grid_y)
    
    def _create_simple_interpolation(self, x_coords: np.ndarray, y_coords: np.ndarray, 
                                   values: np.ndarray, grid_x: np.ndarray, 
                                   grid_y: np.ndarray) -> np.ndarray:
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
    
    def _add_point_labels(self, ax, x_coords: np.ndarray, y_coords: np.ndarray, 
                         values: np.ndarray, label: str) -> None:
        """Add labels for data points"""
        if len(x_coords) <= Config.MAX_POINTS_FOR_LABELS:
            for x, y, val in zip(x_coords, y_coords, values):
                format_str = f'{val:.0f}' if "throughput" in label.lower() else f'{val:.1f}'
                
                style = self.theme_manager.get_annotation_style() if self.theme_manager else {
                    'bbox': dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                    'color': 'black'
                }
                
                ax.annotate(format_str, (x, y), xytext=(5, 5), 
                           textcoords='offset points', fontsize=9, fontweight='bold',
                           **style)
    
    def _plot_single_point(self, ax, x: float, y: float, value: float, 
                          label: str, colormap: str, background_image: Optional[Image.Image]) -> None:
        """Handle plotting when only one data point is available"""
        # Always use full axis range
        x_min, x_max = 0, 200
        y_min, y_max = 0, 100
        
        # Display background image if available
        if background_image:
            img_array = np.array(background_image)
            ax.imshow(img_array, extent=[x_min, x_max, y_min, y_max], 
                     alpha=0.3, aspect='auto')
        
        # Plot the single point
        edge_color = 'white' if self.theme_manager else 'black'
        ax.scatter([x], [y], c=[value], cmap=colormap, s=Config.SINGLE_POINT_SIZE, 
                  edgecolors=edge_color, linewidth=2, alpha=0.9)
        
        # Add label
        format_str = f'{value:.0f}' if "throughput" in label.lower() else f'{value:.1f}'
        
        style = self.theme_manager.get_annotation_style() if self.theme_manager else {
            'bbox': dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
            'color': 'black'
        }
        
        ax.annotate(format_str, (x, y), xytext=(10, 10), 
                   textcoords='offset points', fontsize=12, fontweight='bold',
                   **style)
        
        # Set bounds to full axis range
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        
        title_color = self.theme_manager.colors['dark_fg'] if self.theme_manager else 'black'
        ax.set_title(f'{label} - Single Data Point', color=title_color)
        
        # Hide x and y axis
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
