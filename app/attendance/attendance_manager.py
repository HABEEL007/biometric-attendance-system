from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from app.database.db_manager import db
from app.attendance.cooldown_tracker import CooldownTracker
from app.utils.logger import setup_logger

logger = setup_logger("attendance_manager", "central.log")

class AttendanceManager:
    def __init__(self):
        self.cooldown_tracker = CooldownTracker()

    def process_biometric_event(self, staff_id: int, 
                                face_score: float, face_match: bool,
                                iris_score: float, iris_match: bool,
                                liveness_score: float, liveness_passed: bool,
                                final_confidence: float, approved: bool,
                                reject_reason: str, snapshot_path: str,
                                camera_id: str) -> Tuple[bool, str]:
        """
        Processes biometric verification event. If approved and cooldown checks out,
        it registers a check-in or check-out session & record in the database.
        Returns: (success_bool, message)
        """
        # If biometric check failed, insert a rejected record immediately
        if not approved:
            db.add_attendance_record(
                staff_id=staff_id if staff_id > 0 else None,
                session_id=None,
                event_type="REJECTED",
                status="REJECTED",
                face_score=face_score,
                iris_score=iris_score,
                liveness_score=liveness_score,
                final_confidence=final_confidence,
                snapshot_path=snapshot_path,
                camera_id=camera_id,
                reject_reason=reject_reason
            )
            return False, f"Attendance rejected: {reject_reason}"

        # Cooldown check
        if self.cooldown_tracker.is_on_cooldown(staff_id):
            return False, "User is on cooldown. Please wait before scanning again."

        # Fetch staff details
        staff = db.get_staff_by_id(staff_id)
        if not staff:
            return False, "Staff member not found in database."

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%Y-%m-%d %H:%M:%S")

        # Get or create daily attendance session
        session = db.get_attendance_session(staff_id, date_str)
        
        event_type = "CHECK_IN"
        session_id = None

        if session:
            # They have already marked attendance today
            return False, f"Attendance already marked for today. Have a good day, {staff['name']}!"

        # 1. First scan of the day -> CHECK_IN
        # Determine if late
        is_late = 0
        if staff.get("shift_start_time"):
            try:
                shift_time = datetime.strptime(f"{date_str} {staff['shift_start_time']}", "%Y-%m-%d %H:%M")
                if now > shift_time:
                    is_late = 1
            except ValueError:
                logger.warning(f"Invalid shift start time format '{staff['shift_start_time']}' for staff {staff_id}")

        session_id = db.create_attendance_session(
            staff_id=staff_id,
            date_str=date_str,
            current_status="IN",
            first_check_in=time_str,
            is_late=is_late
        )
        event_type = "CHECK_IN"
        message = f"Attendance Marked successfully. Welcome {staff['name']}!"

        # Add the detailed attendance record
        db.add_attendance_record(
            staff_id=staff_id,
            session_id=session_id,
            event_type=event_type,
            status="APPROVED",
            face_score=face_score,
            iris_score=iris_score,
            liveness_score=liveness_score,
            final_confidence=final_confidence,
            snapshot_path=snapshot_path,
            camera_id=camera_id,
            reject_reason=None
        )

        # Update cooldown
        self.cooldown_tracker.update_cooldown(staff_id)
        
        logger.info(f"Attendance processed for {staff['name']}: {event_type} - {message}")
        return True, message

attendance_mgr = AttendanceManager()
