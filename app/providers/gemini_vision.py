from app.providers.base_vision import BaseVisionProvider
from app.models.vision import VisionRequest, VisionResponse
from app.core.config import settings
import base64
import httpx

class GeminiVisionProvider(BaseVisionProvider):
    def get_url(self, model_name):
        return f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={settings.GEMINI_API_KEY}"

    async def _url_to_base64(self, url: str) -> tuple[str, str]:
        """Resim URL'sini indirir ve Base64 formatına çevirir."""
        # Resmi indir
        response = await self.client.get(url)
        response.raise_for_status()

        # Mime tipini al (örn: image/jpeg)
        mime_type = response.headers.get("content-type", "image/jpeg")

        # Byte verisini Base64 string'e çevir
        b64_data = base64.b64encode(response.content).decode("utf-8")
        return mime_type, b64_data

    async def analyze_image(self, request: VisionRequest) -> VisionResponse:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY eksik.")

        # 1. URL'yi Base64'e çevir (Gemini için gerekli)
        mime_type, b64_data = await self._url_to_base64(request.image_url)

        # 2. Gemini Payload Hazırla
        payload = {
            "contents": [{
                "parts": [
                    {"text": request.prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": b64_data
                        }
                    }
                ]
            }],
            "generationConfig": {
                "maxOutputTokens": request.max_tokens,
                "temperature": request.temperature
            }
        }

        # 3. İsteği Gönder
        api_url = self.get_url(request.model)
        response = await self.client.post(api_url, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        data = response.json()

        # 4. Yanıtı İşle
        try:
            description = data['candidates'][0]['content']['parts'][0]['text']
            return VisionResponse(
                model_used=request.model,
                description=description
            )
        except (KeyError, IndexError):
            raise ValueError(f"Gemini Vision Hatası: {data}")
