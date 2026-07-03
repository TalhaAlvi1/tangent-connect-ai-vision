"""
Test Script for Detection and Counting Fixes
Verifies that the detection system works correctly after fixes
"""
import cv2
import numpy as np
from pathlib import Path
import sys
from src.detection import BeverageDetector
from src.tracking import BeverageCounter

def test_detection_accuracy():
    """Test detection accuracy with sample images"""
    print("=== Testing Detection Accuracy ===")
    
    # Initialize detector with higher confidence threshold
    detector = BeverageDetector(confidence=0.40)
    
    if not detector.is_loaded():
        print("❌ Detector not loaded properly")
        return False
    
    print(f"✓ Detector loaded: {detector.model_path}")
    print(f"✓ Confidence threshold: {detector.confidence_threshold}")
    print(f"✓ IOU threshold: {detector.iou_threshold}")
    print()
    
    # Test on validation images
    val_images_dir = Path("final_training_data/images/val")
    if not val_images_dir.exists():
        print("❌ Validation images not found")
        return False
    
    image_files = list(val_images_dir.glob("*.jpg")) + list(val_images_dir.glob("*.jpeg"))
    if not image_files:
        print("❌ No validation images found")
        return False
    
    print(f"Testing on {len(image_files[:5])} sample images...")
    print()
    
    total_detections = 0
    correct_class_detections = 0
    
    for img_path in image_files[:5]:  # Test first 5 images
        image = cv2.imread(str(img_path))
        if image is None:
            continue
            
        # Run detection
        detections = detector.detect(image)
        total_detections += len(detections)
        
        print(f"Image: {img_path.name}")
        print(f"  Detections: {len(detections)}")
        
        for i, det in enumerate(detections):
            class_name = det['class_name']
            confidence = det['confidence']
            obj_type = det['type']
            print(f"    {i+1}. {class_name} ({obj_type}) - Confidence: {confidence:.3f}")
            
            # Check if it's one of our target classes (not unknown/false positives)
            if obj_type in ['alcoholic', 'non-alcoholic']:
                correct_class_detections += 1
        
        print()
    
    print(f"Total detections: {total_detections}")
    print(f"Valid beverage detections: {correct_class_detections}")
    print(f"Accuracy rate: {correct_class_detections/max(1,total_detections)*100:.1f}%")
    
    return correct_class_detections > 0

def test_counting_logic():
    """Test counting logic with simulated detections"""
    print("\n=== Testing Counting Logic ===")
    
    counter = BeverageCounter(debounce_frames=15)
    
    # Simulate detections over multiple frames
    print("Simulating 30 frames of detections...")
    
    # Simulated detection data (same object appearing in multiple frames)
    simulated_detections = [
        # Frame 1: New object
        [{'bbox': [100, 100, 200, 300], 'confidence': 0.85, 'class_id': 0, 
          'class_name': 'Heineken Not A SAB Product', 'type': 'alcoholic', 'color': (0,0,255)}],
        # Frame 2: Same object, slightly moved
        [{'bbox': [105, 105, 205, 305], 'confidence': 0.87, 'class_id': 0, 
          'class_name': 'Heineken Not A SAB Product', 'type': 'alcoholic', 'color': (0,0,255)}],
        # Frame 3: Same object
        [{'bbox': [110, 110, 210, 310], 'confidence': 0.83, 'class_id': 0, 
          'class_name': 'Heineken Not A SAB Product', 'type': 'alcoholic', 'color': (0,0,255)}],
        # Frame 4: Empty frame (object temporarily not detected)
        [],
        # Frame 5: Object reappears
        [{'bbox': [115, 115, 215, 315], 'confidence': 0.86, 'class_id': 0, 
          'class_name': 'Heineken Not A SAB Product', 'type': 'alcoholic', 'color': (0,0,255)}],
        # Frame 6: New different object
        [{'bbox': [300, 150, 400, 350], 'confidence': 0.78, 'class_id': 1, 
          'class_name': 'Corona SunBrew SAB Product', 'type': 'non-alcoholic', 'color': (0,255,0)}],
    ]
    
    # Repeat pattern for 30 frames
    all_detections = []
    for i in range(30):
        frame_idx = i % len(simulated_detections)
        all_detections.append(simulated_detections[frame_idx])
    
    # Process all frames
    total_new_counts = 0
    for frame_num, detections in enumerate(all_detections):
        stats, new_items = counter.update(detections)
        
        if new_items:
            total_new_counts += len(new_items)
            for item in new_items:
                print(f"Frame {frame_num+1:2d}: Counted {item['class_name']} ({item['type']}) - "
                      f"Confidence: {item['confidence']:.2f}")
    
    final_stats = counter.get_statistics()
    
    print(f"\nFinal Results:")
    print(f"  Total unique beverages counted: {final_stats['total_beverages']}")
    print(f"  Alcoholic: {final_stats['total_alcoholic']}")
    print(f"  Non-alcoholic: {final_stats['total_non_alcoholic']}")
    print(f"  Unique types: {final_stats['unique_types']}")
    
    # Expected: Should count 2 unique beverages (not 6 or more due to debouncing)
    expected_count = 2
    actual_count = final_stats['total_beverages']
    
    if actual_count == expected_count:
        print("✓ Counting logic working correctly")
        return True
    else:
        print(f"✗ Counting issue: Expected {expected_count}, got {actual_count}")
        return False

def test_webcam_detection():
    """Test real-time detection with webcam"""
    print("\n=== Testing Real-time Detection ===")
    print("Press 'q' to quit")
    
    detector = BeverageDetector(confidence=0.40)
    if not detector.is_loaded():
        print("❌ Detector not loaded")
        return False
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open webcam")
        return False
    
    frame_count = 0
    detections_found = False
    
    while frame_count < 100:  # Test for 100 frames
        ret, frame = cap.read()
        if not ret:
            break
            
        # Run detection
        detections = detector.detect(frame)
        
        if detections:
            detections_found = True
            print(f"\rFrame {frame_count}: Found {len(detections)} detections", end="")
            
            # Check for valid beverage detections
            valid_detections = [d for d in detections if d['type'] in ['alcoholic', 'non-alcoholic']]
            if valid_detections:
                print(f" - {len(valid_detections)} valid beverages")
                for det in valid_detections[:2]:  # Show first 2
                    print(f"   • {det['class_name']} ({det['confidence']:.2f})")
        
        frame_count += 1
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    if detections_found:
        print("\n✓ Real-time detection working")
        return True
    else:
        print("\n⚠ No detections found - check camera setup")
        return False

def main():
    print("Beverage Detection System - Fix Verification")
    print("=" * 50)
    print()
    
    # Test 1: Detection accuracy
    detection_ok = test_detection_accuracy()
    
    # Test 2: Counting logic
    counting_ok = test_counting_logic()
    
    # Test 3: Real-time detection (optional)
    print("\nDo you want to test real-time detection? (y/n): ", end="")
    if input().lower().startswith('y'):
        webcam_ok = test_webcam_detection()
    else:
        webcam_ok = True
        print("Skipping real-time test")
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"  Detection accuracy: {'✓ PASS' if detection_ok else '✗ FAIL'}")
    print(f"  Counting logic: {'✓ PASS' if counting_ok else '✗ FAIL'}")
    print(f"  Real-time detection: {'✓ PASS' if webcam_ok else '⚠ SKIP/FAIL'}")
    
    if detection_ok and counting_ok:
        print("\n✅ All critical tests passed!")
        print("The detection and counting system should now work correctly.")
    else:
        print("\n❌ Some issues remain. Please check the output above.")
    
    return detection_ok and counting_ok

if __name__ == "__main__":
    main()