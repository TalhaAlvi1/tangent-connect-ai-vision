"""
Training Setup Script for Custom Beverage Detection
Helps organize images and launch training wizard
"""
import os
import shutil
from pathlib import Path
import random
from tkinter import messagebox
import tkinter as tk

def organize_training_data():
    """Organize images into train/val splits"""
    print("=== Beverage Detection Training Setup ===")
    print()
    
    # Source folder with your images
    source_folder = Path("DETECTION Beverage/images for training")
    target_base = Path("beverage_training_data")
    
    if not source_folder.exists():
        print(f"❌ Source folder not found: {source_folder}")
        print("Please ensure your images are in 'DETECTION Beverage/images for training/'")
        return False
    
    # Create target structure
    train_img_dir = target_base / "images" / "train"
    val_img_dir = target_base / "images" / "val"
    
    for directory in [train_img_dir, val_img_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Get all images
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    images = []
    
    for ext in image_extensions:
        images.extend(source_folder.glob(f"*{ext}"))
        images.extend(source_folder.glob(f"*{ext.upper()}"))
    
    if not images:
        print("❌ No images found in source folder")
        return False
    
    print(f"✓ Found {len(images)} images")
    
    # Split 80/20 for train/val
    random.shuffle(images)
    split_idx = int(len(images) * 0.8)
    train_images = images[:split_idx]
    val_images = images[split_idx:]
    
    print(f"✓ Splitting: {len(train_images)} train, {len(val_images)} validation")
    
    # Copy images
    for img_path in train_images:
        target_path = train_img_dir / img_path.name
        shutil.copy2(img_path, target_path)
    
    for img_path in val_images:
        target_path = val_img_dir / img_path.name
        shutil.copy2(img_path, target_path)
    
    print("✓ Images copied to training structure")
    print(f"   Train images: {train_img_dir}")
    print(f"   Val images:   {val_img_dir}")
    print()
    print("NEXT STEPS:")
    print("1. Label images using the Training Wizard")
    print("2. Run training with 50-100 epochs")
    print("3. Test the trained model")
    print()
    
    return True

def launch_training_wizard():
    """Launch the training wizard"""
    try:
        from training_wizard import TrainingWizard
        root = tk.Tk()
        root.withdraw()  # Hide main window
        wizard = TrainingWizard(root)
        wizard.run()
    except Exception as e:
        print(f"❌ Error launching training wizard: {e}")
        print("Make sure training_wizard.py exists in the project directory")

def main():
    print("Beverage Detection Training Setup")
    print("=" * 50)
    
    # Step 1: Organize data
    if organize_training_data():
        print("✓ Data organization complete!")
        print()
        
        # Ask user if they want to launch training wizard
        response = input("Launch Training Wizard now? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            print("Launching Training Wizard...")
            launch_training_wizard()
        else:
            print("You can launch the wizard later by running:")
            print("python training_wizard.py")
    else:
        print("❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()