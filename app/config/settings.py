import os
from pathlib import Path
from dotenv import load_dotenv

# Load env file
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    # Project Root
    BASE_DIR = Path(__file__).resolve().parents[2]
    
    # API Settings
    CENTRAL_API_HOST = os.getenv("CENTRAL_API_HOST", "127.0.0.1")
    CENTRAL_API_PORT = int(os.getenv("CENTRAL_API_PORT", 8000))
    
    FACE_SERVICE_HOST = os.getenv("FACE_SERVICE_HOST", "127.0.0.1")
    FACE_SERVICE_PORT = int(os.getenv("FACE_SERVICE_PORT", 8001))
    
    IRIS_SERVICE_HOST = os.getenv("IRIS_SERVICE_HOST", "127.0.0.1")
    IRIS_SERVICE_PORT = int(os.getenv("IRIS_SERVICE_PORT", 8002))
    
    LIVENESS_SERVICE_HOST = os.getenv("LIVENESS_SERVICE_HOST", "127.0.0.1")
    LIVENESS_SERVICE_PORT = int(os.getenv("LIVENESS_SERVICE_PORT", 8003))

    # URLs for Microservices
    FACE_SERVICE_URL = f"http://{FACE_SERVICE_HOST}:{FACE_SERVICE_PORT}"
    IRIS_SERVICE_URL = f"http://{IRIS_SERVICE_HOST}:{IRIS_SERVICE_PORT}"
    LIVENESS_SERVICE_URL = f"http://{LIVENESS_SERVICE_HOST}:{LIVENESS_SERVICE_PORT}"

    # Database
    DATABASE_PATH = BASE_DIR / os.getenv("DATABASE_PATH", "data/attendance.db")
    
    # Biometric & Quality Thresholds
    # Face match is now dynamically calculated based on face size, replacing FACE_MATCH_THRESHOLD
    FACE_MATCH_THRESHOLD = float(os.getenv("FACE_MATCH_THRESHOLD", 0.40)) # Kept for UI compatibility
    QUALITY_SCORE_THRESHOLD = 0.40
    POSE_YAW_LIMIT = 65.0
    POSE_PITCH_LIMIT = 50.0
    POSE_ROLL_LIMIT = 45.0
    
    IRIS_MATCH_THRESHOLD = float(os.getenv("IRIS_MATCH_THRESHOLD", 0.65))
    IRIS_DEMO_THRESHOLD = float(os.getenv("IRIS_DEMO_THRESHOLD", 0.65))
    LIVENESS_THRESHOLD = float(os.getenv("LIVENESS_THRESHOLD", 0.70))
    FINAL_DECISION_THRESHOLD = float(os.getenv("FINAL_DECISION_THRESHOLD", 0.75))
    COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", 30))

    # Snapshots
    SNAPSHOT_APPROVED_DIR = BASE_DIR / os.getenv("SNAPSHOT_APPROVED_DIR", "snapshots/approved")
    SNAPSHOT_REJECTED_DIR = BASE_DIR / os.getenv("SNAPSHOT_REJECTED_DIR", "snapshots/rejected")
    SNAPSHOT_UNKNOWN_DIR = BASE_DIR / os.getenv("SNAPSHOT_UNKNOWN_DIR", "snapshots/unknown")
    
    # Hardware
    USE_GPU = os.getenv("USE_GPU", "False").lower() in ("true", "1", "yes")

# Ensure required directories exist
settings = Settings()
for path in [
    settings.DATABASE_PATH.parent,
    settings.SNAPSHOT_APPROVED_DIR,
    settings.SNAPSHOT_REJECTED_DIR,
    settings.SNAPSHOT_UNKNOWN_DIR,
    settings.BASE_DIR / "logs",
    settings.BASE_DIR / "models",
    settings.BASE_DIR / "data/embeddings",
    settings.BASE_DIR / "data/iris_templates"
]:
    path.mkdir(parents=True, exist_ok=True)
