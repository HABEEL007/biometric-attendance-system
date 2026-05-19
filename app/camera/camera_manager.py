import cv2
import threading
import time
from typing import Optional, Tuple
import numpy as np
from app.utils.logger import setup_logger

logger = setup_logger("camera_manager", "central.log")

class CameraManager:
    def __init__(self, source: str = "0", camera_id: str = "default_cam"):
        """
        source: webcam index (e.g. "0" or 0) or RTSP URL / video path string.
        """
        self.camera_id = camera_id
        # Convert numeric source string to int
        if isinstance(source, str) and source.isdigit():
            self.source = int(source)
        else:
            self.source = source
            
        self.cap = None
        self.latest_frame: Optional[np.ndarray] = None
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        self.reconnect_delay = 5.0 # seconds to wait before reconnecting
        self.fps = 0.0
        self.status = "DISCONNECTED"

    def _capture_loop(self):
        """Background thread loop to read frames."""
        while self.is_running:
            if self.cap is None or not self.cap.isOpened():
                self.status = "CONNECTING"
                logger.info(f"Opening camera source {self.source}...")
                if isinstance(self.source, int):
                    self.cap = cv2.VideoCapture(self.source, cv2.CAP_DSHOW if cv2.CAP_DSHOW else 0)
                else:
                    self.cap = cv2.VideoCapture(self.source)
                
                if not self.cap.isOpened():
                    logger.error(f"Failed to open camera source {self.source}. Retrying in {self.reconnect_delay}s...")
                    self.status = "ERROR"
                    time.sleep(self.reconnect_delay)
                    continue
                else:
                    logger.info("Camera source opened successfully.")
                    self.status = "CONNECTED"

            start_time = time.time()
            frame_count = 0
            
            while self.is_running and self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("Failed to grab frame. Reconnecting...")
                    self.status = "DISCONNECTED"
                    break
                
                with self.lock:
                    self.latest_frame = frame.copy()
                
                frame_count += 1
                elapsed = time.time() - start_time
                if elapsed >= 1.0:
                    self.fps = frame_count / elapsed
                    frame_count = 0
                    start_time = time.time()
                    
                # Small sleep to yield execution thread
                time.sleep(0.01)

            if self.cap:
                self.cap.release()
                self.cap = None

        self.status = "DISCONNECTED"
        logger.info("Camera capture loop stopped.")

    def start(self):
        """Starts the background capture thread."""
        if self.is_running:
            logger.warning("Camera is already running.")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        logger.info("Camera manager started.")

    def stop(self):
        """Stops the background capture thread."""
        if not self.is_running:
            return
            
        logger.info("Stopping camera manager...")
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=3.0)
            self.thread = None
        
        if self.cap:
            self.cap.release()
            self.cap = None
        self.status = "DISCONNECTED"
        logger.info("Camera manager stopped.")

    def get_latest_frame(self) -> Optional[np.ndarray]:
        """Gets the most recent captured frame (thread-safe)."""
        with self.lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None

    def get_status(self) -> dict:
        """Returns the status and settings of the camera."""
        return {
            "camera_id": self.camera_id,
            "source": str(self.source),
            "status": self.status,
            "fps": round(self.fps, 2),
            "is_running": self.is_running
        }

if __name__ == "__main__":
    # Test camera manager on default webcam
    cam = CameraManager(source="0")
    cam.start()
    time.sleep(2)
    print("Status:", cam.get_status())
    frame = cam.get_latest_frame()
    if frame is not None:
        print("Successfully grabbed test frame of shape:", frame.shape)
    cam.stop()
