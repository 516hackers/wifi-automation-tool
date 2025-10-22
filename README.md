# WiFi Automation Tool for Kali Linux
   
A comprehensive automated WiFi management tool for Kali Linux that handles driver installation, network scanning, and system repair automatically.

## 🚀 Features

- **Automatic WiFi Detection** - Scan and list available networks
- **Driver Management** - Auto-detect hardware and install appropriate drivers
- **Error Recovery** - Comprehensive error handling and automatic fixes
- **System Health Checks** - Diagnose and repair package management issues
- **Offline Support** - Fallback methods when internet is unavailable

## 📥 Installation

### Clone the Repository

```bash
# Clone using HTTPS
git clone https://github.com/516hackers/wifi-automation-tool.git

# Navigate to directory
cd wifi-automation-tool
```

### Quick Setup

```bash
# Make scripts executable and create directories
chmod +x main.py install.sh recovery.sh
mkdir -p logs backups

# Run the automated installer
sudo ./install.sh
```

## 🛠️ Usage

### Basic Usage
```bash
# Full automated WiFi setup
sudo ./main.py
```

### Specific Operations
```bash
# Only scan for networks
sudo ./main.py --scan-only

# Only install drivers
sudo ./main.py --install-drivers

# Fix WiFi errors
sudo ./main.py --fix-errors

# Run system health check
sudo ./main.py --health-check

# Repair system issues
sudo ./main.py --system-repair
```

### Emergency Recovery
```bash
# Use when system has major issues
sudo ./recovery.sh
```

## 📁 Project Structure

```
wifi-automation-tool/
├── main.py                 # Main executable
├── install.sh             # Installation script
├── recovery.sh            # Emergency recovery
├── test_wifi_tool.py      # Testing suite
├── src/                   # Source code
│   ├── wifi_scanner.py    # Network scanning
│   ├── driver_manager.py  # Driver management
│   ├── package_manager.py # APT/dpkg error handling
│   ├── system_health.py   # System diagnostics
│   ├── error_handler.py   # Error recovery
│   └── utils.py           # Utilities
├── config/                # Configuration files
├── drivers/               # Driver database
├── logs/                  # Log files
└── backups/               # System backups
```

## 🔧 What It Fixes Automatically

- **Package Management**: Broken dependencies, lock files, GPG key issues
- **Driver Issues**: Missing WiFi drivers, kernel module problems
- **Network Problems**: Interface issues, service failures
- **System Errors**: Permission problems, disk space issues

## 🐛 Testing

```bash
# Run comprehensive tests
python3 test_wifi_tool.py

# Quick test only
python3 test_wifi_tool.py quick
```

## ⚠️ Requirements

- **Kali Linux** (tested on rolling release)
- **Root privileges** (required for driver installation)
- **Python 3.7+**
- **Basic networking** (for online driver downloads)

## 🆘 Troubleshooting

If you encounter issues:

1. **Run system repair**: `sudo ./main.py --system-repair`
2. **Use emergency recovery**: `sudo ./recovery.sh`
3. **Check logs**: View `logs/wifi_tool.log` for details

## 📝 Notes

- Always run with `sudo` for full functionality
- The tool creates backups before making system changes
- Logs are saved in `logs/` directory for debugging
- Uses multiple fallback methods for maximum reliability

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

---

**Made for Kali Linux enthusiasts by 516hackers** 🔒
