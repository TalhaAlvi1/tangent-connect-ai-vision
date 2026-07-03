#!/usr/bin/env python3
"""
Beverage Detection & Counting System
Main Application Entry Point

This is a professional desktop application for real-time beverage
identification and counting using AI-powered computer vision.

Author: AI Development Team
Version: 1.0.0
License: MIT
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'cv2', 'numpy', 'PIL', 'tkinter', 
        'ultralytics', 'pandas', 'yaml', 'ttkbootstrap'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'PIL':
                from PIL import Image
            elif package == 'tkinter':
                import tkinter
            elif package == 'ultralytics':
                from ultralytics import YOLO
            elif package == 'pandas':
                import pandas
            elif package == 'numpy':
                import numpy
            elif package == 'yaml':
                import yaml
            elif package == 'ttkbootstrap':
                import ttkbootstrap
        except ImportError:
            missing.append(package)
    
    if missing:
        print("=" * 60)
        print("MISSING DEPENDENCIES")
        print("=" * 60)
        print("\nThe following packages are required but not installed:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nPlease run: pip install -r requirements.txt")
        print("=" * 60)
        return False
    
    return True

def main():
    """Main application entry point"""
    print("=" * 60)
    print("BEVERAGE DETECTION & COUNTING SYSTEM v1.0")
    print("=" * 60)
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        input("\nPress Enter to exit...")
        return 1
    
    print("✓ All dependencies found")
    print()
    
    # Import after dependency check
    try:
        from src.gui.main_window import BeverageDetectionApp
        import tkinter as tk
        from tkinter import messagebox
        
        # Try to use modern theme
        try:
            import ttkbootstrap as ttk
            from ttkbootstrap import Style
            use_modern_theme = True
            print("✓ Using modern theme (ttkbootstrap)")
        except ImportError:
            import tkinter.ttk as ttk
            use_modern_theme = False
            print("ℹ Using standard theme")
        
        print()
        print("Starting application...")
        print("=" * 60)
        print(" Video pipeline improvements loaded:")
        print("   • Enhanced RTSP connection handling")
        print("   • Automatic reconnection (5 attempts)")
        print("   • Improved frame buffering (5 frames)")
        print("   • Frame skipping for better performance")
        print("   • Better error handling and logging")
        print("=" * 60)
        print()
        
        # Create root window
        if use_modern_theme:
            root = ttk.Window(themename="cosmo")  # Modern blue theme
        else:
            root = tk.Tk()
        
        # Create application
        app = BeverageDetectionApp(root)
        
        # Set window close handler
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # Start main loop
        root.mainloop()
        
        return 0
        
    except Exception as e:
        print(f"\nERROR: Failed to start application")
        print(f"Details: {str(e)}")
        print("\nPlease check:")
        print("1. All dependencies are installed")
        print("2. Python version is 3.9 or higher")
        print("3. You're running from the project root directory")
        
        import traceback
        traceback.print_exc()
        
        input("\nPress Enter to exit...")
        return 1

if __name__ == "__main__":
    sys.exit(main())
