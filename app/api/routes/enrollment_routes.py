from fastapi import APIRouter, HTTPException
from app.api.schemas.models import EnrollPayload
from app.enrollment.enrollment_manager import enrollment_mgr
from app.database.db_manager import db

router = APIRouter(prefix="/enrollment", tags=["Enrollment Operations"])

@router.post("/enroll")
def enroll_staff(payload: EnrollPayload):
    result = enrollment_mgr.enroll(
        employee_id=payload.employee_id,
        name=payload.name,
        role=payload.role,
        department=payload.department,
        shift_start_time=payload.shift_start_time,
        face_images=payload.face_images,
        eye_images=payload.eye_images
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result

@router.get("/status/{employee_id}")
def check_enrollment_status(employee_id: str):
    staff = db.get_staff_by_employee_id(employee_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
        
    embeddings = db.get_face_embeddings_by_staff(staff["staff_id"])
    
    # Check iris templates
    db_templates = db.get_all_iris_templates()
    has_iris = False
    for staff_id, _, _ in db_templates:
        if staff_id == staff["staff_id"]:
            has_iris = True
            break
            
    return {
        "employee_id": employee_id,
        "name": staff["name"],
        "face_embeddings_count": len(embeddings),
        "iris_registered": has_iris,
        "ready_for_attendance": len(embeddings) > 0 and has_iris
    }
