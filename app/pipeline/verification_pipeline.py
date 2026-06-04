import cv2
import numpy as np
import time
import asyncio
import faiss
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from app.config.settings import settings
from app.database.db_manager import db
from app.services.face_client import FaceClient
from app.services.iris_client import IrisClient
from app.services.liveness_client import LivenessClient
from app.pipeline.decision_engine import DecisionEngine
from app.attendance.attendance_manager import attendance_mgr
from app.utils.image_utils import frame_to_base64, calculate_blurriness, save_snapshot
from app.utils.logger import setup_logger

logger = setup_logger("verification_pipeline", "central.log")

class VerificationPipeline:
    def __init__(self):
        self.face_client = FaceClient()
        self.iris_client = IrisClient()
        self.liveness_client = LivenessClient()
        self.is_processing = False
        self._build_faiss_index()

    def _build_faiss_index(self):
        """Builds a FAISS index from all embeddings in the database."""
        logger.info("Building FAISS index for face embeddings...")
        self.faiss_index = faiss.IndexFlatIP(512)
        self.index_to_staff = {}
        
        db_embeddings = db.get_all_face_embeddings()
        if not db_embeddings:
            logger.warning("No face embeddings found in database.")
            return

        # Prepare matrix
        emb_matrix = np.zeros((len(db_embeddings), 512), dtype=np.float32)
        for i, (staff_id, emb) in enumerate(db_embeddings):
            # Ensure it is normalized for IP search (cosine similarity)
            norm = np.linalg.norm(emb)
            if norm > 0:
                emb = emb / norm
            emb_matrix[i] = emb
            self.index_to_staff[i] = staff_id
            
        self.faiss_index.add(emb_matrix)
        logger.info(f"FAISS index built with {len(db_embeddings)} faces.")

    def check_quality(self, frame: np.ndarray) -> Tuple[bool, str]:
        """Runs quality checks on the raw frame before running heavy AI APIs."""
        # 1. Blurriness Check
        blur_val = calculate_blurriness(frame)
        if blur_val < 80.0: # Minimum acceptable sharpness
            return False, f"Image too blurry (variance: {blur_val:.1f})"

        # 2. Lighting Check (Brightness average)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        if mean_brightness < 40.0:
            return False, f"Image too dark (brightness: {mean_brightness:.1f})"
        if mean_brightness > 220.0:
            return False, f"Image too bright/washed out (brightness: {mean_brightness:.1f})"

        # 3. Minimum dimensions
        h, w = frame.shape[:2]
        if h < 240 or w < 320:
            return False, f"Image resolution too low ({w}x{h})"

        return True, "Quality Check PASS"

    async def process_frame(self, frame: np.ndarray, camera_id: str = "default_cam") -> dict:
        """
        Main pipeline orchestrator.
        Accepts frame, processes quality, runs face recognition, iris verification, 
        liveness check, decision engine, and records attendance.
        """
        if self.is_processing:
            return {
                "success": False,
                "status": "SKIPPED",
                "message": "Pipeline busy, frame skipped to maintain FPS"
            }
            
        self.is_processing = True
        try:
            # 1. Run Quality Check
            quality_ok, quality_msg = self.check_quality(frame)
            if not quality_ok:
                logger.warning(f"Frame quality check failed: {quality_msg}")
                return {
                    "success": False,
                    "status": "QUALITY_REJECTED",
                    "message": quality_msg
                }

            # Convert frame to base64 for API requests
            b64_frame = frame_to_base64(frame)

            # 2. Hit Face Recognition Service
            face_data = await self.face_client.detect_and_embed(b64_frame)
        if not face_data or not face_data.get("success"):
            # Log raw detection failure
            db.add_raw_detection_log(
                camera_id=camera_id,
                person_detected=0,
                face_detected=0,
                face_score=0.0,
                iris_score=0.0,
                liveness_score=0.0,
                final_decision="NO_FACE_DETECTED",
                frame_path=""
            )
            return {
                "success": False,
                "status": "NO_FACE",
                "message": face_data.get("message") if face_data else "Failed to contact Face service"
            }

        # Face detected successfully
        face_emb = np.array(face_data["embedding"], dtype=np.float32)
        bbox = face_data["bbox"]
        
        # 3. Database Vector Search (Face Match) using FAISS
        identified_staff_id = None
        best_face_score = 0.0
        face_match = False
        
        if self.faiss_index.ntotal > 0:
            query_emb = np.expand_dims(face_emb, axis=0)
            D, I = self.faiss_index.search(query_emb, 1)
            similarity = float(D[0][0])
            if similarity > settings.FACE_MATCH_THRESHOLD:
                best_face_score = similarity
                identified_staff_id = self.index_to_staff.get(int(I[0][0]))
                if identified_staff_id is not None:
                    face_match = True

        # 4. Iris Verification
        iris_score = 0.0
        iris_match = False
        iris_template_data = None
        
        if face_match and identified_staff_id:
            # Extract current template
            iris_template_data = await self.iris_client.extract_template(b64_frame)
            if iris_template_data and iris_template_data.get("success"):
                curr_template = iris_template_data["template"]
                
                # Fetch database templates
                db_templates = db.get_all_iris_templates()
                # Find matching template for this staff member
                for staff_id, l_temp, r_temp in db_templates:
                    if staff_id == identified_staff_id:
                        # Combine DB template if available
                        db_temp = None
                        if l_temp is not None and r_temp is not None:
                            db_temp = np.concatenate([l_temp, r_temp])
                        elif l_temp is not None:
                            db_temp = l_temp
                        elif r_temp is not None:
                            db_temp = r_temp
                            
                        if db_temp is not None:
                            match_res = await self.iris_client.match_templates(curr_template, db_temp.tolist())
                            if match_res:
                                iris_score = match_res["similarity"]
                                iris_match = match_res["match"]
                                break

        # 5. Liveness & Anti-Spoofing Check
        liveness_score = 0.0
        liveness_passed = False
        blink_data = {"eyes_closed": False, "avg_ear": 0.0}
        spoof_data = {"spoof_probability": 1.0, "prediction": "SPOOF"}
        
        liveness_res = await self.liveness_client.check(b64_frame)
        if liveness_res and liveness_res.get("success"):
            liveness_score = liveness_res["spoof"]["liveness_score"]
            liveness_passed = liveness_res["liveness_passed"]
            blink_data = liveness_res["blink"]
            spoof_data = liveness_res["spoof"]
            
            # Log liveness metrics
            db.add_liveness_log(
                staff_id=identified_staff_id,
                blink_detected=1 if blink_data["eyes_closed"] else 0,
                head_movement_detected=0,
                spoof_probability=spoof_data["spoof_probability"],
                liveness_score=liveness_score,
                attack_type=spoof_data["attack_type"],
                decision="PASSED" if liveness_passed else "FAILED"
            )

        # 6. Final Decision Engine
        # If face or iris did not match, we pass score 0
        decision = DecisionEngine.evaluate(
            face_score=best_face_score if face_match else 0.0,
            face_match=face_match,
            iris_score=iris_score if iris_match else 0.0,
            iris_match=iris_match,
            liveness_score=liveness_score,
            liveness_passed=liveness_passed
        )

        # Determine snapshot storage folder
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp_str}_{camera_id}.jpg"
        
        if decision["approved"]:
            snapshot_dir = settings.SNAPSHOT_APPROVED_DIR
            status_label = "APPROVED"
        elif face_match:
            snapshot_dir = settings.SNAPSHOT_REJECTED_DIR
            status_label = "REJECTED"
        else:
            snapshot_dir = settings.SNAPSHOT_UNKNOWN_DIR
            status_label = "UNKNOWN"

        # Save Snapshot
        snapshot_path = save_snapshot(frame, snapshot_dir, filename)

        # 7. Process Attendance Action in SQLite
        attendance_success = False
        attendance_msg = decision["reject_reason"] or "Biometric verification successful"
        
        if face_match and identified_staff_id:
            attendance_success, attendance_msg = attendance_mgr.process_biometric_event(
                staff_id=identified_staff_id,
                face_score=best_face_score,
                face_match=face_match,
                iris_score=iris_score,
                iris_match=iris_match,
                liveness_score=liveness_score,
                liveness_passed=liveness_passed,
                final_confidence=decision["final_score"],
                approved=decision["approved"],
                reject_reason=decision["reject_reason"],
                snapshot_path=snapshot_path,
                camera_id=camera_id
            )
        else:
            # Record failed log for unknown face
            db.add_attendance_record(
                staff_id=None,
                session_id=None,
                event_type="REJECTED",
                status="REJECTED",
                face_score=0.0,
                iris_score=0.0,
                liveness_score=liveness_score,
                final_confidence=decision["final_score"],
                snapshot_path=snapshot_path,
                camera_id=camera_id,
                reject_reason="Face match failed (unknown person)"
            )
            attendance_msg = "Unknown face. Registration or matching failed."

        # Add Raw Detection log
        db.add_raw_detection_log(
            camera_id=camera_id,
            person_detected=1,
            face_detected=1,
            face_score=best_face_score,
            iris_score=iris_score,
            liveness_score=liveness_score,
            final_decision=status_label,
            frame_path=snapshot_path
        )

        # Retrieve staff info if identified
        staff_info = db.get_staff_by_id(identified_staff_id) if identified_staff_id else None

        return {
            "success": decision["approved"] and attendance_success,
            "status": status_label,
            "message": attendance_msg,
            "employee_id": staff_info["employee_id"] if staff_info else None,
            "name": staff_info["name"] if staff_info else "Unknown",
            "scores": {
                "face_similarity": best_face_score,
                "iris_similarity": iris_score,
                "liveness_score": liveness_score,
                "final_weighted_score": decision["final_score"]
            },
            "checks": {
                "face_match": face_match,
                "iris_match": iris_match,
                "liveness_passed": liveness_passed
            },
            "snapshot_path": snapshot_path
        }
        
        finally:
            self.is_processing = False
