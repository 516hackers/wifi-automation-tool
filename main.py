#!/usr/bin/env python3

import os
import sys
import argparse
import logging
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.wifi_scanner import WiFiScanner
from src.driver_manager import DriverManager
from src.error_handler import ErrorHandler
from src.utils import check_root, setup_logging

class WiFiAutomationTool:
    def __init__(self):
        setup_logging()
        self.logger = logging.getLogger(__name__)
        self.scanner = WiFiScanner()
        self.driver_manager = DriverManager()
        self.error_handler = ErrorHandler()
        
    def run(self):
        """Main execution function"""
        try:
            print("🚀 Starting WiFi Automation Tool...")
            
            # Check if running as root
            if not check_root():
                self.logger.error("This tool requires root privileges. Run with sudo!")
                sys.exit(1)
            
            # Scan for WiFi networks
            networks = self.scanner.scan_networks()
            if networks:
                print(f"📡 Found {len(networks)} WiFi networks")
                for i, network in enumerate(networks, 1):
                    print(f"  {i}. {network}")
            
            # Check and install drivers
            self.driver_manager.install_required_drivers()
            
            # Test WiFi functionality
            self.test_wifi_functionality()
            
            print("✅ WiFi Automation Tool completed successfully!")
            
        except Exception as e:
            self.error_handler.handle_error(e)
    
    def test_wifi_functionality(self):
        """Test if WiFi is working properly"""
        self.logger.info("Testing WiFi functionality...")
        
        # Check if WiFi interface is up
        result = os.system("iwconfig 2>/dev/null | grep -q 'IEEE 802.11'")
        if result == 0:
            print("✅ WiFi interface is active")
        else:
            print("❌ WiFi interface not found or inactive")
            self.driver_manager.troubleshoot_wifi()

def main():
    parser = argparse.ArgumentParser(description='WiFi Automation Tool for Kali Linux')
    parser.add_argument('--scan-only', action='store_true', help='Only scan for networks')
    parser.add_argument('--install-drivers', action='store_true', help='Only install drivers')
    parser.add_argument('--fix-errors', action='store_true', help='Try to fix common WiFi errors')
    
    args = parser.parse_args()
    
    tool = WiFiAutomationTool()
    
    if args.scan_only:
        tool.scanner.scan_networks(detailed=True)
    elif args.install_drivers:
        tool.driver_manager.install_required_drivers()
    elif args.fix_errors:
        tool.driver_manager.troubleshoot_wifi()
    else:
        tool.run()

if __name__ == "__main__":
    main()
