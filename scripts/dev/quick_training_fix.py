"""
Quick Training Fix Script
Creates a simple demo model without requiring manual labeling
"""
import os
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO

def create_simple_demo_model():
    """Create a basic detection model that works with your setup"""
    print("=== Creating Simple Demo Model ===")
    print()
    
    # Use pre-trained YOLOv8n model as starting point
    print("Loading pre-trained YOLOv8n model...")
    try:
        model = YOLO('yolov8n.pt')
        print("✓ Model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False
    
    # Create a simple training configuration
    print("Creating training configuration...")
    
    # Since we don't have labels, we'll create a minimal working example
    # This will detect general bottles/cans and classify them based on your 4 products
    
    try:
        print("Starting simplified training...")
        print("This will create a basic detection model...")
        print()
        
        # Train for very few epochs to create a working model quickly
        results = model.train(
            data='data/beverage_dataset.yaml',
            epochs=5,  # Very short training
            imgsz=320,  # Smaller image size for faster training
            batch=8,    # Smaller batch size
            name='quick_demo_beverage_model',
            verbose=True
        )
        
        print("✓ Training completed!")
        print(f"Model saved to: runs/detect/quick_demo_beverage_model/weights/best.pt")
        return True
        
    except Exception as e:
        print(f"❌ Training error: {e}")
        print()
        print("Let's try an alternative approach...")
        return False

def create_manual_labeling_script():
    """Create a script to help with quick labeling"""
    labeling_script = '''
"""
Quick Manual Labeling Tool
Helps create basic labels for your images
"""
import cv2
import os
from pathlib import Path

def create_basic_labels():
    """Create simple label files for all images"""
    train_dir = Path("beverage_training_data/images/train")
    val_dir = Path("beverage_training_data/images/val")
    train_labels = Path("beverage_training_data/labels/train")
    val_labels = Path("beverage_training_data/labels/val")
    
    # Create label directories
    train_labels.mkdir(parents=True, exist_ok=True)
    val_labels.mkdir(parents=True, exist_ok=True)
    
    # Create simple labels (assuming each image contains one beverage)
    # Format: class_id center_x center_y width height (normalized 0-1)
    
    print("Creating basic label files...")
    
    # For training images
    for img_file in train_dir.glob("*.jpeg"):
        # Create a simple label file (you'll need to adjust these values)
        label_file = train_labels / (img_file.stem + ".txt")
        with open(label_file, 'w') as f:
            # Basic label: class 0 (Heineken) at center of image
            f.write("0 0.5 0.5 0.8 0.8\\n")
    
    # For validation images
    for img_file in val_dir.glob("*.jpeg"):
        label_file = val_labels / (img_file.stem + ".txt")
        with open(label_file, 'w') as f:
            # Basic label: class 0 (Heineken) at center of image
            f.write("0 0.5 0.5 0.8 0.8\\n")
    
    print("✓ Basic label files created")
    print("Note: You should manually adjust these labels for accurate training")

if __name__ == "__main__":
    create_basic_labels()
'''
    
    with open("quick_labeling_tool.py", "w") as f:
        f.write(labeling_script)
    
    print("✓ Created quick_labeling_tool.py")
    print("Run this to create basic label files")

def main():
    print("Beverage Detection - Quick Training Fix")
    print("=" * 50)
    print()
    
    # Option 1: Try simplified training
    print("Option 1: Quick demo training (5 epochs)")
    success = create_simple_demo_model()
    
    if not success:
        # Option 2: Create labeling helper
        print()
        print("Option 2: Create manual labeling helper")
        create_manual_labeling_script()
        print()
        print("Next steps:")
        print("1. Run: python quick_labeling_tool.py")
        print("2. Manually edit the .txt label files")
        print("3. Run training again with proper labels")
    
    print()
    print("For immediate testing, you can also:")
    print("- Use the pre-trained model with general bottle detection")
    print("- Manually classify detected objects in post-processing")

if __name__ == "__main__":
    main()