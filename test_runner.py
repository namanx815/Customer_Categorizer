#!/usr/bin/env python
"""
🧪 Interactive Test Suite for Customer Categorizer
Run this to test everything step by step
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

def print_test(test_name):
    print(f"{YELLOW}Testing: {test_name}{RESET}")

def print_pass(message):
    print(f"{GREEN}✅ {message}{RESET}")

def print_fail(message):
    print(f"{RED}❌ {message}{RESET}")

def print_warning(message):
    print(f"{YELLOW}⚠️  {message}{RESET}")

def print_info(message):
    print(f"{BLUE}ℹ️  {message}{RESET}")

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
    def run_all_tests(self):
        """Run all test suites"""
        
        print_header("🧪 CUSTOMER CATEGORIZER - TEST SUITE")
        
        # Basic tests
        self.test_python_installation()
        self.test_git_installation()
        self.test_project_structure()
        self.test_dependencies()
        self.test_module_imports()
        self.test_fastapi_app()
        self.test_environment_variables()
        self.test_docker_installation()
        
        # Optional tests
        try:
            self.test_local_app_startup()
        except Exception as e:
            print_warning(f"Local app test skipped: {e}")
        
        self.print_summary()
    
    def test_python_installation(self):
        """Test Python installation"""
        print_header("1. Python Installation")
        print_test("Checking Python version...")
        
        try:
            result = subprocess.run(
                ["python", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            version = result.stdout.strip() or result.stderr.strip()
            print_pass(f"Python installed: {version}")
            self.passed += 1
        except Exception as e:
            print_fail(f"Python check failed: {e}")
            self.failed += 1
    
    def test_git_installation(self):
        """Test Git installation"""
        print_test("Checking Git installation...")
        
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            version = result.stdout.strip()
            print_pass(f"Git installed: {version}")
            self.passed += 1
        except Exception as e:
            print_warning(f"Git not installed: {e}")
            self.warnings += 1
    
    def test_project_structure(self):
        """Test project structure"""
        print_header("2. Project Structure")
        
        required_files = {
            "app.py": "Main FastAPI application",
            "requirements.txt": "Python dependencies",
            "Dockerfile": "Docker configuration",
            "docker-compose.yml": "Docker Compose configuration",
            ".env.example": "Environment template",
            "DEPLOYMENT.md": "Deployment guide",
            "TESTING.md": "Testing guide",
        }
        
        required_dirs = {
            "src": "Source code",
            "templates": "HTML templates",
            "static": "Static files",
        }
        
        print_test("Checking required files...")
        for file, description in required_files.items():
            if Path(file).exists():
                print_pass(f"{file}: {description}")
                self.passed += 1
            else:
                print_fail(f"{file} missing: {description}")
                self.failed += 1
        
        print_test("Checking required directories...")
        for dir, description in required_dirs.items():
            if Path(dir).exists():
                print_pass(f"{dir}/: {description}")
                self.passed += 1
            else:
                print_fail(f"{dir}/ missing: {description}")
                self.failed += 1
    
    def test_dependencies(self):
        """Test Python dependencies"""
        print_header("3. Python Dependencies")
        print_test("Checking critical dependencies...")
        
        required_packages = {
            "fastapi": "Web framework",
            "uvicorn": "ASGI server",
            "pymongo": "MongoDB driver",
            "pandas": "Data manipulation",
            "scikit-learn": "Machine learning",
            "numpy": "Numerical computing",
            "xgboost": "Gradient boosting",
        }
        
        load_dotenv()
        
        for package, description in required_packages.items():
            try:
                __import__(package)
                print_pass(f"{package}: {description}")
                self.passed += 1
            except ImportError:
                print_fail(f"{package} not installed: {description}")
                self.failed += 1
    
    def test_module_imports(self):
        """Test custom module imports"""
        print_header("4. Custom Module Imports")
        print_test("Checking custom modules...")
        
        modules_to_test = [
            ("src.exception", "Exception handling"),
            ("src.logger", "Logging"),
            ("src.constant.application", "App constants"),
        ]
        
        for module, description in modules_to_test:
            try:
                __import__(module)
                print_pass(f"{module}: {description}")
                self.passed += 1
            except ImportError as e:
                print_fail(f"{module} import failed: {e}")
                self.failed += 1
    
    def test_fastapi_app(self):
        """Test FastAPI app creation"""
        print_header("5. FastAPI Application")
        print_test("Loading FastAPI app...")
        
        try:
            from app import app
            print_pass("FastAPI app loaded successfully")
            self.passed += 1
            
            print_info(f"App title: {app.title}")
            print_info(f"App version: {app.version}")
            print_info(f"Total routes: {len(app.routes)}")
            
            print_test("Checking routes...")
            expected_routes = ["/health", "/", "/train", "/docs"]
            for route in app.routes:
                if route.path in expected_routes:
                    print_pass(f"Route exists: {route.path}")
                    self.passed += 1
            
        except Exception as e:
            print_fail(f"FastAPI app loading failed: {e}")
            self.failed += 1
    
    def test_environment_variables(self):
        """Test environment variables"""
        print_header("6. Environment Variables")
        print_test("Checking .env configuration...")
        
        if Path(".env.example").exists():
            print_pass(".env.example template exists")
            self.passed += 1
        else:
            print_fail(".env.example not found")
            self.failed += 1
        
        if Path(".env").exists():
            print_pass(".env file exists")
            self.passed += 1
            load_dotenv()
            
            env_vars = ["APP_HOST", "APP_PORT"]
            for var in env_vars:
                if os.getenv(var):
                    print_pass(f"${var} is set")
                    self.passed += 1
                else:
                    print_warning(f"${var} not set")
                    self.warnings += 1
        else:
            print_warning(".env file not found (create from .env.example)")
            self.warnings += 1
    
    def test_docker_installation(self):
        """Test Docker installation"""
        print_header("7. Docker Installation")
        print_test("Checking Docker...")
        
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            version = result.stdout.strip()
            print_pass(f"Docker installed: {version}")
            self.passed += 1
        except Exception as e:
            print_warning(f"Docker not installed: {e}")
            self.warnings += 1
        
        print_test("Checking Docker Compose...")
        try:
            result = subprocess.run(
                ["docker-compose", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            version = result.stdout.strip()
            print_pass(f"Docker Compose installed: {version}")
            self.passed += 1
        except Exception as e:
            print_warning(f"Docker Compose not installed: {e}")
            self.warnings += 1
    
    def test_local_app_startup(self):
        """Test local app startup"""
        print_header("8. Local Application Startup (Optional)")
        print_test("Testing HTTP health endpoint...")
        
        try:
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print_pass(f"Health endpoint responded: {data['status']}")
                self.passed += 1
            else:
                print_warning(f"Health endpoint returned: {response.status_code}")
                self.warnings += 1
        except requests.exceptions.ConnectionError:
            print_warning("App not running on localhost:5000")
            self.warnings += 1
        except Exception as e:
            print_warning(f"Could not test running app: {e}")
            self.warnings += 1
    
    def print_summary(self):
        """Print test summary"""
        print_header("TEST SUMMARY")
        
        total = self.passed + self.failed + self.warnings
        
        print(f"{GREEN}✅ Passed:   {self.passed}/{total}{RESET}")
        print(f"{RED}❌ Failed:   {self.failed}/{total}{RESET}")
        print(f"{YELLOW}⚠️  Warnings: {self.warnings}/{total}{RESET}")
        
        print("\n" + "="*60)
        
        if self.failed == 0:
            print(f"{GREEN}{BOLD}✅ ALL TESTS PASSED!{RESET}")
        else:
            print(f"{RED}{BOLD}❌ SOME TESTS FAILED{RESET}")
        
        print("="*60 + "\n")
        
        if self.failed == 0:
            print(f"{GREEN}Next steps:{RESET}")
            print(f"1. Configure .env: cp .env.example .env && nano .env")
            print(f"2. Start app: python app.py")
            print(f"3. Open browser: http://localhost:5000")
            print(f"4. See docs: Read TESTING.md and DEPLOYMENT.md")
        else:
            print(f"{RED}Please fix the failed tests above and run again.{RESET}")

def main():
    """Main entry point"""
    try:
        runner = TestRunner()
        runner.run_all_tests()
        sys.exit(0 if runner.failed == 0 else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Test interrupted by user{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}Unexpected error: {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
