#!/usr/bin/env python3
"""
Dependency checker for the Motivation Letter Generator
This script will check if all required dependencies are installed and 
if the .env file is properly configured.
"""

import sys
import os
import importlib.util
import subprocess
from textwrap import dedent

# List of required packages
REQUIRED_PACKAGES = [
    "decouple",
    "google.generativeai",
    "crewai",
    "langchain",
    "bs4",  # beautifulsoup4 is imported as bs4
    "requests",
    "pydantic",
]

# Color codes for console output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def check_package(package_name):
    """Check if a package is installed"""
    try:
        # Try to import the module directly - more reliable than find_spec
        __import__(package_name)
        return True
    except ImportError:
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    if not os.path.exists('.env'):
        print(f"{RED}❌ .env file not found!{RESET}")
        return False
    
    try:
        from decouple import config
        api_key = config("GOOGLE_API_KEY", default=None)
        if not api_key:
            print(f"{YELLOW}⚠️ GOOGLE_API_KEY not found in .env file!{RESET}")
            return False
        return True
    except ImportError:
        print(f"{YELLOW}⚠️ Could not check .env file because 'decouple' is not installed.{RESET}")
        return False
    except Exception as e:
        print(f"{RED}❌ Error checking .env file: {e}{RESET}")
        return False

def check_poetry_env():
    """Check if we're running in the poetry environment"""
    try:
        result = subprocess.run(
            ["poetry", "env", "info"], 
            capture_output=True, 
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print(f"{GREEN}✓ Poetry environment is configured{RESET}")
            
            # Check if we're running inside the poetry env
            if "Path" in result.stdout:
                env_path = None
                for line in result.stdout.splitlines():
                    if "Path:" in line:
                        env_path = line.split("Path:")[1].strip()
                        break
                
                if env_path:
                    executable = sys.executable
                    if env_path in executable:
                        print(f"{GREEN}✓ Running inside poetry environment{RESET}")
                    else:
                        print(f"{RED}❌ Not running inside poetry environment!{RESET}")
                        print(f"Current Python: {executable}")
                        print(f"Poetry Python: {env_path}")
                        return False
            return True
        else:
            print(f"{RED}❌ Poetry environment not found or not configured{RESET}")
            return False
    except Exception as e:
        print(f"{RED}❌ Error checking poetry environment: {e}{RESET}")
        return False

def main():
    """Main function to check all dependencies"""
    print(f"\n{BOLD}Checking dependencies for Motivation Letter Generator...{RESET}\n")
    
    # Check Python version
    python_version = sys.version.split()[0]
    print(f"Python version: {python_version}")
    
    # Check if running in poetry environment
    poetry_env_ok = check_poetry_env()
    
    # Check packages
    all_packages_installed = True
    for package in REQUIRED_PACKAGES:
        installed = check_package(package)
        if installed:
            print(f"{GREEN}✓ {package} is installed{RESET}")
        else:
            print(f"{RED}❌ {package} is NOT installed{RESET}")
            all_packages_installed = False
    
    # Check .env file if decouple is installed
    env_ok = True
    if check_package("decouple"):
        print("\nChecking .env configuration...")
        env_ok = check_env_file()
    else:
        env_ok = False
        
    # Summary
    print("\n" + "="*50)
    if all_packages_installed and env_ok and poetry_env_ok:
        print(f"{GREEN}{BOLD}All dependencies are installed and configured correctly!{RESET}")
        print(f"You can now run the application with: {BOLD}python launcher.py{RESET}")
    else:
        print(f"{RED}{BOLD}Some dependencies are missing or misconfigured.{RESET}")
        
        if not poetry_env_ok:
            print("\nActivate the poetry environment with:")
            print(f"{BOLD}poetry shell{RESET}")
            print("Or run the application directly with:")
            print(f"{BOLD}poetry run python launcher.py{RESET}")
        
        if not all_packages_installed:
            print("\nInstall missing packages with one of these commands:")
            print(f"{BOLD}poetry install{RESET}")
            print("or")
            print(f"{BOLD}pip install -r requirements.txt{RESET}")
        
        if not env_ok:
            print("\nCreate or update your .env file with:")
            print(f"{BOLD}GOOGLE_API_KEY=your_api_key_here{RESET}")
    
    print("="*50 + "\n")
    
    return 0 if (all_packages_installed and env_ok and poetry_env_ok) else 1

if __name__ == "__main__":
    sys.exit(main())
