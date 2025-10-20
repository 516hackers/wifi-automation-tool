import os
import sys
import logging
import subprocess
from typing import bool

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

def run_command(cmd: list, timeout: int = 30) -> tuple:
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
