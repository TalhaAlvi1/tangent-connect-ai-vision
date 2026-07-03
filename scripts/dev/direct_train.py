"""
Direct Training Script - Bypasses dataset configuration issues
"""
import os
from ultralytics import YOLO

def direct_training():
    """Train directly with explicit paths"""
    print("=== Direct Beverage Training ===")
    print()
    
    # Create a simple dataset dict instead of YAML file
    dataset_config = {
        'path': 'datasets/beverage_training_data',
        'train': 'images/train',
        'val': 'images/val',
        'nc': 4,
        'names': ['Heineken Not A SAB Product', 'Corona SunBrew SAB Product', 'Castke Lite SAB Product', 'Hansa Pilsner SAB Product']
    }
    
    print("Dataset configuration:")
    for key, value in dataset_config.items():
        print(f"  {key}: {value}")
    print()
    
    # Load model
    print("Loading YOLOv8 model...")
    model = YOLO('yolov8n.pt')
    print("✓ Model loaded")
    print()
    
    # Train with explicit configuration
    print("Starting training...")
    print("This will take 15-25 minutes")
    print()
    
    try:
        # Train with minimal parameters
        results = model.train(
            data=dataset_config,
            epochs=20,
            imgsz=256,
            batch=4,
            name='direct_beverage_model',
            verbose=True
        )
        
        print()
        print("🎉 TRAINING COMPLETED SUCCESSFULLY!")
        print()
        print("Model location: runs/detect/direct_beverage_model/weights/best.pt")
        print()
        print("Your trained model is ready to use!")
        print("Load it in the main application to detect your 4 specific products.")
        
        return True
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return False

if __name__ == "__main__":
    print("Beverage Detection - Direct Training")
    print("=" * 40)
    print()
    
    success = direct_training()
    
    if success:
        print()
        print("✅ Training successful!")
        print("Next steps:")
        print("1. Test the model: python test_trained_model.py")
        print("2. Use in main app: Load model file in GUI")
    else:
        print()
        print("❌ Training failed. Check error messages above.")