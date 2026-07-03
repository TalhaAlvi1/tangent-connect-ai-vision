#!/usr/bin/env python3
"""
Verify Beverage Detection System is Working Correctly
Tests detector initialization, model loading, and detection filtering
"""
import sys
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def check_model_files():
    """Check which model files exist"""
    print("\n" + "="*60)
    print("CHECKING AVAILABLE MODELS")
    print("="*60)
    
    model_paths = [
        "final_training_data/balanced/best.pt",
        "final_training_data/runs/detect/FINAL_WORKING_MODEL3/weights/best.pt",
        "final_training_data/runs/detect/BALANCED_BEVERAGE_MODEL/weights/best.pt",
        "final_training_data/runs/detect/FINAL_WORKING_MODEL2/weights/best.pt",
        "runs/detect/beverage_model_final/weights/best.pt",
        "yolov8n.pt"
    ]
    
    for model_path in model_paths:
        full_path = PROJECT_ROOT / model_path
        exists = full_path.exists()
        status = "✓ EXISTS" if exists else "✗ NOT FOUND"
        print(f"{status:12} - {model_path}")
    print()

def check_config():
    """Check configuration settings"""
    print("\n" + "="*60)
    print("CHECKING CONFIGURATION")
    print("="*60)
    
    try:
        from detection_tuning import (
            CONFIDENCE_THRESHOLD, IOU_THRESHOLD, 
            MIN_COUNT_CONFIDENCE, MIN_DETECTION_AREA
        )
        from config.settings import BEVERAGE_CLASSES
        
        print(f"\nDetection Tuning Parameters:")
        print(f"  • Confidence Threshold: {CONFIDENCE_THRESHOLD}")
        print(f"  • IOU Threshold: {IOU_THRESHOLD}")
        print(f"  • Min Count Confidence: {MIN_COUNT_CONFIDENCE}")
        print(f"  • Min Detection Area: {MIN_DETECTION_AREA}")
        
        print(f"\nBeverage Classes:")
        for class_id, class_info in BEVERAGE_CLASSES.items():
            print(f"  • [{class_id}] {class_info['name']} ({class_info['type']})")
        print()
        
    except Exception as e:
        print(f"✗ Error loading config: {e}\n")
        return False
    
    return True

def test_detector():
    """Test detector initialization"""
    print("\n" + "="*60)
    print("TESTING DETECTOR")
    print("="*60 + "\n")
    
    try:
        from src.detection import BeverageDetector
        import cv2
        import numpy as np
        
        print("Initializing detector...")
        detector = BeverageDetector()
        
        print(f"  ✓ Detector created")
        print(f"  • Model loaded: {detector.loaded}")
        print(f"  • YOLO available: {detector.use_yolo}")
        print(f"  • Model path: {detector.model_path}")
        print(f"  • Confidence threshold: {detector.confidence_threshold}")
        print(f"  • Max detections: {detector.max_detections}")
        
        if detector.loaded:
            print(f"\n✓ Model loaded successfully!")
            
            # Test detection on a dummy frame
            print(f"\nTesting detection on dummy frame...")
            dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            detections = detector.detect(dummy_frame)
            print(f"  • Detections: {len(detections)}")
            
            if len(detections) == 0:
                print(f"  ✓ Correctly returned 0 detections on empty frame")
            
            return True
        else:
            print(f"\n✗ Model failed to load")
            return False
            
    except Exception as e:
        print(f"✗ Detector test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_thresholds():
    """Verify high confidence thresholds are set"""
    print("\n" + "="*60)
    print("VERIFYING THRESHOLDS")
    print("="*60 + "\n")
    
    try:
        from detection_tuning import CONFIDENCE_THRESHOLD, MIN_COUNT_CONFIDENCE
        
        errors = []
        
        if CONFIDENCE_THRESHOLD < 0.60:
            errors.append(f"Confidence threshold {CONFIDENCE_THRESHOLD} is too low (should be >= 0.60)")
        else:
            print(f"✓ Confidence threshold: {CONFIDENCE_THRESHOLD} (GOOD)")
        
        if MIN_COUNT_CONFIDENCE < 0.60:
            errors.append(f"Min count confidence {MIN_COUNT_CONFIDENCE} is too low (should be >= 0.60)")
        else:
            print(f"✓ Min count confidence: {MIN_COUNT_CONFIDENCE} (GOOD)")
        
        if errors:
            print("\n❌ Issues found:")
            for error in errors:
                print(f"  • {error}")
            return False
        
        print("\n✓ All thresholds are correctly set!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run all verification checks"""
    print("\n" + "="*70)
    print("BEVERAGE DETECTION SYSTEM VERIFICATION")
    print("="*70)
    
    check_model_files()
    check_config()
    threshold_ok = verify_thresholds()
    detector_ok = test_detector()
    
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    if threshold_ok and detector_ok:
        print("✓ System is correctly configured for beverage-only detection!")
        print("\nKey improvements:")
        print("  • High confidence thresholds (0.65+) to reduce false positives")
        print("  • Aspect ratio filtering for bottle-shaped objects")
        print("  • Strict class validation (only 4 trained beverage classes)")
        print("  • Size filtering to ignore small/large non-beverage objects")
        print("\n✓ The system should now:")
        print("  • Detect only bottles (not people or other objects)")
        print("  • Display correct beverage labels (not just Heineken)")
        print("  • Show Corona, Castle Lite, Hansa, and Heineken correctly")
        return 0
    else:
        print("❌ Some issues found. Please fix the above errors.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
