import cv2
import numpy as np
import base64
from PIL import Image
import io
from pathlib import Path

def frame_to_base64(frame: np.ndarray) -> str:
    """Converts a numpy frame to a base64 string."""
    _, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    return jpg_as_text

def base64_to_frame(b64_str: str) -> np.ndarray:
    """Converts a base64 string to a numpy frame."""
    if ',' in b64_str:
        b64_str = b64_str.split(',')[1]
        
    # Ensure correct padding
    missing_padding = len(b64_str) % 4
    if missing_padding:
        b64_str += '=' * (4 - missing_padding)
        
    img_data = base64.b64decode(b64_str)
    nparr = np.frombuffer(img_data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if frame is None:
        raise ValueError("Could not decode image from base64 string. The image data may be invalid.")
        
    return frame

def bytes_to_frame(image_bytes: bytes) -> np.ndarray:
    """Converts raw image bytes to a numpy frame."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return frame

def calculate_blurriness(frame: np.ndarray) -> float:
    """Calculates focus measure of an image using the Laplacian operator."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

def crop_box(frame: np.ndarray, box: list) -> np.ndarray:
    """
    Crops an area out of a frame.
    box: [xmin, ymin, xmax, ymax]
    """
    h, w = frame.shape[:2]
    xmin, ymin, xmax, ymax = map(int, box)
    xmin = max(0, xmin)
    ymin = max(0, ymin)
    xmax = min(w, xmax)
    ymax = min(h, ymax)
    return frame[ymin:ymax, xmin:xmax]

def save_snapshot(frame: np.ndarray, directory: Path, filename: str) -> str:
    """Saves a frame to the specified directory and returns the absolute path."""
    directory.mkdir(parents=True, exist_ok=True)
    file_path = directory / filename
    cv2.imwrite(str(file_path), frame)
    return str(file_path)
