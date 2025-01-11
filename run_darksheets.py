#!/usr/bin/env python3
"""
DarkSheets Runner
"""
import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from darkweb_gui import DarkWebGUI

def main():
    """Run the DarkSheets GUI application"""
    try:
        app = DarkWebGUI()
        app.run()
    except Exception as e:
        print(f"Error starting DarkSheets: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
