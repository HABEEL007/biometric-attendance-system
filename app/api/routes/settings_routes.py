from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import set_key
from app.config.settings import settings, env_path

router = APIRouter(prefix="/settings", tags=["Settings"])

class SettingsUpdate(BaseModel):
    FACE_MATCH_THRESHOLD: float = None
    IRIS_MATCH_THRESHOLD: float = None
    LIVENESS_THRESHOLD: float = None
    FINAL_DECISION_THRESHOLD: float = None
    COOLDOWN_SECONDS: int = None

@router.get("")
def get_settings():
    return {
        "FACE_MATCH_THRESHOLD": settings.FACE_MATCH_THRESHOLD,
        "IRIS_MATCH_THRESHOLD": settings.IRIS_MATCH_THRESHOLD,
        "LIVENESS_THRESHOLD": settings.LIVENESS_THRESHOLD,
        "FINAL_DECISION_THRESHOLD": settings.FINAL_DECISION_THRESHOLD,
        "COOLDOWN_SECONDS": settings.COOLDOWN_SECONDS
    }

@router.post("")
def update_settings(payload: SettingsUpdate):
    updates = payload.dict(exclude_unset=True)
    
    # Update in memory
    for k, v in updates.items():
        if hasattr(settings, k):
            setattr(settings, k, v)
            
    # Persist to .env file
    if env_path.exists():
        for k, v in updates.items():
            set_key(str(env_path), k, str(v))
            
    return {"success": True, "message": "Settings updated successfully"}
