#!/usr/bin/env python3
"""
DarkSheets Launcher
Starts the DarkSheets GUI application
"""

import os
import sys

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from darkweb_gui import DarkWebGUI

if __name__ == "__main__":
    try:
        gui = DarkWebGUI()
        gui.run()
    except Exception as e:
        print(f"Error starting DarkSheets: {str(e)}")
        input("Press Enter to exit...")
