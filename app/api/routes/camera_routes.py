from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import cv2
import time
from app.api.schemas.models import CameraStartPayload
from app.camera.camera_manager import CameraManager
from app.pipeline.verification_pipeline import VerificationPipeline
from app.utils.logger import setup_logger

router = APIRouter(prefix="/camera", tags=["Camera Controls"])
logger = setup_logger("camera_routes", "central.log")

# Global reference to the active CameraManager
camera_manager = None
pipeline = VerificationPipeline()
latest_recognition = {"name": "Detecting...", "time": 0}

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
    
    # Update global recognition state for the live video stream overlay
    global latest_recognition
    if result.get("success"):
        latest_recognition = {"name": result.get("name"), "time": time.time()}
    elif result.get("status") == "REJECTED":
        latest_recognition = {"name": "Unknown Face", "time": time.time()}
        
    return result

def generate_frames():
    global camera_manager
    
    while camera_manager is not None and camera_manager.is_running:
        frame = camera_manager.get_latest_frame()
        if frame is not None:
            display_frame = frame.copy()
            
            global latest_recognition
            # Show recognition status if it's recent (within 5 seconds)
            if time.time() - latest_recognition["time"] < 5.0:
                label = latest_recognition["name"]
                color = (0, 0, 255) if label == "Unknown Face" else (0, 255, 0)
                cv2.putText(display_frame, f"Status: {label}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
                
            # Compress to JPG (quality 70 for smoother streaming)
            ret, buffer = cv2.imencode('.jpg', display_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        
        # Target ~30 FPS
        time.sleep(0.033)

@router.get("/stream")
def video_feed():
    """Stream live MJPEG frames from the active camera."""
    global camera_manager
    if camera_manager is None or not camera_manager.is_running:
        raise HTTPException(status_code=400, detail="Camera is not active.")
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")
