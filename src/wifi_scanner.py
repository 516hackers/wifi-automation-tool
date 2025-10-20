import subprocess
import json
import logging
import re
from typing import List, Dict

class WiFiScanner:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def scan_networks(self, detailed: bool = False) -> List[str]:
        """Scan for available WiFi networks"""
        try:
            self.logger.info("Scanning for WiFi networks...")
            
            # Bring WiFi interface up
            self._enable_wifi_interface()
            
            # Scan using iwlist
            result = subprocess.run(
                ['iwlist', 'scan'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                networks = self._parse_iwlist_output(result.stdout)
                if detailed:
                    self._display_detailed_networks(networks)
                return networks
            else:
                self.logger.error("Failed to scan networks")
                return []
                
        except subprocess.TimeoutExpired:
            self.logger.error("Network scan timed out")
            return []
        except Exception as e:
            self.logger.error(f"Error scanning networks: {e}")
            return []
    
    def _enable_wifi_interface(self):
        """Enable WiFi interface"""
        try:
            # Find WiFi interface
            result = subprocess.run(['iwconfig'], capture_output=True, text=True)
            interfaces = re.findall(r'^(\w+)\s+IEEE', result.stdout, re.MULTILINE)
            
            if interfaces:
                wifi_interface = interfaces[0]
                subprocess.run(['ip', 'link', 'set', wifi_interface, 'up'], check=True)
                self.logger.info(f"Enabled WiFi interface: {wifi_interface}")
        except Exception as e:
            self.logger.warning(f"Could not enable WiFi interface: {e}")
    
    def _parse_iwlist_output(self, output: str) -> List[str]:
        """Parse iwlist scan output"""
        networks = []
        current_network = {}
        
        for line in output.split('\n'):
            line = line.strip()
            
            # ESSID
            if 'ESSID:' in line:
                essid = line.split('ESSID:')[1].strip().strip('"')
                if essid and essid not in networks:
                    networks.append(essid)
            
            # Signal level
            elif 'Signal level=' in line:
                signal_match = re.search(r'Signal level=(-?\d+)', line)
                if signal_match:
                    current_network['signal'] = signal_match.group(1)
        
        return networks
    
    def _display_detailed_networks(self, networks: List[str]):
        """Display detailed network information"""
        print("\n" + "="*50)
        print("📡 DETECTED WIFI NETWORKS")
        print("="*50)
        
        if not networks:
            print("No networks found")
            return
            
        for i, network in enumerate(networks, 1):
            print(f"{i:2d}. {network}")
        
        print("="*50)
