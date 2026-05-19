import numpy as np
from typing import List, Dict, Any, Tuple
from app.database.db_manager import db
from app.services.face_client import FaceClient
from app.services.iris_client import IrisClient
from app.utils.logger import setup_logger

logger = setup_logger("enrollment_manager", "central.log")

class EnrollmentManager:
    def __init__(self):
        self.face_client = FaceClient()
        self.iris_client = IrisClient()

    def enroll(self, employee_id: str, name: str, role: str = None, 
               department: str = None, shift_start_time: str = None, 
               face_images: List[str] = None, eye_images: List[str] = None) -> dict:
        """
        Registers a staff member, extracts and saves face embeddings and iris templates.
        face_images: List of base64 encoded strings
        eye_images: List of base64 encoded strings
        """
        logger.info(f"Starting enrollment for employee_id: {employee_id}, name: {name}")
        
        # 1. Input Validation
        if not employee_id or not name:
            return {"success": False, "message": "employee_id and name are required."}
            
        # Check if already exists
        existing_staff = db.get_staff_by_employee_id(employee_id)
        if existing_staff:
            return {"success": False, "message": f"Staff member with employee_id '{employee_id}' already exists."}

        # 2. Extract Face Embeddings
        valid_embeddings = []
        if face_images:
            for i, img_b64 in enumerate(face_images):
                face_data = self.face_client.detect_and_embed(img_b64)
                if face_data and face_data.get("success"):
                    valid_embeddings.append(np.array(face_data["embedding"], dtype=np.float32))
                else:
                    msg = face_data.get("message") if face_data else "No response from Face service"
                    logger.warning(f"Face image {i} skipped during enrollment: {msg}")

        if not valid_embeddings:
            return {"success": False, "message": "No valid face detected in the provided images. Enrollment aborted."}

        # 3. Extract Iris Templates
        best_template = None
        best_quality = -1.0
        if eye_images:
            for i, img_b64 in enumerate(eye_images):
                iris_data = self.iris_client.extract_template(img_b64)
                if iris_data and iris_data.get("success"):
                    q_score = iris_data["quality_score"]
                    if q_score > best_quality:
                        best_quality = q_score
                        best_template = np.array(iris_data["template"], dtype=np.float32)
                else:
                    msg = iris_data.get("message") if iris_data else "No response from Iris service"
                    logger.warning(f"Eye image {i} skipped during enrollment: {msg}")

        # If iris template is missing but required, we can warn or fail.
        # Let's save what is available.
        
        # 4. Save to Database
        try:
            # Create staff entry
            staff_id = db.add_staff(
                employee_id=employee_id,
                name=name,
                role=role,
                department=department,
                shift_start_time=shift_start_time
            )
            
            if not staff_id:
                return {"success": False, "message": "Failed to create staff database record."}

            # Save all valid face embeddings
            for emb in valid_embeddings:
                db.add_face_embedding(staff_id, emb)

            # Save iris template
            if best_template is not None:
                # Left template is first 256, right is second 256
                left_eye = best_template[:256]
                right_eye = best_template[256:]
                db.add_iris_template(
                    staff_id=staff_id,
                    left_template=left_eye,
                    right_template=right_eye,
                    quality_score=best_quality
                )

            logger.info(f"Enrollment completed successfully for staff_id: {staff_id} ({name})")
            return {
                "success": True,
                "staff_id": staff_id,
                "employee_id": employee_id,
                "name": name,
                "embeddings_count": len(valid_embeddings),
                "iris_registered": best_template is not None,
                "iris_quality_score": best_quality if best_template is not None else 0.0,
                "message": "Staff enrolled successfully."
            }
        except Exception as e:
            logger.error(f"Error during enrollment save: {e}", exc_info=True)
            # Cleanup if partially created
            if 'staff_id' in locals() and staff_id:
                db.delete_staff(staff_id)
            return {"success": False, "message": f"Database transaction failed: {str(e)}"}

enrollment_mgr = EnrollmentManager()
