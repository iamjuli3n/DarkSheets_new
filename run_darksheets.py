#!/usr/bin/env python3
"""
DarkSheets Launcher
Starts the DarkSheets GUI application
"""

import os
import sys

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.darkweb_gui import main

if __name__ == "__main__":
    main()
