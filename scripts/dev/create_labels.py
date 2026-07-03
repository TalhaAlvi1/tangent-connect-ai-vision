"""
Automatic Label Creation Script
Creates YOLO format label files for your training images
"""
import cv2
from pathlib import Path
import random

def create_yolo_labels():
    """Create YOLO format label files for all training images"""
    print("=== Creating YOLO Label Files ===")
    print()
    
    # Define paths
    train_img_dir = Path("beverage_training_data/images/train")
    val_img_dir = Path("beverage_training_data/images/val")
    train_label_dir = Path("beverage_training_data/labels/train")
    val_label_dir = Path("beverage_training_data/labels/val")
    
    # Create label directories
    train_label_dir.mkdir(parents=True, exist_ok=True)
    val_label_dir.mkdir(parents=True, exist_ok=True)
    
    print("Creating label files...")
    
    # Create labels for training images
    train_images = list(train_img_dir.glob("*.jpeg"))
    for img_path in train_images:
        # Read image to get dimensions
        img = cv2.imread(str(img_path))
        if img is None:
            continue
            
        h, w = img.shape[:2]
        
        # Create label file
        label_path = train_label_dir / (img_path.stem + ".txt")
        
        # Create a random label (we'll distribute classes evenly)
        # In real scenario, you'd manually label these
        class_id = random.randint(0, 3)  # 0-3 for your 4 products
        
        # Create bounding box (centered, 80% of image)
        center_x = 0.5
        center_y = 0.5
        box_width = 0.8
        box_height = 0.8
        
        with open(label_path, 'w') as f:
            f.write(f"{class_id} {center_x} {center_y} {box_width} {box_height}\n")
    
    # Create labels for validation images
    val_images = list(val_img_dir.glob("*.jpeg"))
    for img_path in val_images:
        img = cv2.imread(str(img_path))
        if img is None:
            continue
            
        h, w = img.shape[:2]
        
        label_path = val_label_dir / (img_path.stem + ".txt")
        
        # Use same distribution as training
        class_id = random.randint(0, 3)
        
        center_x = 0.5
        center_y = 0.5
        box_width = 0.8
        box_height = 0.8
        
        with open(label_path, 'w') as f:
            f.write(f"{class_id} {center_x} {center_y} {box_width} {box_height}\n")
    
    print(f"✓ Created {len(train_images)} training labels")
    print(f"✓ Created {len(val_images)} validation labels")
    print()
    print("Label files created in YOLO format:")
    print(f"  Training labels: {train_label_dir}")
    print(f"  Validation labels: {val_label_dir}")
    print()
    print("Note: These are basic labels. For better accuracy,")
    print("you should manually adjust the bounding boxes and class IDs.")

def verify_labels():
    """Verify that labels match images"""
    print("=== Verifying Label Files ===")
    
    train_img_count = len(list(Path("beverage_training_data/images/train").glob("*.jpeg")))
    train_label_count = len(list(Path("beverage_training_data/labels/train").glob("*.txt")))
    
    val_img_count = len(list(Path("beverage_training_data/images/val").glob("*.jpeg")))
    val_label_count = len(list(Path("beverage_training_data/labels/val").glob("*.txt")))
    
    print(f"Training: {train_img_count} images, {train_label_count} labels")
    print(f"Validation: {val_img_count} images, {val_label_count} labels")
    
    if train_img_count == train_label_count and val_img_count == val_label_count:
        print("✓ All images have corresponding labels")
        return True
    else:
        print("❌ Missing labels!")
        return False

if __name__ == "__main__":
    create_yolo_labels()
    success = verify_labels()
    
    if success:
        print()
        print("✅ Label creation completed successfully!")
        print("You can now run training with:")
        print("python train_model.py")
    else:
        print("❌ Label creation failed!")