"""
Data processing module for WiFi analysis data
"""

import json
import glob
import os
import numpy as np
from typing import List, Dict, Any, Tuple

class DataProcessor:
    """Handles loading and processing of WiFi analysis data"""
    
    def __init__(self):
        self.wifi_data = []
        self.json_folder = None
    
    def load_json_data(self, folder_path: str) -> None:
        """Load WiFi data from JSON files in the specified folder"""
        self.wifi_data = []
        self.json_folder = folder_path
        
        if not folder_path:
            return
        
        json_files = glob.glob(os.path.join(folder_path, "*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                # Handle both single analysis and multiple results
                if isinstance(data, list):
                    for item in data:
                        self._extract_wifi_data(item)
                else:
                    self._extract_wifi_data(data)
                    
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
    
    def _extract_wifi_data(self, data: Dict[str, Any]) -> None:
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
    
    def get_data_summary(self) -> str:
        """Generate a summary of the loaded data"""
        summary = []
        
        if self.json_folder:
            json_count = len(glob.glob(os.path.join(self.json_folder, "*.json")))
            summary.append(f"JSON Files: {json_count}")
        
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
        
        return '\n'.join(summary)
    
    def get_heatmap_data(self, heatmap_type: str) -> Tuple[List[float], str, str]:
        """Get data values based on selected heat map type"""
        from .config import Config
        
        data_key = Config.HEATMAP_TYPES.get(heatmap_type, "rssi")
        
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
    
    def get_coordinates_and_values(self, heatmap_type: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Get coordinates and values for the specified heatmap type"""
        x_coords = np.array([d['x'] for d in self.wifi_data])
        y_coords = np.array([d['y'] for d in self.wifi_data])
        values, _, _ = self.get_heatmap_data(heatmap_type)
        return x_coords, y_coords, np.array(values)
    
    def has_data(self) -> bool:
        """Check if any data is loaded"""
        return len(self.wifi_data) > 0
    
    def clear_data(self) -> None:
        """Clear all loaded data"""
        self.wifi_data = []
        self.json_folder = None
