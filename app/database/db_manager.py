import sqlite3
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
from app.config.settings import settings
from app.utils.logger import setup_logger

logger = setup_logger("db_manager", "central.log")

class DatabaseManager:
    def __init__(self, db_path: Path = settings.DATABASE_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Returns a sqlite3 connection with row factory and foreign key enabled."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self):
        """Initializes the database using the schema.sql file."""
        schema_path = Path(__file__).resolve().parent / "schema.sql"
        if not schema_path.exists():
            logger.error(f"Schema file not found at {schema_path}")
            return
            
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        try:
            with self.get_connection() as conn:
                conn.executescript(schema_sql)
                conn.commit()
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing database: {e}", exc_info=True)

    # --- Staff Operations ---
    def add_staff(self, employee_id: str, name: str, role: str = None, 
                  department: str = None, shift_start_time: str = None) -> Optional[int]:
        """Inserts a new staff member and returns their staff_id."""
        query = """
            INSERT INTO staff (employee_id, name, role, department, shift_start_time)
            VALUES (?, ?, ?, ?, ?)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (employee_id, name, role, department, shift_start_time))
                conn.commit()
                staff_id = cursor.lastrowid
                logger.info(f"Staff added successfully: {name} (ID: {employee_id}, staff_id: {staff_id})")
                return staff_id
        except sqlite3.IntegrityError:
            logger.warning(f"Staff member with employee_id '{employee_id}' already exists.")
            return None
        except Exception as e:
            logger.error(f"Error adding staff: {e}", exc_info=True)
            return None

    def get_staff_by_id(self, staff_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a staff member by database staff_id."""
        query = "SELECT * FROM staff WHERE staff_id = ?"
        try:
            with self.get_connection() as conn:
                row = conn.execute(query, (staff_id,)).fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error retrieving staff by staff_id: {e}", exc_info=True)
            return None

    def get_staff_by_employee_id(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a staff member by business employee_id."""
        query = "SELECT * FROM staff WHERE employee_id = ?"
        try:
            with self.get_connection() as conn:
                row = conn.execute(query, (employee_id,)).fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error retrieving staff by employee_id: {e}", exc_info=True)
            return None

    def get_all_staff(self) -> List[Dict[str, Any]]:
        """Retrieves all staff members."""
        query = "SELECT * FROM staff WHERE is_active = 1"
        try:
            with self.get_connection() as conn:
                rows = conn.execute(query).fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error retrieving all staff: {e}", exc_info=True)
            return []

    def delete_staff(self, staff_id: int) -> bool:
        """Deletes a staff member (cascades embeddings and iris templates)."""
        query = "DELETE FROM staff WHERE staff_id = ?"
        try:
            with self.get_connection() as conn:
                conn.execute(query, (staff_id,))
                conn.commit()
                logger.info(f"Staff with staff_id {staff_id} deleted successfully.")
                return True
        except Exception as e:
            logger.error(f"Error deleting staff: {e}", exc_info=True)
            return False

    # --- Face Embeddings Operations ---
    def add_face_embedding(self, staff_id: int, embedding: np.ndarray) -> bool:
        """Saves a 512-D face embedding as a blob."""
        query = "INSERT INTO face_embeddings (staff_id, embedding, embedding_dimension) VALUES (?, ?, ?)"
        try:
            embedding_bytes = embedding.astype(np.float32).tobytes()
            with self.get_connection() as conn:
                conn.execute(query, (staff_id, embedding_bytes, len(embedding)))
                conn.commit()
            logger.debug(f"Face embedding added for staff_id: {staff_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving face embedding: {e}", exc_info=True)
            return False

    def get_all_face_embeddings(self) -> List[Tuple[int, np.ndarray]]:
        """Loads all face embeddings from the database."""
        query = "SELECT staff_id, embedding FROM face_embeddings"
        embeddings_list = []
        try:
            with self.get_connection() as conn:
                rows = conn.execute(query).fetchall()
                for row in rows:
                    staff_id = row['staff_id']
                    emb_bytes = row['embedding']
                    emb_array = np.frombuffer(emb_bytes, dtype=np.float32)
                    embeddings_list.append((staff_id, emb_array))
            return embeddings_list
        except Exception as e:
            logger.error(f"Error loading face embeddings: {e}", exc_info=True)
            return []

    def get_face_embeddings_by_staff(self, staff_id: int) -> List[np.ndarray]:
        """Loads face embeddings for a specific staff member."""
        query = "SELECT embedding FROM face_embeddings WHERE staff_id = ?"
        embeddings_list = []
        try:
            with self.get_connection() as conn:
                rows = conn.execute(query, (staff_id,)).fetchall()
                for row in rows:
                    emb_bytes = row['embedding']
                    emb_array = np.frombuffer(emb_bytes, dtype=np.float32)
                    embeddings_list.append(emb_array)
            return embeddings_list
        except Exception as e:
            logger.error(f"Error loading face embeddings for staff {staff_id}: {e}", exc_info=True)
            return []

    # --- Iris Templates Operations ---
    def add_iris_template(self, staff_id: int, left_template: np.ndarray, 
                          right_template: np.ndarray, quality_score: float) -> bool:
        """Saves left and right eye iris templates as blobs."""
        query = """
            INSERT INTO iris_templates (staff_id, left_eye_template, right_eye_template, quality_score)
            VALUES (?, ?, ?, ?)
        """
        try:
            left_bytes = left_template.astype(np.float32).tobytes() if left_template is not None else None
            right_bytes = right_template.astype(np.float32).tobytes() if right_template is not None else None
            with self.get_connection() as conn:
                conn.execute(query, (staff_id, left_bytes, right_bytes, quality_score))
                conn.commit()
            logger.debug(f"Iris templates added for staff_id: {staff_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving iris template: {e}", exc_info=True)
            return False

    def get_all_iris_templates(self) -> List[Tuple[int, np.ndarray, np.ndarray]]:
        """Loads all iris templates (staff_id, left_template, right_template)."""
        query = "SELECT staff_id, left_eye_template, right_eye_template FROM iris_templates"
        templates = []
        try:
            with self.get_connection() as conn:
                rows = conn.execute(query).fetchall()
                for row in rows:
                    staff_id = row['staff_id']
                    
                    left_bytes = row['left_eye_template']
                    left_arr = np.frombuffer(left_bytes, dtype=np.float32) if left_bytes else None
                    
                    right_bytes = row['right_eye_template']
                    right_arr = np.frombuffer(right_bytes, dtype=np.float32) if right_bytes else None
                    
                    templates.append((staff_id, left_arr, right_arr))
            return templates
        except Exception as e:
            logger.error(f"Error loading iris templates: {e}", exc_info=True)
            return []

    def get_iris_template_by_staff(self, staff_id: int) -> Optional[Tuple[Optional[np.ndarray], Optional[np.ndarray]]]:
        """Loads iris templates for a specific staff member (left_template, right_template)."""
        query = "SELECT left_eye_template, right_eye_template FROM iris_templates WHERE staff_id = ?"
        try:
            with self.get_connection() as conn:
                row = conn.execute(query, (staff_id,)).fetchone()
                if row:
                    left_bytes = row['left_eye_template']
                    left_arr = np.frombuffer(left_bytes, dtype=np.float32) if left_bytes else None
                    
                    right_bytes = row['right_eye_template']
                    right_arr = np.frombuffer(right_bytes, dtype=np.float32) if right_bytes else None
                    return left_arr, right_arr
                return None
        except Exception as e:
            logger.error(f"Error loading iris template for staff {staff_id}: {e}", exc_info=True)
            return None

    # --- Attendance Sessions ---
    def get_attendance_session(self, staff_id: int, date_str: str) -> Optional[Dict[str, Any]]:
        """Gets attendance session for a staff member for a specific date (YYYY-MM-DD)."""
        query = "SELECT * FROM attendance_sessions WHERE staff_id = ? AND attendance_date = ?"
        try:
            with self.get_connection() as conn:
                row = conn.execute(query, (staff_id, date_str)).fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting attendance session: {e}", exc_info=True)
            return None

    def create_attendance_session(self, staff_id: int, date_str: str, current_status: str, 
                                  first_check_in: str, is_late: int = 0) -> Optional[int]:
        """Creates a new attendance session (usually at first check-in of the day)."""
        query = """
            INSERT INTO attendance_sessions (staff_id, attendance_date, current_status, first_check_in, is_late)
            VALUES (?, ?, ?, ?, ?)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (staff_id, date_str, current_status, first_check_in, is_late))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error creating attendance session: {e}", exc_info=True)
            return None

    def update_attendance_session(self, session_id: int, current_status: str, 
                                  last_check_out: str, total_work_minutes: float, 
                                  total_break_minutes: float) -> bool:
        """Updates an existing attendance session (checkout or break trigger)."""
        query = """
            UPDATE attendance_sessions 
            SET current_status = ?, last_check_out = ?, total_work_minutes = ?, total_break_minutes = ?
            WHERE session_id = ?
        """
        try:
            with self.get_connection() as conn:
                conn.execute(query, (current_status, last_check_out, total_work_minutes, total_break_minutes, session_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating attendance session: {e}", exc_info=True)
            return False

    # --- Attendance Records ---
    def add_attendance_record(self, staff_id: Optional[int], session_id: Optional[int], 
                              event_type: str, status: str, face_score: float, 
                              iris_score: float, liveness_score: float, final_confidence: float, 
                              snapshot_path: str, camera_id: str, reject_reason: str = None) -> Optional[int]:
        """Adds a record for a specific check-in / check-out / rejection event."""
        query = """
            INSERT INTO attendance_records 
            (staff_id, session_id, event_type, status, face_score, iris_score, liveness_score, 
             final_confidence, snapshot_path, camera_id, reject_reason, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (
                    staff_id, session_id, event_type, status, face_score, iris_score, 
                    liveness_score, final_confidence, snapshot_path, camera_id, reject_reason, timestamp
                ))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error adding attendance record: {e}", exc_info=True)
            return None

    def get_todays_records(self, date_str: str) -> List[Dict[str, Any]]:
        """Retrieves all attendance records for a specific day."""
        query = """
            SELECT ar.*, s.name, s.employee_id, s.department 
            FROM attendance_records ar
            LEFT JOIN staff s ON ar.staff_id = s.staff_id
            WHERE ar.timestamp LIKE ?
            ORDER BY ar.timestamp DESC
        """
        try:
            with self.get_connection() as conn:
                rows = conn.execute(query, (f"{date_str}%",)).fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error retrieving today's records: {e}", exc_info=True)
            return []

    def delete_attendance_record(self, record_id: int) -> bool:
        """Deletes a specific attendance record by its record_id."""
        query = "DELETE FROM attendance_records WHERE record_id = ?"
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, (record_id,))
                conn.commit()
                # Check if any row was actually deleted
                if cursor.rowcount > 0:
                    logger.info(f"Attendance record {record_id} deleted successfully.")
                    return True
                else:
                    logger.warning(f"Attendance record {record_id} not found.")
                    return False
        except Exception as e:
            logger.error(f"Error deleting attendance record {record_id}: {e}", exc_info=True)
            return False

    # --- Liveness Logs ---
    def add_liveness_log(self, staff_id: Optional[int], blink_detected: int, 
                         head_movement_detected: int, spoof_probability: float, 
                         liveness_score: float, attack_type: str, decision: str) -> Optional[int]:
        """Logs detailed liveness check metrics for audits."""
        query = """
            INSERT INTO liveness_logs 
            (staff_id, blink_detected, head_movement_detected, spoof_probability, liveness_score, attack_type, decision)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (staff_id, blink_detected, head_movement_detected, spoof_probability, liveness_score, attack_type, decision))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving liveness log: {e}", exc_info=True)
            return None

    # --- Raw Detection Logs ---
    def add_raw_detection_log(self, camera_id: str, person_detected: int, face_detected: int, 
                              face_score: float, iris_score: float, liveness_score: float, 
                              final_decision: str, frame_path: str) -> Optional[int]:
        """Logs raw detection metrics (for analysis/debugging)."""
        query = """
            INSERT INTO raw_detection_logs 
            (camera_id, person_detected, face_detected, face_score, iris_score, liveness_score, final_decision, frame_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (camera_id, person_detected, face_detected, face_score, iris_score, liveness_score, final_decision, frame_path))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving raw detection log: {e}", exc_info=True)
            return None

# Singleton DB manager
db = DatabaseManager()
if __name__ == "__main__":
    # Test script if executed directly
    print("Database path:", db.db_path)
    print("Tables loaded successfully.")
