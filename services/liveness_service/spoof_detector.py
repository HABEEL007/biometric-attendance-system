import cv2
import numpy as np
import onnxruntime as ort
from pathlib import Path
from app.utils.logger import setup_logger
from app.utils.gpu_utils import get_onnx_execution_providers

logger = setup_logger("spoof_detector", "liveness_service.log")

class SpoofDetector:
    def __init__(self, use_gpu: bool = False):
        self.base_dir = Path(__file__).resolve().parents[2]
        self.model_path = self.base_dir / "models" / "anti_spoof.onnx"
        self.session = None
        
        if self.model_path.exists():
            try:
                logger.info(f"Loading Anti-Spoof ONNX model from {self.model_path}...")
                providers = get_onnx_execution_providers(use_gpu)
                self.session = ort.InferenceSession(str(self.model_path), providers=providers)
                self.input_name = self.session.get_inputs()[0].name
            except Exception as e:
                logger.error(f"Failed to load ONNX anti-spoof model: {e}", exc_info=True)
        else:
            logger.info("ONNX anti-spoof model not found. Using advanced heuristic analyzer.")

    def check_spoof(self, face_crop: np.ndarray) -> dict:
        """
        Runs anti-spoofing detection on the face crop.
        returns: dict with success status, spoof_probability, and prediction (REAL or SPOOF)
        """
        if face_crop is None or face_crop.size == 0:
            return {"success": False, "message": "Invalid face crop image"}

        if self.session is not None:
            # Model-based detection
            return self._run_model_spoof(face_crop)
        else:
            # Advanced Heuristics detection
            return self._run_heuristic_spoof(face_crop)

    def _run_model_spoof(self, face_crop: np.ndarray) -> dict:
        """Runs the custom ONNX model if present."""
        try:
            # Resize image to model input shape (typically 80x80 or 128x128 or 256x256)
            # We'll assume a standard size of 128x128 for general models
            input_shape = self.session.get_inputs()[0].shape
            w_in, h_in = input_shape[2], input_shape[3] # Assuming NCHW
            
            resized = cv2.resize(face_crop, (w_in, h_in))
            x = resized.astype(np.float32) / 255.0
            x = np.transpose(x, (2, 0, 1)) # HWC to CHW
            x = np.expand_dims(x, axis=0)
            
            outputs = self.session.run(None, {self.input_name: x})
            logits = outputs[0][0]
            
            # Simple softmax/sigmoid calculation depending on output dimensions
            if len(logits) == 2: # Binary classification logits
                exp_l = np.exp(logits - np.max(logits))
                probs = exp_l / np.sum(exp_l)
                spoof_prob = float(probs[1]) # Assuming class 1 is Spoof
            else: # Sigmoid output
                spoof_prob = float(1.0 / (1.0 + np.exp(-logits[0])))

            is_spoof = spoof_prob > 0.5
            return {
                "success": True,
                "spoof_probability": spoof_prob,
                "liveness_score": float(1.0 - spoof_prob),
                "prediction": "SPOOF" if is_spoof else "REAL",
                "method": "ONNX_model"
            }
        except Exception as e:
            logger.error(f"Error running anti-spoof model: {e}", exc_info=True)
            return self._run_heuristic_spoof(face_crop)

    def _run_heuristic_spoof(self, face_crop: np.ndarray) -> dict:
        """
        Analyzes image quality, high frequencies (FFT), color reflection, and LBP texture.
        Combined Score is calculated to identify spoofing attempts.
        """
        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # 1. Blurriness Check (Laplacian Variance)
        # Re-projections on screens or prints lose sharpness
        lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        blur_score = min(1.0, max(0.0, 1.0 - (lap_var / 500.0))) # Higher means more blurry (likely spoof)

        # 2. FFT frequency analysis (high-frequency energy)
        # Screens/prints lack fine skin texture details, lowering high frequencies.
        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-7)
        
        # Define high-frequency mask (corners of shifted spectrum)
        cy, cx = h // 2, w // 2
        r = min(h, w) // 6
        mask = np.ones((h, w), dtype=np.uint8)
        mask[cy-r:cy+r, cx-r:cx+r] = 0 # zero-out low frequencies
        
        high_freq_val = np.sum(magnitude_spectrum * mask) / (np.sum(mask) + 1e-7)
        
        # Real faces generally have high-freq values between 6.0 and 15.0
        # If too low (< 5.0), it's likely a blurry print or low-res screen
        high_freq_score = 0.0
        if high_freq_val < 5.5:
            high_freq_score = 0.8
        elif high_freq_val < 7.0:
            high_freq_score = 0.4

        # 3. Specular Reflection Check (Mobile screen glare)
        # Convert to HSV and find pixels with high Value and Saturation
        hsv = cv2.cvtColor(face_crop, cv2.COLOR_BGR2HSV)
        s_chan = hsv[:, :, 1]
        v_chan = hsv[:, :, 2]
        
        # Glare from screens usually has very bright and saturated spots
        glare_mask = (v_chan > 235) & (s_chan > 40)
        glare_pct = float(np.sum(glare_mask) / (h * w))
        
        glare_score = 0.0
        if glare_pct > 0.03: # More than 3% glare pixels
            glare_score = min(1.0, glare_pct * 10.0)

        # 4. Final Aggregated Spoof Probability
        # Combine heuristics:
        # Spoof prob = (Blur * 0.3) + (FFT * 0.4) + (Specular * 0.3)
        spoof_prob = float((blur_score * 0.3) + (high_freq_score * 0.4) + (glare_score * 0.3))
        
        # Clip to [0.0, 1.0]
        spoof_prob = min(1.0, max(0.0, spoof_prob))
        is_spoof = spoof_prob > 0.50

        # Identify attack type
        attack_type = "NONE"
        if is_spoof:
            if glare_score > 0.4:
                attack_type = "SCREEN_REPLAY_ATTACK"
            elif blur_score > 0.6:
                attack_type = "PRINTED_PHOTO_ATTACK"
            else:
                attack_type = "STATIC_PHOTO_OR_MASK"

        return {
            "success": True,
            "spoof_probability": spoof_prob,
            "liveness_score": float(1.0 - spoof_prob),
            "prediction": "SPOOF" if is_spoof else "REAL",
            "attack_type": attack_type,
            "heuristics": {
                "laplacian_variance": float(lap_var),
                "fft_high_freq_energy": float(high_freq_val),
                "specular_glare_pct": glare_pct
            },
            "method": "heuristic_analyzer"
        }
