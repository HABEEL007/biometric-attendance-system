from app.config.settings import settings
from app.utils.logger import setup_logger

logger = setup_logger("decision_engine", "central.log")

class DecisionEngine:
    @staticmethod
    def evaluate(face_score: float, face_match: bool, 
                 iris_score: float, iris_match: bool, 
                 liveness_score: float, liveness_passed: bool) -> dict:
        """
        Final Score = (Face Score * 0.40) + (Iris Score * 0.35) + (Liveness Score * 0.25)
        
        Approval conditions:
        - Face Match = PASS
        - Iris Match = PASS
        - Liveness = PASS
        - Final Score >= 0.75
        """
        # Calculate combined weighted score
        final_score = (face_score * 0.40) + (iris_score * 0.35) + (liveness_score * 0.25)
        
        # Verify individual and weighted passes
        conditions = {
            "face_match_passed": face_match,
            "iris_match_passed": iris_match,
            "liveness_passed": liveness_passed,
            "score_passed": final_score >= settings.FINAL_DECISION_THRESHOLD
        }
        
        approved = all(conditions.values())
        
        reject_reason = None
        if not approved:
            reasons = []
            if not face_match:
                reasons.append("Face verification failed (unknown face or mismatch)")
            if not iris_match:
                reasons.append("Iris verification failed")
            if not liveness_passed:
                reasons.append("Liveness check failed (potential spoofing)")
            if not conditions["score_passed"]:
                reasons.append(f"Combined score {final_score:.2f} is below threshold {settings.FINAL_DECISION_THRESHOLD}")
                
            reject_reason = " | ".join(reasons)
            
        logger.info(f"Decision evaluation - Final Score: {final_score:.2f}, Approved: {approved}, Reason: {reject_reason}")
        
        return {
            "approved": approved,
            "final_score": float(final_score),
            "reject_reason": reject_reason,
            "conditions": conditions
        }
