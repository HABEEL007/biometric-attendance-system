from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.api.schemas.models import StaffCreate
from app.database.db_manager import db

router = APIRouter(prefix="/staff", tags=["Staff Management"])

@router.post("")
def create_staff(payload: StaffCreate):
    staff_id = db.add_staff(
        employee_id=payload.employee_id,
        name=payload.name,
        role=payload.role,
        department=payload.department,
        shift_start_time=payload.shift_start_time
    )
    if not staff_id:
        raise HTTPException(status_code=400, detail="Staff member already exists or DB error.")
    return {"message": "Staff member created", "staff_id": staff_id, "employee_id": payload.employee_id}

@router.get("", response_model=List[dict])
def list_staff():
    return db.get_all_staff()

@router.get("/{employee_id}")
def get_staff(employee_id: str):
    staff = db.get_staff_by_employee_id(employee_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return staff

@router.delete("/{employee_id}")
def delete_staff(employee_id: str):
    staff = db.get_staff_by_employee_id(employee_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    success = db.delete_staff(staff["staff_id"])
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete staff member")
    return {"message": f"Staff member with employee_id '{employee_id}' deleted successfully."}
