import logging
import subprocess
import sys
import os

class ErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def handle_error(self, error: Exception):
        """Handle different types of errors"""
        error_msg = str(error)
        self.logger.error(f"Error occurred: {error_msg}")
        
        print(f"❌ Error: {error_msg}")
        print("🛠️ Attempting to fix...")
        
        if "permission" in error_msg.lower() or "root" in error_msg.lower():
            self._fix_permission_issues()
        elif "driver" in error_msg.lower() or "firmware" in error_msg.lower():
            self._fix_driver_issues()
        elif "network" in error_msg.lower() or "interface" in error_msg.lower():
            self._fix_network_issues()
        else:
            self._general_fix()
    
    def _fix_permission_issues(self):
        """Fix permission related issues"""
        print("🔑 Fixing permission issues...")
        try:
            # Ensure proper permissions
            subprocess.run(['chmod', '+x', 'install.sh'], check=True)
            subprocess.run(['chmod', '+x', 'main.py'], check=True)
            print("✅ Permission issues fixed")
        except Exception as e:
            self.logger.error(f"Could not fix permissions: {e}")
    
    def _fix_driver_issues(self):
        """Fix driver related issues"""
        print("📟 Fixing driver issues...")
        try:
            # Update system
            subprocess.run(['apt', 'update'], check=True)
            
            # Reinstall WiFi packages
            subprocess.run([
                'apt', 'install', '--reinstall', '-y',
                'firmware-linux-nonfree',
                'wireless-tools',
                'linux-firmware'
            ], check=True)
            
            print("✅ Driver issues fixed")
        except Exception as e:
            self.logger.error(f"Could not fix driver issues: {e}")
    
    def _fix_network_issues(self):
        """Fix network related issues"""
        print("🌐 Fixing network issues...")
        try:
            # Restart networking services
            subprocess.run(['systemctl', 'restart', 'NetworkManager'], check=True)
            subprocess.run(['systemctl', 'restart', 'networking'], check=True)
            
            # Reset network interfaces
            subprocess.run(['rfkill', 'unblock', 'all'], check=True)
            
            print("✅ Network issues fixed")
        except Exception as e:
            self.logger.error(f"Could not fix network issues: {e}")
    
    def _general_fix(self):
        """General error fixing"""
        print("🛠️ Applying general fixes...")
        try:
            # Update system
            subprocess.run(['apt', 'update'], check=True)
            subprocess.run(['apt', 'upgrade', '-y'], check=True)
            
            # Clean up
            subprocess.run(['apt', 'autoremove', '-y'], check=True)
            subprocess.run(['apt', 'autoclean'], check=True)
            
            print("✅ General fixes applied")
        except Exception as e:
            self.logger.error(f"Could not apply general fixes: {e}")
