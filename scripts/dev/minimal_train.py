"""
Minimal Training Script - Direct Approach
Bypasses complex dataset configuration issues
"""
from ultralytics import YOLO
import os

def minimal_training():
    """Run minimal training with direct approach"""
    print("=== Minimal Training Approach ===")
    print()
    
    # Create a simple dataset configuration in current directory
    dataset_yaml = """
# Simple beverage dataset
path: .
train: beverage_training_data/images/train
val: beverage_training_data/images/val

# Classes
nc: 4
names: ['Heineken Not A SAB Product', 'Corona SunBrew SAB Product', 'Castke Lite SAB Product', 'Hansa Pilsner SAB Product']
"""
    
    # Write temporary dataset file
    with open('temp_dataset.yaml', 'w') as f:
        f.write(dataset_yaml)
    
    print("✓ Created temporary dataset configuration")
    print()
    
    # Load model
    print("Loading YOLOv8 model...")
    try:
        model = YOLO('yolov8n.pt')
        print("✓ Model loaded")
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False
    
    # Run training with minimal parameters
    print("Starting minimal training...")
    print("(This may take 10-20 minutes)")
    print()
    
    try:
        results = model.train(
            data='temp_dataset.yaml',
            epochs=20,        # Fewer epochs for faster completion
            imgsz=256,        # Smaller images
            batch=4,          # Smaller batch
            name='minimal_beverage_model',
            verbose=True
        )
        
        print()
        print("🎉 MINIMAL TRAINING COMPLETED!")
        print()
        print("Model saved to: runs/detect/minimal_beverage_model/weights/best.pt")
        print()
        print("You can now:")
        print("1. Test with: python test_trained_model.py")
        print("2. Use in main application by loading the model file")
        
        # Clean up temporary file
        if os.path.exists('temp_dataset.yaml'):
            os.remove('temp_dataset.yaml')
            print("✓ Cleaned up temporary files")
            
        return True
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return False

if __name__ == "__main__":
    print("Beverage Detection - Minimal Training")
    print("=" * 40)
    print()
    
    success = minimal_training()
    
    if success:
        print()
        print("✅ Training successful!")
    else:
        print()
        print("❌ Training failed. Check error messages above.")