"""
Immediate Solution - Template-based Detection
Works without training by using template matching
"""
import cv2
import numpy as np
from pathlib import Path
import os
from config.settings import BEVERAGE_CLASSES

class TemplateBasedDetector:
    """Simple template matching detector for your specific products"""
    
    def __init__(self):
        self.templates = {}
        self.load_templates()
    
    def load_templates(self):
        """Load template images for matching"""
        print("Loading template images...")
        template_dir = Path("DETECTION Beverage/images for training")
        
        if not template_dir.exists():
            print("Template directory not found")
            return
        
        # Get sample images for each class
        images = list(template_dir.glob("*.jpeg"))[:4]  # First 4 images as templates
        
        for i, img_path in enumerate(images):
            if i < 4:  # 4 classes
                class_name = list(BEVERAGE_CLASSES.values())[i]['name']
                try:
                    template = cv2.imread(str(img_path))
                    if template is not None:
                        # Resize for faster matching
                        template = cv2.resize(template, (100, 150))
                        self.templates[class_name] = template
                        print(f"  Loaded template for: {class_name}")
                except Exception as e:
                    print(f"  Error loading {img_path}: {e}")
    
    def detect(self, frame):
        """Detect beverages using template matching"""
        detections = []
        
        if not self.templates:
            return detections
        
        # Convert frame to grayscale for matching
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Try to detect each template
        for class_name, template in self.templates.items():
            gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            
            # Template matching
            result = cv2.matchTemplate(gray_frame, gray_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # If match is good enough
            if max_val > 0.6:  # Confidence threshold
                # Get class info
                class_id = None
                for cid, info in BEVERAGE_CLASSES.items():
                    if info['name'] == class_name:
                        class_id = cid
                        break
                
                if class_id is not None:
                    h, w = gray_template.shape
                    x, y = max_loc
                    bbox = [float(x), float(y), float(x + w), float(y + h)]
                    
                    detection = {
                        'bbox': bbox,
                        'confidence': float(max_val),
                        'class_id': class_id,
                        'class_name': class_name,
                        'type': BEVERAGE_CLASSES[class_id]['type'],
                        'color': BEVERAGE_CLASSES[class_id]['color']
                    }
                    detections.append(detection)
        
        return detections

def test_template_detector():
    """Test the template-based detector"""
    print("Testing Template-Based Detection")
    print("=" * 40)
    
    detector = TemplateBasedDetector()
    
    if not detector.templates:
        print("No templates loaded. Please check your image folder.")
        return
    
    print(f"Loaded {len(detector.templates)} templates")
    print()
    
    # Test with webcam
    print("Testing with webcam (Press 'q' to quit)")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Could not open webcam")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect beverages
        detections = detector.detect(frame)
        
        # Draw detections
        for det in detections:
            x1, y1, x2, y2 = [int(v) for v in det['bbox']]
            color = det['color']
            label = f"{det['class_name']} ({det['confidence']:.2f})"
            
            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            cv2.putText(frame, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Display count
        if detections:
            cv2.putText(frame, f"Detections: {len(detections)}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow("Template-Based Detection", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("Testing completed!")

if __name__ == "__main__":
    test_template_detector()