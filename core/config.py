"""
Configuration settings for HeatMapHero
"""

class Config:
    """Application configuration"""
    
    # Application settings
    APP_NAME = "HeatMapHero - WiFi Analysis Heat Map Generator"
    APP_VERSION = "1.0.0"
    WINDOW_SIZE = "1400x900"
    
    # Heat map types
    HEATMAP_TYPES = {
        "RSSI (Signal Strength)": "rssi",
        "Average Latency": "latency",
        "TCP Throughput": "tcp_throughput",
        "UDP Throughput": "udp_throughput",
        "Packet Loss": "packet_loss",
        "Jitter": "jitter"
    }
    
    # File types for image loading
    IMAGE_FILETYPES = [
        ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
        ("PNG files", "*.png"),
        ("JPEG files", "*.jpg *.jpeg"),
        ("All files", "*.*")
    ]
    
    # Interpolation settings
    INTERPOLATION_METHODS = ['cubic', 'linear', 'nearest']
    INTERPOLATION_GRID_SIZE = 100
    INTERPOLATION_PADDING = 0.2
    
    # Plot settings
    MAX_POINTS_FOR_LABELS = 10
    SCATTER_POINT_SIZE = 100
    SINGLE_POINT_SIZE = 200
