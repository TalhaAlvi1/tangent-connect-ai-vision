"""
Configuration Settings for Beverage Detection System
All configurable parameters in one place
"""
from pathlib import Path

# ============================================================================
# PROJECT PATHS
# ============================================================================
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
EXPORTS_DIR = PROJECT_ROOT / "exports"
LOGS_DIR = PROJECT_ROOT / "logs"
ASSETS_DIR = PROJECT_ROOT
LOGO_PATH = ASSETS_DIR / "app_logo.jpg"

# Create directories if they don't exist
for directory in [DATA_DIR, MODELS_DIR, EXPORTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# CAMERA SETTINGS
# ============================================================================
# Default camera sources - use webcam (0) or video file
DEFAULT_CAMERA_SOURCE = 0  # 0 = webcam, or path to video file
DEFAULT_RTSP_URL = "0"  # Default to webcam
ALTERNATE_RTSP_URLS = [
    "0",  # Webcam
    "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4",
    "https://www.pexels.com/video/854100/download/",  # Sample video
]
CAMERA_BUFFER_SIZE = 3
FPS_TARGET = 30
FRAME_SKIP = 0  # Skip N frames between processing (0 = process every frame)
CAMERA_TIMEOUT = 10  # Timeout in seconds for camera connection

# ============================================================================
# DETECTION SETTINGS
# ============================================================================
# YOLO Model Configuration
DEFAULT_MODEL = "yolov8n.pt"  # Options: yolov8n, yolov8s, yolov8m, yolov8l, yolov8x
CUSTOM_MODEL_PATH = MODELS_DIR / "beverage_custom.pt"
INPUT_SIZE = 640  # Image size for YOLO (640, 512, 416)

# Detection Thresholds
CONFIDENCE_THRESHOLD = 0.65  # Minimum confidence to accept detection (0.0-1.0) - Increased for beverage-only
IOU_THRESHOLD = 0.45  # IoU threshold for Non-Maximum Suppression
MAX_DETECTIONS = 10  # Maximum detections per frame - Limited to reduce false detections

# ============================================================================
# BEVERAGE CLASSES - CUSTOM TRAINED MODEL
# ============================================================================
# Format: class_id: {name, type, color (BGR)}
# Custom trained for your specific products
BEVERAGE_CLASSES = {
    0: {
        "name": "Heineken Not A SAB Product",
        "type": "alcoholic",
        "color": (0, 0, 255),  # Red
        "description": "Heineken Non SAB Product - Alcoholic Beer"
    },
    1: {
        "name": "Corona SunBrew SAB Product",
        "type": "non-alcoholic",
        "color": (0, 255, 0),  # Green
        "description": "Corona SunBrew - SAB Product - Non Alcoholic"
    },
    2: {
        "name": "Castle Lite SAB Product",
        "type": "alcoholic",
        "color": (255, 165, 0),  # Orange
        "description": "Castle Lite - SAB Product - Alcoholic"
    },
    3: {
        "name": "Hansa Pilsner SAB Product",
        "type": "alcoholic",
        "color": (138, 43, 226),  # BlueViolet
        "description": "Hansa Pilsner - SAB Product - Alcoholic"
    },
}

# ============================================================================
# TRACKING SETTINGS
# ============================================================================
TRACKING_MAX_DISTANCE = 50  # Maximum pixel distance for matching objects
TRACKING_MAX_FRAMES_LOST = 30  # Maximum frames before considering object lost
TRACKING_IOU_THRESHOLD = 0.3  # IoU threshold for tracking

# ============================================================================
# UI SETTINGS
# ============================================================================
WINDOW_TITLE = "Tangent Connect - AI Vision Beverage System"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
VIDEO_PANEL_WIDTH_RATIO = 0.70  # 70% for video, 30% for controls
UI_UPDATE_INTERVAL = 33  # milliseconds (30 FPS)

# Color scheme for UI
COLOR_ALCOHOLIC = "#FF0000"  # Red
COLOR_NON_ALCOHOLIC = "#00FF00"  # Green
COLOR_PRIMARY = "#2196F3"  # Blue
COLOR_SECONDARY = "#757575"  # Gray
COLOR_SUCCESS = "#4CAF50"  # Green
COLOR_WARNING = "#FF9800"  # Orange
COLOR_ERROR = "#F44336"  # Red

# ============================================================================
# TRAINING SETTINGS
# ============================================================================
TRAIN_EPOCHS = 50
TRAIN_BATCH_SIZE = 16
TRAIN_IMAGE_SIZE = 640
TRAIN_VALIDATION_SPLIT = 0.2  # 20% for validation
TRAIN_AUGMENTATION = True
TRAIN_PATIENCE = 10  # Early stopping patience

# ============================================================================
# DATABASE SETTINGS
# ============================================================================
DATABASE_PATH = DATA_DIR / "beverage_counts.db"
DATABASE_BACKUP = True
DATABASE_BACKUP_INTERVAL = 3600  # seconds (1 hour)

# ============================================================================
# EXPORT SETTINGS
# ============================================================================
EXPORT_FORMAT = "csv"
EXPORT_COLUMNS = [
    "timestamp",
    "session_id",
    "beverage_class",
    "beverage_type",
    "confidence",
    "bbox_x1",
    "bbox_y1",
    "bbox_x2",
    "bbox_y2"
]

# ============================================================================
# LOGGING SETTINGS
# ============================================================================
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = LOGS_DIR / "app.log"
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================
USE_GPU = True  # Use GPU if available
NUM_THREADS = 4  # Number of threads for processing
ENABLE_PROFILING = False  # Enable performance profiling

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def get_class_by_name(name: str):
    """Get class ID by beverage name"""
    for class_id, info in BEVERAGE_CLASSES.items():
        if info['name'] == name:
            return class_id
    return None

def get_class_info(class_id: int):
    """Get beverage class information"""
    return BEVERAGE_CLASSES.get(class_id, None)

def get_all_class_names():
    """Get list of all beverage class names"""
    return [info['name'] for info in BEVERAGE_CLASSES.values()]

def get_alcoholic_classes():
    """Get list of alcoholic beverage class IDs"""
    return [cid for cid, info in BEVERAGE_CLASSES.items() if info['type'] == 'alcoholic']

def get_non_alcoholic_classes():
    """Get list of non-alcoholic beverage class IDs"""
    return [cid for cid, info in BEVERAGE_CLASSES.items() if info['type'] == 'non-alcoholic']
