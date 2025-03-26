#!/usr/bin/env python3
"""
Dependency fixer for the Motivation Letter Generator
This script will install all required dependencies using pip
for users who aren't comfortable with Poetry.
"""

import subprocess
import sys
import os
from textwrap import dedent

# Color codes for console output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def check_pip():
    """Check if pip is available"""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError:
        return False

def install_package(package):
    """Install a package using pip"""
    print(f"Installing {package}...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"{GREEN}✓ {package} installed successfully{RESET}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{RED}Failed to install {package}{RESET}")
        print(f"Error: {e}")
        return False

def main():
    """Main function to fix dependencies"""
    print(f"\n{BOLD}Motivation Letter Generator - Dependency Fixer{RESET}\n")
    
    if not check_pip():
        print(f"{RED}Pip is not available. Please install pip first.{RESET}")
        return 1
    
    print(f"{YELLOW}This script will install all required dependencies for the Motivation Letter Generator.{RESET}")
    print("Required packages:")
    print("- python-decouple (for environment variables)")
    print("- google-generativeai (for text generation)")
    print("- beautifulsoup4 (for web scraping)")
    print("- requests (for HTTP requests)")
    print("- crewai (optional, for advanced features)")
    print("- langchain and langchain-community (optional, for advanced features)")
    
    choice = input("\nDo you want to install these packages? (y/n): ").lower()
    if choice != 'y':
        print("Installation cancelled.")
        return 0
    
    # Essential packages
    essential_packages = [
        "python-decouple", 
        "google-generativeai", 
        "beautifulsoup4", 
        "requests"
    ]
    
    # Advanced packages (optional)
    advanced_packages = [
        "crewai", 
        "langchain", 
        "langchain-community", 
        "duckduckgo-search",
        "pydantic"
    ]
    
    # Install essential packages
    print(f"\n{BOLD}Installing essential dependencies...{RESET}")
    all_successful = True
    for package in essential_packages:
        if not install_package(package):
            all_successful = False
    
    # Ask for advanced packages
    print(f"\n{YELLOW}Do you want to install optional advanced dependencies?{RESET}")
    print("These are only needed if you want to use the CrewAI features.")
    advanced_choice = input("Install advanced dependencies? (y/n): ").lower()
    
    if advanced_choice == 'y':
        print(f"\n{BOLD}Installing advanced dependencies...{RESET}")
        for package in advanced_packages:
            if not install_package(package):
                all_successful = False
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        print(f"\n{YELLOW}You need a Google API key to use this application.{RESET}")
        create_env = input("Do you want to create a .env file with your API key? (y/n): ").lower()
        
        if create_env == 'y':
            api_key = input("Enter your Google API key: ")
            with open('.env', 'w') as f:
                f.write(f"GOOGLE_API_KEY={api_key}\n")
            print(f"{GREEN}.env file created successfully!{RESET}")
    
    # Final message
    if all_successful:
        print(f"\n{GREEN}{BOLD}All dependencies installed successfully!{RESET}")
        print(f"You can now run the application with: {BOLD}python launcher.py{RESET}")
    else:
        print(f"\n{YELLOW}{BOLD}Some dependencies could not be installed.{RESET}")
        print("Try installing them manually or use Poetry with: poetry install")
    
    return 0 if all_successful else 1

if __name__ == "__main__":
    sys.exit(main())
