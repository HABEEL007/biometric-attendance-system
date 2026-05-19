import requests
from typing import Optional, Dict, Any
from app.config.settings import settings
from app.utils.logger import setup_logger

logger = setup_logger("face_client", "central.log")

class FaceClient:
    def __init__(self, base_url: str = settings.FACE_SERVICE_URL):
        self.base_url = base_url

    def detect_and_embed(self, image_base64: str) -> Optional[Dict[str, Any]]:
        """Hits the Face Service /detect endpoint."""
        url = f"{self.base_url}/detect"
        try:
            response = requests.post(url, json={"image": image_base64}, timeout=5.0)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Face service returned error {response.status_code}: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Failed to connect to Face service at {url}: {e}")
            return None

    def match(self, embedding1: list, embedding2: list, threshold: float = settings.FACE_MATCH_THRESHOLD) -> Optional[Dict[str, Any]]:
        """Hits the Face Service /match endpoint."""
        url = f"{self.base_url}/match"
        payload = {
            "embedding1": embedding1,
            "embedding2": embedding2,
            "threshold": threshold
        }
        try:
            response = requests.post(url, json=payload, timeout=3.0)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Face service /match returned error {response.status_code}: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Failed to connect to Face service /match at {url}: {e}")
            return None
