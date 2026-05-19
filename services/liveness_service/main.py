import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
from services.liveness_service.blink_detector import BlinkDetector
from services.liveness_service.spoof_detector import SpoofDetector
from app.utils.image_utils import base64_to_frame, crop_box
from app.config.settings import settings
from app.utils.logger import setup_logger

logger = setup_logger("liveness_service", "liveness_service.log")

app = FastAPI(title="Liveness Detection Service", version="2.0")
blink_detector = BlinkDetector()
spoof_detector = SpoofDetector(use_gpu=settings.USE_GPU)

class ImagePayload(BaseModel):
    image: str # Base64 encoded string of image

@app.get("/health")
def health():
    return {"status": "healthy", "service": "liveness_service"}

@app.post("/check")
def check(payload: ImagePayload):
    try:
        frame = base64_to_frame(payload.image)
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image encoding")
        
        # 1. Run Blink Detection (extracts landmarks and computes EAR)
        blink_res = blink_detector.process_frame(frame)
        
        # 2. Run Spoof Detection on Cropped Face
        # We need a face crop. We can run MediaPipe inside blink_detector or spoof_detector.
        # Since blink_res contains face coordinates indirectly (if success is True), let's crop the face.
        # But wait! It is easier to crop using the face detection bounding box or compute it here.
        # Let's extract face box from MediaPipe results in blink_detector.
        # Wait, let's write a simple bounding box calculator if Face Mesh succeeded.
        # Let's see: we can run the spoof check on the whole frame or a cropped face.
        # Cropping is much better because background details confuse texture analysis.
        # Let's write a small face crop extractor here using face mesh coordinates.
        face_crop = frame
        if blink_res.get("success"):
            # We can run Face Mesh or get landmarks to crop.
            # Let's extract landmarks from the face mesh process to crop the face.
            # Let's retrieve the face mesh results from blink_detector's internal solution.
            # Wait, let's just run a quick crop in the main check.
            # MediaPipe is fast enough to run. Let's do it cleanly!
            h, w = frame.shape[:2]
            # Convert frame to RGB for mediapipe
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = blink_detector.mp_face_mesh.process(rgb)
            if res.multi_face_landmarks:
                landmarks = res.multi_face_landmarks[0].landmark
                coords = np.array([[lm.x * w, lm.y * h] for lm in landmarks])
                xmin, ymin = coords.min(axis=0)
                xmax, ymax = coords.max(axis=0)
                pad_w = (xmax - xmin) * 0.1
                pad_h = (ymax - ymin) * 0.1
                box = [
                    max(0, xmin - pad_w),
                    max(0, ymin - pad_h),
                    min(w, xmax + pad_w),
                    min(h, ymax + pad_h)
                ]
                face_crop = crop_box(frame, box)
        
        spoof_res = spoof_detector.check_spoof(face_crop)
        
        liveness_passed = False
        if spoof_res.get("success") and spoof_res.get("prediction") == "REAL":
            liveness_passed = True
            
        return {
            "success": True,
            "blink": {
                "eyes_closed": blink_res.get("eyes_closed", False),
                "avg_ear": blink_res.get("avg_ear", 0.0),
                "left_ear": blink_res.get("left_ear", 0.0),
                "right_ear": blink_res.get("right_ear", 0.0)
            },
            "spoof": {
                "spoof_probability": spoof_res.get("spoof_probability", 1.0),
                "liveness_score": spoof_res.get("liveness_score", 0.0),
                "prediction": spoof_res.get("prediction", "SPOOF"),
                "attack_type": spoof_res.get("attack_type", "UNKNOWN"),
                "method": spoof_res.get("method", "none")
            },
            "liveness_passed": liveness_passed
        }
    except Exception as e:
        logger.error(f"Error during liveness check: {e}", exc_info=True)
        return {"success": False, "message": str(e)}

import cv2
if __name__ == "__main__":
    uvicorn.run(app, host=settings.LIVENESS_SERVICE_HOST, port=settings.LIVENESS_SERVICE_PORT)
