import subprocess
import logging
import os
import requests
import re
from typing import List, Dict

class DriverManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.drivers_installed = False
    
    def install_required_drivers(self):
        """Install required WiFi drivers"""
        try:
            print("🔍 Checking WiFi hardware...")
            
            # Detect WiFi hardware
            hardware_info = self._detect_wifi_hardware()
            
            if not hardware_info:
                print("❌ No WiFi hardware detected")
                return
            
            print(f"📟 Detected WiFi hardware: {hardware_info}")
            
            # Install appropriate drivers
            self._install_drivers_based_on_hardware(hardware_info)
            
            # Load drivers
            self._load_wifi_modules()
            
            self.drivers_installed = True
            print("✅ Driver installation completed")
            
        except Exception as e:
            self.logger.error(f"Error installing drivers: {e}")
            self._fallback_driver_installation()
    
    def _detect_wifi_hardware(self) -> str:
        """Detect WiFi hardware"""
        try:
            # Check PCI devices
            pci_result = subprocess.run(
                ['lspci'], 
                capture_output=True, 
                text=True
            )
            
            wifi_devices = []
            for line in pci_result.stdout.split('\n'):
                if 'Network controller' in line or 'Wireless' in line.lower():
                    wifi_devices.append(line.strip())
                    self.logger.info(f"Found WiFi device: {line.strip()}")
            
            # Check USB devices
            usb_result = subprocess.run(
                ['lsusb'], 
                capture_output=True, 
                text=True
            )
            
            for line in usb_result.stdout.split('\n'):
                if 'Wireless' in line or '802.11' in line:
                    wifi_devices.append(line.strip())
                    self.logger.info(f"Found USB WiFi: {line.strip()}")
            
            return ', '.join(wifi_devices) if wifi_devices else "Unknown"
            
        except Exception as e:
            self.logger.error(f"Error detecting hardware: {e}")
            return "Unknown"
    
    def _install_drivers_based_on_hardware(self, hardware_info: str):
        """Install drivers based on detected hardware"""
        drivers_to_install = []
        
        # Common WiFi drivers
        common_drivers = [
            'firmware-linux',
            'firmware-linux-nonfree',
            'firmware-atheros',
            'firmware-realtek',
            'firmware-iwlwifi',
            'firmware-brcm80211'
        ]
        
        # Hardware-specific drivers
        hardware_lower = hardware_info.lower()
        
        if 'atheros' in hardware_lower:
            drivers_to_install.extend(['firmware-atheros'])
        elif 'realtek' in hardware_lower:
            drivers_to_install.extend(['firmware-realtek', 'rtl8812au-dkms'])
        elif 'intel' in hardware_lower or 'iwlwifi' in hardware_lower:
            drivers_to_install.extend(['firmware-iwlwifi'])
        elif 'broadcom' in hardware_lower:
            drivers_to_install.extend(['firmware-brcm80211', 'b43-fwcutter'])
        
        # Add common drivers
        drivers_to_install.extend(common_drivers)
        
        # Remove duplicates
        drivers_to_install = list(set(drivers_to_install))
        
        print(f"📥 Installing drivers: {', '.join(drivers_to_install)}")
        
        # Install drivers
        for driver in drivers_to_install:
            try:
                subprocess.run(
                    ['apt', 'install', '-y', driver],
                    check=True,
                    capture_output=True
                )
                self.logger.info(f"Installed driver: {driver}")
            except subprocess.CalledProcessError:
                self.logger.warning(f"Failed to install driver: {driver}")
    
    def _load_wifi_modules(self):
        """Load WiFi kernel modules"""
        modules = [
            'ath9k', 'ath9k_common', 'ath9k_hw',
            'ath10k_pci', 'rt2800usb', 'rt2x00usb',
            'iwlwifi', 'rtl8192cu', 'rtl8xxxu'
        ]
        
        for module in modules:
            try:
                subprocess.run(['modprobe', module], check=True)
                self.logger.info(f"Loaded module: {module}")
            except subprocess.CalledProcessError:
                self.logger.debug(f"Could not load module: {module}")
    
    def _fallback_driver_installation(self):
        """Fallback method for driver installation"""
        print("🔄 Attempting fallback driver installation...")
        
        try:
            # Update package list
            subprocess.run(['apt', 'update'], check=True)
            
            # Install common WiFi packages
            subprocess.run([
                'apt', 'install', '-y',
                'kali-linux-wireless',
                'wireless-tools',
                'wpasupplicant',
                'network-manager'
            ], check=True)
            
            print("✅ Fallback installation completed")
        except Exception as e:
            self.logger.error(f"Fallback installation failed: {e}")
    
    def troubleshoot_wifi(self):
        """Troubleshoot WiFi issues"""
        print("🔧 Troubleshooting WiFi...")
        
        try:
            # Restart network services
            subprocess.run(['systemctl', 'restart', 'NetworkManager'], check=True)
            subprocess.run(['systemctl', 'restart', 'wpa_supplicant'], check=True)
            
            # Reload kernel modules
            self._load_wifi_modules()
            
            # Reset WiFi interface
            subprocess.run(['rfkill', 'unblock', 'all'], check=True)
            
            print("✅ WiFi troubleshooting completed")
            
        except Exception as e:
            self.logger.error(f"Troubleshooting failed: {e}")
