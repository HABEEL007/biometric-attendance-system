from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import cv2
import time
import asyncio
import numpy as np
import av
import fractions
from aiortc import VideoStreamTrack, RTCPeerConnection, RTCSessionDescription
from pydantic import BaseModel
from app.api.schemas.models import CameraStartPayload
from app.camera.camera_manager import CameraManager
from app.pipeline.verification_pipeline import VerificationPipeline
from app.pipeline.person_tracking_pipeline import SmartAttendancePipeline, draw_results
from app.utils.logger import setup_logger

router = APIRouter(prefix="/camera", tags=["Camera Controls"])
logger = setup_logger("camera_routes", "central.log")

# Global reference to the active CameraManager
camera_manager = None
pipeline = VerificationPipeline()
smart_pipeline = SmartAttendancePipeline(pipeline)
latest_recognition = {"name": "Detecting...", "time": 0}

# WebRTC Global State
pcs = set()

class WebRTCOffer(BaseModel):
    sdp: str
    type: str

class CameraStreamTrack(VideoStreamTrack):
    """
    A video stream track that transforms frames from an OpenCV camera.
    """
    def __init__(self):
        super().__init__()  # Initialize the base class
        
    async def recv(self):
        global camera_manager, smart_pipeline
        pts, time_base = await self.next_timestamp()
        
        frame = None
        if camera_manager is not None and camera_manager.is_running:
            frame = camera_manager.get_latest_frame()
            
        if frame is None:
            # Send a black frame if no camera is active
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
        else:
            # Process through SmartAttendancePipeline for tracking/bounding boxes
            results = await smart_pipeline.process(frame)
            frame = draw_results(frame, results)
            
        # Convert BGR (OpenCV) to RGB (PyAV expects RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create an av.VideoFrame
        video_frame = av.VideoFrame.from_ndarray(frame_rgb, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        
        return video_frame

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
        latest_recognition = {"name": result.get("name"), "time": time.time(), "bbox": result.get("bbox")}
    elif result.get("status") == "REJECTED":
        latest_recognition = {"name": "Unknown Face", "time": time.time(), "bbox": result.get("bbox")}
        
    return result

async def generate_frames_async():
    global camera_manager, smart_pipeline
    
    while camera_manager is not None and camera_manager.is_running:
        frame = camera_manager.get_latest_frame()
        if frame is not None:
            display_frame = frame.copy()
            
            # Process through SmartAttendancePipeline
            results = await smart_pipeline.process(display_frame)
            
            # Draw tracking results
            display_frame = draw_results(display_frame, results)
                
            # Compress to JPG (quality 70 for smoother streaming)
            ret, buffer = cv2.imencode('.jpg', display_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        
        # Target ~30 FPS
        await asyncio.sleep(0.033)

@router.get("/stream")
async def video_feed():
    """Stream live MJPEG frames from the active camera (Legacy/Fallback)."""
    global camera_manager
    if camera_manager is None or not camera_manager.is_running:
        raise HTTPException(status_code=400, detail="Camera is not active.")
    return StreamingResponse(generate_frames_async(), media_type="multipart/x-mixed-replace; boundary=frame")

@router.post("/webrtc/offer")
async def webrtc_offer(offer: WebRTCOffer):
    """WebRTC endpoint to establish a low-latency video stream."""
    global camera_manager
    if camera_manager is None or not camera_manager.is_running:
        raise HTTPException(status_code=400, detail="Camera is not active.")
        
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info(f"WebRTC Connection state is {pc.connectionState}")
        if pc.connectionState == "failed" or pc.connectionState == "closed":
            pcs.discard(pc)

    # Attach our custom camera track
    pc.addTrack(CameraStreamTrack())

    # Create session description from the offer
    offer_sdp = RTCSessionDescription(sdp=offer.sdp, type=offer.type)
    await pc.setRemoteDescription(offer_sdp)

    # Generate answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
