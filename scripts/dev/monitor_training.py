"""
Training Monitor Script
Check training progress and view results
"""
import os
import time
from pathlib import Path

def check_training_status():
    """Check if training is complete and show results"""
    print("=== Training Status Monitor ===")
    print()
    
    # Check for training results
    runs_dir = Path("runs/detect")
    
    if not runs_dir.exists():
        print("⏳ Training not started or still in progress")
        print("Check your training wizard window for progress")
        return False
    
    # Look for recent training runs
    training_runs = list(runs_dir.iterdir())
    if not training_runs:
        print("⏳ No training runs found")
        return False
    
    # Get most recent run
    latest_run = max(training_runs, key=os.path.getctime)
    print(f"Latest training run: {latest_run.name}")
    print(f"Created: {time.ctime(os.path.getctime(latest_run))}")
    print()
    
    # Check for trained model
    weights_dir = latest_run / "weights"
    if weights_dir.exists():
        best_model = weights_dir / "best.pt"
        last_model = weights_dir / "last.pt"
        
        if best_model.exists():
            print("✅ Training COMPLETE!")
            print(f"Best model: {best_model}")
            print(f"Size: {best_model.stat().st_size / (1024*1024):.1f} MB")
            print()
            
            # Check for training plots
            plots = list(latest_run.glob("*.png"))
            if plots:
                print("📊 Training plots available:")
                for plot in plots:
                    print(f"  - {plot.name}")
            print()
            
            return True
        elif last_model.exists():
            print("🔄 Training in progress...")
            print(f"Last checkpoint: {last_model}")
            return False
        else:
            print("⏳ Training still initializing...")
            return False
    else:
        print("⏳ Training in progress (no weights directory yet)")
        return False

def show_training_tips():
    """Show tips for successful training"""
    print("💡 Training Tips:")
    print("• Training 50-100 epochs typically takes 30-60 minutes")
    print("• Monitor GPU usage if available (task manager -> Performance)")
    print("• Don't close the training wizard window")
    print("• Check console output for progress updates")
    print("• mAP (mean Average Precision) should improve over epochs")
    print()

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        status = check_training_status()
        show_training_tips()
        
        if status:
            print("🎉 Training completed successfully!")
            print("Next step: Test your trained model")
            print()
            response = input("Test the trained model now? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                # Launch test script
                os.system("python test_trained_model.py")
            break
        else:
            print("Checking again in 30 seconds... (Ctrl+C to exit)")
            try:
                time.sleep(30)
            except KeyboardInterrupt:
                print("\nMonitoring stopped.")
                break

if __name__ == "__main__":
    main()