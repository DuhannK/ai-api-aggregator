from abc import ABC, abstractmethod
from app.models.vision import VisionRequest, VisionResponse
import httpx

class BaseVisionProvider(ABC):
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    @abstractmethod
    async def analyze_image(self, request: VisionRequest) -> VisionResponse:
        """Bir resmi analiz eder ve metin açıklaması döner."""
        pass
