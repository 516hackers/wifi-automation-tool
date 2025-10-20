import subprocess
import logging
import os
import shutil
import psutil
from typing import Dict, List

class SystemHealth:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def comprehensive_health_check(self) -> Dict:
        """Run comprehensive system health check"""
        self.logger.info("Running comprehensive system health check...")
        
        health_report = {
            'system': self._check_system_health(),
            'package_manager': self._check_package_manager_health(),
            'network': self._check_network_health(),
            'hardware': self._check_hardware_health(),
            'security': self._check_security_health(),
            'overall_health': True
        }
        
        # Determine overall health
        critical_checks = [
            health_report['package_manager']['apt_working'],
            health_report['system']['disk_space_adequate'],
            health_report['network']['internet_connectivity']
        ]
        
        health_report['overall_health'] = all(critical_checks)
        
        return health_report
    
    def _check_system_health(self) -> Dict:
        """Check system-level health"""
        system_health = {
            'disk_space_adequate': self._check_disk_space(),
            'memory_adequate': self._check_memory(),
            'cpu_healthy': self._check_cpu_health(),
            'kernel_version': self._get_kernel_version(),
            'uptime': self._get_system_uptime()
        }
        return system_health
    
    def _check_package_manager_health(self) -> Dict:
        """Check package manager health"""
        package_health = {
            'apt_working': self._check_apt_working(),
            'sources_valid': self._check_sources_valid(),
            'gpg_keys_valid': self._check_gpg_keys_valid(),
            'no_broken_packages': self._check_no_broken_packages(),
            'cache_updated': self._check_apt_cache_updated()
        }
        return package_health
    
    def _check_network_health(self) -> Dict:
        """Check network health"""
        network_health = {
            'internet_connectivity': self._check_internet_connectivity(),
            'dns_working': self._check_dns_working(),
            'wifi_hardware_present': self._check_wifi_hardware(),
            'network_services_running': self._check_network_services()
        }
        return network_health
    
    def _check_hardware_health(self) -> Dict:
        """Check hardware health"""
        hardware_health = {
            'wifi_devices': self._get_wifi_devices(),
            'usb_devices': self._get_usb_devices(),
            'pci_devices': self._get_pci_devices(),
            'kernel_modules': self._get_wifi_modules()
        }
        return hardware_health
    
    def _check_security_health(self) -> Dict:
        """Check security health"""
        security_health = {
            'firewall_status': self._check_firewall_status(),
            'root_user': self._check_root_user(),
            'system_updates': self._check_system_updates()
        }
        return security_health
    
    def _check_disk_space(self, min_gb: int = 2) -> bool:
        """Check if sufficient disk space is available"""
        try:
            usage = shutil.disk_usage("/")
            free_gb = usage.free / (1024**3)  # Convert to GB
            return free_gb >= min_gb
        except Exception as e:
            self.logger.error(f"Disk space check failed: {e}")
            return False
    
    def _check_memory(self, min_gb: int = 1) -> bool:
        """Check if sufficient memory is available"""
        try:
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            return available_gb >= min_gb
        except Exception as e:
            self.logger.error(f"Memory check failed: {e}")
            return False
    
    def _check_cpu_health(self) -> bool:
        """Check CPU health"""
        try:
            # Simple check - if we can get CPU times, CPU is probably working
            psutil.cpu_times()
            return True
        except Exception as e:
            self.logger.error(f"CPU health check failed: {e}")
            return False
    
    def _get_kernel_version(self) -> str:
        """Get kernel version"""
        try:
            with open('/proc/version', 'r') as f:
                return f.read().strip()
        except:
            return "Unknown"
    
    def _get_system_uptime(self) -> str:
        """Get system uptime"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.read().split()[0])
                return f"{int(uptime_seconds / 3600)} hours"
        except:
            return "Unknown"
    
    def _check_apt_working(self) -> bool:
        """Check if APT is working"""
        try:
            result = subprocess.run(
                ['apt', '--version'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_sources_valid(self) -> bool:
        """Check if APT sources are valid"""
        try:
            if not os.path.exists('/etc/apt/sources.list'):
                return False
            
            with open('/etc/apt/sources.list', 'r') as f:
                content = f.read()
                return 'kali' in content.lower() and 'http' in content
        except:
            return False
    
    def _check_gpg_keys_valid(self) -> bool:
        """Check if GPG keys are valid"""
        try:
            result = subprocess.run(
                ['apt-key', 'list'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0 and 'kali' in result.stdout.lower()
        except:
            return False
    
    def _check_no_broken_packages(self) -> bool:
        """Check for broken packages"""
        try:
            result = subprocess.run(
                ['dpkg', '--audit'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0 and result.stdout.strip() == ""
        except:
            return False
    
    def _check_apt_cache_updated(self) -> bool:
        """Check if APT cache is recently updated"""
        try:
            list_dir = '/var/lib/apt/lists'
            if not os.path.exists(list_dir):
                return False
            
            # Check if any list files are newer than 24 hours
            import time
            current_time = time.time()
            for file in os.listdir(list_dir):
                file_path = os.path.join(list_dir, file)
                if os.path.isfile(file_path):
                    file_time = os.path.getmtime(file_path)
                    if current_time - file_time < 86400:  # 24 hours
                        return True
            return False
        except:
            return False
    
    def _check_internet_connectivity(self) -> bool:
        """Check internet connectivity"""
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '3', '8.8.8.8'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_dns_working(self) -> bool:
        """Check if DNS is working"""
        try:
            result = subprocess.run(
                ['nslookup', 'google.com'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_wifi_hardware(self) -> bool:
        """Check if WiFi hardware is present"""
        try:
            # Check PCI devices
            pci_result = subprocess.run(
                ['lspci'],
                capture_output=True,
                text=True
            )
            pci_wifi = 'Network controller' in pci_result.stdout or 'Wireless' in pci_result.stdout
            
            # Check USB devices
            usb_result = subprocess.run(
                ['lsusb'],
                capture_output=True,
                text=True
            )
            usb_wifi = 'Wireless' in usb_result.stdout
            
            return pci_wifi or usb_wifi
        except:
            return False
    
    def _check_network_services(self) -> bool:
        """Check if network services are running"""
        services = ['NetworkManager', 'networking']
        running_services = 0
        
        for service in services:
            try:
                result = subprocess.run(
                    ['systemctl', 'is-active', service],
                    capture_output=True,
                    text=True
                )
                if result.stdout.strip() == 'active':
                    running_services += 1
            except:
                continue
        
        return running_services >= 1
    
    def _get_wifi_devices(self) -> List[str]:
        """Get list of WiFi devices"""
        devices = []
        try:
            # Check iwconfig
            result = subprocess.run(
                ['iwconfig'],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                if 'IEEE 802.11' in line:
                    device = line.split()[0]
                    devices.append(device)
        except:
            pass
        
        return devices
    
    def _get_usb_devices(self) -> List[str]:
        """Get USB devices"""
        devices = []
        try:
            result = subprocess.run(
                ['lsusb'],
                capture_output=True,
                text=True
            )
            devices = result.stdout.strip().split('\n')
        except:
            pass
        
        return devices
    
    def _get_pci_devices(self) -> List[str]:
        """Get PCI devices"""
        devices = []
        try:
            result = subprocess.run(
                ['lspci'],
                capture_output=True,
                text=True
            )
            devices = result.stdout.strip().split('\n')
        except:
            pass
        
        return devices
    
    def _get_wifi_modules(self) -> List[str]:
        """Get loaded WiFi modules"""
        modules = []
        try:
            result = subprocess.run(
                ['lsmod'],
                capture_output=True,
                text=True
            )
            wifi_keywords = ['ath', 'rtl', 'iwl', 'brcm', 'cfg']
            for line in result.stdout.split('\n'):
                for keyword in wifi_keywords:
                    if keyword in line.lower():
                        modules.append(line.split()[0])
                        break
        except:
            pass
        
        return modules
    
    def _check_firewall_status(self) -> str:
        """Check firewall status"""
        try:
            result = subprocess.run(
                ['ufw', 'status'],
                capture_output=True,
                text=True
            )
            if 'inactive' in result.stdout:
                return 'Disabled'
            elif 'active' in result.stdout:
                return 'Enabled'
        except:
            pass
        
        return 'Unknown'
    
    def _check_root_user(self) -> bool:
        """Check if running as root"""
        return os.geteuid() == 0
    
    def _check_system_updates(self) -> str:
        """Check if system updates are available"""
        try:
            result = subprocess.run(
                ['apt', 'list', '--upgradable'],
                capture_output=True,
                text=True
            )
            lines = result.stdout.strip().split('\n')
            # First line is header, so count actual packages
            update_count = len([line for line in lines if '/' in line])
            
            if update_count == 0:
                return 'Up to date'
            else:
                return f'{update_count} updates available'
        except:
            return 'Unknown'
    
    def print_health_report(self, health_report: Dict):
        """Print formatted health report"""
        print("\n" + "="*60)
        print("🔍 COMPREHENSIVE SYSTEM HEALTH REPORT")
        print("="*60)
        
        # System Health
        print("\n💻 SYSTEM HEALTH:")
        system = health_report['system']
        print(f"  Disk Space: {'✅ Adequate' if system['disk_space_adequate'] else '❌ Low'}")
        print(f"  Memory: {'✅ Adequate' if system['memory_adequate'] else '❌ Low'}")
        print(f"  CPU: {'✅ Healthy' if system['cpu_healthy'] else '❌ Issues'}")
        print(f"  Kernel: {system['kernel_version'][:50]}...")
        print(f"  Uptime: {system['uptime']}")
        
        # Package Manager Health
        print("\n📦 PACKAGE MANAGER HEALTH:")
        pm = health_report['package_manager']
        print(f"  APT Working: {'✅ Yes' if pm['apt_working'] else '❌ No'}")
        print(f"  Sources Valid: {'✅ Yes' if pm['sources_valid'] else '❌ No'}")
        print(f"  GPG Keys: {'✅ Valid' if pm['gpg_keys_valid'] else '❌ Invalid'}")
        print(f"  Broken Packages: {'✅ None' if pm['no_broken_packages'] else '❌ Found'}")
        print(f"  Cache Updated: {'✅ Yes' if pm['cache_updated'] else '❌ Stale'}")
        
        # Network Health
        print("\n🌐 NETWORK HEALTH:")
        network = health_report['network']
        print(f"  Internet: {'✅ Connected' if network['internet_connectivity'] else '❌ Disconnected'}")
        print(f"  DNS: {'✅ Working' if network['dns_working'] else '❌ Failing'}")
        print(f"  WiFi Hardware: {'✅ Present' if network['wifi_hardware_present'] else '❌ Missing'}")
        print(f"  Network Services: {'✅ Running' if network['network_services_running'] else '❌ Stopped'}")
        
        # Hardware Health
        print("\n🔧 HARDWARE HEALTH:")
        hardware = health_report['hardware']
        print(f"  WiFi Devices: {len(hardware['wifi_devices'])} found")
        print(f"  USB Devices: {len(hardware['usb_devices'])} found")
        print(f"  PCI Devices: {len(hardware['pci_devices'])} found")
        print(f"  WiFi Modules: {len(hardware['kernel_modules'])} loaded")
        
        # Security Health
        print("\n🛡️ SECURITY HEALTH:")
        security = health_report['security']
        print(f"  Firewall:
