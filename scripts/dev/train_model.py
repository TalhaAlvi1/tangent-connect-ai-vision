"""
Direct Training Script - Command Line Only
Trains your custom beverage detection model without GUI
"""
import os
from pathlib import Path
from ultralytics import YOLO

def train_beverage_model():
    """Train the beverage detection model"""
    print("=== Beverage Detection Model Training ===")
    print()
    
    # Verify label files exist
    print("Checking training data...")
    train_labels = Path("beverage_training_data/labels/train")
    val_labels = Path("beverage_training_data/labels/val")
    
    if not train_labels.exists() or not val_labels.exists():
        print("❌ Label directories not found!")
        print("Run create_labels.py first to generate label files")
        return False
    
    train_label_count = len(list(train_labels.glob("*.txt")))
    val_label_count = len(list(val_labels.glob("*.txt")))
    
    if train_label_count == 0 or val_label_count == 0:
        print("❌ No label files found!")
        print("Run create_labels.py to generate labels")
        return False
    
    print(f"✓ Found {train_label_count} training labels")
    print(f"✓ Found {val_label_count} validation labels")
    print()
    
    # Load pre-trained model
    print("Loading pre-trained YOLOv8 model...")
    try:
        model = YOLO('yolov8n.pt')  # Start with nano model for faster training
        print("✓ Model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False
    
    # Training configuration
    print()
    print("Starting training with configuration:")
    print("  Model: YOLOv8n (nano)")
    print("  Epochs: 50")
    print("  Image size: 320x320")
    print("  Batch size: 8")
    print("  Classes: 4 (your specific products)")
    print()
    
    try:
        # Run training
        results = model.train(
            data='data/beverage_dataset.yaml',
            epochs=50,           # 50 epochs for good results
            imgsz=320,           # Smaller size for faster training
            batch=8,             # Batch size
            name='beverage_detector_v1',
            patience=15,         # Stop if no improvement for 15 epochs
            save=True,           # Save checkpoints
            plots=True,          # Generate plots
            verbose=True         # Show detailed output
        )
        
        print()
        print("🎉 TRAINING COMPLETED SUCCESSFULLY!")
        print()
        print("Model location:")
        model_path = Path("runs/detect/beverage_detector_v1/weights/best.pt")
        if model_path.exists():
            size_mb = model_path.stat().st_size / (1024 * 1024)
            print(f"  Best model: {model_path}")
            print(f"  Size: {size_mb:.1f} MB")
        else:
            print("  Model files saved in runs/detect/beverage_detector_v1/")
        
        print()
        print("Next steps:")
        print("1. Test the model: python test_trained_model.py")
        print("2. Use in main app: Load model in GUI")
        print("3. Check training plots in: runs/detect/beverage_detector_v1/")
        
        return True
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        print()
        print("Troubleshooting tips:")
        print("- Check that all paths are correct")
        print("- Ensure you have enough disk space")
        print("- Try reducing epochs or batch size")
        print("- Check system resources (CPU/RAM)")
        return False

def show_training_progress():
    """Show what to expect during training"""
    print("=== Training Progress Guide ===")
    print()
    print("During training, you'll see:")
    print("• Epoch progress: 1/50 → 2/50 → ... → 50/50")
    print("• Training loss decreasing over time")
    print("• Validation metrics (mAP, precision, recall)")
    print("• Speed information (FPS, processing time)")
    print()
    print("Expected timeline:")
    print("• 50 epochs: 15-30 minutes (depending on system)")
    print("• Each epoch: 15-30 seconds")
    print("• Final model size: 6-8 MB")
    print()
    print("Training will continue automatically.")
    print("Don't close this window until completion!")

if __name__ == "__main__":
    print("Beverage Detection Training - Command Line Mode")
    print("=" * 50)
    print()
    
    show_training_progress()
    print()
    
    # Ask for confirmation
    response = input("Start training now? (y/n): ").strip().lower()
    if response in ['y', 'yes']:
        print()
        print("Starting training...")
        print()
        success = train_beverage_model()
        
        if success:
            print()
            print("✅ Training successful! Your model is ready.")
        else:
            print()
            print("❌ Training encountered issues.")
            print("Check the error messages above for details.")
    else:
        print("Training cancelled.")
        print("You can run it later with: python train_model.py")