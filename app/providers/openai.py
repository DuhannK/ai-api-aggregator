from app.providers.base import BaseProvider
from app.models.chat import ChatRequest, ChatResponse
from app.core.config import settings
from typing import Dict, Any, AsyncGenerator
import json

class OpenAIProvider(BaseProvider):
    def get_headers(self) -> Dict[str, str]:
        if not settings.OPENAI_API_KEY:
            raise ValueError("Yapılandırma Hatası: .env dosyasında OPENAI_API_KEY bulunamadı.")
        return {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

    def get_url(self, request: ChatRequest) -> str:
        return "https://api.openai.com/v1/chat/completions"

    def convert_request(self, request: ChatRequest) -> Dict[str, Any]:
        # Bizim Message modelimizi dict'e çevir
        messages_dict = [msg.model_dump() for msg in (request.messages or [])]

        payload = {
            "model": request.model,
            "messages": messages_dict,
            "stream": request.stream,
            "temperature": request.temperature,
        }

        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        if request.json_mode:
            payload["response_format"] = {"type": "json_object"}

        return payload

    def convert_response(self, provider_response: Dict[str, Any], model_name: str) -> ChatResponse:
        try:
            content = provider_response['choices'][0]['message']['content']
            finish_reason = provider_response['choices'][0]['finish_reason']
            return ChatResponse(
                model_used=model_name,
                content=content,
                finish_reason=finish_reason
            )
        except KeyError:
             raise ValueError(f"OpenAI Yanıt Hatası: {provider_response}")

    async def stream_chat(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        url = self.get_url(request)
        headers = self.get_headers()
        payload = self.convert_request(request)

        async with self.client.stream("POST", url, json=payload, headers=headers) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk_data = json.loads(data_str)
                        delta = chunk_data['choices'][0]['delta'].get('content')
                        if delta:
                            yield delta
                    except json.JSONDecodeError:
                        continue
