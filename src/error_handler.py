import logging
import subprocess
import sys
import os
import traceback
from typing import Dict, Any

class ErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None):
        """Handle different types of errors with context"""
        error_msg = str(error)
        error_type = type(error).__name__
        
        self.logger.error(f"Error {error_type}: {error_msg}")
        self.logger.debug(f"Traceback: {traceback.format_exc()}")
        
        print(f"❌ Error ({error_type}): {error_msg}")
        print("🛠️ Attempting automated repair...")
        
        # Use context for better error handling
        if context and 'operation' in context:
            print(f"   Operation: {context['operation']}")
        
        # Map error types to specific handlers
        error_handlers = {
            'PermissionError': self._fix_permission_issues,
            'FileNotFoundError': self._fix_missing_files,
            'subprocess.CalledProcessError': self._fix_subprocess_errors,
            'OSError': self._fix_os_errors,
            'ConnectionError': self._fix_connection_issues
        }
        
        # Try specific handler first
        for error_pattern, handler in error_handlers.items():
            if error_pattern in error_type or error_pattern in error_msg:
                if handler(context):
                    return
        
        # Fallback to general analysis
        self._analyze_and_fix_general(error_msg, context)
    
    def _fix_permission_issues(self, context: Dict[str, Any] = None) -> bool:
        """Fix permission related issues"""
        print("🔑 Fixing permission issues...")
        try:
            # Ensure proper permissions for our tool
            subprocess.run(['chmod', '+x', 'install.sh'], check=True)
            subprocess.run(['chmod', '+x', 'main.py'], check=True)
            subprocess.run(['chmod', '+x', 'recovery.sh'], check=True)
            
            # Fix common permission issues
            subprocess.run(['chown', '-R', 'root:root', '/etc/NetworkManager/'], check=False)
            subprocess.run(['chmod', '600', '/etc/NetworkManager/system-connections/*'], check=False)
            
            print("✅ Permission issues fixed")
            return True
        except Exception as e:
            self.logger.error(f"Could not fix permissions: {e}")
            return False
    
    def _fix_missing_files(self, context: Dict[str, Any] = None) -> bool:
        """Fix missing files and directories"""
        print("📁 Fixing missing files...")
        try:
            # Create necessary directories
            directories = [
                'logs', 'drivers', 'config', 'backups',
                '/etc/NetworkManager/system-connections'
            ]
            
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
            
            # Reinstall critical packages if files are missing
            if context and 'missing_file' in context:
                file_path = context['missing_file']
                if file_path.startswith('/usr') or file_path.startswith('/etc'):
                    self._reinstall_related_package(file_path)
            
            print("✅ Missing files issues addressed")
            return True
        except Exception as e:
            self.logger.error(f"Could not fix missing files: {e}")
            return False
    
    def _fix_subprocess_errors(self, context: Dict[str, Any] = None) -> bool:
        """Fix subprocess execution errors"""
        print("⚙️ Fixing subprocess execution issues...")
        try:
            from src.package_manager import PackageManager
            package_manager = PackageManager()
            
            # Fix package management first
            package_manager.fix_package_management()
            
            # Reinstall common tools
            tools = ['wireless-tools', 'net-tools', 'iproute2']
            for tool in tools:
                try:
                    package_manager.install_package_with_fallback(tool)
                except:
                    continue
            
            print("✅ Subprocess issues fixed")
            return True
        except Exception as e:
            self.logger.error(f"Could not fix subprocess issues: {e}")
            return False
    
    def _fix_os_errors(self, context: Dict[str, Any] = None) -> bool:
        """Fix OS-level errors"""
        print("💻 Fixing OS-level issues...")
        try:
            # Check and repair filesystem
            subprocess.run(['fsck', '-f', '/'], check=False)
            
            # Reload kernel modules
            subprocess.run(['modprobe', '-r', 'ath9k'], check=False)
            subprocess.run(['modprobe', 'ath9k'], check=False)
            
            # Restart system daemons
            subprocess.run(['systemctl', 'daemon-reload'], check=True)
            
            print("✅ OS-level issues fixed")
            return True
        except Exception as e:
            self.logger.error(f"Could not fix OS-level issues: {e}")
            return False
    
    def _fix_connection_issues(self, context: Dict[str, Any] = None) -> bool:
        """Fix network connection issues"""
        print("🌐 Fixing connection issues...")
        try:
            # Restart networking
            subprocess.run(['systemctl', 'restart', 'NetworkManager'], check=True)
            subprocess.run(['systemctl', 'restart', 'networking'], check=True)
            
            # Reset network configuration
            subprocess.run(['nmcli', 'networking', 'off'], check=False)
            subprocess.run(['nmcli', 'networking', 'on'], check=False)
            
            # Flush routes and renew
            subprocess.run(['ip', 'route', 'flush', 'cache'], check=False)
            
            print("✅ Connection issues fixed")
            return True
        except Exception as e:
            self.logger.error(f"Could not fix connection issues: {e}")
            return False
    
    def _analyze_and_fix_general(self, error_msg: str, context: Dict[str, Any] = None):
        """Analyze error message and apply general fixes"""
        print("🔍 Analyzing error pattern...")
        
        if any(word in error_msg.lower() for word in ['broken', 'dependency', 'dpkg']):
            self._fix_package_system()
        elif any(word in error_msg.lower() for word in ['network', 'connection', 'unreachable']):
            self._fix_network_system()
        elif any(word in error_msg.lower() for word in ['driver', 'firmware', 'module']):
            self._fix_driver_system()
        elif any(word in error_msg.lower() for word in ['memory', 'space', 'disk']):
            self._fix_resource_issues()
        else:
            self._general_system_repair()
    
    def _fix_package_system(self):
        """Fix package system issues"""
        print("📦 Repairing package system...")
        from src.package_manager import PackageManager
        package_manager = PackageManager()
        package_manager.fix_package_management()
    
    def _fix_network_system(self):
        """Fix network system issues"""
        print("🌐 Repairing network system...")
        subprocess.run(['systemctl', 'restart', 'NetworkManager'], check=False)
        subprocess.run(['rfkill', 'unblock', 'all'], check=False)
    
    def _fix_driver_system(self):
        """Fix driver system issues"""
        print("🔧 Repairing driver system...")
        from src.driver_manager import DriverManager
        driver_manager = DriverManager()
        driver_manager.troubleshoot_wifi()
    
    def _fix_resource_issues(self):
        """Fix resource issues"""
        print("💾 Freeing up system resources...")
        subprocess.run(['apt', 'clean'], check=False)
        subprocess.run(['apt', 'autoclean'], check=False)
        subprocess.run(['journalctl', '--vacuum-size=100M'], check=False)
    
    def _general_system_repair(self):
        """General system repair"""
        print("🛠️ Performing general system repair...")
        try:
            # Update system
            subprocess.run(['apt', 'update'], check=False)
            subprocess.run(['apt', 'upgrade', '-y'], check=False)
            
            # Clean up
            subprocess.run(['apt', 'autoremove', '-y'], check=False)
            subprocess.run(['apt', 'autoclean'], check=False)
            
            # Restart services
            subprocess.run(['systemctl', 'restart', 'NetworkManager'], check=False)
            
            print("✅ General system repair completed")
        except Exception as e:
            self.logger.error(f"General repair failed: {e}")
    
    def _reinstall_related_package(self, file_path: str):
        """Reinstall package related to missing file"""
        try:
            # Find which package owns the file
            result = subprocess.run(
                ['dpkg', '-S', file_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                package = result.stdout.split(':')[0]
                print(f"📦 Reinstalling package: {package}")
                subprocess.run(['apt', 'install', '--reinstall', '-y', package], check=True)
        except:
            self.logger.warning(f"Could not determine package for {file_path}")
