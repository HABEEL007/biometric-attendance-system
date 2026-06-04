import cv2
import numpy as np
import onnxruntime as ort
import mediapipe as mp
import urllib.request
import os
from pathlib import Path
from app.utils.logger import setup_logger
from app.utils.gpu_utils import get_onnx_execution_providers

logger = setup_logger("face_detector", "face_service.log")

import threading

class FaceDetector:
    MODEL_URL = "https://github.com/serengil/deepface_models/releases/download/v1.0/arcface_mixed_lfw.onnx"
    MODEL_FILENAME = "arcface_mixed_lfw.onnx"

    def __init__(self, use_gpu: bool = False):
        self.base_dir = Path(__file__).resolve().parents[2]
        self.model_dir = self.base_dir / "models"
        self.model_path = self.model_dir / self.MODEL_FILENAME
        self.use_gpu = use_gpu
        self.is_ready = False
        self.session = None
        self.input_name = None
        
        # Ensure models directory exists
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize MediaPipe Face Mesh immediately
        logger.info("Initializing MediaPipe Face Mesh...")
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Start background thread for model download and session init
        threading.Thread(target=self._init_model_async, daemon=True).start()

    def _init_model_async(self):
        try:
            self._ensure_model_exists()
            logger.info(f"Loading ArcFace ONNX model from {self.model_path}...")
            providers = get_onnx_execution_providers(self.use_gpu)
            self.session = ort.InferenceSession(str(self.model_path), providers=providers)
            self.input_name = self.session.get_inputs()[0].name
            self.is_ready = True
            logger.info("ArcFace ONNX model loaded successfully and is ready.")
        except Exception as e:
            logger.error(f"Failed to initialize FaceDetector background task: {e}")

    def _ensure_model_exists(self):
        if not self.model_path.exists():
            logger.info(f"ArcFace model not found. Downloading from {self.MODEL_URL}...")
            try:
                # Custom downloader with progress reporting
                def progress_hook(block_num, block_size, total_size):
                    downloaded = block_num * block_size
                    percent = min(100, (downloaded / total_size) * 100)
                    if int(percent) % 20 == 0:
                        logger.info(f"Downloading: {percent:.1f}% ({downloaded/(1024*1024):.1f}MB / {total_size/(1024*1024):.1f}MB)")
                
                urllib.request.urlretrieve(self.MODEL_URL, str(self.model_path), progress_hook)
                logger.info("ArcFace model downloaded successfully.")
            except Exception as e:
                logger.error(f"Failed to download ArcFace model: {e}", exc_info=True)
                raise RuntimeError(f"Could not download model from {self.MODEL_URL}")

    def detect_and_embed(self, image: np.ndarray) -> dict:
        """
        Detects face, landmarks, and computes ArcFace 512-D embedding.
        image: BGR numpy image
        returns: dict containing detection success, bounding box, landmarks, and embedding
        """
        if not self.is_ready:
            return {"success": False, "message": "Face model is still downloading or initializing"}
            
        h, w = image.shape[:2]
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.mp_face_mesh.process(rgb_image)
        
        if not results.multi_face_landmarks:
            return {"success": False, "message": "No face detected"}

        face_landmarks = results.multi_face_landmarks[0]
        
        # 1. Calculate Bounding Box from Landmarks
        coords = np.array([[lm.x * w, lm.y * h] for lm in face_landmarks.landmark])
        xmin, ymin = coords.min(axis=0)
        xmax, ymax = coords.max(axis=0)
        
        # Add padding to bounding box
        pad_w = (xmax - xmin) * 0.1
        pad_h = (ymax - ymin) * 0.1
        bbox = [
            max(0, xmin - pad_w),
            max(0, ymin - pad_h),
            min(w, xmax + pad_w),
            min(h, ymax + pad_h)
        ]
        
        # 2. Extract Landmarks (we focus on eye and key regions)
        # Standard 5 landmarks for alignment: Left Eye, Right Eye, Nose Tip, Left Mouth Corner, Right Mouth Corner
        # MediaPipe landmarks map:
        # Left Eye center approx: 33 (left corner), 133 (right corner) -> mean is eye center
        # Right Eye center approx: 362 (left corner), 263 (right corner) -> mean is eye center
        # Nose Tip: 4
        # Mouth Left: 61, Mouth Right: 291
        
        lm = face_landmarks.landmark
        
        def get_pt(idx):
            return int(lm[idx].x * w), int(lm[idx].y * h)
            
        left_eye = np.mean([get_pt(33), get_pt(133)], axis=0).astype(int)
        right_eye = np.mean([get_pt(362), get_pt(263)], axis=0).astype(int)
        nose = np.array(get_pt(4))
        mouth_left = np.array(get_pt(61))
        mouth_right = np.array(get_pt(291))
        
        landmarks_5 = [
            left_eye.tolist(),
            right_eye.tolist(),
            nose.tolist(),
            mouth_left.tolist(),
            mouth_right.tolist()
        ]

        # 3. Align and Crop Face for ArcFace (112x112)
        cropped_face = self._align_face(image, left_eye, right_eye)
        
        # 4. Generate Embedding using ArcFace ONNX model
        embedding = self._get_embedding(cropped_face)

        # 5. Return detailed landmarks for Iris module (e.g. eye landmark regions)
        # MediaPipe Eye landmarks:
        # Left Eye outer boundary: 33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7
        # Right Eye outer boundary: 362, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382
        left_eye_pts = [get_pt(i) for i in [33, 160, 159, 158, 133, 153, 145, 163]]
        right_eye_pts = [get_pt(i) for i in [362, 385, 386, 387, 263, 373, 374, 381]]
        
        return {
            "success": True,
            "bbox": [int(b) for b in bbox],
            "landmarks_5": landmarks_5,
            "left_eye_landmarks": left_eye_pts,
            "right_eye_landmarks": right_eye_pts,
            "embedding": embedding.tolist(),
            "score": float(1.0) # MediaPipe detected successfully
        }

    def _align_face(self, image: np.ndarray, left_eye: np.ndarray, right_eye: np.ndarray) -> np.ndarray:
        """Aligns the face based on eyes location and crops it to 112x112."""
        dy = right_eye[1] - left_eye[1]
        dx = right_eye[0] - left_eye[0]
        angle = np.degrees(np.arctan2(dy, dx))
        
        # Desired eye position in 112x112 image
        desired_left_eye = (0.35, 0.35)
        desired_right_eye = (0.65, 0.35)
        
        # Calculate scale
        dist = np.sqrt(dx**2 + dy**2)
        desired_dist = (desired_right_eye[0] - desired_left_eye[0]) * 112
        scale = desired_dist / dist
        
        # Center between eyes
        eyes_center = ((left_eye[0] + right_eye[0]) / 2, (left_eye[1] + right_eye[1]) / 2)
        
        # Get rotation matrix
        M = cv2.getRotationMatrix2D(eyes_center, angle, scale)
        
        # Update translation
        t_x = 112 * 0.5
        t_y = 112 * desired_left_eye[1]
        M[0, 2] += (t_x - eyes_center[0])
        M[1, 2] += (t_y - eyes_center[1])
        
        # Warp image
        aligned = cv2.warpAffine(image, M, (112, 112), flags=cv2.INTER_CUBIC)
        return aligned

    def _get_embedding(self, aligned_face: np.ndarray) -> np.ndarray:
        """Runs ArcFace model to generate normalized 512-D embedding."""
        # Preprocessing: convert BGR to RGB, scale to [0, 255] then normalize by (x - 127.5) / 127.5
        # Note: DeepFace ArcFace expects RGB inputs in shape (1, 112, 112, 3), scaled to float32
        # Let's inspect the model input details
        input_shape = self.session.get_inputs()[0].shape
        
        rgb_face = cv2.cvtColor(aligned_face, cv2.COLOR_BGR2RGB)
        
        # Model input format might be NCHW or NHWC
        # arcface_mixed_lfw.onnx usually has shape [None, 112, 112, 3] or [None, 3, 112, 112]
        # Let's dynamically check input shape
        if input_shape[1] == 3: # NCHW
            x = rgb_face.transpose(2, 0, 1) # HWC to CHW
            x = np.expand_dims(x, axis=0).astype(np.float32)
        else: # NHWC
            x = np.expand_dims(rgb_face, axis=0).astype(np.float32)
            
        # Normalization
        x = (x - 127.5) / 127.5
        
        # Run inference
        outputs = self.session.run(None, {self.input_name: x})
        raw_emb = outputs[0][0]
        
        # Normalize embedding (L2 Norm)
        norm = np.linalg.norm(raw_emb)
        if norm > 0:
            raw_emb = raw_emb / norm
            
        return raw_emb

    @staticmethod
    def cosine_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Computes cosine similarity between two normalized embeddings."""
        return float(np.dot(emb1, emb2))
