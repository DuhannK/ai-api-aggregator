from app.providers.base_vision import BaseVisionProvider
from app.models.vision import VisionRequest, VisionResponse
from app.core.config import settings
import json

class OpenAIVisionProvider(BaseVisionProvider):
    def get_headers(self):
        return {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

    async def analyze_image(self, request: VisionRequest) -> VisionResponse:
        url = "https://api.openai.com/v1/chat/completions"

        # OpenAI Vision Formatı
        payload = {
            "model": request.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": request.prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": request.image_url}
                        }
                    ]
                }
            ],
            "max_tokens": request.max_tokens
        }

        response = await self.client.post(url, json=payload, headers=self.get_headers())
        response.raise_for_status()
        data = response.json()

        return VisionResponse(
            model_used=request.model,
            description=data['choices'][0]['message']['content']
        )
