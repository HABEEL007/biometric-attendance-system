from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import List
from app.api.schemas.models import ManualCheckInPayload, FrameVerificationPayload
from app.database.db_manager import db
from app.pipeline.verification_pipeline import VerificationPipeline
from app.utils.image_utils import base64_to_frame

router = APIRouter(prefix="/attendance", tags=["Attendance Records"])
pipeline = VerificationPipeline()

@router.get("/today", response_model=List[dict])
def get_today_attendance():
    date_str = datetime.now().strftime("%Y-%m-%d")
    return db.get_todays_records(date_str)

@router.get("/report", response_model=List[dict])
def get_attendance_report(date: str = Query(..., description="Format YYYY-MM-DD")):
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    return db.get_todays_records(date)

@router.post("/manual-checkin")
def manual_checkin(payload: ManualCheckInPayload):
    staff = db.get_staff_by_employee_id(payload.employee_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    
    session = db.get_attendance_session(staff["staff_id"], date_str)
    
    session_id = None
    event_type = payload.event_type.upper()
    if event_type not in ("CHECK_IN", "CHECK_OUT"):
         raise HTTPException(status_code=400, detail="event_type must be CHECK_IN or CHECK_OUT")

    if not session:
        if event_type == "CHECK_OUT":
            raise HTTPException(status_code=400, detail="Cannot Check-Out before checking in.")
        session_id = db.create_attendance_session(
            staff_id=staff["staff_id"],
            date_str=date_str,
            current_status="IN",
            first_check_in=time_str
        )
    else:
        session_id = session["session_id"]
        # Update current status
        db.update_attendance_session(
            session_id=session_id,
            current_status="IN" if event_type == "CHECK_IN" else "OUT",
            last_check_out=time_str if event_type == "CHECK_OUT" else session["last_check_out"],
            total_work_minutes=session["total_work_minutes"] or 0.0,
            total_break_minutes=session["total_break_minutes"] or 0.0
        )

    record_id = db.add_attendance_record(
        staff_id=staff["staff_id"],
        session_id=session_id,
        event_type=event_type,
        status="APPROVED",
        face_score=1.0,
        iris_score=1.0,
        liveness_score=1.0,
        final_confidence=1.0,
        snapshot_path="MANUAL_BYPASS",
        camera_id="MANUAL_API",
        reject_reason="Manually marked by administrator"
    )

    return {"message": "Attendance marked manually", "record_id": record_id, "staff_name": staff["name"]}

@router.post("/verify-frame")
async def verify_frame(payload: FrameVerificationPayload):
    """
    Main API endpoint for processing frames sent from external client applications.
    Decodes the frame, runs it through the biometric verification pipeline,
    and returns a full biometric matching & logging report.
    """
    frame = base64_to_frame(payload.image)
    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image encoding")
        
    result = await pipeline.process_frame(frame, camera_id=payload.camera_id)
    return result
