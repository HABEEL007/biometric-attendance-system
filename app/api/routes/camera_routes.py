from fastapi import APIRouter, HTTPException
from app.api.schemas.models import CameraStartPayload
from app.camera.camera_manager import CameraManager
from app.pipeline.verification_pipeline import VerificationPipeline
from app.utils.logger import setup_logger

router = APIRouter(prefix="/camera", tags=["Camera Controls"])
logger = setup_logger("camera_routes", "central.log")

# Global reference to the active CameraManager
camera_manager = None
pipeline = VerificationPipeline()

@router.post("/start")
def start_camera(payload: CameraStartPayload):
    global camera_manager
    if camera_manager is not None and camera_manager.is_running:
         return {"message": "Camera already running", "status": camera_manager.get_status()}
         
    try:
        camera_manager = CameraManager(source=payload.source, camera_id=payload.camera_id)
        camera_manager.start()
        return {"message": "Camera started", "status": camera_manager.get_status()}
    except Exception as e:
        logger.error(f"Error starting camera: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
def stop_camera():
    global camera_manager
    if camera_manager is None or not camera_manager.is_running:
         return {"message": "Camera is not running"}
         
    camera_manager.stop()
    status = camera_manager.get_status()
    camera_manager = None
    return {"message": "Camera stopped", "status": status}

@router.get("/status")
def get_camera_status():
    global camera_manager
    if camera_manager is None:
        return {"status": "INACTIVE", "is_running": False}
    return camera_manager.get_status()

@router.get("/snapshot")
async def process_snapshot():
    """Grabs the latest frame from the running camera and runs it through the verification pipeline."""
    global camera_manager
    if camera_manager is None or not camera_manager.is_running:
        raise HTTPException(status_code=400, detail="Camera is not active. Start the camera first.")
        
    frame = camera_manager.get_latest_frame()
    if frame is None:
        raise HTTPException(status_code=503, detail="Camera is active but no frame is captured yet. Try again.")
        
    result = await pipeline.process_frame(frame, camera_id=camera_manager.camera_id)
    return result
