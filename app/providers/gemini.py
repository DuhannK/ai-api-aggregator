from app.providers.base import BaseProvider
from app.models.chat import ChatRequest, ChatResponse
from app.core.config import settings
from typing import Dict, Any, AsyncGenerator
import json

class GeminiProvider(BaseProvider):
    def get_headers(self) -> Dict[str, str]:
        return {"Content-Type": "application/json"}

    def get_url(self, request: ChatRequest) -> str:
        if not settings.GEMINI_API_KEY:
            raise ValueError("HATA: .env dosyasında GEMINI_API_KEY eksik!")

        base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{request.model}:"
        if request.stream:
            return f"{base_url}streamGenerateContent?key={settings.GEMINI_API_KEY}&alt=sse"
        return f"{base_url}generateContent?key={settings.GEMINI_API_KEY}"

    def convert_request(self, request: ChatRequest) -> Dict[str, Any]:
        contents = []
        system_instruction = None

        source_messages = request.messages if request.messages else []
        for msg in source_messages:
            if msg.role == "system":
                system_instruction = {"parts": [{"text": msg.content}]}
            elif msg.role == "user":
                contents.append({"role": "user", "parts": [{"text": msg.content}]})
            elif msg.role == "assistant":
                contents.append({"role": "model", "parts": [{"text": msg.content}]})

        # İçerik boşsa varsayılan ekle
        if not contents:
             contents.append({"role": "user", "parts": [{"text": "Hello"}]})

        # Güvenlik Ayarları (Her şeyi serbest bırak)
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        generation_config = {
            "temperature": request.temperature,
            "maxOutputTokens": request.max_tokens,
        }

        if request.json_mode:
            generation_config["responseMimeType"] = "application/json"

        payload = {
            "contents": contents,
            "generationConfig": generation_config,
            "safetySettings": safety_settings
        }

        if system_instruction:
            payload["systemInstruction"] = system_instruction

        return payload

    def convert_response(self, provider_response: Dict[str, Any], model_name: str) -> ChatResponse:
        # --- GELİŞMİŞ HATA YÖNETİMİ ---
        # 1. 'candidates' kontrolü
        if not provider_response.get('candidates'):
            # Güvenlik filtresi (promptFeedback) kontrolü
            feedback = provider_response.get('promptFeedback')
            if feedback:
                block_reason = feedback.get('blockReason', 'UNKNOWN')
                # Hata fırlatmak yerine, güvenli bir "Ret" mesajı dönüyoruz
                return ChatResponse(
                    model_used=model_name,
                    content=f"⚠️ Model yanıt vermeyi reddetti (Güvenlik). Sebep: {block_reason}",
                    finish_reason="safety"
                )

            error = provider_response.get('error')
            if error:
                raise ValueError(f"Gemini API Hatası: {error.get('message')}")

            raise ValueError(f"Beklenmeyen Gemini Yanıtı: {json.dumps(provider_response)}")

        try:
            candidate = provider_response['candidates'][0]
            # 2. İçerik (content) kontrolü
            if 'content' in candidate and 'parts' in candidate['content']:
                content = candidate['content']['parts'][0]['text']
            else:
                finish_reason = candidate.get('finishReason', 'UNKNOWN')
                content = f"⚠️ İçerik boş döndü. (Bitiş Sebebi: {finish_reason})"

            return ChatResponse(
                model_used=model_name,
                content=content,
                finish_reason=candidate.get('finishReason')
            )
        except (KeyError, IndexError) as e:
            # Yeni hata mesajımız bu olmalı:
            raise ValueError(f"Yanıt Ayrıştırma Hatası: {str(e)}")

    async def stream_chat(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        url = self.get_url(request)
        headers = self.get_headers()
        payload = self.convert_request(request)

        async with self.client.stream("POST", url, json=payload, headers=headers) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    json_str = line[5:].strip()
                    if not json_str: continue
                    try:
                        chunk = json.loads(json_str)
                        if 'candidates' in chunk and chunk['candidates']:
                            content = chunk['candidates'][0].get('content')
                            if content and 'parts' in content:
                                text = content['parts'][0].get('text')
                                if text: yield text
                    except: continue
