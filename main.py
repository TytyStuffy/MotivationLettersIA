#!/usr/bin/env python3
"""
Motivation Letter Generator - Main entry point
This script redirects to the launcher for backward compatibility.
"""
import sys
import os
from textwrap import dedent

try:
    from launcher import main as launcher_main
    
    if __name__ == "__main__":
        sys.exit(launcher_main())
except ImportError as e:
    print(f"\n❌ ERROR: {e}")
    print("Please install all dependencies using one of the following commands:")
    print("    pip install -r requirements.txt")
    print("    or")
    print("    poetry install\n")
    sys.exit(1)
