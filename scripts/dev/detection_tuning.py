"""
Detection Tuning Configuration
Easy-to-adjust parameters for optimizing detection performance
"""
import cv2

# ============================================================================
# DETECTION TUNING PARAMETERS
# Adjust these values to optimize for your specific use case
# ============================================================================

# Confidence Threshold
# Higher values = fewer false positives, but might miss some detections
# Lower values = more detections, but more false positives
CONFIDENCE_THRESHOLD = 0.65  # Range: 0.25 - 0.80 (default: 0.65 - Increased for beverage-only detection)

# IOU Threshold (Non-Maximum Suppression)
# Higher values = allow more overlapping detections
# Lower values = remove more overlapping detections
IOU_THRESHOLD = 0.50  # Range: 0.30 - 0.70 (default: 0.50)

# Minimum Bounding Box Area
# Filter out very small detections that are likely false positives
MIN_DETECTION_AREA = 1000  # Range: 500 - 5000 pixels² (default: 1000)

# Maximum Detections Per Frame
# Limit total detections to prevent overwhelming the system
MAX_DETECTIONS_PER_FRAME = 10  # Range: 5 - 20 (default: 10)

# ============================================================================
# TRACKING TUNING PARAMETERS
# ============================================================================

# Tracking Distance Threshold
# Maximum distance (pixels) to consider same object in consecutive frames
TRACKING_MAX_DISTANCE = 80  # Range: 50 - 150 pixels (default: 80)

# Maximum Frames Lost
# Number of frames an object can be missing before being considered gone
TRACKING_MAX_FRAMES_LOST = 20  # Range: 10 - 50 frames (default: 20)

# Count Debounce Frames
# Minimum frames between counting the same object again
# Higher values = less duplicate counting, but slower to count new objects
COUNT_DEBOUNCE_FRAMES = 15  # Range: 10 - 30 frames (default: 15)

# Minimum Confidence for Counting
# Only count detections with confidence above this threshold
MIN_COUNT_CONFIDENCE = 0.60  # Range: 0.30 - 0.70 (default: 0.60 - Increased to ensure only valid beverages)

# ============================================================================
# PERFORMANCE TUNING
# ============================================================================

# Frame Skip Rate
# Process every Nth frame (0 = process all frames)
FRAME_SKIP_RATE = 0  # Range: 0 - 3 (default: 0)

# Input Image Size
# Larger = more accurate but slower
# Smaller = faster but less accurate
INPUT_IMAGE_SIZE = 640  # Options: 416, 512, 640, 1024 (default: 640)

# Use GPU (if available)
USE_GPU = True  # Set to False if experiencing GPU memory issues

# ============================================================================
# PRESETS
# ============================================================================

PRESETS = {
    "beverage_only": {  # OPTIMIZED for beverage detection - high confidence to avoid false positives
        "confidence_threshold": 0.65,
        "iou_threshold": 0.50,
        "min_detection_area": 1000,
        "max_detections": 10,
        "tracking_distance": 80,
        "frames_lost": 20,
        "debounce_frames": 15,
        "min_count_confidence": 0.60
    },
    
    "high_precision": {  # Prioritize accuracy over speed
        "confidence_threshold": 0.50,
        "iou_threshold": 0.55,
        "min_detection_area": 1500,
        "max_detections": 8,
        "tracking_distance": 100,
        "frames_lost": 15,
        "debounce_frames": 20,
        "min_count_confidence": 0.60
    },
    
    "balanced": {  # Good balance of accuracy and speed
        "confidence_threshold": 0.40,
        "iou_threshold": 0.50,
        "min_detection_area": 1000,
        "max_detections": 10,
        "tracking_distance": 80,
        "frames_lost": 20,
        "debounce_frames": 15,
        "min_count_confidence": 0.50
    },
    
    "high_recall": {  # Prioritize finding all objects over avoiding false positives
        "confidence_threshold": 0.30,
        "iou_threshold": 0.45,
        "min_detection_area": 800,
        "max_detections": 15,
        "tracking_distance": 60,
        "frames_lost": 25,
        "debounce_frames": 10,
        "min_count_confidence": 0.40
    }
}

def apply_preset(preset_name: str):
    """Apply a preset configuration"""
    if preset_name not in PRESETS:
        print(f"Warning: Preset '{preset_name}' not found. Using 'balanced'")
        preset_name = "balanced"
    
    preset = PRESETS[preset_name]
    
    global CONFIDENCE_THRESHOLD, IOU_THRESHOLD, MIN_DETECTION_AREA
    global MAX_DETECTIONS_PER_FRAME, TRACKING_MAX_DISTANCE
    global TRACKING_MAX_FRAMES_LOST, COUNT_DEBOUNCE_FRAMES
    global MIN_COUNT_CONFIDENCE
    
    CONFIDENCE_THRESHOLD = preset["confidence_threshold"]
    IOU_THRESHOLD = preset["iou_threshold"]
    MIN_DETECTION_AREA = preset["min_detection_area"]
    MAX_DETECTIONS_PER_FRAME = preset["max_detections"]
    TRACKING_MAX_DISTANCE = preset["tracking_distance"]
    TRACKING_MAX_FRAMES_LOST = preset["frames_lost"]
    COUNT_DEBOUNCE_FRAMES = preset["debounce_frames"]
    MIN_COUNT_CONFIDENCE = preset["min_count_confidence"]
    
    print(f"Applied preset: {preset_name}")
    print(f"  Confidence threshold: {CONFIDENCE_THRESHOLD}")
    print(f"  Count debounce: {COUNT_DEBOUNCE_FRAMES} frames")

def print_current_settings():
    """Print current configuration"""
    print("Current Detection Settings:")
    print(f"  Confidence threshold: {CONFIDENCE_THRESHOLD}")
    print(f"  IOU threshold: {IOU_THRESHOLD}")
    print(f"  Minimum detection area: {MIN_DETECTION_AREA}px²")
    print(f"  Max detections per frame: {MAX_DETECTIONS_PER_FRAME}")
    print(f"  Tracking distance: {TRACKING_MAX_DISTANCE}px")
    print(f"  Max frames lost: {TRACKING_MAX_FRAMES_LOST}")
    print(f"  Count debounce: {COUNT_DEBOUNCE_FRAMES} frames")
    print(f"  Min count confidence: {MIN_COUNT_CONFIDENCE}")

# Apply default preset for beverage-only detection
apply_preset("beverage_only")