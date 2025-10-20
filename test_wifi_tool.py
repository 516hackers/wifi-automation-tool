#!/usr/bin/env python3

"""
Comprehensive Test Suite for WiFi Automation Tool
Run this to check for syntax errors, import issues, and basic functionality
"""

import os
import sys
import subprocess
import importlib
import ast
import logging

class WiFiToolTester:
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for tests"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def print_result(self, test_name, passed, error=None):
        """Print test result"""
        if passed:
            print(f"✅ {test_name} - PASSED")
            self.passed_tests += 1
        else:
            print(f"❌ {test_name} - FAILED")
            if error:
                print(f"   Error: {error}")
            self.failed_tests += 1
    
    def test_file_exists(self, filepath):
        """Test if file exists"""
        try:
            exists = os.path.exists(filepath)
            self.print_result(f"File exists: {filepath}", exists)
            return exists
        except Exception as e:
            self.print_result(f"File exists: {filepath}", False, str(e))
            return False
    
    def test_python_syntax(self, filepath):
        """Test Python file syntax"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source_code = f.read()
            ast.parse(source_code)
            self.print_result(f"Python syntax: {filepath}", True)
            return True
        except SyntaxError as e:
            self.print_result(f"Python syntax: {filepath}", False, f"Syntax error: {e}")
            return False
        except Exception as e:
            self.print_result(f"Python syntax: {filepath}", False, str(e))
            return False
    
    def test_import_module(self, module_path, module_name):
        """Test if module can be imported"""
        try:
            # Add to Python path
            if os.path.dirname(module_path) not in sys.path:
                sys.path.insert(0, os.path.dirname(module_path))
            
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            self.print_result(f"Import module: {module_name}", True)
            return True
        except Exception as e:
            self.print_result(f"Import module: {module_name}", False, str(e))
            return False
    
    def test_requirements_parsing(self):
        """Test requirements.txt parsing"""
        try:
            if not self.test_file_exists("requirements.txt"):
                return False
            
            with open("requirements.txt", "r") as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            
            self.print_result("Requirements.txt parsing", True)
            return True
        except Exception as e:
            self.print_result("Requirements.txt parsing", False, str(e))
            return False
    
    def test_directory_structure(self):
        """Test project directory structure"""
        required_dirs = ["src", "drivers", "logs", "config", "backups"]
        required_files = ["main.py", "requirements.txt", "install.sh", "recovery.sh"]
        
        all_passed = True
        
        # Test directories
        for directory in required_dirs:
            if os.path.exists(directory) and os.path.isdir(directory):
                self.print_result(f"Directory exists: {directory}", True)
            else:
                self.print_result(f"Directory exists: {directory}", False)
                all_passed = False
        
        # Test files
        for file in required_files:
            if os.path.exists(file) and os.path.isfile(file):
                self.print_result(f"File exists: {file}", True)
            else:
                self.print_result(f"File exists: {file}", False)
                all_passed = False
        
        return all_passed
    
    def test_shell_scripts(self):
        """Test shell script syntax"""
        scripts = ["install.sh", "recovery.sh"]
        
        for script in scripts:
            if not self.test_file_exists(script):
                continue
            
            try:
                # Check if script has valid shebang and basic syntax
                with open(script, 'r') as f:
                    first_line = f.readline().strip()
                
                if first_line.startswith("#!/bin/bash") or first_line.startswith("#!/bin/sh"):
                    # Test basic syntax check
                    result = subprocess.run(
                        ["bash", "-n", script],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        self.print_result(f"Shell script syntax: {script}", True)
                    else:
                        self.print_result(f"Shell script syntax: {script}", False, result.stderr)
                else:
                    self.print_result(f"Shell script syntax: {script}", False, "Missing or invalid shebang")
            except Exception as e:
                self.print_result(f"Shell script syntax: {script}", False, str(e))
    
    def test_main_script_execution(self):
        """Test main script basic execution (dry run)"""
        try:
            # Test with help flag to avoid actual operations
            result = subprocess.run(
                [sys.executable, "main.py", "--help"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 or "usage:" in result.stdout or "usage:" in result.stderr:
                self.print_result("Main script basic execution", True)
                return True
            else:
                self.print_result("Main script basic execution", False, result.stderr)
                return False
        except subprocess.TimeoutExpired:
            self.print_result("Main script basic execution", False, "Timeout")
            return False
        except Exception as e:
            self.print_result("Main script basic execution", False, str(e))
            return False
    
    def test_class_initialization(self):
        """Test if main classes can be initialized"""
        try:
            # Add src to path
            sys.path.insert(0, 'src')
            
            # Test WiFiScanner
            from src.wifi_scanner import WiFiScanner
            scanner = WiFiScanner()
            self.print_result("WiFiScanner initialization", True)
            
            # Test DriverManager
            from src.driver_manager import DriverManager
            driver_mgr = DriverManager()
            self.print_result("DriverManager initialization", True)
            
            # Test ErrorHandler
            from src.error_handler import ErrorHandler
            error_handler = ErrorHandler()
            self.print_result("ErrorHandler initialization", True)
            
            # Test PackageManager
            from src.package_manager import PackageManager
            pkg_mgr = PackageManager()
            self.print_result("PackageManager initialization", True)
            
            # Test SystemHealth
            from src.system_health import SystemHealth
            sys_health = SystemHealth()
            self.print_result("SystemHealth initialization", True)
            
            return True
            
        except Exception as e:
            self.print_result("Class initialization", False, str(e))
            return False
    
    def test_config_files(self):
        """Test configuration files"""
        config_files = {
            "config/config.json": self._test_json_syntax,
            "drivers/common_drivers.json": self._test_json_syntax
        }
        
        for config_file, test_func in config_files.items():
            if self.test_file_exists(config_file):
                test_func(config_file)
    
    def _test_json_syntax(self, filepath):
        """Test JSON file syntax"""
        try:
            import json
            with open(filepath, 'r') as f:
                json.load(f)
            self.print_result(f"JSON syntax: {filepath}", True)
            return True
        except Exception as e:
            self.print_result(f"JSON syntax: {filepath}", False, str(e))
            return False
    
    def test_permissions(self):
        """Test file permissions"""
        executable_files = ["main.py", "install.sh", "recovery.sh"]
        
        for file in executable_files:
            if not self.test_file_exists(file):
                continue
            
            try:
                # Check if file is executable
                if os.access(file, os.X_OK):
                    self.print_result(f"File executable: {file}", True)
                else:
                    self.print_result(f"File executable: {file}", False, "File not executable")
            except Exception as e:
                self.print_result(f"File executable: {file}", False, str(e))
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive WiFi Tool Tests")
        print("=" * 50)
        
        # Phase 1: Basic structure tests
        print("\n📁 PHASE 1: Project Structure Tests")
        self.test_directory_structure()
        
        # Phase 2: File existence tests
        print("\n📄 PHASE 2: File Existence Tests")
        important_files = [
            "main.py", "requirements.txt", "install.sh", "recovery.sh",
            "src/__init__.py", "src/wifi_scanner.py", "src/driver_manager.py",
            "src/error_handler.py", "src/package_manager.py", "src/system_health.py",
            "src/utils.py", "config/config.json", "drivers/common_drivers.json"
        ]
        
        for file in important_files:
            self.test_file_exists(file)
        
        # Phase 3: Syntax tests
        print("\n🔍 PHASE 3: Syntax Validation Tests")
        python_files = [
            "main.py", 
            "src/wifi_scanner.py", 
            "src/driver_manager.py",
            "src/error_handler.py", 
            "src/package_manager.py",
            "src/system_health.py", 
            "src/utils.py",
            "test_wifi_tool.py"
        ]
        
        for py_file in python_files:
            if self.test_file_exists(py_file):
                self.test_python_syntax(py_file)
        
        self.test_shell_scripts()
        self.test_config_files()
        self.test_requirements_parsing()
        
        # Phase 4: Import tests
        print("\n🐍 PHASE 4: Import Tests")
        python_modules = [
            ("src/wifi_scanner.py", "wifi_scanner"),
            ("src/driver_manager.py", "driver_manager"),
            ("src/error_handler.py", "error_handler"),
            ("src/package_manager.py", "package_manager"),
            ("src/system_health.py", "system_health"),
            ("src/utils.py", "utils")
        ]
        
        for filepath, module_name in python_modules:
            if self.test_file_exists(filepath):
                self.test_import_module(filepath, module_name)
        
        # Phase 5: Functionality tests
        print("\n⚙️ PHASE 5: Basic Functionality Tests")
        self.test_class_initialization()
        self.test_main_script_execution()
        self.test_permissions()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"📈 Success Rate: {(self.passed_tests/(self.passed_tests + self.failed_tests))*100:.1f}%")
        
        if self.failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED! Your WiFi tool should work correctly.")
            return True
        else:
            print(f"\n⚠️  {self.failed_tests} tests failed. Please check the errors above.")
            return False

def quick_test():
    """Quick test for basic functionality"""
    print("🔍 Running Quick Test...")
    
    # Check essential files
    essential_files = ["main.py", "src/__init__.py", "requirements.txt"]
    missing_files = []
    
    for file in essential_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    # Check Python syntax of main file
    try:
        with open("main.py", "r") as f:
            ast.parse(f.read())
        print("✅ Main.py syntax: OK")
    except SyntaxError as e:
        print(f"❌ Main.py syntax error: {e}")
        return False
    
    # Check if we can import basic modules
    try:
        sys.path.insert(0, 'src')
        from src.utils import check_root, setup_logging
        print("✅ Basic imports: OK")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    print("✅ Quick test passed!")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        success = quick_test()
        sys.exit(0 if success else 1)
    else:
        tester = WiFiToolTester()
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
