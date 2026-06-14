import httpx
from typing import Optional, Dict, Any
from app.config.settings import settings
from app.utils.logger import setup_logger

logger = setup_logger("liveness_client", "central.log")

class LivenessClient:
    def __init__(self, base_url: str = settings.LIVENESS_SERVICE_URL):
        self.base_url = base_url

    async def check(self, image_base64: str) -> Optional[Dict[str, Any]]:
        """Hits the Liveness Service /check endpoint."""
        url = f"{self.base_url}/check"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json={"image": image_base64}, timeout=5.0)
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Liveness service returned error {response.status_code}: {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Failed to connect to Liveness service at {url}: {e}")
            return None
