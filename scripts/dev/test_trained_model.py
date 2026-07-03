"""
Test Trained Model Script
Verify that your custom-trained model correctly identifies your 4 beverage products
"""
import cv2
import numpy as np
from pathlib import Path
import sys
from config.settings import BEVERAGE_CLASSES

def find_trained_model():
    """Find the most recent trained model"""
    runs_dir = Path("runs/detect")
    if not runs_dir.exists():
        return None
    
    # Get latest training run
    training_runs = list(runs_dir.iterdir())
    if not training_runs:
        return None
    
    latest_run = max(training_runs, key=lambda x: x.stat().st_ctime)
    best_model = latest_run / "weights" / "best.pt"
    
    return best_model if best_model.exists() else None

def test_model_detection():
    """Test model on sample images or webcam"""
    print("=== Testing Custom-Trained Model ===")
    print()
    
    # Find trained model
    model_path = find_trained_model()
    if not model_path:
        print("❌ No trained model found!")
        print("Please complete training first.")
        return False
    
    print(f"✓ Using model: {model_path}")
    print()
    
    try:
        from ultralytics import YOLO
        model = YOLO(str(model_path))
        print("✓ Model loaded successfully")
        print()
        
        # Test options
        print("Choose test method:")
        print("1. Test with webcam (real-time)")
        print("2. Test with sample image")
        print("3. Test with your training images")
        print()
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            test_webcam(model)
        elif choice == "2":
            test_sample_image(model)
        elif choice == "3":
            test_training_images(model)
        else:
            print("Invalid choice")
            return False
            
        return True
        
    except ImportError:
        print("❌ Ultralytics not installed")
        print("Install with: pip install ultralytics")
        return False
    except Exception as e:
        print(f"❌ Error testing model: {e}")
        return False

def test_webcam(model):
    """Test model with webcam"""
    print("\n=== Webcam Test ===")
    print("Press 'q' to quit")
    print()
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open webcam")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Run detection
        results = model(frame, conf=0.25, verbose=False)
        
        # Draw results
        annotated_frame = results[0].plot()
        
        # Display counts
        detections = results[0].boxes
        if len(detections) > 0:
            print(f"\rDetections: {len(detections)} objects", end="")
        
        cv2.imshow("Beverage Detection Test", annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

def test_sample_image(model):
    """Test model with a single image"""
    image_path = input("Enter image path: ").strip()
    if not Path(image_path).exists():
        print("❌ Image not found")
        return
    
    # Load and process image
    image = cv2.imread(str(image_path))
    if image is None:
        print("❌ Could not load image")
        return
    
    # Run detection
    results = model(image, conf=0.25, verbose=False)
    annotated_image = results[0].plot()
    
    # Show results
    cv2.imshow("Detection Results", annotated_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # Print detection details
    detections = results[0].boxes
    print(f"\nFound {len(detections)} detections:")
    for i, box in enumerate(detections):
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        class_name = BEVERAGE_CLASSES.get(class_id, {}).get('name', f'Class {class_id}')
        print(f"  {i+1}. {class_name} (confidence: {confidence:.2f})")

def test_training_images(model):
    """Test model on training images to verify accuracy"""
    print("\n=== Training Image Verification ===")
    
    # Test on validation images
    val_images_dir = Path("beverage_training_data/images/val")
    if not val_images_dir.exists():
        print("❌ Validation images directory not found")
        return
    
    image_files = list(val_images_dir.glob("*.jpg")) + list(val_images_dir.glob("*.jpeg"))
    if not image_files:
        print("❌ No validation images found")
        return
    
    print(f"Testing on {len(image_files)} validation images...")
    print()
    
    correct_predictions = 0
    total_predictions = 0
    
    for img_path in image_files[:10]:  # Test first 10 images
        image = cv2.imread(str(img_path))
        if image is None:
            continue
            
        results = model(image, conf=0.25, verbose=False)
        detections = results[0].boxes
        
        print(f"Image: {img_path.name}")
        print(f"  Detections: {len(detections)}")
        
        for box in detections:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            class_name = BEVERAGE_CLASSES.get(class_id, {}).get('name', f'Class {class_id}')
            print(f"    - {class_name} ({confidence:.2f})")
            total_predictions += 1
            
            # You can manually verify if predictions are correct
            # This would require manual labeling comparison
            
        print()
    
    print(f"Total predictions made: {total_predictions}")
    print("Review the detections above to verify accuracy")

def main():
    print("Beverage Detection Model Testing")
    print("=" * 40)
    
    success = test_model_detection()
    
    if success:
        print("\n✅ Testing completed!")
        print("\nYour model is ready to use in the main application.")
        print("To use in main app:")
        print("1. Run the main application: python main.py")
        print("2. Go to Model -> Load Custom Model")
        print("3. Select your trained model file")
        print("4. The system will now detect your 4 specific products:")
        for class_id, info in BEVERAGE_CLASSES.items():
            print(f"   • {info['name']} ({info['type']})")
    else:
        print("\n❌ Testing failed. Please check the errors above.")

if __name__ == "__main__":
    main()