"""
Demo Video Generator
Creates a simulated video feed with beverage objects for testing
"""
import cv2
import numpy as np
import time
from datetime import datetime

class DemoVideoGenerator:
    """Generates demo video with simulated beverage objects"""
    
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height
        self.frame_count = 0
        
        # Beverage objects (x, y, width, height, label, color)
        self.beverages = [
            {'x': 200, 'y': 300, 'w': 80, 'h': 200, 'label': 'Beer Bottle', 'color': (0, 0, 255), 'type': 'alcoholic'},
            {'x': 400, 'y': 320, 'w': 60, 'h': 180, 'label': 'Soda Can', 'color': (0, 255, 0), 'type': 'non-alcoholic'},
            {'x': 600, 'y': 280, 'w': 70, 'h': 220, 'label': 'Water Bottle', 'color': (0, 200, 100), 'type': 'non-alcoholic'},
            {'x': 800, 'y': 310, 'w': 75, 'h': 190, 'label': 'Wine Bottle', 'color': (0, 0, 200), 'type': 'alcoholic'},
            {'x': 1000, 'y': 330, 'w': 65, 'h': 170, 'label': 'Energy Drink', 'color': (0, 200, 200), 'type': 'non-alcoholic'},
        ]
    
    def generate_frame(self):
        """Generate a single frame with beverages"""
        # Create background
        frame = np.ones((self.height, self.width, 3), dtype=np.uint8) * 240
        
        # Add title
        cv2.putText(frame, 'DEMO MODE - Simulated Beverage Detection', 
                   (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        # Add timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cv2.putText(frame, f'Time: {timestamp}', 
                   (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        
        # Draw counter background
        cv2.rectangle(frame, (10, 100), (400, 200), (255, 255, 255), -1)
        cv2.rectangle(frame, (10, 100), (400, 200), (0, 0, 0), 2)
        
        # Calculate counts
        alcoholic = sum(1 for b in self.beverages if b['type'] == 'alcoholic')
        non_alcoholic = sum(1 for b in self.beverages if b['type'] == 'non-alcoholic')
        
        # Display counts
        cv2.putText(frame, f"Total Beverages: {len(self.beverages)}", 
                   (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(frame, f"Alcoholic: {alcoholic}", 
                   (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(frame, f"Non-Alcoholic: {non_alcoholic}", 
                   (20, 185), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Animate beverages (slight movement)
        offset = int(5 * np.sin(self.frame_count * 0.05))
        
        # Draw beverages
        for i, bev in enumerate(self.beverages):
            x = bev['x'] + offset
            y = bev['y']
            w = bev['w']
            h = bev['h']
            
            # Draw bottle/can shape
            cv2.rectangle(frame, (x, y), (x+w, y+h), bev['color'], 3)
            cv2.rectangle(frame, (x+5, y+5), (x+w-5, y+h-5), bev['color'], -1)
            
            # Add gradient effect
            overlay = frame.copy()
            cv2.rectangle(overlay, (x+10, y+10), (x+w-10, y+h//2), (255, 255, 255), -1)
            cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
            
            # Draw label
            label_bg_h = 30
            cv2.rectangle(frame, (x, y-label_bg_h), (x+w+100, y), bev['color'], -1)
            cv2.putText(frame, bev['label'], (x+5, y-8), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add instruction text
        cv2.putText(frame, 'This is a DEMO simulation. Connect a real camera for actual detection.', 
                   (10, self.height-40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)
        cv2.putText(frame, 'Select "Webcam" source and click "Connect" to use your camera.', 
                   (10, self.height-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)
        
        self.frame_count += 1
        return frame


class DemoCameraStream:
    """Simulates a camera stream using generated frames"""
    
    def __init__(self):
        self.generator = DemoVideoGenerator()
        self.running = False
    
    def isOpened(self):
        return True
    
    def read(self):
        if not self.running:
            self.running = True
        
        # Simulate frame delay
        time.sleep(0.033)  # ~30 FPS
        
        frame = self.generator.generate_frame()
        return True, frame
    
    def release(self):
        self.running = False
    
    def set(self, prop, value):
        pass


if __name__ == "__main__":
    print("Demo Video Generator Test")
    print("="*60)
    print("Press 'q' to quit")
    print("="*60)
    
    demo = DemoCameraStream()
    
    while True:
        ret, frame = demo.read()
        if ret:
            cv2.imshow('Demo Video Generator', frame)
            
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
    
    demo.release()
    cv2.destroyAllWindows()
    print("Demo ended.")
