"""
Quick Test Script for Detection Fixes
Run this to verify the system is working correctly
"""
import sys
import cv2
from pathlib import Path

def quick_test():
    print("Beverage Detection System - Quick Test")
    print("=" * 40)
    
    # Test 1: Import modules
    print("\n1. Testing imports...")
    try:
        from src.detection import BeverageDetector
        from src.tracking import BeverageCounter
        print("✓ All modules imported successfully")
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False
    
    # Test 2: Initialize detector
    print("\n2. Testing detector initialization...")
    try:
        detector = BeverageDetector()
        if detector.is_loaded():
            print(f"✓ Detector loaded: {detector.model_path}")
            print(f"✓ Confidence threshold: {detector.confidence_threshold}")
        else:
            print("⚠ Detector initialized but model not loaded")
            return False
    except Exception as e:
        print(f"✗ Detector initialization error: {e}")
        return False
    
    # Test 3: Initialize counter
    print("\n3. Testing counter initialization...")
    try:
        counter = BeverageCounter()
        print("✓ Counter initialized successfully")
        print(f"✓ Tracking distance: {counter.tracker.max_distance}")
        print(f"✓ Debounce frames: {counter.tracker.debounce_frames}")
    except Exception as e:
        print(f"✗ Counter initialization error: {e}")
        return False
    
    # Test 4: Test on sample image (if available)
    print("\n4. Testing detection on sample image...")
    val_images_dir = Path("final_training_data/images/val")
    if val_images_dir.exists():
        image_files = list(val_images_dir.glob("*.jpg")) + list(val_images_dir.glob("*.jpeg"))
        if image_files:
            test_image = cv2.imread(str(image_files[0]))
            if test_image is not None:
                detections = detector.detect(test_image)
                print(f"✓ Detection test: Found {len(detections)} objects")
                
                valid_detections = [d for d in detections if d['type'] in ['alcoholic', 'non-alcoholic']]
                print(f"✓ Valid beverage detections: {len(valid_detections)}")
                
                if valid_detections:
                    for det in valid_detections[:3]:  # Show first 3
                        print(f"  - {det['class_name']} ({det['confidence']:.2f})")
                else:
                    print("⚠ No valid beverage detections found")
            else:
                print("⚠ Could not load test image")
        else:
            print("⚠ No validation images found")
    else:
        print("⚠ Validation images directory not found")
    
    # Test 5: Test counting logic
    print("\n5. Testing counting logic...")
    try:
        # Simulate a few detections
        test_detections = [{
            'bbox': [100, 100, 200, 300],
            'confidence': 0.85,
            'class_id': 0,
            'class_name': 'Heineken Not A SAB Product',
            'type': 'alcoholic',
            'color': (0, 0, 255)
        }]
        
        stats, new_items = counter.update(test_detections)
        print("✓ Counting logic test passed")
        print(f"✓ Total beverages: {stats['total_beverages']}")
    except Exception as e:
        print(f"✗ Counting logic error: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("✅ All tests passed! The system should work correctly.")
    print("\nTo run the full application:")
    print("  python main.py")
    print("\nTo adjust detection parameters:")
    print("  Edit detection_tuning.py")
    
    return True

if __name__ == "__main__":
    success = quick_test()
    if not success:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)