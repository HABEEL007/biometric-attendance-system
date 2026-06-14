import time
from typing import Dict
from app.config.settings import settings
from app.utils.logger import setup_logger

logger = setup_logger("cooldown_tracker", "central.log")

class CooldownTracker:
    def __init__(self, cooldown_seconds: int = settings.COOLDOWN_SECONDS):
        self.cooldown_seconds = cooldown_seconds
        # Maps staff_id -> timestamp of last attendance record
        self.last_records: Dict[int, float] = {}

    def is_on_cooldown(self, staff_id: int) -> bool:
        """Returns True if the staff member has checked in/out within the cooldown period."""
        if staff_id not in self.last_records:
            return False
            
        elapsed = time.time() - self.last_records[staff_id]
        if elapsed < self.cooldown_seconds:
            remaining = self.cooldown_seconds - elapsed
            logger.info(f"Staff {staff_id} is on cooldown. {remaining:.1f}s remaining.")
            return True
            
        return False

    def update_cooldown(self, staff_id: int):
        """Updates the last check-in/out timestamp for the staff member."""
        self.last_records[staff_id] = time.time()
        logger.debug(f"Cooldown updated for staff {staff_id}.")
        
    def clear_cooldown(self, staff_id: int):
        """Clears the cooldown (useful if attendance failed to save or was rolled back)."""
        if staff_id in self.last_records:
            del self.last_records[staff_id]
