import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
from services.iris_service.iris_detector import IrisDetector
from app.utils.image_utils import base64_to_frame
from app.config.settings import settings
from app.utils.logger import setup_logger

logger = setup_logger("iris_service", "iris_service.log")

app = FastAPI(title="Iris Biometric Service", version="2.0")
detector = IrisDetector()

class ImagePayload(BaseModel):
    image: str # Base64 encoded string of image

class MatchPayload(BaseModel):
    template1: list
    template2: list
    threshold: float = settings.IRIS_MATCH_THRESHOLD

@app.get("/health")
def health():
    return {"status": "healthy", "service": "iris_service"}

@app.post("/extract-template")
def extract_template(payload: ImagePayload):
    try:
        frame = base64_to_frame(payload.image)
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image encoding")
        
        result = detector.extract_iris_template(frame)
        return result
    except Exception as e:
        logger.error(f"Error during iris template extraction: {e}", exc_info=True)
        return {"success": False, "message": str(e)}

@app.post("/match-templates")
def match_templates(payload: MatchPayload):
    try:
        temp1 = np.array(payload.template1, dtype=np.float32)
        temp2 = np.array(payload.template2, dtype=np.float32)
        
        if len(temp1) != 512 or len(temp2) != 512:
            raise HTTPException(status_code=400, detail="Iris templates must be 512-dimensional (256 bins per eye)")
            
        similarity = IrisDetector.match_templates(temp1, temp2)
        match_result = similarity >= payload.threshold
        
        return {
            "similarity": similarity,
            "match": match_result,
            "threshold": payload.threshold
        }
    except Exception as e:
        logger.error(f"Error during iris template matching: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host=settings.IRIS_SERVICE_HOST, port=settings.IRIS_SERVICE_PORT)
