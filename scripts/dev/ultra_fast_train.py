"""
Ultra-Fast Beverage Detection Training with Mini Dataset
Creates a smaller subset for maximum speed while maintaining accuracy
"""

import os
import shutil
import random
from pathlib import Path
import yaml
from ultralytics import YOLO

def create_mini_dataset(source_dir='balanced_dataset', target_dir='mini_dataset', 
                       train_ratio=0.7, max_images_per_class=100):
    """
    Create a smaller dataset for ultra-fast training
    """
    print("📦 Creating mini dataset for ultra-fast training...")
    
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    # Create target directories
    (target_path / 'images' / 'train').mkdir(parents=True, exist_ok=True)
    (target_path / 'images' / 'val').mkdir(parents=True, exist_ok=True)
    (target_path / 'labels' / 'train').mkdir(parents=True, exist_ok=True)
    (target_path / 'labels' / 'val').mkdir(parents=True, exist_ok=True)
    
    # Class mapping from your dataset
    class_names = [
        'Heineken Not A SAB Product',
        'Corona SunBrew SAB Product', 
        'Castle Lite SAB Product',
        'Hansa Pilsner SAB Product'
    ]
    
    # Count images per class
    train_images = list((source_path / 'images' / 'train').glob('*.*'))
    val_images = list((source_path / 'images' / 'val').glob('*.*'))
    
    print(f"Found {len(train_images)} training images and {len(val_images)} validation images")
    
    # Sample images per class (limited for speed)
    sampled_train = []
    sampled_val = []
    
    for class_idx in range(4):  # 4 classes
        # Get images for this class (based on filename patterns)
        # Training images: class0_, class1_, class2_, class3_ or _class0_, _class1_, etc.
        class_train = [img for img in train_images if f'class{class_idx}_' in img.name or f'_class{class_idx}_' in img.name]
        # Validation images: val_0_, val_1_, val_2_, val_3_
        class_val = [img for img in val_images if f'val_{class_idx}_' in img.name]
        
        # Limit images per class for speed
        max_per_class = min(max_images_per_class, len(class_train))
        selected_train = random.sample(class_train, min(max_per_class, len(class_train)))
        # Ensure we have validation images - use at least 10 per class
        val_count = max(10, min(20, len(class_val)))
        selected_val = random.sample(class_val, min(val_count, len(class_val)))  # 10-20 val images per class
        
        sampled_train.extend(selected_train)
        sampled_val.extend(selected_val)
        
        print(f"Class {class_idx}: {len(selected_train)} train, {len(selected_val)} val images")
    
    # Copy sampled images and labels
    print("Copying files...")
    for img_path in sampled_train:
        # Copy image
        target_img = target_path / 'images' / 'train' / img_path.name
        shutil.copy2(img_path, target_img)
        
        # Copy corresponding label
        label_path = source_path / 'labels' / 'train' / (img_path.stem + '.txt')
        if label_path.exists():
            target_label = target_path / 'labels' / 'train' / (img_path.stem + '.txt')
            shutil.copy2(label_path, target_label)
    
    for img_path in sampled_val:
        # Copy image
        target_img = target_path / 'images' / 'val' / img_path.name
        shutil.copy2(img_path, target_img)
        
        # Copy corresponding label
        label_path = source_path / 'labels' / 'val' / (img_path.stem + '.txt')
        if label_path.exists():
            target_label = target_path / 'labels' / 'val' / (img_path.stem + '.txt')
            shutil.copy2(label_path, target_label)
    
    # Create data.yaml for mini dataset
    mini_data = {
        'names': class_names,
        'nc': 4,
        'path': './mini_dataset',
        'train': 'images/train',
        'val': 'images/val'
    }
    
    with open(target_path / 'data.yaml', 'w') as f:
        yaml.dump(mini_data, f, default_flow_style=False)
    
    total_train = len(list((target_path / 'images' / 'train').glob('*.*')))
    total_val = len(list((target_path / 'images' / 'val').glob('*.*')))
    
    print(f"✅ Mini dataset created:")
    print(f"   - Training images: {total_train}")
    print(f"   - Validation images: {total_val}")
    print(f"   - Configuration: {target_path / 'data.yaml'}")
    
    return str(target_path / 'data.yaml')

def ultra_fast_training():
    """Ultra-fast training with mini dataset"""
    print("=" * 60)
    print("⚡ ULTRA-FAST BEVERAGE DETECTION TRAINING")
    print("=" * 60)
    
    # Create mini dataset
    mini_data_yaml = create_mini_dataset(max_images_per_class=75)  # 75 images per class
    
    # Create model
    print("\n📦 Loading YOLOv8n model (fastest)...")
    model = YOLO('yolov8n.pt')
    
    # Ultra-fast training parameters
    print("⚙️ Starting ultra-fast training...")
    print("   - Model: YOLOv8n (smallest, fastest)")
    print("   - Epochs: 25")
    print("   - Batch Size: 32")
    print("   - Image Size: 416 (smaller for speed)")
    print("   - Optimizer: SGD (faster for small datasets)")
    print()
    
    try:
        results = model.train(
            data=mini_data_yaml,
            epochs=25,
            imgsz=416,      # Smaller image size for speed
            batch=32,       # Larger batch size
            name='beverage_detection_ultra_fast',
            project='runs/detect',
            
            # Fast optimizer
            optimizer='SGD',
            lr0=0.01,
            momentum=0.937,
            
            # Quick training settings
            patience=10,
            warmup_epochs=2,
            
            # Minimal augmentation for speed
            hsv_h=0.015,
            hsv_s=0.5,      # Reduced augmentation
            hsv_v=0.3,      # Reduced augmentation
            degrees=0.0,
            translate=0.05, # Reduced augmentation
            scale=0.2,      # Reduced augmentation
            fliplr=0.3,     # Reduced augmentation
            mosaic=0.5,     # Reduced augmentation
            
            # Performance
            amp=True,
            workers=8,
            cache=True,     # Cache for speed
            verbose=True
        )
        
        # Validate
        print("\n🔍 Validating model...")
        metrics = model.val(data=mini_data_yaml, imgsz=416, batch=32)
        
        # Results
        print("\n" + "=" * 60)
        print("🎉 ULTRA-FAST TRAINING COMPLETED!")
        print("=" * 60)
        print(f"📊 Results:")
        print(f"   mAP50:     {metrics.box.map50:.4f}")
        print(f"   mAP50-95:  {metrics.box.map:.4f}")
        print(f"   Precision: {metrics.box.mp:.4f}")
        print(f"   Recall:    {metrics.box.mr:.4f}")
        print()
        print(f"📁 Model saved to:")
        print(f"   Best:  runs/detect/beverage_detection_ultra_fast/weights/best.pt")
        print("=" * 60)
        
        return model, results, metrics
        
    except Exception as e:
        print(f"\n❌ Training failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        model, results, metrics = ultra_fast_training()
        print("\n✅ Ultra-fast training completed!")
        print("Model ready for beverage detection!")
    except Exception as e:
        print(f"\n💥 Error: {str(e)}")