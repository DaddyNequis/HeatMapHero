#!/usr/bin/env python3
"""
Cross-platform WiFi Analysis Script
Analyzes WiFi performance metrics including RSSI, throughput, latency, and more.
"""

import json
import time
import platform
import subprocess
import threading
import argparse
from datetime import datetime
from typing import Dict, Any, Optional
import os
import sys

class WiFiAnalyzer:
    def __init__(self, interface: str = None, iperf_server: str = None, x: float = None, y: float = None):
        self.os_type = platform.system().lower()
        self.interface = interface or self._get_default_interface()
        self.iperf_server = iperf_server
        self.x = x
        self.y = y
        self.results = []
        
    def _get_default_interface(self) -> str:
        """Get default WiFi interface based on OS"""
        if self.os_type == "darwin":  # macOS
            return "en0"
        elif self.os_type == "linux":
            return "wlan0"
        elif self.os_type == "windows":
            return "Wi-Fi"  # Default Windows WiFi adapter name
        return "wlan0"
    
    def get_wifi_info(self) -> Dict[str, Any]:
        """Get WiFi connection information based on OS"""
        try:
            if self.os_type == "darwin":
                return self._get_macos_wifi_info()
            elif self.os_type == "linux":
                return self._get_linux_wifi_info()
            elif self.os_type == "windows":
                return self._get_windows_wifi_info()
            else:
                raise OSError(f"Unsupported OS: {self.os_type}")
        except Exception as e:
            print(f"Error getting WiFi info: {e}")
            return {}
    
    def _get_macos_wifi_info(self) -> Dict[str, Any]:
        """Get WiFi info on macOS using airport command"""
        try:
            # Get airport command path
            airport_path = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
            if not os.path.exists(airport_path):
                airport_path = "airport"  # Try system PATH
            
            result = subprocess.run([airport_path, "-I"], 
                                  capture_output=True, text=True, check=True)
            
            wifi_info = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.strip().split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    wifi_info[key] = value
            
            return {
                'ssid': wifi_info.get('SSID', 'N/A'),
                'bssid': wifi_info.get('BSSID', 'N/A'),
                'rssi': self._safe_int(wifi_info.get('agrCtlRSSI', '0')),
                'channel': wifi_info.get('channel', 'N/A'),
                'cc': wifi_info.get('CC', 'N/A'),
                'phy_mode': wifi_info.get('PHY CC', 'N/A'),
                'tx_rate': wifi_info.get('lastTxRate', 'N/A'),
                'mcs': wifi_info.get('MCS', 'N/A')
            }
        except Exception as e:
            print(f"Error getting macOS WiFi info: {e}")
            return {}
    
    def _get_linux_wifi_info(self) -> Dict[str, Any]:
        """Get WiFi info on Linux using iw command"""
        try:
            result = subprocess.run(['iw', 'dev', self.interface, 'link'], 
                                  capture_output=True, text=True, check=True)
            
            wifi_info = {}
            for line in result.stdout.split('\n'):
                line = line.strip()
                if 'Connected to' in line:
                    wifi_info['bssid'] = line.split()[-1]
                elif 'SSID:' in line:
                    wifi_info['ssid'] = line.split('SSID: ')[1]
                elif 'freq:' in line:
                    wifi_info['frequency'] = line.split('freq: ')[1].split()[0]
                elif 'signal:' in line:
                    wifi_info['rssi'] = line.split('signal: ')[1].split()[0]
                elif 'tx bitrate:' in line:
                    wifi_info['tx_rate'] = line.split('tx bitrate: ')[1]
            
            # Get additional info from iwconfig
            try:
                iwconfig_result = subprocess.run(['iwconfig', self.interface], 
                                               capture_output=True, text=True, check=True)
                # Parse iwconfig output for additional details
            except:
                pass
            
            return {
                'ssid': wifi_info.get('ssid', 'N/A'),
                'bssid': wifi_info.get('bssid', 'N/A'),
                'rssi': self._safe_int(wifi_info.get('rssi', '0')),
                'frequency': wifi_info.get('frequency', 'N/A'),
                'tx_rate': wifi_info.get('tx_rate', 'N/A')
            }
        except Exception as e:
            print(f"Error getting Linux WiFi info: {e}")
            return {}
    
    def _get_windows_wifi_info(self) -> Dict[str, Any]:
        """Get WiFi info on Windows using netsh command"""
        try:
            result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                                  capture_output=True, text=True, check=True, shell=True)
            
            wifi_info = {}
            for line in result.stdout.split('\n'):
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if 'ssid' in key:
                        wifi_info['ssid'] = value
                    elif 'bssid' in key:
                        wifi_info['bssid'] = value
                    elif 'signal' in key:
                        wifi_info['signal'] = value
                    elif 'channel' in key:
                        wifi_info['channel'] = value
                    elif 'receive rate' in key:
                        wifi_info['rx_rate'] = value
                    elif 'transmit rate' in key:
                        wifi_info['tx_rate'] = value
            
            return {
                'ssid': wifi_info.get('ssid', 'N/A'),
                'bssid': wifi_info.get('bssid', 'N/A'),
                'signal': wifi_info.get('signal', 'N/A'),
                'channel': wifi_info.get('channel', 'N/A'),
                'tx_rate': wifi_info.get('tx_rate', 'N/A'),
                'rx_rate': wifi_info.get('rx_rate', 'N/A')
            }
        except Exception as e:
            print(f"Error getting Windows WiFi info: {e}")
            return {}
    
    def _safe_int(self, value: str) -> int:
        """Safely convert string to int"""
        try:
            return int(value)
        except:
            return 0
    
    def get_gateway_ip(self) -> Optional[str]:
        """Get default gateway IP address"""
        try:
            if self.os_type == "windows":
                result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
                for line in result.stdout.split('\n'):
                    if 'Default Gateway' in line and ':' in line:
                        gateway = line.split(':')[1].strip()
                        if gateway and gateway != '':
                            return gateway
            else:
                if self.os_type == "darwin":
                    result = subprocess.run(['route', '-n', 'get', 'default'], 
                                          capture_output=True, text=True)
                    for line in result.stdout.split('\n'):
                        if 'gateway:' in line:
                            return line.split('gateway: ')[1].strip()
                else:  # Linux
                    result = subprocess.run(['ip', 'route', 'show', 'default'], 
                                          capture_output=True, text=True)
                    if result.stdout:
                        return result.stdout.split()[2]
        except Exception as e:
            print(f"Error getting gateway IP: {e}")
        return None
    
    def measure_latency(self, target: str, count: int = 10) -> Dict[str, Any]:
        """Measure ping latency, jitter, and packet loss"""
        try:
            if self.os_type == "windows":
                cmd = ['ping', '-n', str(count), target]
            else:
                cmd = ['ping', '-c', str(count), target]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Parse ping results
            lines = result.stdout.split('\n')
            times = []
            packets_sent = count
            packets_received = 0
            
            for line in lines:
                if 'time=' in line or 'time<' in line:
                    packets_received += 1
                    try:
                        if 'time=' in line:
                            time_str = line.split('time=')[1].split()[0].replace('ms', '')
                            times.append(float(time_str))
                        elif 'time<' in line:
                            times.append(1.0)  # Assume <1ms
                    except:
                        continue
            
            if times:
                avg_latency = sum(times) / len(times)
                min_latency = min(times)
                max_latency = max(times)
                
                # Calculate jitter (standard deviation)
                if len(times) > 1:
                    variance = sum((x - avg_latency) ** 2 for x in times) / (len(times) - 1)
                    jitter = variance ** 0.5
                else:
                    jitter = 0
            else:
                avg_latency = min_latency = max_latency = jitter = 0
            
            packet_loss = ((packets_sent - packets_received) / packets_sent) * 100
            
            return {
                'target': target,
                'packets_sent': packets_sent,
                'packets_received': packets_received,
                'packet_loss_percent': packet_loss,
                'avg_latency_ms': avg_latency,
                'min_latency_ms': min_latency,
                'max_latency_ms': max_latency,
                'jitter_ms': jitter
            }
        except Exception as e:
            print(f"Error measuring latency: {e}")
            return {}
    
    def measure_throughput(self, server: str, duration: int = 10) -> Dict[str, Any]:
        """Measure throughput using iperf3"""
        if not server:
            return {'error': 'No iperf3 server specified'}
        
        results = {}
        
        # Test TCP throughput
        try:
            cmd = ['iperf3', '-c', server, '-t', str(duration), '-J']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 10)
            
            if result.returncode == 0:
                tcp_data = json.loads(result.stdout)
                if 'end' in tcp_data and 'sum_received' in tcp_data['end']:
                    results['tcp_throughput_mbps'] = tcp_data['end']['sum_received']['bits_per_second'] / 1e6
                    results['tcp_retransmits'] = tcp_data['end']['sum_sent'].get('retransmits', 0)
        except Exception as e:
            results['tcp_error'] = str(e)
        
        # Test UDP throughput
        try:
            cmd = ['iperf3', '-c', server, '-u', '-t', str(duration), '-b', '100M', '-J']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 10)
            
            if result.returncode == 0:
                udp_data = json.loads(result.stdout)
                if 'end' in udp_data and 'sum' in udp_data['end']:
                    results['udp_throughput_mbps'] = udp_data['end']['sum']['bits_per_second'] / 1e6
                    results['udp_jitter_ms'] = udp_data['end']['sum'].get('jitter_ms', 0)
                    results['udp_lost_percent'] = udp_data['end']['sum'].get('lost_percent', 0)
        except Exception as e:
            results['udp_error'] = str(e)
        
        return results
    
    def analyze_once(self) -> Dict[str, Any]:
        """Perform a single WiFi analysis"""
        timestamp = datetime.now().isoformat()
        
        print(f"[{timestamp}] Starting WiFi analysis...")
        if self.x is not None and self.y is not None:
            print(f"Location: x={self.x}, y={self.y}")
        
        # Get WiFi information
        wifi_info = self.get_wifi_info()
        
        # Get gateway IP for latency testing
        gateway_ip = self.get_gateway_ip()
        
        # Measure latency to gateway
        latency_info = {}
        if gateway_ip:
            print(f"Measuring latency to gateway: {gateway_ip}")
            latency_info = self.measure_latency(gateway_ip)
        
        # Measure throughput if iperf server is specified
        throughput_info = {}
        if self.iperf_server:
            print(f"Measuring throughput to: {self.iperf_server}")
            throughput_info = self.measure_throughput(self.iperf_server)
        
        # Combine all results
        analysis_result = {
            'timestamp': timestamp,
            'coordinates': {
                'x': self.x,
                'y': self.y
            },
            'os': self.os_type,
            'interface': self.interface,
            'wifi_info': wifi_info,
            'gateway_ip': gateway_ip,
            'latency': latency_info,
            'throughput': throughput_info
        }
        
        return analysis_result
    
    def continuous_monitor(self, interval: int = 30, duration: int = None):
        """Continuously monitor WiFi performance"""
        start_time = time.time()
        iteration = 1
        
        try:
            while True:
                print(f"\n=== Analysis Iteration {iteration} ===")
                
                result = self.analyze_once()
                self.results.append(result)
                
                # Save results to JSON file
                self.save_results()
                
                iteration += 1
                
                # Check if duration limit reached
                if duration and (time.time() - start_time) >= duration:
                    break
                
                print(f"Waiting {interval} seconds until next analysis...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        except Exception as e:
            print(f"Error in continuous monitoring: {e}")
    
    def save_results(self, filename: str = None):
        """Save analysis results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wifi_analysis_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"Results saved to: {filename}")
        except Exception as e:
            print(f"Error saving results: {e}")

def main():
    parser = argparse.ArgumentParser(description="Cross-platform WiFi Network Analyzer")
    parser.add_argument('--interface', '-i', help='WiFi interface name')
    parser.add_argument('--iperf-server', '-s', help='iperf3 server IP for throughput testing')
    parser.add_argument('--x', type=float, help='X coordinate for location tracking')
    parser.add_argument('--y', type=float, help='Y coordinate for location tracking')
    parser.add_argument('--interval', '-t', type=int, default=30, 
                       help='Monitoring interval in seconds (default: 30)')
    parser.add_argument('--duration', '-d', type=int, 
                       help='Total monitoring duration in seconds')
    parser.add_argument('--once', action='store_true', 
                       help='Run analysis once and exit')
    parser.add_argument('--output', '-o', help='Output JSON filename')
    
    args = parser.parse_args()
    
    # Create analyzer instance
    analyzer = WiFiAnalyzer(interface=args.interface, iperf_server=args.iperf_server, x=args.x, y=args.y)
    
    print("WiFi Network Analyzer")
    print("===================")
    print(f"OS: {analyzer.os_type}")
    print(f"Interface: {analyzer.interface}")
    if args.iperf_server:
        print(f"iperf3 server: {args.iperf_server}")
    if args.x is not None and args.y is not None:
        print(f"Coordinates: x={args.x}, y={args.y}")
    print()
    
    if args.once:
        # Single analysis
        result = analyzer.analyze_once()
        analyzer.results.append(result)
        analyzer.save_results(args.output)
        
        # Print summary
        print("\n=== Analysis Summary ===")
        wifi = result.get('wifi_info', {})
        print(f"SSID: {wifi.get('ssid', 'N/A')}")
        print(f"BSSID: {wifi.get('bssid', 'N/A')}")
        print(f"Signal: {wifi.get('rssi', wifi.get('signal', 'N/A'))}")
        
        latency = result.get('latency', {})
        if latency:
            print(f"Avg Latency: {latency.get('avg_latency_ms', 'N/A')} ms")
            print(f"Packet Loss: {latency.get('packet_loss_percent', 'N/A')}%")
        
        throughput = result.get('throughput', {})
        if throughput:
            print(f"TCP Throughput: {throughput.get('tcp_throughput_mbps', 'N/A')} Mbps")
            print(f"UDP Throughput: {throughput.get('udp_throughput_mbps', 'N/A')} Mbps")
    else:
        # Continuous monitoring
        analyzer.continuous_monitor(interval=args.interval, duration=args.duration)
        if args.output:
            analyzer.save_results(args.output)

if __name__ == "__main__":
    main()
