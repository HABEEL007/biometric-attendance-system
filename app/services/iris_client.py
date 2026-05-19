import requests
from typing import Optional, Dict, Any
from app.config.settings import settings
from app.utils.logger import setup_logger

logger = setup_logger("iris_client", "central.log")

class IrisClient:
    def __init__(self, base_url: str = settings.IRIS_SERVICE_URL):
        self.base_url = base_url

    def extract_template(self, image_base64: str) -> Optional[Dict[str, Any]]:
        """Hits the Iris Service /extract-template endpoint."""
        url = f"{self.base_url}/extract-template"
        try:
            response = requests.post(url, json={"image": image_base64}, timeout=5.0)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Iris service returned error {response.status_code}: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Failed to connect to Iris service at {url}: {e}")
            return None

    def match_templates(self, template1: list, template2: list, threshold: float = settings.IRIS_MATCH_THRESHOLD) -> Optional[Dict[str, Any]]:
        """Hits the Iris Service /match-templates endpoint."""
        url = f"{self.base_url}/match-templates"
        payload = {
            "template1": template1,
            "template2": template2,
            "threshold": threshold
        }
        try:
            response = requests.post(url, json=payload, timeout=3.0)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Iris service /match-templates returned error {response.status_code}: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Failed to connect to Iris service /match-templates at {url}: {e}")
            return None
