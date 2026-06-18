import cv2
import time
import asyncio
import numpy as np
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional
from ultralytics import YOLO
import supervision as sv

# ─── CONFIG ───────────────────────────────────────────────────────────────────
PERSON_MODEL_PATH   = "yolo11n.pt"          # Auto-downloads if not present
PERSON_CONF         = 0.45
RECOGNITION_TTL     = 30.0                   # Seconds — re-verify after this
MIN_TRACK_AGE       = 3                      # Frames before triggering recognition
FACE_CHECK_INTERVAL = 5                      # Check face every N frames per track

# ─── PER-TRACK STATE ──────────────────────────────────────────────────────────
@dataclass
class TrackState:
    track_id:           int
    first_seen:         float
    frame_count:        int = 0
    last_recognized_at: Optional[float] = None
    employee_id:        Optional[str]   = None
    employee_name:      Optional[str]   = None
    face_match_score:   float = 0.0
    iris_match_score:   float = 0.0
    liveness_score:     float = 0.0
    final_score:        float = 0.0
    status:             str   = "PENDING"   # PENDING / VERIFYING / APPROVED / REJECTED / QUALITY_REJECTED
    attendance_marked:  bool  = False
    bbox:               tuple = (0, 0, 0, 0)

    def needs_recognition(self) -> bool:
        if self.last_recognized_at is None:
            return self.frame_count >= MIN_TRACK_AGE

        elapsed = time.time() - self.last_recognized_at
        if elapsed > RECOGNITION_TTL:
            return True

        if self.status == "APPROVED" and elapsed < RECOGNITION_TTL:
            return False

        if self.status in ("PENDING", "REJECTED", "QUALITY_REJECTED"):
            return self.frame_count % FACE_CHECK_INTERVAL == 0

        return False


# ─── TRACK MANAGER ────────────────────────────────────────────────────────────
class TrackManager:
    def __init__(self, stale_timeout: float = 5.0):
        self.tracks: dict[int, TrackState] = {}
        self.stale_timeout = stale_timeout

    def update(self, track_id: int, bbox: tuple) -> TrackState:
        now = time.time()
        if track_id not in self.tracks:
            self.tracks[track_id] = TrackState(
                track_id=track_id,
                first_seen=now,
            )
            print(f"🆕 New track detected: ID={track_id}")

        state = self.tracks[track_id]
        state.frame_count += 1
        state.bbox = bbox
        return state

    def mark_recognized(
        self,
        track_id: int,
        employee_id:    Optional[str],
        employee_name:  Optional[str],
        face_score:     float,
        iris_score:     float,
        liveness_score: float,
        final_score:    float,
        status:         str,
    ) -> None:
        state = self.tracks.get(track_id)
        if not state:
            return
        state.last_recognized_at = time.time()
        state.employee_id        = employee_id
        state.employee_name      = employee_name
        state.face_match_score   = face_score
        state.iris_match_score   = iris_score
        state.liveness_score     = liveness_score
        state.final_score        = final_score
        state.status             = status

    def cleanup_stale(self, active_track_ids: set[int]) -> None:
        now = time.time()
        to_remove = []
        for tid, state in self.tracks.items():
            if tid not in active_track_ids:
                last_update = state.last_recognized_at or state.first_seen
                if now - last_update > self.stale_timeout:
                    to_remove.append(tid)

        for tid in to_remove:
            print(f"🗑️  Removing stale track: ID={tid}")
            del self.tracks[tid]

    def get_state(self, track_id: int) -> Optional[TrackState]:
        return self.tracks.get(track_id)


# ─── PERSON DETECTOR + TRACKER ────────────────────────────────────────────────
class PersonDetectionPipeline:
    def __init__(self, model_path: str = PERSON_MODEL_PATH):
        print("⏳ YOLOv11n person detection model loading...")
        import torch
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        self.model  = YOLO(model_path)
        self.device = device

        self.tracker = sv.ByteTrack(
            track_activation_threshold=0.25,
            lost_track_buffer=30,      
            minimum_matching_threshold=0.8,
            frame_rate=30,
        )

        self.PERSON_CLASS_ID = 0
        print("✅ Person detection + tracking ready!")

    def process_frame(self, frame: np.ndarray) -> sv.Detections:
        results = self.model.predict(
            frame,
            conf=PERSON_CONF,
            classes=[self.PERSON_CLASS_ID],
            verbose=False,
            device=self.device,
        )[0]
        detections = sv.Detections.from_ultralytics(results)
        tracked_detections = self.tracker.update_with_detections(detections)
        return tracked_detections


# ─── FACE RECOGNITION TRIGGER ─────────────────────────────────────────────────
class FaceRecognitionGate:
    def __init__(self, verification_pipeline):
        self.verification_pipeline = verification_pipeline

    async def run_full_pipeline(
        self,
        frame:    np.ndarray,
        bbox:     tuple,
        track_id: int,
    ) -> dict:
        x1, y1, x2, y2 = bbox
        
        # Add a small margin to the bounding box to capture the face/head well
        h, w = frame.shape[:2]
        margin_x = int((x2 - x1) * 0.1)
        margin_y = int((y2 - y1) * 0.1)
        
        crop_x1 = max(0, x1 - margin_x)
        crop_y1 = max(0, y1 - margin_y)
        crop_x2 = min(w, x2 + margin_x)
        crop_y2 = min(h, y2 + margin_y)
        
        person_crop = frame[crop_y1:crop_y2, crop_x1:crop_x2]
        
        # Call the existing async pipeline
        result = await self.verification_pipeline.process_frame(person_crop, camera_id=f"track_{track_id}")
        
        if not result.get("success"):
            return {
                "employee_id":     None,
                "employee_name":   None,
                "face_score":      0.0,
                "iris_score":      0.0,
                "liveness_score":  0.0,
                "final_score":     0.0,
                "status":          result.get("status", "REJECTED"),
            }

        return {
            "employee_id":     result.get("employee_id"),
            "employee_name":   result.get("name"),
            "face_score":      result.get("face_score", 0.0),
            "iris_score":      result.get("iris_score", 0.0),
            "liveness_score":  result.get("liveness_score", 0.0),
            "final_score":     result.get("final_score", 0.0),
            "status":          "APPROVED",
        }


# ─── MAIN ORCHESTRATOR ────────────────────────────────────────────────────────
class SmartAttendancePipeline:
    def __init__(self, verification_pipeline):
        self.person_pipeline = PersonDetectionPipeline()
        self.track_manager   = TrackManager(stale_timeout=5.0)
        self.face_gate        = FaceRecognitionGate(verification_pipeline)
        
        self.stats = {
            "total_frames":          0,
            "frames_with_person":    0,
            "recognition_triggered": 0,
            "recognition_skipped":   0,
        }

    async def process(self, frame: np.ndarray) -> list[dict]:
        self.stats["total_frames"] += 1
        results = []

        detections = self.person_pipeline.process_frame(frame)

        if len(detections) == 0:
            self.track_manager.cleanup_stale(active_track_ids=set())
            return results

        self.stats["frames_with_person"] += 1
        active_ids = set()

        # Gather tasks to process multiple persons asynchronously
        tasks = []
        track_ids = []
        bboxes = []
        states = []

        for i in range(len(detections)):
            track_id = detections.tracker_id[i]
            if track_id is None:
                continue

            active_ids.add(int(track_id))
            bbox = tuple(map(int, detections.xyxy[i]))
            
            state = self.track_manager.update(int(track_id), bbox)

            if state.needs_recognition():
                self.stats["recognition_triggered"] += 1
                state.status = "VERIFYING"
                # Queue the async recognition task
                tasks.append(self.face_gate.run_full_pipeline(frame, bbox, int(track_id)))
            else:
                self.stats["recognition_skipped"] += 1
            
            track_ids.append(int(track_id))
            bboxes.append(bbox)
            states.append(state)

        # Run all pending face recognitions concurrently
        if tasks:
            recog_results = await asyncio.gather(*tasks)
            
            # Update states with results
            res_idx = 0
            for state in states:
                if state.status == "VERIFYING":
                    r = recog_results[res_idx]
                    res_idx += 1
                    
                    self.track_manager.mark_recognized(
                        track_id=state.track_id,
                        employee_id=r["employee_id"],
                        employee_name=r["employee_name"],
                        face_score=r["face_score"],
                        iris_score=r["iris_score"],
                        liveness_score=r["liveness_score"],
                        final_score=r["final_score"],
                        status=r["status"],
                    )
                    
                    if r["status"] == "APPROVED" and not state.attendance_marked:
                        state.attendance_marked = True

        for i in range(len(track_ids)):
            results.append({
                "track_id": track_ids[i],
                "bbox":     bboxes[i],
                "state":    states[i],
            })

        self.track_manager.cleanup_stale(active_ids)
        return results

    def get_stats_string(self) -> str:
        s = self.stats
        skip_rate = (
            s["recognition_skipped"] /
            max(1, s["recognition_triggered"] + s["recognition_skipped"])
            * 100
        )
        return (
            f"Frames: {s['total_frames']} | "
            f"With Person: {s['frames_with_person']} | "
            f"Recognition Triggered: {s['recognition_triggered']} | "
            f"Skipped (cached): {s['recognition_skipped']} | "
            f"Efficiency: {skip_rate:.1f}% saved"
        )


# ─── DRAWING UTILS ────────────────────────────────────────────────────────────
def draw_results(frame: np.ndarray, results: list[dict]) -> np.ndarray:
    STATUS_COLORS = {
        "PENDING":   (100, 100, 100),
        "VERIFYING": (0, 165, 255),
        "APPROVED":  (0, 200, 0),
        "REJECTED":  (0, 0, 255),
        "QUALITY_REJECTED": (128, 0, 128)
    }

    for r in results:
        x1, y1, x2, y2 = r["bbox"]
        state = r["state"]
        color = STATUS_COLORS.get(state.status, (255, 255, 255))

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        label = f"ID:{state.track_id} "
        if state.employee_name:
            label += f"{state.employee_name} ({state.final_score*100:.0f}%)"
        else:
            label += state.status

        cv2.putText(
            frame, label, (x1, y1 - 8),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2,
        )

    return frame
