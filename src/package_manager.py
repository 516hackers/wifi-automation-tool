import subprocess
import logging
import os
import re
import tempfile
import json
import time
from typing import Tuple, List, Dict

class PackageManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def check_system_health(self) -> Dict:
        """Comprehensive system health check"""
        health_status = {
            'apt_working': False,
            'sources_valid': False,
            'gpg_keys_valid': False,
            'network_connected': False,
            'disk_space_adequate': False,
            'dependencies_ok': False,
            'overall_health': False
        }
        
        try:
            # Check if APT is working
            health_status['apt_working'] = self._test_apt_functionality()
            
            # Check repository sources
            health_status['sources_valid'] = self._check_sources_list()
            
            # Check GPG keys
            health_status['gpg_keys_valid'] = self._check_gpg_keys()
            
            # Check network connectivity to repositories
            health_status['network_connected'] = self._test_repository_connectivity()
            
            # Check disk space
            health_status['disk_space_adequate'] = self._check_disk_space()
            
            # Check for broken dependencies
            health_status['dependencies_ok'] = self._check_broken_dependencies()
            
            # Overall health
            health_status['overall_health'] = all([
                health_status['apt_working'],
                health_status['sources_valid'], 
                health_status['network_connected'],
                health_status['disk_space_adequate']
            ])
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return health_status

    def _test_apt_functionality(self) -> bool:
        """Test if APT is functioning properly"""
        try:
            result = subprocess.run(
                ['apt', 'update'],
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.returncode == 0 or "Reading package lists" in result.stdout
        except Exception as e:
            self.logger.error(f"APT functionality test failed: {e}")
            return False

    def _check_sources_list(self) -> bool:
        """Check if sources.list is valid"""
        try:
            if not os.path.exists('/etc/apt/sources.list'):
                return False
            
            with open('/etc/apt/sources.list', 'r') as f:
                content = f.read()
            
            # Check for Kali repositories
            kali_patterns = [
                'kali-rolling',
                'http.kali.org',
                'kali.download'
            ]
            
            return any(pattern in content for pattern in kali_patterns)
            
        except Exception as e:
            self.logger.error(f"Sources list check failed: {e}")
            return False

    def _check_gpg_keys(self) -> bool:
        """Check if GPG keys are valid"""
        try:
            result = subprocess.run(
                ['apt-key', 'list'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0 and 'Kali Linux' in result.stdout
        except Exception as e:
            self.logger.error(f"GPG keys check failed: {e}")
            return False

    def _test_repository_connectivity(self) -> bool:
        """Test connectivity to Kali repositories"""
        try:
            repositories = [
                'http.kali.org',
                'kali.download',
                'archive-4.kali.org'
            ]
            
            for repo in repositories:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '3', repo],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return True
            
            return False
        except Exception as e:
            self.logger.error(f"Repository connectivity test failed: {e}")
            return False

    def _check_disk_space(self, required_mb: int = 500) -> bool:
        """Check if there's enough disk space"""
        try:
            result = subprocess.run(
                ['df', '/'],
                capture_output=True,
                text=True
            )
            
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                available = int(lines[1].split()[3])  # Available in KB
                available_mb = available / 1024
                return available_mb >= required_mb
            
            return False
        except Exception as e:
            self.logger.error(f"Disk space check failed: {e}")
            return False

    def _check_broken_dependencies(self) -> bool:
        """Check for broken dependencies"""
        try:
            result = subprocess.run(
                ['dpkg', '--audit'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0 and 'broken' not in result.stdout.lower()
        except Exception as e:
            self.logger.error(f"Broken dependencies check failed: {e}")
            return False

    def fix_package_management(self):
        """Fix common package management issues"""
        self.logger.info("Fixing package management issues...")
        
        fixes = [
            self._remove_lock_files,
            self._fix_broken_packages,
            self._clean_apt_cache,
            self._update_package_lists,
            self._fix_missing_dependencies
        ]
        
        for fix_func in fixes:
            try:
                fix_func()
                time.sleep(2)  # Brief pause between fixes
            except Exception as e:
                self.logger.warning(f"Fix {fix_func.__name__} failed: {e}")

    def _remove_lock_files(self):
        """Remove APT lock files"""
        lock_files = [
            '/var/lib/dpkg/lock',
            '/var/lib/dpkg/lock-frontend', 
            '/var/lib/apt/lists/lock',
            '/var/cache/apt/archives/lock'
        ]
        
        for lock_file in lock_files:
            if os.path.exists(lock_file):
                self.logger.info(f"Removing lock file: {lock_file}")
                os.remove(lock_file)

    def _fix_broken_packages(self):
        """Fix broken packages"""
        self.logger.info("Fixing broken packages...")
        
        commands = [
            ['dpkg', '--configure', '-a'],
            ['apt', '--fix-broken', 'install', '-y'],
            ['apt', 'install', '--fix-missing', '-y']
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd, check=True, timeout=300)
                self.logger.info(f"Successfully ran: {' '.join(cmd)}")
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"Command failed: {' '.join(cmd)} - {e}")
            except subprocess.TimeoutExpired:
                self.logger.warning(f"Command timed out: {' '.join(cmd)}")

    def _clean_apt_cache(self):
        """Clean APT cache"""
        self.logger.info("Cleaning APT cache...")
        
        commands = [
            ['apt', 'clean'],
            ['apt', 'autoclean'],
            ['apt', 'autoremove', '-y']
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd, check=True, timeout=120)
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"Cache clean failed: {e}")

    def _update_package_lists(self):
        """Update package lists"""
        self.logger.info("Updating package lists...")
        try:
            subprocess.run(['apt', 'update'], check=True, timeout=180)
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Package list update failed: {e}")

    def _fix_missing_dependencies(self):
        """Fix missing dependencies"""
        self.logger.info("Fixing missing dependencies...")
        try:
            subprocess.run(
                ['apt', 'install', '-f', '-y'],
                check=True,
                timeout=300
            )
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Missing dependencies fix failed: {e}")

    def repair_system_health(self, health_status: Dict):
        """Repair system based on health status"""
        self.logger.info("Repairing system health issues...")
        
        if not health_status['apt_working']:
            self._emergency_apt_repair()
        
        if not health_status['sources_valid']:
            self._fix_sources_list()
            
        if not health_status['gpg_keys_valid']:
            self._fix_gpg_keys()
            
        if not health_status['disk_space_adequate']:
            self._free_up_disk_space()

    def _emergency_apt_repair(self):
        """Emergency APT repair"""
        self.logger.info("Performing emergency APT repair...")
        
        # Kill any stuck processes
        subprocess.run(['pkill', '-f', 'apt'], capture_output=True)
        subprocess.run(['pkill', '-f', 'dpkg'], capture_output=True)
        
        # Remove all lock files
        self._remove_lock_files()
        
        # Force dpkg repair
        subprocess.run(['dpkg', '--configure', '-a', '--force-all'], check=False)
        
        # Complete system repair
        repair_commands = [
            ['apt', 'update', '--allow-unauthenticated'],
            ['apt', 'install', '--fix-broken', '--yes', '--allow-downgrades'],
            ['apt', 'dist-upgrade', '--yes']
        ]
        
        for cmd in repair_commands:
            try:
                subprocess.run(cmd, timeout=300, check=False)
            except subprocess.TimeoutExpired:
                self.logger.warning("Command timed out during emergency repair")

    def _fix_sources_list(self):
        """Fix Kali sources.list"""
        self.logger.info("Fixing Kali sources.list...")
        
        kali_sources = """# Kali Linux repositories
deb http://http.kali.org/kali kali-rolling main contrib non-free
# deb-src http://http.kali.org/kali kali-rolling main contrib non-free
"""
        
        try:
            # Backup original
            if os.path.exists('/etc/apt/sources.list'):
                backup_name = f'/etc/apt/sources.list.backup.{int(time.time())}'
                os.rename('/etc/apt/sources.list', backup_name)
                self.logger.info(f"Backed up sources.list to {backup_name}")
            
            # Write new sources
            with open('/etc/apt/sources.list', 'w') as f:
                f.write(kali_sources)
            
            self.logger.info("Updated sources.list with Kali repositories")
        except Exception as e:
            self.logger.error(f"Failed to fix sources.list: {e}")

    def _fix_gpg_keys(self):
        """Fix Kali GPG keys"""
        self.logger.info("Fixing Kali GPG keys...")
        
        key_commands = [
            ['wget', '-q', '-O', '-', 'https://archive.kali.org/archive-key.asc'],
            ['apt-key', 'add', '-']
        ]
        
        try:
            # Download and add key
            result1 = subprocess.run(key_commands[0], capture_output=True, text=True)
            if result1.returncode == 0:
                result2 = subprocess.run(
                    key_commands[1], 
                    input=result1.stdout,
                    text=True,
                    capture_output=True
                )
                if result2.returncode == 0:
                    self.logger.info("Successfully added Kali GPG key")
                    return
        
        except Exception as e:
            self.logger.warning(f"GPG key download failed: {e}")
        
        # Fallback: Update keyring package
        try:
            subprocess.run([
                'apt', 'install', '--reinstall', '-y',
                'kali-archive-keyring'
            ], check=True, timeout=120)
        except Exception as e:
            self.logger.error(f"Keyring package reinstall failed: {e}")

    def _free_up_disk_space(self):
        """Free up disk space"""
        self.logger.info("Freeing up disk space...")
        
        cleanup_commands = [
            ['apt', 'clean'],
            ['apt', 'autoclean'], 
            ['apt', 'autoremove', '-y'],
            ['rm', '-rf', '/var/cache/apt/archives/*.deb'],
            ['rm', '-rf', '/tmp/*'],
            ['journalctl', '--vacuum-size=100M']
        ]
        
        for cmd in cleanup_commands:
            try:
                subprocess.run(cmd, check=False, timeout=60)
            except Exception as e:
                self.logger.debug(f"Cleanup command failed: {e}")

    def install_package_with_fallback(self, package_name: str) -> bool:
        """Install package with multiple fallback methods"""
        methods = [
            self._install_normal,
            self._install_fix_broken, 
            self._install_allow_downgrades,
            self._install_force_yes
        ]
        
        for method in methods:
            if method(package_name):
                self.logger.info(f"Successfully installed {package_name}")
                return True
        
        self.logger.error(f"All installation methods failed for {package_name}")
        return False

    def _install_normal(self, package_name: str) -> bool:
        """Normal installation"""
        try:
            subprocess.run(
                ['apt', 'install', '-y', package_name],
                check=True,
                timeout=300
            )
            return True
        except Exception:
            return False

    def _install_fix_broken(self, package_name: str) -> bool:
        """Install with fix-broken"""
        try:
            subprocess.run([
                'apt', 'install', '-y', '--fix-broken', package_name
            ], check=True, timeout=300)
            return True
        except Exception:
            return False

    def _install_allow_downgrades(self, package_name: str) -> bool:
        """Install with allow downgrades"""
        try:
            subprocess.run([
                'apt', 'install', '-y', '--allow-downgrades', package_name
            ], check=True, timeout=300)
            return True
        except Exception:
            return False

    def _install_force_yes(self, package_name: str) -> bool:
        """Install with force-yes"""
        try:
            subprocess.run([
                'apt', 'install', '-y', '--force-yes', package_name
            ], check=True, timeout=300)
            return True
        except Exception:
            return False
