"""
Camera Stream Manager
Handles RTSP camera connections and frame reading with threading
"""
import cv2
import threading
import queue
import time
import numpy as np
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Available OpenCV backends for video capture
BACKENDS = {
    'CAP_FFMPEG': cv2.CAP_FFMPEG,
    'CAP_GSTREAMER': cv2.CAP_GSTREAMER,
    'CAP_INTEL_MFX': cv2.CAP_INTEL_MFX,
    'CAP_DSHOW': cv2.CAP_DSHOW,
    'CAP_MSMF': cv2.CAP_MSMF,
    'CAP_V4L2': cv2.CAP_V4L2
}


class CameraManager:
    """Manages RTSP camera connection with buffered reading"""
    
    def __init__(self, rtsp_url: str, buffer_size: int = 5, timeout: int = 15):
        """
        Initialize camera manager
        
        Args:
            rtsp_url: RTSP URL of the camera, or '0' for webcam, or path to video file
            buffer_size: Size of frame buffer (increased for stability)
            timeout: Connection timeout in seconds
        """
        # Handle webcam index
        if rtsp_url.isdigit():
            self.rtsp_url = int(rtsp_url)
        else:
            self.rtsp_url = rtsp_url
        
        self.buffer_size = buffer_size
        self.timeout = timeout
        self.cap: Optional[cv2.VideoCapture] = None
        self.frame_queue = queue.Queue(maxsize=buffer_size)
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.last_frame: Optional[np.ndarray] = None
        self.frame_count = 0
        self.fps = 0
        self.connection_error = None
        self.fps_start_time = time.time()
        self.fps_frame_count = 0
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 2.0  # seconds
        
        logger.info(f"CameraManager initialized for: {rtsp_url} with buffer_size={buffer_size}")
        
    def connect(self) -> bool:
        """
        Connect to the camera with robust RTSP handling
        
        Returns:
            bool: True if connection successful
        """
        try:
            logger.info(f"Attempting to connect to camera: {self.rtsp_url}")
            
            # Handle demo mode
            if self.rtsp_url == "demo":
                from demo_video import DemoCameraStream
                self.cap = DemoCameraStream()
                self.last_frame = self.cap.read()[1]
                logger.info("Demo mode activated")
                return True
            
            # Create VideoCapture with appropriate backend
            if isinstance(self.rtsp_url, int):
                # Webcam - try multiple backends
                backends_to_try = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
                for backend in backends_to_try:
                    self.cap = cv2.VideoCapture(self.rtsp_url, backend)
                    if self.cap.isOpened():
                        logger.info(f"Webcam opened with backend: {backend}")
                        break
                    self.cap.release()
                else:
                    self.connection_error = "Failed to open webcam with any backend"
                    logger.error(self.connection_error)
                    return False
            else:
                # RTSP or file - use FFMPEG for better RTSP support
                if str(self.rtsp_url).startswith(('rtsp://', 'http://', 'https://')):
                    # Configure RTSP-specific settings
                    self.cap = cv2.VideoCapture(str(self.rtsp_url), cv2.CAP_FFMPEG)
                    
                    # Set RTSP transport to TCP for reliability
                    self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
                    
                    # Set timeouts
                    self.cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, self.timeout * 1000)
                    self.cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000)  # 5 seconds for reads
                    
                    # Buffer settings for RTSP
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 4)  # Increased buffer for RTSP
                    
                    logger.info(f"RTSP stream configured with FFMPEG backend")
                else:
                    # Regular file
                    self.cap = cv2.VideoCapture(str(self.rtsp_url))
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
            
            # Verify connection
            if not self.cap.isOpened():
                self.connection_error = "Failed to open camera stream"
                logger.error(self.connection_error)
                return False
            
            # Read test frames with proper retries
            for attempt in range(5):  # Increased retries
                ret, frame = self.cap.read()
                if ret and frame is not None and frame.size > 0:
                    self.last_frame = frame.copy()
                    self.connection_error = None
                    logger.info(f"Camera connected successfully! Frame size: {frame.shape}")
                    return True
                logger.warning(f"Connection attempt {attempt + 1} failed, retrying...")
                time.sleep(0.5)
            
            self.connection_error = "Failed to read valid frames from camera"
            logger.error(self.connection_error)
            return False
                
        except Exception as e:
            self.connection_error = f"Connection error: {str(e)}"
            logger.error(f"Camera connection failed: {e}")
            return False
    
    def start(self) -> bool:
        """
        Start reading frames in a separate thread with reconnection capability
        
        Returns:
            bool: True if started successfully
        """
        if not self.connect():
            return False
            
        self.running = True
        self.reconnect_attempts = 0
        self.thread = threading.Thread(target=self._read_frames_loop, daemon=True)
        self.thread.start()
        logger.info("Camera frame reading started with reconnection support")
        return True
    
    def _read_frames_loop(self):
        """Main frame reading loop with reconnection support"""
        while self.running:
            try:
                if self._read_frames_single_session():
                    # Normal exit
                    break
                else:
                    # Connection lost - attempt reconnection
                    if self.reconnect_attempts < self.max_reconnect_attempts:
                        self.reconnect_attempts += 1
                        logger.info(f"Reconnection attempt {self.reconnect_attempts}/{self.max_reconnect_attempts}")
                        time.sleep(self.reconnect_delay)
                        if self.connect():
                            logger.info("Reconnection successful!")
                            self.reconnect_attempts = 0
                            continue
                    else:
                        logger.error("Max reconnection attempts reached")
                        break
            except Exception as e:
                logger.error(f"Unexpected error in frame reading loop: {e}")
                break
        
        logger.info("Frame reading loop ended")
    
    def _read_frames_single_session(self) -> bool:
        """Read frames for a single connection session"""
        self.fps_start_time = time.time()
        self.fps_frame_count = 0
        
        while self.running and self.cap is not None:
            try:
                ret, frame = self.cap.read()
                
                if not ret or frame is None or frame.size == 0:
                    self.connection_error = "Lost connection to camera or invalid frame"
                    logger.warning(f"Frame read failed: ret={ret}, frame_valid={frame is not None and frame.size > 0}")
                    return False  # Signal for reconnection
                
                self.frame_count += 1
                self.fps_frame_count += 1
                
                # Calculate FPS every second
                elapsed = time.time() - self.fps_start_time
                if elapsed >= 1.0:
                    self.fps = self.fps_frame_count / elapsed
                    self.fps_frame_count = 0
                    self.fps_start_time = time.time()
                
                # Update queue (remove old frames if buffer is full)
                if self.frame_queue.full():
                    try:
                        self.frame_queue.get_nowait()
                    except queue.Empty:
                        pass
                
                self.frame_queue.put(frame.copy())  # Store copy to avoid memory issues
                self.last_frame = frame.copy()
                
                # Small delay to prevent CPU spinning
                time.sleep(0.001)
                
            except Exception as e:
                self.connection_error = f"Error reading frame: {str(e)}"
                logger.error(f"Error reading frame: {e}")
                return False  # Signal for reconnection
        
        return True  # Normal exit
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read the latest frame with improved reliability
        
        Returns:
            Tuple of (success, frame)
        """
        if not self.running or self.cap is None:
            return False, None
        
        try:
            # First try to get from queue
            if not self.frame_queue.empty():
                try:
                    frame = self.frame_queue.get_nowait()
                    return True, frame
                except queue.Empty:
                    pass
            
            # If queue is empty, return last frame if available
            if self.last_frame is not None:
                return True, self.last_frame.copy()
            
            # If no frames available at all
            return False, None
                
        except Exception as e:
            logger.error(f"Error in read(): {e}")
            return False, None
    
    def get_frame_size(self) -> Optional[Tuple[int, int]]:
        """
        Get frame dimensions (width, height)
        
        Returns:
            Tuple of (width, height) or None
        """
        if self.last_frame is not None:
            h, w = self.last_frame.shape[:2]
            return (w, h)
        return None
    
    def stop(self):
        """Stop reading frames and release camera"""
        logger.info("Stopping camera...")
        self.running = False
        
        if self.thread is not None:
            self.thread.join(timeout=3.0)  # Increased timeout
        
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        
        # Clear queue
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                break
        
        self.reconnect_attempts = 0
        logger.info("Camera stopped")
    
    def is_connected(self) -> bool:
        """Check if camera is connected and running"""
        return self.running and self.cap is not None
    
    def get_fps(self) -> float:
        """Get current FPS"""
        return self.fps
    
    def get_error(self) -> Optional[str]:
        """Get last error message"""
        return self.connection_error
    
    def __del__(self):
        """Cleanup on deletion"""
        self.stop()
