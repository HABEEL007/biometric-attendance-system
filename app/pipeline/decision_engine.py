from app.config.settings import settings
from app.utils.logger import setup_logger

logger = setup_logger("decision_engine", "central.log")

class DecisionEngine:
    @staticmethod
    def evaluate(face_score: float, face_match: bool, 
                 liveness_score: float, liveness_passed: bool) -> dict:
        """
        Final Score = (Face Score * 0.70) + (Liveness Score * 0.30)
        
        Approval conditions:
        - Face Match = PASS
        - Liveness = PASS
        - Final Score >= 0.75
        """
        # Face Score (Cosine Similarity) is typically between 0.40 and 0.70.
        # We need to normalize it to behave like a percentage (0.0 to 1.0) before weighting.
        # If it's a match, we boost it. 0.50 similarity becomes ~0.85 confidence.
        normalized_face = min(1.0, face_score * 1.7) if face_match else 0.0
        
        # Calculate combined weighted score
        final_score = (normalized_face * 0.70) + (liveness_score * 0.30)
        
        # Verify individual and weighted passes
        conditions = {
            "face_match_passed": face_match,
            "liveness_passed": liveness_passed,
            "score_passed": final_score >= settings.FINAL_DECISION_THRESHOLD
        }
        
        approved = all(conditions.values())
        
        reject_reason = None
        if not approved:
            reasons = []
            if not face_match:
                reasons.append("Face verification failed (unknown face or mismatch)")
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
