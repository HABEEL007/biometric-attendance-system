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

    def detect_and_embed(self, image: np.ndarray) -> dict:
        """
        Detects face, landmarks, and computes 512-D embedding using InsightFace.
        image: BGR numpy image
        returns: dict containing detection success, bounding box, landmarks, and embedding
        """
        if not self.is_ready or self.app is None:
            return {"success": False, "message": "Face model is still downloading or initializing"}
            
        faces = self.app.get(image)
        
        if len(faces) == 0:
            return {"success": False, "message": "No face detected"}

        # Select the largest face by bounding box area
        face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
        
        # 1. Bounding Box
        bbox = face.bbox.astype(int).tolist()
        
        # 2. Extract Landmarks (5 keypoints)
        # InsightFace kps format: [left_eye, right_eye, nose, mouth_left, mouth_right]
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
            "score": float(face.det_score)
        }

    @staticmethod
    def cosine_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Computes cosine similarity between two normalized embeddings."""
        return float(np.dot(emb1, emb2))
