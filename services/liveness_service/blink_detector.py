import numpy as np
import mediapipe as mp
from typing import Dict, Any, Tuple
from app.utils.logger import setup_logger

logger = setup_logger("blink_detector", "liveness_service.log")

class BlinkDetector:
    def __init__(self):
        logger.info("Initializing MediaPipe for Blink Detection...")
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # EAR threshold under which eye is considered closed
        self.ear_threshold = 0.20

    def calculate_ear(self, landmarks, w: int, h: int) -> Tuple[float, float]:
        """
        Calculates Eye Aspect Ratio (EAR) for left and right eyes.
        Formula: EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
        """
        def get_pt(idx):
            lm = landmarks[idx]
            return np.array([lm.x * w, lm.y * h])

        # Left Eye Landmark Indices:
        # p1: 33 (outer corner), p4: 133 (inner corner)
        # p2: 160, p6: 144 (vertical pair 1)
        # p3: 158, p5: 153 (vertical pair 2)
        l_p1 = get_pt(33)
        l_p4 = get_pt(133)
        l_p2 = get_pt(160)
        l_p6 = get_pt(144)
        l_p3 = get_pt(158)
        l_p5 = get_pt(153)

        # Right Eye Landmark Indices:
        # p1: 362 (inner corner), p4: 263 (outer corner)
        # p2: 385, p6: 373 (vertical pair 1)
        # p3: 387, p5: 381 (vertical pair 2)
        r_p1 = get_pt(362)
        r_p4 = get_pt(263)
        r_p2 = get_pt(385)
        r_p6 = get_pt(373)
        r_p3 = get_pt(387)
        r_p5 = get_pt(381)

        # Left EAR
        l_ear = (np.linalg.norm(l_p2 - l_p6) + np.linalg.norm(l_p3 - l_p5)) / (2.0 * np.linalg.norm(l_p1 - l_p4) + 1e-7)
        
        # Right EAR
        r_ear = (np.linalg.norm(r_p2 - r_p6) + np.linalg.norm(r_p3 - r_p5)) / (2.0 * np.linalg.norm(r_p1 - r_p4) + 1e-7)

        return float(l_ear), float(r_ear)

    def process_frame(self, image: np.ndarray) -> dict:
        """Processes a frame to calculate EAR and blink status."""
        h, w = image.shape[:2]
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.mp_face_mesh.process(rgb_image)

        if not results.multi_face_landmarks:
            return {"success": False, "message": "No face detected for blink check"}

        landmarks = results.multi_face_landmarks[0].landmark
        left_ear, right_ear = self.calculate_ear(landmarks, w, h)
        avg_ear = (left_ear + right_ear) / 2.0
        
        eyes_closed = avg_ear < self.ear_threshold

        return {
            "success": True,
            "left_ear": left_ear,
            "right_ear": right_ear,
            "avg_ear": avg_ear,
            "eyes_closed": bool(eyes_closed),
            "threshold": self.ear_threshold
        }
import cv2
