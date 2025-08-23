#!/usr/bin/env python3
"""
Example usage patterns for WiFi Analyzer
"""

from wifi_analyzer import WiFiAnalyzer
import time

def example_single_analysis():
    """Example: Single WiFi analysis"""
    print("=== Single Analysis Example ===")
    
    analyzer = WiFiAnalyzer()
    result = analyzer.analyze_once()
    
    # Print key metrics
    wifi = result.get('wifi_info', {})
    print(f"Connected to: {wifi.get('ssid', 'Unknown')}")
    print(f"Signal strength: {wifi.get('rssi', wifi.get('signal', 'Unknown'))}")
    
    # Save results
    analyzer.results.append(result)
    analyzer.save_results("single_analysis.json")

def example_custom_monitoring():
    """Example: Custom monitoring with specific parameters"""
    print("=== Custom Monitoring Example ===")
    
    # Create analyzer with specific interface and iperf server
    analyzer = WiFiAnalyzer(
        interface="wlan0",  # Adjust for your system
        iperf_server="192.168.1.100"  # Replace with your server
    )
    
    # Monitor for 5 minutes with 10-second intervals
    try:
        start_time = time.time()
        iteration = 1
        
        while (time.time() - start_time) < 300:  # 5 minutes
            print(f"\nIteration {iteration}")
            result = analyzer.analyze_once()
            analyzer.results.append(result)
            
            # Print summary
            wifi = result.get('wifi_info', {})
            latency = result.get('latency', {})
            throughput = result.get('throughput', {})
            
            print(f"SSID: {wifi.get('ssid', 'N/A')}")
            print(f"RSSI: {wifi.get('rssi', wifi.get('signal', 'N/A'))}")
            if latency:
                print(f"Latency: {latency.get('avg_latency_ms', 'N/A')} ms")
            if throughput:
                print(f"TCP Throughput: {throughput.get('tcp_throughput_mbps', 'N/A')} Mbps")
            
            iteration += 1
            time.sleep(10)  # 10-second intervals
            
    except KeyboardInterrupt:
        print("Monitoring stopped")
    
    # Save all results
    analyzer.save_results("custom_monitoring.json")

def example_batch_analysis():
    """Example: Analyze multiple times and calculate averages"""
    print("=== Batch Analysis Example ===")
    
    analyzer = WiFiAnalyzer()
    
    # Collect 5 samples with 5-second intervals
    samples = 5
    for i in range(samples):
        print(f"Sample {i+1}/{samples}")
        result = analyzer.analyze_once()
        analyzer.results.append(result)
        
        if i < samples - 1:  # Don't sleep after last sample
            time.sleep(5)
    
    # Calculate averages
    if analyzer.results:
        rssi_values = []
        latency_values = []
        
        for result in analyzer.results:
            wifi = result.get('wifi_info', {})
            latency = result.get('latency', {})
            
            # Collect RSSI values
            rssi = wifi.get('rssi', wifi.get('signal'))
            if rssi and str(rssi).replace('-', '').isdigit():
                rssi_values.append(int(rssi))
            
            # Collect latency values
            if latency.get('avg_latency_ms'):
                latency_values.append(latency['avg_latency_ms'])
        
        # Print averages
        if rssi_values:
            avg_rssi = sum(rssi_values) / len(rssi_values)
            print(f"Average RSSI: {avg_rssi:.1f} dBm")
        
        if latency_values:
            avg_latency = sum(latency_values) / len(latency_values)
            print(f"Average Latency: {avg_latency:.2f} ms")
    
    # Save results
    analyzer.save_results("batch_analysis.json")

if __name__ == "__main__":
    print("WiFi Analyzer Examples")
    print("=====================")
    
    # Run examples
    example_single_analysis()
    print("\n" + "="*50 + "\n")
    
    example_batch_analysis()
    print("\n" + "="*50 + "\n")
    
    # Uncomment to run custom monitoring example
    # example_custom_monitoring()
