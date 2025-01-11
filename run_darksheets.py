#!/usr/bin/env python3
"""
DarkSheets Runner
"""
import os
import sys
import traceback
from tkinter import messagebox

def main():
    try:
        # Add src directory to Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.join(current_dir, 'src')
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)

        from darkweb_gui import main
        main()
    except Exception as e:
        error_msg = f"Error starting DarkSheets:\n{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        messagebox.showerror("DarkSheets Error", error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()
