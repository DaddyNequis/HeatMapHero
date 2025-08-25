# HeatMapHero - WiFi Analysis Heat Map Generator

A cross-platform desktop application for visualizing WiFi performance data through interactive heat maps. HeatMapHero combines WiFi analysis capabilities with an intuitive GUI for creating professional-quality heat maps overlaid on background images.

![HeatMapHero Screenshot](docs/screenshot.png)

## Features

### 🎯 Core Functionality
- **Interactive Heat Maps**: Generate beautiful heat maps for various WiFi metrics
- **Background Image Support**: Overlay heat maps on floor plans, maps, or any image
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Dark Theme**: Modern dark UI for comfortable viewing
- **Click Analysis**: Run WiFi analysis by clicking directly on the heat map

### 📊 Supported Metrics
- **RSSI (Signal Strength)**: Measure signal quality in dBm
- **Latency**: Network response times and jitter
- **Throughput**: TCP and UDP bandwidth measurements
- **Packet Loss**: Connection reliability metrics
- **Jitter**: Network stability analysis

### 🔧 Technical Features
- Interpolated heat map visualization with multiple methods
- JSON data format for easy integration
- Real-time WiFi analysis using system tools
- Automatic data reloading and visualization updates
- Comprehensive error handling and logging

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Required Dependencies
```bash
pip install -r requirements.txt
```

**Core Dependencies:**
- `tkinter` (usually included with Python)
- `matplotlib` - for plotting and visualization
- `scipy` - for interpolation algorithms
- `numpy` - for numerical computations
- `Pillow` - for image processing

**Optional Dependencies:**
- `iperf3` - for throughput testing (install separately)

### System Requirements

#### Windows
- Windows 10 or later
- Administrative privileges for WiFi analysis

#### macOS
- macOS 10.14 or later
- Airport utility (built-in)

#### Linux
- Modern Linux distribution
- `iw` and `iwconfig` utilities
- `ping` command

## Quick Start

### 1. Launch the Application
```bash
python hmh.py
```

### 2. Load Background Image (Optional)
- Click "Load Background" to select a floor plan or map
- Supported formats: PNG, JPEG, GIF, BMP, TIFF

### 3. Load WiFi Data
- Click "Select Folder" to choose a directory containing JSON analysis files
- Or use the click analysis feature to generate new data points

### 4. Generate Heat Map
- Select desired metric from dropdown
- Click "Generate Heat Map"

## WiFi Analysis Tool

### Manual Analysis
Run standalone WiFi analysis:
```bash
# Single analysis
python wifianalizer/wifi_analyzer.py --once --x 10.5 --y 25.0

# Continuous monitoring
python wifianalizer/wifi_analyzer.py --interval 30 --duration 3600

# With iperf3 server
python wifianalizer/wifi_analyzer.py --iperf-server 192.168.1.100 --once
```

### Click Analysis Mode
1. Enable "Click Analysis" checkbox in the GUI
2. Click anywhere on the heat map
3. WiFi analysis runs automatically at clicked coordinates
4. Data automatically reloads and updates visualization

## Data Format

WiFi analysis data is stored in JSON format:

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "coordinates": {
    "x": 10.5,
    "y": 25.0
  },
  "wifi_info": {
    "ssid": "MyNetwork",
    "bssid": "aa:bb:cc:dd:ee:ff",
    "rssi": -45,
    "channel": "6",
    "tx_rate": "866.7 Mbps"
  },
  "latency": {
    "avg_latency_ms": 15.2,
    "packet_loss_percent": 0.0,
    "jitter_ms": 2.1
  },
  "throughput": {
    "tcp_throughput_mbps": 450.2,
    "udp_throughput_mbps": 380.5
  }
}
```

## Usage Guide

### Heat Map Types

#### RSSI (Signal Strength)
- **Range**: -100 dBm (poor) to -30 dBm (excellent)
- **Color Scale**: Red (weak) to Green (strong)
- **Best For**: Coverage analysis and dead spot identification

#### Latency
- **Units**: Milliseconds (ms)
- **Color Scale**: Blue (low) to Red (high)
- **Best For**: Real-time application performance analysis

#### Throughput
- **Units**: Megabits per second (Mbps)
- **Types**: TCP and UDP measurements
- **Best For**: Bandwidth capacity planning

#### Packet Loss
- **Units**: Percentage (%)
- **Color Scale**: White (no loss) to Red (high loss)
- **Best For**: Connection reliability assessment

### Advanced Features

#### Interpolation Methods
- **Cubic**: Smooth curves, best for dense data
- **Linear**: Balanced approach for most scenarios
- **Nearest**: Sharp boundaries, good for sparse data

#### Coordinate System
- Origin (0,0) at bottom-left
- X-axis: horizontal (left to right)
- Y-axis: vertical (bottom to top)
- Units can be meters, feet, or arbitrary

## Configuration

### Application Settings
Edit `core/config.py` to customize:
- Window size and appearance
- Interpolation parameters
- Plot styling options
- File type associations

### Theme Customization
Modify `gui/theme.py` for:
- Color schemes
- Font preferences
- Plot styling
- UI element appearance

## Troubleshooting

### Common Issues

#### "No WiFi interface found"
- **Windows**: Ensure WiFi adapter is enabled
- **macOS**: Check System Preferences > Network
- **Linux**: Verify `iw` utility is installed

#### "iperf3 command not found"
```bash
# Install iperf3
# Windows: Download from iperf.fr
# macOS: brew install iperf3
# Linux: sudo apt install iperf3
```

#### Interpolation Errors
- Reduce data density or use 'nearest' method
- Ensure coordinates are within reasonable ranges
- Check for duplicate coordinate entries

#### Permission Denied
- Run with administrator/sudo privileges
- Check file permissions for JSON folder
- Verify network interface access rights

### Debug Mode
Enable verbose logging:
```bash
python hmh.py --debug
```

## Development

### Project Structure
```
HeatMapHero/
├── core/                   # Core functionality
│   ├── config.py          # Configuration settings
│   ├── data_processor.py  # Data loading and processing
│   └── heatmap_generator.py # Heat map creation
├── gui/                   # User interface
│   ├── main_window.py     # Main application window
│   └── theme.py           # Theme and styling
├── wifianalizer/          # WiFi analysis tools
│   └── wifi_analyzer.py   # Cross-platform WiFi analyzer
├── hmh.py                 # Main application entry point
└── README.md              # This file
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Testing
```bash
# Run basic functionality test
python -m pytest tests/

# Test WiFi analyzer
python wifianalizer/wifi_analyzer.py --once --x 0 --y 0
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **matplotlib** team for excellent plotting capabilities
- **scipy** team for interpolation algorithms
- **tkinter** community for GUI framework
- WiFi analysis inspiration from various network tools

## Support

### Documentation
- [User Manual](docs/user_manual.md)
- [API Reference](docs/api_reference.md)
- [Examples](examples/)

### Community
- [GitHub Issues](https://github.com/yourusername/HeatMapHero/issues)
- [Discussions](https://github.com/yourusername/HeatMapHero/discussions)

### Version History
- **v1.0.0**: Initial release with core functionality
- **v0.9.0**: Beta release with click analysis
- **v0.8.0**: Alpha release with basic heat maps

---

**HeatMapHero** - Visualizing WiFi Performance, One Heat Map at a Time 🗺️📶
