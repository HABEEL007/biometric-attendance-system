import cv2
import numpy as np
import mediapipe as mp
from typing import Optional, Tuple, Dict, Any
from app.utils.logger import setup_logger
from app.config.settings import settings

logger = setup_logger("iris_detector", "iris_service.log")

class IrisDetector:
    def __init__(self):
        logger.info("Initializing MediaPipe Face Mesh for Iris Detection...")
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def extract_iris_template(self, image: np.ndarray) -> dict:
        """
        Detects left/right iris, crops eye regions, enhances texture, 
        and extracts LBP feature templates.
        """
        h, w = image.shape[:2]
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.mp_face_mesh.process(rgb_image)

        if not results.multi_face_landmarks:
            return {"success": False, "message": "No face detected for iris scan"}

        landmarks = results.multi_face_landmarks[0].landmark
        
        # Check if iris landmarks exist (indices 468-477 are iris landmarks)
        if len(landmarks) < 478:
            return {"success": False, "message": "Iris landmarks not available. Ensure high resolution."}

        # Left Iris landmarks (index 468 is center)
        # Right Iris landmarks (index 473 is center)
        left_center = np.array([landmarks[468].x * w, landmarks[468].y * h])
        right_center = np.array([landmarks[473].x * w, landmarks[473].y * h])

        # Estimate eye size based on distance between corners to determine crop size
        # Left eye corners: 33, 133
        # Right eye corners: 362, 263
        left_corner1 = np.array([landmarks[33].x * w, landmarks[33].y * h])
        left_corner2 = np.array([landmarks[133].x * w, landmarks[133].y * h])
        right_corner1 = np.array([landmarks[362].x * w, landmarks[362].y * h])
        right_corner2 = np.array([landmarks[263].x * w, landmarks[263].y * h])

        left_eye_w = np.linalg.norm(left_corner1 - left_corner2)
        right_eye_w = np.linalg.norm(right_corner1 - right_corner2)
        
        crop_size_l = int(left_eye_w * 1.2)
        crop_size_r = int(right_eye_w * 1.2)

        # Crop eye regions
        left_eye_crop = self._crop_eye(image, left_center, crop_size_l)
        right_eye_crop = self._crop_eye(image, right_center, crop_size_r)

        if left_eye_crop is None or right_eye_crop is None:
            return {"success": False, "message": "Failed to crop eye regions"}

        # Extract features
        left_template, q_score_l = self._extract_features(left_eye_crop)
        right_template, q_score_r = self._extract_features(right_eye_crop)

        # Combine templates
        combined_template = np.concatenate([left_template, right_template])
        avg_quality = float((q_score_l + q_score_r) / 2)

        return {
            "success": True,
            "template": combined_template.tolist(),
            "quality_score": avg_quality
        }

    def _crop_eye(self, image: np.ndarray, center: np.ndarray, crop_size: int) -> Optional[np.ndarray]:
        """Crops eye region around center landmark."""
        h, w = image.shape[:2]
        cx, cy = int(center[0]), int(center[1])
        r = crop_size // 2

        xmin, ymin = cx - r, cy - r
        xmax, ymax = cx + r, cy + r

        if xmin < 0 or ymin < 0 or xmax > w or ymax > h:
            # Pad image if crop goes out of bounds
            pad_val = max(-xmin, -ymin, xmax - w, ymax - h)
            padded = cv2.copyMakeBorder(image, pad_val, pad_val, pad_val, pad_val, cv2.BORDER_CONSTANT, value=[0,0,0])
            cx += pad_val
            cy += pad_val
            crop = padded[cy-r:cy+r, cx-r:cx+r]
        else:
            crop = image[ymin:ymax, xmin:xmax]

        if crop.size == 0:
            return None
        return cv2.resize(crop, (64, 64))

    def _extract_features(self, eye_image: np.ndarray) -> Tuple[np.ndarray, float]:
        """Extracts CLAHE-enhanced LBP texture features and evaluates image quality."""
        gray = cv2.cvtColor(eye_image, cv2.COLOR_BGR2GRAY)
        
        # 1. Apply CLAHE to enhance iris patterns
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # 2. Compute LBP
        lbp = self._compute_lbp(enhanced)
        
        # 3. Calculate Histogram of LBP (256 bins)
        hist, _ = np.histogram(lbp.ravel(), bins=256, range=(0, 256))
        
        # Normalize histogram
        hist = hist.astype("float32")
        hist /= (hist.sum() + 1e-7)
        
        # 4. Compute quality score (contrast / sharpness)
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = np.mean(gray)
        
        # Normalize quality metric (0.0 to 1.0)
        quality = 1.0
        if sharpness < 10.0:
            quality *= 0.5
        if brightness < 40 or brightness > 220:
            quality *= 0.6
            
        return hist, float(quality)

    def _compute_lbp(self, gray_image: np.ndarray) -> np.ndarray:
        """Computes Local Binary Patterns for a grayscale image."""
        h, w = gray_image.shape
        lbp = np.zeros((h - 2, w - 2), dtype=np.uint8)
        
        for i in range(1, h - 1):
            for j in range(1, w - 1):
                center = gray_image[i, j]
                code = 0
                code |= (gray_image[i-1, j-1] >= center) << 7
                code |= (gray_image[i-1, j]   >= center) << 6
                code |= (gray_image[i-1, j+1] >= center) << 5
                code |= (gray_image[i,   j+1] >= center) << 4
                code |= (gray_image[i+1, j+1] >= center) << 3
                code |= (gray_image[i+1, j]   >= center) << 2
                code |= (gray_image[i+1, j-1] >= center) << 1
                code |= (gray_image[i,   j-1] >= center) << 0
                lbp[i-1, j-1] = code
        return lbp

    @staticmethod
    def match_templates(temp1: np.ndarray, temp2: np.ndarray) -> float:
        """Computes cosine similarity of two normalized LBP histograms."""
        dot_product = np.dot(temp1, temp2)
        norm1 = np.linalg.norm(temp1)
        norm2 = np.linalg.norm(temp2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot_product / (norm1 * norm2))
