"""
System Verification Script
Tests all components before delivery
"""
import sys
import os
from pathlib import Path

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def check_mark(status):
    return "✓" if status else "✗"

def main():
    print_header("TANGENT CONNECT - AI VISION BEVERAGE SYSTEM - FINAL VERIFICATION")
    
    all_passed = True
    
    # 1. Check Python Version
    print_header("1. Python Version Check")
    version = sys.version_info
    python_ok = version.major == 3 and version.minor >= 9
    print(f"{check_mark(python_ok)} Python {version.major}.{version.minor}.{version.micro}")
    if not python_ok:
        print("   WARNING: Python 3.9+ required")
        all_passed = False
    
    # 2. Check Dependencies
    print_header("2. Required Packages")
    packages = {
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'PIL': 'Pillow',
        'tkinter': 'tkinter (built-in)',
        'ultralytics': 'ultralytics',
        'pandas': 'pandas',
        'ttkbootstrap': 'ttkbootstrap',
        'yaml': 'pyyaml'
    }
    
    for import_name, package_name in packages.items():
        try:
            if import_name == 'cv2':
                import cv2
            elif import_name == 'PIL':
                from PIL import Image
            elif import_name == 'tkinter':
                import tkinter
            elif import_name == 'ultralytics':
                from ultralytics import YOLO
            elif import_name == 'pandas':
                import pandas
            elif import_name == 'numpy':
                import numpy
            elif import_name == 'ttkbootstrap':
                import ttkbootstrap
            elif import_name == 'yaml':
                import yaml
            
            print(f"✓ {package_name}")
        except ImportError:
            print(f"✗ {package_name} - NOT INSTALLED")
            all_passed = False
    
    # 3. Check Project Structure
    print_header("3. Project Structure")
    required_files = [
        'main.py',
        'RUN_APP.bat',
        'requirements.txt',
        'config/settings.py',
        'app_logo.jpg',
        'src/__init__.py',
        'src/gui/main_window.py',
        'src/camera/stream_manager.py',
        'src/detection/yolo_detector.py',
        'src/tracking/centroid_tracker.py',
        'src/database/db_manager.py',
        'training_wizard.py',
        'demo_video.py',
        'test_camera.py'
    ]
    
    for file_path in required_files:
        path = Path(file_path)
        exists = path.exists()
        print(f"{check_mark(exists)} {file_path}")
        if not exists:
            all_passed = False
    
    # 4. Check Directories
    print_header("4. Required Directories")
    required_dirs = ['data', 'models', 'exports', 'logs', 'config', 'src']
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        exists = path.exists() and path.is_dir()
        print(f"{check_mark(exists)} {dir_path}/")
        if not exists:
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"   → Created {dir_path}/")
            except:
                all_passed = False
    
    # 5. Test Imports
    print_header("5. Module Import Test")
    try:
        sys.path.insert(0, str(Path.cwd()))
        
        from src.camera import CameraManager
        print("✓ CameraManager imported")
        
        from src.detection import BeverageDetector
        print("✓ BeverageDetector imported")
        
        from src.tracking import BeverageCounter
        print("✓ BeverageCounter imported")
        
        from src.database import DatabaseManager
        print("✓ DatabaseManager imported")
        
        from config.settings import WINDOW_TITLE
        print("✓ Settings imported")
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        all_passed = False
    
    # 6. Test Camera Access
    print_header("6. Camera Access Test")
    try:
        import cv2
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✓ Webcam accessible (Resolution: {frame.shape[1]}x{frame.shape[0]})")
            else:
                print("⚠ Webcam opened but cannot read frames")
            cap.release()
        else:
            print("⚠ Webcam not accessible (may be in use or not connected)")
            print("   Note: This is OK if you plan to use Demo/RTSP/File mode")
    except Exception as e:
        print(f"⚠ Camera test error: {e}")
    
    # 7. Test Demo Mode
    print_header("7. Demo Mode Test")
    try:
        from demo_video import DemoCameraStream
        demo = DemoCameraStream()
        ret, frame = demo.read()
        if ret and frame is not None:
            print(f"✓ Demo mode working (Frame shape: {frame.shape})")
        else:
            print("✗ Demo mode failed")
            all_passed = False
        demo.release()
    except Exception as e:
        print(f"✗ Demo mode error: {e}")
        all_passed = False
    
    # 8. Test YOLO Model
    print_header("8. YOLO Model Test")
    try:
        from ultralytics import YOLO
        print("✓ Ultralytics YOLO available")
        
        # Check if model file exists
        model_files = list(Path('.').glob('yolov8*.pt'))
        if model_files:
            print(f"✓ YOLO model found: {model_files[0].name}")
        else:
            print("⚠ No YOLO model file (will download on first run)")
    except Exception as e:
        print(f"✗ YOLO test error: {e}")
        all_passed = False
    
    # 9. Test Database
    print_header("9. Database Test")
    try:
        from src.database import DatabaseManager
        db = DatabaseManager("data/test_verify.db")
        session_id = db.create_session("test_url")
        db.end_session(session_id, {'total_beverages': 5, 'total_alcoholic': 2, 'total_non_alcoholic': 3})
        print("✓ Database operations working")
        db.close()
        
        # Clean up test db
        test_db = Path("data/test_verify.db")
        if test_db.exists():
            test_db.unlink()
    except Exception as e:
        print(f"✗ Database test error: {e}")
        all_passed = False
    
    # Final Report
    print_header("FINAL VERIFICATION RESULT")
    if all_passed:
        print("\n✅ ALL CHECKS PASSED!")
        print("\nThe system is ready for delivery.")
        print("\nQuick Start:")
        print("  1. Double-click RUN_APP.bat")
        print("  2. Select camera source (Webcam/Demo/RTSP/File)")
        print("  3. Click Connect")
        print("  4. Click Start")
        print("\nFor detailed instructions, see:")
        print("  - README.md")
        print("  - QUICK_USER_GUIDE.md")
        print("  - FINAL_WORKING_GUIDE.txt")
    else:
        print("\n⚠️ SOME CHECKS FAILED")
        print("\nPlease fix the issues above before delivery.")
        print("\nCommon solutions:")
        print("  - Run: pip install -r requirements.txt")
        print("  - Check Python version: python --version")
        print("  - Ensure all files are in correct locations")
    
    print("\n" + "="*70)
    print("\nPress Enter to exit...")
    input()
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
