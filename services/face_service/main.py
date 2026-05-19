import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
from services.face_service.face_detector import FaceDetector
from app.utils.image_utils import base64_to_frame
from app.config.settings import settings
from app.utils.logger import setup_logger

logger = setup_logger("face_service", "face_service.log")

app = FastAPI(title="Face Recognition Microservice", version="2.0")
detector = FaceDetector(use_gpu=settings.USE_GPU)

class ImagePayload(BaseModel):
    image: str # Base64 encoded string of image

class MatchPayload(BaseModel):
    embedding1: list
    embedding2: list
    threshold: float = settings.FACE_MATCH_THRESHOLD

@app.get("/health")
def health():
    return {"status": "healthy", "service": "face_service"}

@app.post("/detect")
def detect(payload: ImagePayload):
    try:
        # Decode image
        frame = base64_to_frame(payload.image)
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image encoding")
        
        # Run detection and embedding
        result = detector.detect_and_embed(frame)
        return result
    except Exception as e:
        logger.error(f"Error during face detection: {e}", exc_info=True)
        return {"success": False, "message": str(e)}

@app.post("/match")
def match(payload: MatchPayload):
    try:
        emb1 = np.array(payload.embedding1, dtype=np.float32)
        emb2 = np.array(payload.embedding2, dtype=np.float32)
        
        if len(emb1) != 512 or len(emb2) != 512:
            raise HTTPException(status_code=400, detail="Embeddings must be 512-dimensional vectors")
            
        similarity = FaceDetector.cosine_similarity(emb1, emb2)
        match_result = similarity >= payload.threshold
        
        return {
            "similarity": similarity,
            "match": match_result,
            "threshold": payload.threshold
        }
    except Exception as e:
        logger.error(f"Error during match: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host=settings.FACE_SERVICE_HOST, port=settings.FACE_SERVICE_PORT)
