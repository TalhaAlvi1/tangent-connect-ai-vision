"""
Test Camera Access
Quick test to verify camera is accessible
"""
import cv2
import sys

print("="*60)
print("CAMERA ACCESS TEST")
print("="*60)

# Test webcam
print("\n1. Testing Webcam (Index 0)...")
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if cap.isOpened():
    ret, frame = cap.read()
    if ret and frame is not None:
        print("✓ Webcam WORKING!")
        print(f"  Frame size: {frame.shape}")
        print(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
        
        # Show frame for 2 seconds
        cv2.imshow('Camera Test - Press any key to close', frame)
        cv2.waitKey(2000)
        cv2.destroyAllWindows()
    else:
        print("✗ Webcam opened but cannot read frames")
else:
    print("✗ Cannot open webcam")
    print("  Troubleshooting:")
    print("  - Check if camera is connected")
    print("  - Close other apps using the camera")
    print("  - Check camera permissions in Windows Settings")

cap.release()

print("\n2. Available Camera Backends:")
backends = [
    ("DirectShow (Windows)", cv2.CAP_DSHOW),
    ("Microsoft Media Foundation", cv2.CAP_MSMF),
    ("Any", cv2.CAP_ANY)
]

for name, backend in backends:
    cap = cv2.VideoCapture(0, backend)
    if cap.isOpened():
        print(f"  ✓ {name}")
        cap.release()
    else:
        print(f"  ✗ {name}")

print("\n" + "="*60)
print("Test completed. Press Enter to exit...")
input()
