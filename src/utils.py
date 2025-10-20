import os
import sys
import logging
import subprocess
import time
import json
from typing import Tuple, List, Dict, Any

def check_root() -> bool:
    """Check if script is running as root"""
    return os.geteuid() == 0

def setup_logging():
    """Setup logging configuration"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'{log_dir}/wifi_tool.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def run_command(cmd: List[str], timeout: int = 30) -> Tuple[int, str, str]:
    """Run shell command with timeout"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def check_package_installed(package: str) -> bool:
    """Check if a package is installed"""
    try:
        subprocess.run(
            ['dpkg', '-s', package],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def create_backup(file_path: str) -> str:
    """Create a backup of a file"""
    if not os.path.exists(file_path):
        return ""
    
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = int(time.time())
    backup_name = f"{os.path.basename(file_path)}.backup.{timestamp}"
    backup_path = os.path.join(backup_dir, backup_name)
    
    try:
        with open(file_path, 'r') as original:
            with open(backup_path, 'w') as backup:
                backup.write(original.read())
        return backup_path
    except Exception as e:
        logging.error(f"Backup failed for {file_path}: {e}")
        return ""

def restore_backup(backup_path: str, original_path: str) -> bool:
    """Restore a file from backup"""
    try:
        if os.path.exists(backup_path):
            with open(backup_path, 'r') as backup:
                with open(original_path, 'w') as original:
                    original.write(backup.read())
            return True
    except Exception as e:
        logging.error(f"Restore failed from {backup_path}: {e}")
    
    return False

def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information"""
    info = {
        'kernel': '',
        'distribution': '',
        'architecture': '',
        'python_version': '',
        'available_memory': 0,
        'disk_usage': {}
    }
    
    try:
        # Kernel version
        with open('/proc/version', 'r') as f:
            info['kernel'] = f.read().strip()
        
        # Distribution
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('PRETTY_NAME='):
                        info['distribution'] = line.split('=')[1].strip().strip('"')
                        break
        
        # Architecture
        info['architecture'] = os.uname().machine
        
        # Python version
        info['python_version'] = sys.version
        
        # Memory
        import psutil
        memory = psutil.virtual_memory()
        info['available_memory'] = memory.available / (1024**3)  # GB
        
        # Disk usage
        disk = psutil.disk_usage('/')
        info['disk_usage'] = {
            'total_gb': disk.total / (1024**3),
            'used_gb': disk.used / (1024**3),
            'free_gb': disk.free / (1024**3)
        }
        
    except Exception as e:
        logging.error(f"Failed to get system info: {e}")
    
    return info

def is_internet_available() -> bool:
    """Check if internet connection is available"""
    try:
        # Try DNS resolution
        import socket
        socket.gethostbyname('google.com')
        
        # Try HTTP connection
        import urllib.request
        urllib.request.urlopen('http://http.kali.org/', timeout=5)
        
        return True
    except:
        return False

def download_file(url: str, local_path: str) -> bool:
    """Download a file with fallback methods"""
    try:
        # Try wget first
        result = subprocess.run(
            ['wget', '-O', local_path, url],
            capture_output=True,
            timeout=60
        )
        if result.returncode == 0:
            return True
        
        # Try curl as fallback
        result = subprocess.run(
            ['curl', '-L', '-o', local_path, url],
            capture_output=True,
            timeout=60
        )
        return result.returncode == 0
        
    except Exception as e:
        logging.error(f"Download failed for {url}: {e}")
        return False

def safe_file_write(file_path: str, content: str, backup: bool = True) -> bool:
    """Safely write to a file with optional backup"""
    try:
        if backup:
            create_backup(file_path)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        return True
    except Exception as e:
        logging.error(f"File write failed for {file_path}: {e}")
        return False

def parse_apt_error(error_output: str) -> Dict[str, Any]:
    """Parse APT error output for better handling"""
    error_analysis = {
        'type': 'unknown',
        'suggested_fix': 'general_repair',
        'critical': False
    }
    
    error_lower = error_output.lower()
    
    if 'broken' in error_lower or 'dependency' in error_lower:
        error_analysis['type'] = 'broken_dependencies'
        error_analysis['suggested_fix'] = 'fix_broken'
    elif 'lock' in error_lower:
        error_analysis['type'] = 'lock_file'
        error_analysis['suggested_fix'] = 'remove_locks'
    elif 'public key' in error_lower or 'gpg' in error_lower:
        error_analysis['type'] = 'gpg_error'
        error_analysis['suggested_fix'] = 'update_keys'
    elif '404' in error_lower or 'not found' in error_lower:
        error_analysis['type'] = 'not_found'
        error_analysis['suggested_fix'] = 'update_sources'
    elif 'space' in error_lower:
        error_analysis['type'] = 'disk_space'
        error_analysis['suggested_fix'] = 'clean_disk'
        error_analysis['critical'] = True
    elif 'permission' in error_lower:
        error_analysis['type'] = 'permission'
        error_analysis['suggested_fix'] = 'fix_permissions'
    
    return error_analysis
