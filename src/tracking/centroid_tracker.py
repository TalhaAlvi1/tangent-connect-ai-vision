"""
Centroid Tracker
Tracks objects across frames to prevent duplicate counting
"""
import numpy as np
from typing import List, Dict, Tuple
from collections import defaultdict, deque
import time
import logging

# Import tuning configuration
try:
    from detection_tuning import (
        TRACKING_MAX_DISTANCE, TRACKING_MAX_FRAMES_LOST, 
        COUNT_DEBOUNCE_FRAMES, MIN_COUNT_CONFIDENCE
    )
    TUNING_AVAILABLE = True
except ImportError:
    # Default values if tuning module not available
    TRACKING_MAX_DISTANCE = 80
    TRACKING_MAX_FRAMES_LOST = 20
    COUNT_DEBOUNCE_FRAMES = 15
    MIN_COUNT_CONFIDENCE = 0.50
    TUNING_AVAILABLE = False

logger = logging.getLogger(__name__)


class CentroidTracker:
    """Simple centroid-based object tracker"""
    
    def __init__(self, max_distance: int = None, max_frames_lost: int = None, debounce_frames: int = None):
        """
        Initialize tracker
        
        Args:
            max_distance: Maximum distance for matching objects (pixels) - uses tuning config if None
            max_frames_lost: Maximum frames before considering object lost - uses tuning config if None
            debounce_frames: Minimum frames before counting same object again - uses tuning config if None
        """
        self.max_distance = max_distance if max_distance is not None else TRACKING_MAX_DISTANCE
        self.max_frames_lost = max_frames_lost if max_frames_lost is not None else TRACKING_MAX_FRAMES_LOST
        self.debounce_frames = debounce_frames if debounce_frames is not None else COUNT_DEBOUNCE_FRAMES
        self.next_id = 0
        self.tracked_objects = {}  # {id: {'centroid': (x,y), 'class': str, 'lost_frames': int, 'detection': dict, 'last_counted_frame': int}}
        self.current_frame = 0
        
        if TUNING_AVAILABLE:
            logger.info("✓ Using tracking tuning configuration")
        
        logger.debug("CentroidTracker initialized")
        
    def update(self, detections: List[Dict]) -> Dict[int, Dict]:
        """
        Update tracker with new detections
        
        Args:
            detections: List of current frame detections
            
        Returns:
            Dict of tracked objects {id: object_data}
        """
        self.current_frame += 1
        
        # Calculate centroids of detections
        current_centroids = []
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            current_centroids.append((cx, cy, det))
        
        # If no tracked objects, register all detections
        if len(self.tracked_objects) == 0:
            for cx, cy, det in current_centroids:
                self._register(cx, cy, det)
        
        # If no current detections, increment lost frames
        elif len(current_centroids) == 0:
            for obj_id in list(self.tracked_objects.keys()):
                self.tracked_objects[obj_id]['lost_frames'] += 1
                if self.tracked_objects[obj_id]['lost_frames'] > self.max_frames_lost:
                    del self.tracked_objects[obj_id]
        
        # Otherwise, match detections to tracked objects
        else:
            self._match_objects(current_centroids)
        
        # Return tracked objects that are currently detected
        result = {}
        for obj_id, obj_data in self.tracked_objects.items():
            if obj_data['lost_frames'] == 0:
                result[obj_id] = obj_data
        
        return result
    
    def _register(self, cx: float, cy: float, detection: Dict):
        """Register a new object"""
        self.tracked_objects[self.next_id] = {
            'centroid': (cx, cy),
            'class': detection['class_name'],
            'type': detection['type'],
            'lost_frames': 0,
            'detection': detection,
            'last_counted_frame': 0
        }
        logger.debug(f"Registered new object ID {self.next_id}: {detection['class_name']}")
        self.next_id += 1
    
    def _match_objects(self, current_centroids: List[Tuple]):
        """Match current detections to tracked objects with improved logic"""
        if len(self.tracked_objects) == 0:
            for cx, cy, det in current_centroids:
                self._register(cx, cy, det)
            return
        
        # Get tracked object centroids
        object_ids = list(self.tracked_objects.keys())
        object_centroids = [self.tracked_objects[oid]['centroid'] for oid in object_ids]
        
        # Calculate distance matrix
        distances = np.zeros((len(object_centroids), len(current_centroids)))
        for i, (ox, oy) in enumerate(object_centroids):
            for j, (cx, cy, _) in enumerate(current_centroids):
                distances[i, j] = np.sqrt((ox - cx)**2 + (oy - cy)**2)
        
        # Match using greedy approach with class matching priority
        matched_objects = set()
        matched_detections = set()
        
        # First pass: match same class objects with distance constraint
        rows, cols = np.where(distances < self.max_distance)
        indices = sorted(zip(rows, cols), key=lambda x: distances[x[0], x[1]])
        
        for row, col in indices:
            if row in matched_objects or col in matched_detections:
                continue
            
            obj_id = object_ids[row]
            cx, cy, det = current_centroids[col]
            
            # Only match if same class or if object is lost (class might change due to better detection)
            tracked_class = self.tracked_objects[obj_id]['class']
            current_class = det['class_name']
            
            # If same class, match immediately
            if tracked_class == current_class:
                self._update_object(obj_id, cx, cy, det)
                matched_objects.add(row)
                matched_detections.add(col)
            # If object is lost and new detection is close enough, allow class change
            elif self.tracked_objects[obj_id]['lost_frames'] > 0:
                self._update_object(obj_id, cx, cy, det)
                matched_objects.add(row)
                matched_detections.add(col)
        
        # Second pass: match remaining objects by distance only (for new objects)
        for row, col in indices:
            if row in matched_objects or col in matched_detections:
                continue
            
            obj_id = object_ids[row]
            cx, cy, det = current_centroids[col]
            
            # Update tracked object
            self._update_object(obj_id, cx, cy, det)
            matched_objects.add(row)
            matched_detections.add(col)
        
        # Handle unmatched tracked objects
        for i, obj_id in enumerate(object_ids):
            if i not in matched_objects:
                self.tracked_objects[obj_id]['lost_frames'] += 1
                if self.tracked_objects[obj_id]['lost_frames'] > self.max_frames_lost:
                    logger.debug(f"Removing lost object ID {obj_id}: {self.tracked_objects[obj_id]['class']})")
                    del self.tracked_objects[obj_id]
        
        # Register unmatched detections (new objects)
        for i, (cx, cy, det) in enumerate(current_centroids):
            if i not in matched_detections:
                self._register(cx, cy, det)
    
    def _update_object(self, obj_id: int, cx: float, cy: float, detection: Dict):
        """Update tracked object information"""
        self.tracked_objects[obj_id]['centroid'] = (cx, cy)
        self.tracked_objects[obj_id]['class'] = detection['class_name']
        self.tracked_objects[obj_id]['type'] = detection['type']
        self.tracked_objects[obj_id]['lost_frames'] = 0
        self.tracked_objects[obj_id]['detection'] = detection
    
    def is_count_ready(self, obj_id: int) -> bool:
        """Check if object is ready to be counted again"""
        if obj_id not in self.tracked_objects:
            return False
        obj = self.tracked_objects[obj_id]
        frames_since_last_count = self.current_frame - obj['last_counted_frame']
        return frames_since_last_count >= self.debounce_frames
    
    def mark_counted(self, obj_id: int):
        """Mark object as counted in current frame"""
        if obj_id in self.tracked_objects:
            self.tracked_objects[obj_id]['last_counted_frame'] = self.current_frame
    
    def get_count(self) -> int:
        """Get total number of tracked objects"""
        return len(self.tracked_objects)
    
    def reset(self):
        """Reset tracker"""
        self.tracked_objects.clear()
        self.next_id = 0
        logger.info("Tracker reset")


class BeverageCounter:
    """Counts beverages with tracking"""
    
    def __init__(self, debounce_frames: int = None):
        """Initialize counter with improved tracking parameters
        
        Args:
            debounce_frames: Minimum frames before counting same object again
        """
        self.tracker = CentroidTracker(
            max_distance=None,      # Use tuning config
            max_frames_lost=None,   # Use tuning config
            debounce_frames=debounce_frames  # Use tuning config if None
        )
        self.counts = defaultdict(int)
        self.total_alcoholic = 0
        self.total_non_alcoholic = 0
        self.count_history = deque(maxlen=1000)
        self.seen_ids = set()
        self.seen_with_debounce = set()
        
        if TUNING_AVAILABLE:
            logger.info("✓ Using counter tuning configuration")
        
        logger.info("BeverageCounter initialized")
        
    def update(self, detections: List[Dict]) -> Tuple[Dict, List[Dict]]:
        """
        Update counts with new detections
        
        Args:
            detections: List of detections from current frame
            
        Returns:
            Tuple: (Statistics Dict, List of newly counted detections)
        """
        # Update tracker
        tracked = self.tracker.update(detections)
        new_detections = []
        
        # Count objects with improved debouncing logic
        current_frame_objects = set()  # Track objects in current frame
        
        for obj_id, obj_data in tracked.items():
            current_frame_objects.add(obj_id)
            
            # Only count if object is ready (debounce check)
            if self.tracker.is_count_ready(obj_id):
                # Additional check: ensure we haven't counted this object recently
                if obj_id not in self.seen_with_debounce:
                    self.seen_with_debounce.add(obj_id)
                    self.tracker.mark_counted(obj_id)
                    
                    class_name = obj_data['class']
                    beverage_type = obj_data['type']
                    confidence = obj_data['detection'].get('confidence', 0)
                    
                    # Only count high-confidence detections
                    if confidence >= MIN_COUNT_CONFIDENCE:  # Minimum confidence for counting
                        # Increment counts
                        self.counts[class_name] += 1
                        
                        # Update category totals
                        if beverage_type == 'alcoholic':
                            self.total_alcoholic += 1
                        else:
                            self.total_non_alcoholic += 1
                        
                        # Record in history
                        count_entry = {
                            'timestamp': time.time(),
                            'class_name': class_name,
                            'type': beverage_type,
                            'id': obj_id,
                            'confidence': confidence,
                            'bbox': obj_data['detection'].get('bbox', [])
                        }
                        self.count_history.append(count_entry)
                        new_detections.append(count_entry)
                        
                        logger.info(f"✓ Counted: {class_name} ({beverage_type}) - Confidence: {confidence:.2f}")
                    else:
                        logger.debug(f"✗ Skipped low-confidence detection: {class_name} ({confidence:.2f})")
        
        # Cleanup old object IDs from seen set to prevent memory growth
        # Keep only objects from recent frames (last 100 frames)
        if self.tracker.current_frame % 100 == 0:  # Cleanup every 100 frames
            active_objects = set(tracked.keys())
            self.seen_with_debounce = self.seen_with_debounce.intersection(active_objects)
        
        return self.get_statistics(), new_detections
    
    def get_statistics(self) -> Dict:
        """Get current counting statistics"""
        return {
            'counts': dict(self.counts),
            'total_alcoholic': self.total_alcoholic,
            'total_non_alcoholic': self.total_non_alcoholic,
            'total_beverages': self.total_alcoholic + self.total_non_alcoholic,
            'unique_types': len(self.counts),
            'tracked_objects': self.tracker.get_count()
        }
    
    def reset(self):
        """Reset all counts"""
        self.tracker.reset()
        self.counts.clear()
        self.total_alcoholic = 0
        self.total_non_alcoholic = 0
        self.count_history.clear()
        self.seen_ids.clear()
        self.seen_with_debounce.clear()
        logger.info("Counter reset")
    
    def export_history(self) -> List[Dict]:
        """Export counting history"""
        return list(self.count_history)
