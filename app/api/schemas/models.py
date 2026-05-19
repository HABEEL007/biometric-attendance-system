from pydantic import BaseModel, Field
from typing import List, Optional

class StaffCreate(BaseModel):
    employee_id: str = Field(..., description="Unique business employee ID")
    name: str = Field(..., description="Full name of the employee")
    role: Optional[str] = Field(None, description="Job title/role")
    department: Optional[str] = Field(None, description="Department name")
    shift_start_time: Optional[str] = Field(None, description="Format HH:MM")

class StaffResponse(BaseModel):
    staff_id: int
    employee_id: str
    name: str
    role: Optional[str]
    department: Optional[str]
    shift_start_time: Optional[str]
    is_active: int
    created_at: str

class EnrollPayload(BaseModel):
    employee_id: str
    name: str
    role: Optional[str] = None
    department: Optional[str] = None
    shift_start_time: Optional[str] = None
    face_images: List[str] = Field(default=[], description="List of base64 encoded face images")
    eye_images: List[str] = Field(default=[], description="List of base64 encoded eye images")

class ManualCheckInPayload(BaseModel):
    employee_id: str
    event_type: str = Field("CHECK_IN", description="CHECK_IN or CHECK_OUT")

class CameraStartPayload(BaseModel):
    source: str = Field("0", description="Webcam index (e.g. 0) or RTSP URL / video path")
    camera_id: str = Field("default_cam", description="Identifier for the camera feed")

class FrameVerificationPayload(BaseModel):
    image: str = Field(..., description="Base64 encoded string of the camera frame")
    camera_id: str = Field("default_cam", description="Identifier of the camera source")
