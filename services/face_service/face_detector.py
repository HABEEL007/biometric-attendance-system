import cv2
import numpy as np
import os
from pathlib import Path
from insightface.app import FaceAnalysis
from app.utils.logger import setup_logger
import threading

logger = setup_logger("face_detector", "face_service.log")

class FaceDetector:
    def __init__(self, use_gpu: bool = False):
        self.base_dir = Path(__file__).resolve().parents[2]
        self.model_dir = self.base_dir / "models"
        self.use_gpu = use_gpu
        self.is_ready = False
        self.app = None
        
        # Ensure models directory exists
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Start background thread for model download and session init
        threading.Thread(target=self._init_model_async, daemon=True).start()

    def _init_model_async(self):
        try:
            logger.info("Initializing InsightFace (buffalo_l) model...")
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if self.use_gpu else ['CPUExecutionProvider']
            ctx_id = 0 if self.use_gpu else -1
            
            # This will automatically download buffalo_l to ~/.insightface/models/buffalo_l
            # if root is specified, it downloads there.
            self.app = FaceAnalysis(name='buffalo_l', root=str(self.base_dir), providers=providers)
            self.app.prepare(ctx_id=ctx_id, det_size=(640, 640))
            
            self.is_ready = True
            logger.info("InsightFace model loaded successfully and is ready.")
        except Exception as e:
            logger.error(f"Failed to initialize FaceDetector background task: {e}", exc_info=True)

    def _apply_clahe(self, image: np.ndarray) -> np.ndarray:
        """Applies CLAHE on the lightness channel to improve contrast and handle bad lighting."""
        try:
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l_channel, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            cl = clahe.apply(l_channel)
            limg = cv2.merge((cl,a,b))
            return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        except Exception as e:
            logger.warning(f"CLAHE failed, using original image: {e}")
            return image

    def detect_and_embed(self, image: np.ndarray) -> dict:
        """
        Detects face, landmarks, and computes 512-D embedding using InsightFace.
        image: BGR numpy image
        returns: dict containing detection success, bounding box, landmarks, and embedding
        """
        if not self.is_ready or self.app is None:
            return {"success": False, "message": "Face model is still downloading or initializing"}
            
        # Apply CLAHE to improve detection and embeddings in harsh lighting
        enhanced_image = self._apply_clahe(image)
        faces = self.app.get(enhanced_image)
        
        if len(faces) == 0:
            return {"success": False, "message": "No face detected"}

        # Select the largest face by bounding box area
        face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
        
        # --- NEW LOGIC: Dynamic Resolution Refinement ---
        w = face.bbox[2] - face.bbox[0]
        if w < 100:
            pad_x = int(w * 0.5)
            h = face.bbox[3] - face.bbox[1]
            pad_y = int(h * 0.5)
            
            x1 = max(0, int(face.bbox[0]) - pad_x)
            y1 = max(0, int(face.bbox[1]) - pad_y)
            x2 = min(enhanced_image.shape[1], int(face.bbox[2]) + pad_x)
            y2 = min(enhanced_image.shape[0], int(face.bbox[3]) + pad_y)
            
            crop = enhanced_image[y1:y2, x1:x2]
            if crop.shape[0] > 0 and crop.shape[1] > 0:
                upscaled = cv2.resize(crop, (224, 224), interpolation=cv2.INTER_CUBIC)
                upscaled_faces = self.app.get(upscaled)
                if upscaled_faces:
                    upscaled_face = max(upscaled_faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
                    face.embedding = upscaled_face.embedding
        
        # --- NEW LOGIC: 3D Head Pose Validation ---
        from app.config.settings import settings
        pitch, yaw, roll = face.pose
        
        # In real-world webcams, pitch can be naturally high if camera is above/below monitor. 
        # Using relaxed settings thresholds:
        pose_valid = abs(yaw) <= settings.POSE_YAW_LIMIT and abs(pitch) <= settings.POSE_PITCH_LIMIT and abs(roll) <= settings.POSE_ROLL_LIMIT
        
        # Calculate pose score (1.0 is perfectly frontal)
        pose_score = 1.0 - (abs(yaw)/settings.POSE_YAW_LIMIT * 0.4 + abs(pitch)/settings.POSE_PITCH_LIMIT * 0.4 + abs(roll)/settings.POSE_ROLL_LIMIT * 0.2)
        pose_score = max(0.0, min(1.0, pose_score))

        # --- NEW LOGIC: Advanced Quality Gate ---
        bbox_int = face.bbox.astype(int)
        cx1, cy1 = max(0, bbox_int[0]), max(0, bbox_int[1])
        cx2, cy2 = min(enhanced_image.shape[1], bbox_int[2]), min(enhanced_image.shape[0], bbox_int[3])
        face_crop = enhanced_image[cy1:cy2, cx1:cx2]
        
        blur_score = 0.0
        illumination_valid = True
        if face_crop.shape[0] > 0 and face_crop.shape[1] > 0:
            gray_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
            lap_var = cv2.Laplacian(gray_crop, cv2.CV_64F).var()
            
            face_w = cx2 - cx1
            min_blur = 8.0 if face_w < 100 else 25.0
            
            if lap_var < min_blur:
                blur_score = lap_var / min_blur * 0.5
            else:
                blur_score = min(1.0, 0.5 + (lap_var - min_blur) / 100.0)
                
            mean_brightness = np.mean(gray_crop)
            if mean_brightness < 15.0 or mean_brightness > 254.0:
                illumination_valid = False
                blur_score = 0.0

        det_score = float(face.det_score)
        combined_quality_score = (det_score * 0.4) + (blur_score * 0.4) + (pose_score * 0.2)

        # 1. Bounding Box
        bbox = face.bbox.astype(int).tolist()
        
        # 2. Extract Landmarks (5 keypoints)
        kps = face.kps.astype(int)
        landmarks_5 = kps.tolist()

        # Mock detailed landmarks for Iris module (it expects 8 points each)
        left_eye_pts = [kps[0].tolist()] * 8
        right_eye_pts = [kps[1].tolist()] * 8
        
        # 3. Generate Embedding (512-D)
        embedding = face.embedding
        
        # Ensure L2 normalization
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return {
            "success": True,
            "bbox": bbox,
            "landmarks_5": landmarks_5,
            "left_eye_landmarks": left_eye_pts,
            "right_eye_landmarks": right_eye_pts,
            "embedding": embedding.tolist(),
            "score": det_score,
            "quality_score": float(combined_quality_score),
            "pose_valid": bool(pose_valid),
            "illumination_valid": bool(illumination_valid)
        }

    @staticmethod
    def cosine_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Computes cosine similarity between two normalized embeddings."""
        return float(np.dot(emb1, emb2))
