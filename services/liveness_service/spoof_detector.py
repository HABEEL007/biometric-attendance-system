import cv2
import numpy as np
import torch
import albumentations as A
from albumentations.pytorch import ToTensorV2
from pathlib import Path
from app.utils.logger import setup_logger

logger = setup_logger("spoof_detector", "liveness_service.log")

class SpoofDetector:
    def __init__(self, use_gpu: bool = False):
        self.base_dir = Path(__file__).resolve().parents[2]
        self.model_path = self.base_dir / "models" / "best_liveness_model.pth"
        self.device = torch.device('cuda' if use_gpu and torch.cuda.is_available() else 'cpu')
        self.model = None
        
        self.transform = A.Compose([
            A.Resize(224, 224),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ])
        
        if self.model_path.exists():
            try:
                logger.info(f"Loading PyTorch Liveness model from {self.model_path}...")
                
                # Import LivenessModel here to avoid circular imports and path issues
                import sys
                scripts_dir = str(self.base_dir / "scripts")
                if scripts_dir not in sys.path:
                    sys.path.append(scripts_dir)
                from model import LivenessModel
                
                self.model = LivenessModel()
                self.model.load_state_dict(torch.load(str(self.model_path), map_location=self.device, weights_only=True))
                self.model.to(self.device)
                self.model.eval()
            except Exception as e:
                logger.error(f"Failed to load PyTorch liveness model: {e}", exc_info=True)
        else:
            logger.info("PyTorch liveness model not found. Using advanced heuristic analyzer.")

    def check_spoof(self, face_crop: np.ndarray) -> dict:
        """
        Runs anti-spoofing detection on the face crop.
        returns: dict with success status, spoof_probability, and prediction (REAL or SPOOF)
        """
        if face_crop is None or face_crop.size == 0:
            return {"success": False, "message": "Invalid face crop image"}

        if self.model is not None:
            # Deep Learning Model-based detection
            return self._run_model_spoof(face_crop)
        else:
            # Advanced Heuristics detection
            return self._run_heuristic_spoof(face_crop)

    def _run_model_spoof(self, face_crop: np.ndarray) -> dict:
        """Runs the PyTorch EfficientNet-B0 model."""
        try:
            # Ensure face crop is RGB (OpenCV uses BGR)
            rgb_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
            
            # Apply albumentations
            transformed = self.transform(image=rgb_crop)
            tensor = transformed['image'].unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                output = self.model(tensor)
                probs = torch.softmax(output, 1)
                confidence, pred = torch.max(probs, 1)
            
            real_prob = probs[0][0].item()
            spoof_prob = probs[0][1].item()
            is_spoof = pred.item() == 1
            
            return {
                "success": True,
                "spoof_probability": spoof_prob,
                "liveness_score": real_prob,
                "prediction": "SPOOF" if is_spoof else "REAL",
                "method": "efficientnet_b0_pytorch"
            }
        except Exception as e:
            logger.error(f"Error running PyTorch liveness model: {e}", exc_info=True)
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
