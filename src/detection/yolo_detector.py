"""
YOLO Detector
Real YOLOv8 integration using Ultralytics library
"""
import cv2
import numpy as np
from typing import List, Dict, Optional
from pathlib import Path
import logging

# Import tuning configuration
try:
    from detection_tuning import CONFIDENCE_THRESHOLD, IOU_THRESHOLD, MIN_DETECTION_AREA, MAX_DETECTIONS_PER_FRAME
    TUNING_AVAILABLE = True
except ImportError:
    # Default values if tuning module not available
    CONFIDENCE_THRESHOLD = 0.40
    IOU_THRESHOLD = 0.50
    MIN_DETECTION_AREA = 1000
    MAX_DETECTIONS_PER_FRAME = 10
    TUNING_AVAILABLE = False

logger = logging.getLogger(__name__)


class BeverageDetector:
    """Handles beverage detection using YOLOv8"""
    
    def __init__(self, model_path: Optional[str] = None, confidence: float = None):
        """
        Initialize detector
        
        Args:
            model_path: Path to YOLO model weights
            confidence: Confidence threshold for detections (uses tuning config if None)
        """
        self.model_path = model_path
        # Use higher confidence threshold for beverage-only detection
        self.confidence_threshold = confidence if confidence is not None else max(CONFIDENCE_THRESHOLD, 0.65)
        self.iou_threshold = IOU_THRESHOLD
        self.min_area = MIN_DETECTION_AREA
        self.max_detections = MAX_DETECTIONS_PER_FRAME
        self.model = None
        self.loaded = False
        self.use_yolo = True
        
        if TUNING_AVAILABLE:
            logger.info("✓ Using detection tuning configuration")
        else:
            logger.warning("⚠ Using default detection parameters")
        
        # Try to import YOLO
        try:
            from ultralytics import YOLO
            self.YOLO = YOLO
            logger.info("✓ Ultralytics YOLO imported successfully")
        except ImportError:
            logger.warning("⚠ Ultralytics not installed. Using simulation mode.")
            logger.warning("Install with: pip install ultralytics")
            self.use_yolo = False
            self.YOLO = None
        
        # Load model if path provided
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
        elif self.use_yolo:
            # First try to load balanced trained model (best performance)
            model_options = [
                "final_training_data/balanced/best.pt",
                "final_training_data/runs/detect/FINAL_WORKING_MODEL3/weights/best.pt",
                "final_training_data/runs/detect/BALANCED_BEVERAGE_MODEL/weights/best.pt",
                "final_training_data/runs/detect/FINAL_WORKING_MODEL2/weights/best.pt",
                "runs/detect/beverage_model_final/weights/best.pt",
                "yolov8n.pt"
            ]
            
            model_loaded = False
            for custom_model_path in model_options:
                if Path(custom_model_path).exists():
                    try:
                        self.load_model(custom_model_path)
                        logger.info(f"✓ Loaded custom trained model: {custom_model_path}")
                        model_loaded = True
                        break
                    except Exception as e:
                        logger.warning(f"Failed to load {custom_model_path}: {e}")
                        continue
            
            if not model_loaded:
                # Fallback to default YOLOv8n model
                default_model = "yolov8n.pt"
                if Path(default_model).exists():
                    try:
                        self.load_model(default_model)
                        logger.warning("⚠ Using default YOLOv8n model (not custom trained)")
                    except Exception as e:
                        logger.error(f"Error loading default model: {e}")
                        self.use_yolo = False
                else:
                    logger.error("❌ No model found - detection will not work properly")
                    self.use_yolo = False
    
    def load_model(self, model_path: str) -> bool:
        """
        Load YOLO model
        
        Args:
            model_path: Path to model file
            
        Returns:
            bool: True if loaded successfully
        """
        if not self.use_yolo:
            logger.warning("Cannot load YOLO model - Ultralytics not installed")
            return False
        
        try:
            logger.info(f"Loading YOLO model: {model_path}")
            self.model = self.YOLO(model_path)
            self.model_path = model_path
            self.loaded = True
            logger.info(f"✓ Model loaded successfully: {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.loaded = False
            return False
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect beverages in frame
        
        Args:
            frame: Input image (BGR format)
            
        Returns:
            List of detections with format:
            {
                'bbox': [x1, y1, x2, y2],
                'confidence': float,
                'class_id': int,
                'class_name': str,
                'type': 'alcoholic' or 'non-alcoholic'
            }
        """
        if not self.use_yolo or not self.loaded:
            # Use simulation mode
            return self._simulate_detections(frame)
        
        try:
            # Real YOLO inference
            results = self.model(
                frame,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                verbose=False
            )
            
            return self._parse_results(results)
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return []
    
    def _parse_results(self, results) -> List[Dict]:
        """
        Parse YOLO results into standard format with strict filtering
        - Only detects valid beverage classes
        - Filters out non-beverages and low-confidence detections
        - Prevents duplicate class detections in same frame
        
        Args:
            results: YOLO detection results
            
        Returns:
            List of detection dictionaries (filtered to only beverages)
        """
        detections = []
        
        # Import beverage classes
        try:
            from config.settings import BEVERAGE_CLASSES
        except:
            # Fallback classes for 4 custom products
            BEVERAGE_CLASSES = {
                0: {"name": "Heineken Not A SAB Product", "type": "alcoholic", "color": (0, 0, 255)},
                1: {"name": "Corona SunBrew SAB Product", "type": "non-alcoholic", "color": (0, 255, 0)},
                2: {"name": "Castle Lite SAB Product", "type": "alcoholic", "color": (255, 165, 0)},
                3: {"name": "Hansa Pilsner SAB Product", "type": "alcoholic", "color": (138, 43, 226)}
            }
        
        # Valid beverage class IDs (0-3 are our 4 beverage products)
        VALID_BEVERAGE_CLASSES = {0, 1, 2, 3}
        
        # Track processed class IDs to avoid duplicates
        processed_classes = set()
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                
                # ===== STRICT FILTERING =====
                # 1. Only accept valid beverage classes (0-3)
                if class_id not in VALID_BEVERAGE_CLASSES:
                    logger.debug(f"Filtered: class_id {class_id} not in valid beverage classes")
                    continue
                
                # 2. Filter by HIGH confidence threshold (0.65+ required)
                if confidence < self.confidence_threshold:
                    logger.debug(f"Filtered: confidence {confidence:.2f} < threshold {self.confidence_threshold}")
                    continue
                
                # 3. Skip duplicate detections of same class in same frame
                if class_id in processed_classes:
                    logger.debug(f"Filtered: duplicate class {class_id} in same frame")
                    continue
                
                # 4. Validate bounding box coordinates
                xyxy = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = xyxy
                if x2 <= x1 or y2 <= y1:
                    logger.debug(f"Filtered: invalid bounding box")
                    continue
                
                # 5. Filter very small or very large detections
                area = (x2 - x1) * (y2 - y1)
                if area < self.min_area:
                    logger.debug(f"Filtered: area {area} < min_area {self.min_area}")
                    continue
                
                # 6. Check aspect ratio (bottles are taller than wide, not too extreme)
                height = y2 - y1
                width = x2 - x1
                aspect_ratio = height / (width + 1e-6)
                
                # Beverages should have aspect ratio between 0.8 and 3.0 (bottles are taller)
                if aspect_ratio < 0.8 or aspect_ratio > 3.5:
                    logger.debug(f"Filtered: invalid aspect ratio {aspect_ratio:.2f}")
                    continue
                
                # If all filters passed, add to detections
                detection = {
                    'bbox': xyxy.tolist(),
                    'confidence': confidence,
                    'class_id': class_id,
                    'class_name': BEVERAGE_CLASSES[class_id]['name'],
                    'type': BEVERAGE_CLASSES[class_id]['type'],
                    'color': BEVERAGE_CLASSES[class_id]['color']
                }
                detections.append(detection)
                processed_classes.add(class_id)
                
                logger.debug(f"Accepted: {BEVERAGE_CLASSES[class_id]['name']} (conf: {confidence:.2f}, area: {area:.0f})")
        
        # Sort by confidence (highest first) and limit to max detections per frame
        detections = sorted(detections, key=lambda x: x['confidence'], reverse=True)[:self.max_detections]
        
        logger.debug(f"Frame detections: {len(detections)} (after filtering)")
        
        return detections
    
    def _simulate_detections(self, frame: np.ndarray) -> List[Dict]:
        """
        Simulate detections for demo purposes (when YOLO not available)
        
        Args:
            frame: Input frame
            
        Returns:
            List of simulated detections
        """
        # Import beverage classes
        try:
            from config.settings import BEVERAGE_CLASSES
        except:
            BEVERAGE_CLASSES = {
                0: {"name": "beer_bottle", "type": "alcoholic", "color": (0, 0, 255)},
                1: {"name": "soda_can", "type": "non-alcoholic", "color": (0, 255, 0)}
            }
        
        detections = []
        h, w = frame.shape[:2]
        
        # Simulate finding 2-4 beverages at random locations
        np.random.seed(int(cv2.getTickCount()) % 1000)
        num_beverages = np.random.randint(2, 5)
        
        for i in range(num_beverages):
            # Random position
            x1 = np.random.randint(50, w - 150)
            y1 = np.random.randint(50, h - 200)
            box_w = np.random.randint(80, 120)
            box_h = np.random.randint(150, 250)
            x2 = min(x1 + box_w, w - 10)
            y2 = min(y1 + box_h, h - 10)
            
            # Random class
            class_id = np.random.randint(0, len(BEVERAGE_CLASSES))
            class_info = BEVERAGE_CLASSES[class_id]
            
            detection = {
                'bbox': [float(x1), float(y1), float(x2), float(y2)],
                'confidence': np.random.uniform(0.6, 0.95),
                'class_id': class_id,
                'class_name': class_info['name'],
                'type': class_info['type'],
                'color': class_info['color']
            }
            detections.append(detection)
        
        return detections
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Draw bounding boxes and labels on frame
        - Only draws valid beverage detections
        - Displays confidence score and beverage type
        
        Args:
            frame: Input image
            detections: List of detections (only beverages)
            
        Returns:
            Annotated frame with beverage boxes only
        """
        annotated = frame.copy()
        
        # Valid beverage class IDs
        VALID_BEVERAGE_CLASSES = {0, 1, 2, 3}
        
        for det in detections:
            # Double-check it's a valid beverage
            if det['class_id'] not in VALID_BEVERAGE_CLASSES:
                logger.warning(f"Skipping non-beverage detection: {det['class_name']}")
                continue
            
            # Ensure high confidence for display
            if det['confidence'] < 0.60:
                logger.debug(f"Skipping low confidence detection: {det['confidence']:.2f}")
                continue
            
            x1, y1, x2, y2 = [int(v) for v in det['bbox']]
            color = det['color']
            
            # Format label with beverage name, type, and confidence
            label = f"{det['class_name']} [{det['type']}] {det['confidence']:.1%}"
            
            # Draw bounding box
            thickness = 2
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, thickness)
            
            # Draw label background
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            font_thickness = 1
            label_size, baseline = cv2.getTextSize(label, font, font_scale, font_thickness)
            
            # Position label above bounding box
            y1_label = max(y1, label_size[1] + 10)
            cv2.rectangle(
                annotated,
                (x1, y1_label - label_size[1] - 10),
                (x1 + label_size[0] + 5, y1_label + baseline - 10),
                color,
                -1  # Filled rectangle
            )
            
            # Draw label text in white
            cv2.putText(
                annotated, label, (x1 + 2, y1_label - 5),
                font, font_scale, (255, 255, 255), font_thickness
            )
            
            # Optional: draw confidence bar inside box
            box_height = y2 - y1
            bar_height = int(box_height * 0.1)
            bar_y = y1 + box_height - bar_height
            bar_width = int((x2 - x1) * det['confidence'])
            cv2.rectangle(annotated, (x1, bar_y), (x1 + bar_width, y2), color, -1)
        
        return annotated
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.loaded
    
    def get_model_info(self) -> Dict:
        """Get information about loaded model"""
        return {
            'loaded': self.loaded,
            'model_path': self.model_path,
            'use_yolo': self.use_yolo,
            'confidence_threshold': self.confidence_threshold,
            'iou_threshold': self.iou_threshold
        }
