# HeatMapHero

![WiFi Network Analyzer](Assets/Gemini_Generated_Image_strvptstrvptstrv.png)

A cross-platform Python script for comprehensive WiFi network analysis and monitoring.

## Features

- **Cross-platform support**: Windows, macOS, Linux
- **WiFi Metrics**: RSSI/Signal strength, SSID, BSSID, Channel, PHY rates
- **Network Performance**: Latency, jitter, packet loss, throughput
- **Continuous Monitoring**: Configurable intervals and duration
- **JSON Output**: Structured data export for further analysis

## Installation

### System Dependencies

**Windows:**
- Download iperf3 from https://iperf.fr/iperf-download.php
- Add iperf3 to your PATH

**macOS:**
```bash
brew install iperf3
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install iw iperf3
```

**Linux (RHEL/CentOS):**
```bash
sudo yum install iw iperf3
```

## Usage

### Basic Usage

```bash
# Single analysis
python wifi_analyzer.py --once

# Continuous monitoring (30-second intervals)
python wifi_analyzer.py

# Custom interval (60 seconds)
python wifi_analyzer.py --interval 60

# Monitor for 10 minutes
python wifi_analyzer.py --duration 600
```

### Advanced Options

```bash
# Specify WiFi interface
python wifi_analyzer.py --interface wlan0

# Include throughput testing
python wifi_analyzer.py --iperf-server 192.168.1.100

# Custom output file
python wifi_analyzer.py --once --output my_analysis.json

# Full example
python wifi_analyzer.py --interface en0 --iperf-server 192.168.1.1 --interval 15 --duration 3600 --output hourly_monitor.json
```

## Command Line Options

- `--interface, -i`: WiFi interface name (auto-detected if not specified)
- `--iperf-server, -s`: iperf3 server IP address for throughput testing
- `--interval, -t`: Monitoring interval in seconds (default: 30)
- `--duration, -d`: Total monitoring duration in seconds
- `--once`: Run single analysis and exit
- `--output, -o`: Output JSON filename

## Output Data Structure

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "os": "darwin",
  "interface": "en0",
  "wifi_info": {
    "ssid": "MyNetwork",
    "bssid": "00:11:22:33:44:55",
    "rssi": -45,
    "channel": "6",
    "tx_rate": "866.7 Mbps"
  },
  "gateway_ip": "192.168.1.1",
  "latency": {
    "avg_latency_ms": 2.5,
    "packet_loss_percent": 0,
    "jitter_ms": 0.8
  },
  "throughput": {
    "tcp_throughput_mbps": 450.2,
    "udp_throughput_mbps": 425.8
  }
}
```

## Troubleshooting

### Common Issues

1. **Permission denied**: Run with appropriate privileges (sudo on Linux/macOS)
2. **Interface not found**: Specify correct interface with `--interface`
3. **iperf3 not found**: Install iperf3 and ensure it's in PATH
4. **No WiFi connection**: Ensure device is connected to WiFi network

### Platform-Specific Notes

**Windows:**
- May require running as Administrator for some operations
- Default interface name is "Wi-Fi"

**macOS:**
- Airport command path may vary between versions
- Default interface is usually "en0"

**Linux:**
- Requires iw package for WiFi information
- Default interface is usually "wlan0"

## License

This script is provided as-is for network analysis purposes.
