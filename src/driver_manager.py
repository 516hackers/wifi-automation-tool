import subprocess
import logging
import os
import re
import json
from typing import List, Dict

class DriverManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.drivers_installed = False
        self.offline_drivers = self._load_offline_drivers()
    
    def _load_offline_drivers(self) -> Dict:
        """Load offline driver database"""
        offline_db = {
            'atheros': {
                'packages': ['firmware-atheros', 'firmware-linux-nonfree'],
                'modules': ['ath9k', 'ath9k_common', 'ath9k_hw'],
                'devices': ['Atheros', 'AR93', 'AR94', 'AR95']
            },
            'realtek': {
                'packages': ['firmware-realtek', 'firmware-linux-nonfree'],
                'modules': ['rtl8192cu', 'rtl8xxxu', 'rt2800usb'],
                'devices': ['Realtek', 'RTL81', 'RTL82']
            },
            'intel': {
                'packages': ['firmware-iwlwifi', 'firmware-linux'],
                'modules': ['iwlwifi', 'iwlmvm'],
                'devices': ['Intel', 'Centrino', 'Wireless-AC']
            },
            'broadcom': {
                'packages': ['firmware-brcm80211', 'b43-fwcutter'],
                'modules': ['brcmsmac', 'b43'],
                'devices': ['Broadcom', 'BCM43']
            }
        }
        
        # Try to load from file
        try:
            with open('drivers/common_drivers.json', 'r') as f:
                file_db = json.load(f)
                offline_db.update(file_db)
        except:
            self.logger.warning("Could not load offline driver database file")
        
        return offline_db
    
    def install_required_drivers(self):
        """Install required WiFi drivers with fallback support"""
        try:
            print("🔍 Detecting WiFi hardware...")
            
            # Detect WiFi hardware
            hardware_info = self._detect_wifi_hardware()
            
            if not hardware_info:
                print("❌ No WiFi hardware detected")
                self._install_generic_drivers()
                return
            
            print(f"📟 Detected WiFi hardware: {hardware_info}")
            
            # Try online installation first
            if self._try_online_installation(hardware_info):
                self.drivers_installed = True
                print("✅ Online driver installation completed")
                return
            
            # Fallback to offline installation
            print("🌐 Online installation failed, trying offline methods...")
            if self._try_offline_installation(hardware_info):
                self.drivers_installed = True
                print("✅ Offline driver installation completed")
                return
            
            # Last resort: generic drivers
            print("🔄 Trying generic driver installation...")
            self._install_generic_drivers()
            
        except Exception as e:
            self.logger.error(f"Error installing drivers: {e}")
            self._emergency_driver_installation()
    
    def _try_online_installation(self, hardware_info: str) -> bool:
        """Try online driver installation"""
        from src.package_manager import PackageManager
        
        package_manager = PackageManager()
        driver_packages = self._get_driver_packages(hardware_info)
        
        print(f"📥 Attempting to install: {', '.join(driver_packages)}")
        
        success_count = 0
        for package in driver_packages:
            if package_manager.install_package_with_fallback(package):
                success_count += 1
            else:
                self.logger.warning(f"Failed to install: {package}")
        
        # Load modules after installation
        self._load_wifi_modules()
        
        return success_count >= len(driver_packages) * 0.5  # At least 50% success
    
    def _try_offline_installation(self, hardware_info: str) -> bool:
        """Try offline driver installation"""
        print("🔧 Attempting offline driver solutions...")
        
        # Identify hardware type
        hardware_lower = hardware_info.lower()
        driver_type = None
        
        for driver_key, driver_info in self.offline_drivers.items():
            if any(device in hardware_lower for device in driver_info['devices']):
                driver_type = driver_key
                break
        
        if not driver_type:
            driver_type = 'generic'
        
        print(f"🛠️  Identified driver type: {driver_type}")
        
        # Try to use already installed packages
        if self._activate_existing_drivers(driver_type):
            return True
        
        # Try to compile from source if possible
        if self._compile_drivers_from_source(driver_type):
            return True
        
        return False
    
    def _activate_existing_drivers(self, driver_type: str) -> bool:
        """Try to activate existing drivers"""
        if driver_type in self.offline_drivers:
            driver_info = self.offline_drivers[driver_type]
            
            # Load modules
            modules_loaded = 0
            for module in driver_info['modules']:
                if self._load_kernel_module(module):
                    modules_loaded += 1
            
            return modules_loaded > 0
        
        return False
    
    def _compile_drivers_from_source(self, driver_type: str) -> bool:
        """Attempt to compile drivers from source"""
        print(f"⚙️  Attempting source compilation for {driver_type}...")
        
        try:
            # Install build essentials if possible
            subprocess.run([
                'apt', 'install', '-y', '--allow-unauthenticated',
                'build-essential', 'linux-headers-$(uname -r)', 'git', 'dkms'
            ], capture_output=True, timeout=300)
            
            # Try to compile common open-source drivers
            if driver_type == 'realtek':
                return self._compile_realtek_drivers()
            elif driver_type == 'atheros':
                return self._compile_ath9k_drivers()
            elif driver_type == 'broadcom':
                return self._compile_broadcom_drivers()
                
        except Exception as e:
            self.logger.warning(f"Source compilation failed: {e}")
        
        return False
    
    def _compile_realtek_drivers(self) -> bool:
        """Compile Realtek drivers from source"""
        try:
            # Try RTL8188EU driver
            subprocess.run([
                'git', 'clone', 'https://github.com/lwfinger/rtl8188eu.git'
            ], check=True, timeout=120)
            
            os.chdir('rtl8188eu')
            subprocess.run(['make'], check=True, timeout=300)
            subprocess.run(['make', 'install'], check=True, timeout=120)
            subprocess.run(['modprobe', '8188eu'], check=True)
            
            os.chdir('..')
            return True
        except:
            return False
    
    def _compile_ath9k_drivers(self) -> bool:
        """ath9k is usually in kernel, just load modules"""
        return self._load_kernel_module('ath9k')
    
    def _compile_broadcom_drivers(self) -> bool:
        """Handle Broadcom drivers"""
        try:
            # Try to install broadcom-sta-dkms
            subprocess.run([
                'apt', 'install', '-y', 'broadcom-sta-dkms'
            ], check=True, timeout=300)
            
            subprocess.run(['modprobe', '-r', 'b44', 'b43', 'bcma'], check=False)
            subprocess.run(['modprobe', 'wl'], check=True)
            return True
        except:
            return False
    
    def _install_generic_drivers(self):
        """Install generic WiFi drivers"""
        print("📦 Installing generic WiFi drivers...")
        
        generic_packages = [
            'firmware-linux',
            'firmware-linux-nonfree',
            'wireless-tools',
            'wpasupplicant',
            'net-tools',
            'iw'
        ]
        
        from src.package_manager import PackageManager
        package_manager = PackageManager()
        
        for package in generic_packages:
            try:
                package_manager.install_package_with_fallback(package)
            except Exception as e:
                self.logger.warning(f"Failed to install {package}: {e}")
        
        self._load_wifi_modules()
    
    def _emergency_driver_installation(self):
        """Emergency driver installation as last resort"""
        print("🚨 Performing emergency driver installation...")
        
        # Load all possible WiFi modules
        all_modules = [
            'ath9k', 'ath9k_common', 'ath9k_hw', 'ath10k_pci',
            'rtl8192cu', 'rtl8xxxu', 'rt2800usb', 'rt2x00usb',
            'iwlwifi', 'iwlmvm', 'brcmsmac', 'b43', 'wl'
        ]
        
        for module in all_modules:
            self._load_kernel_module(module)
        
        # Reset network
        subprocess.run(['rfkill', 'unblock', 'all'], check=False)
        subprocess.run(['systemctl', 'restart', 'NetworkManager'], check=False)
    
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
    
    def _get_driver_packages(self, hardware_info: str) -> List[str]:
        """Get appropriate driver packages based on hardware"""
        hardware_lower = hardware_info.lower()
        packages = [
            'firmware-linux',
            'firmware-linux-nonfree',
            'wireless-tools',
            'wpasupplicant'
        ]
        
        # Hardware-specific packages
        if 'atheros' in hardware_lower:
            packages.extend(['firmware-atheros'])
        elif 'realtek' in hardware_lower:
            packages.extend(['firmware-realtek', 'firmware-realtek'])
        elif 'intel' in hardware_lower or 'iwlwifi' in hardware_lower:
            packages.extend(['firmware-iwlwifi'])
        elif 'broadcom' in hardware_lower:
            packages.extend(['firmware-brcm80211', 'b43-fwcutter'])
        
        return list(set(packages))  # Remove duplicates
    
    def _load_wifi_modules(self):
        """Load WiFi kernel modules"""
        modules = [
            'ath9k', 'ath9k_common', 'ath9k_hw',
            'ath10k_pci', 'rt2800usb', 'rt2x00usb',
            'iwlwifi', 'rtl8192cu', 'rtl8xxxu'
        ]
        
        for module in modules:
            self._load_kernel_module(module)
    
    def _load_kernel_module(self, module: str) -> bool:
        """Load a kernel module"""
        try:
            subprocess.run(['modprobe', module], check=True)
            self.logger.info(f"Loaded module: {module}")
            return True
        except subprocess.CalledProcessError:
            self.logger.debug(f"Could not load module: {module}")
            return False
    
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
            
            # Bring interfaces up
            subprocess.run(['ip', 'link', 'set', 'wlan0', 'up'], check=False)
            
            print("✅ WiFi troubleshooting completed")
            
        except Exception as e:
            self.logger.error(f"Troubleshooting failed: {e}")
