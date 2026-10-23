from abc import ABC, abstractmethod
from app.models.chat import ChatRequest, ChatResponse
import httpx
from typing import Dict, Any, AsyncGenerator

class BaseProvider(ABC):
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    @abstractmethod
    def get_url(self, request: ChatRequest) -> str:
        """API uç noktası URL'sini döndürür."""
        pass

    @abstractmethod
    def get_headers(self) -> Dict[str, str]:
        """Yetkilendirme başlıklarını döndürür."""
        pass

    @abstractmethod
    def convert_request(self, request: ChatRequest) -> Dict[str, Any]:
        """Bizim standart isteğimizi, sağlayıcının formatına çevirir."""
        pass

    @abstractmethod
    def convert_response(self, provider_response: Dict[str, Any], model_name: str) -> ChatResponse:
        """Sağlayıcının cevabını, bizim standart formatımıza çevirir."""
        pass

    @abstractmethod
    async def stream_chat(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """Akışlı (Streaming) yanıt üretir."""
        yield "" # Abstract method placeholder
