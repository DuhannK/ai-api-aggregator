from app.models.chat import ChatRequest, ChatResponse, Message
from app.providers import get_provider
from fastapi import HTTPException
import httpx
import json
import time
from typing import AsyncGenerator

# Varsayılan "oto" modeli
DEFAULT_MODEL = "gemini-2.5-flash"

def normalize_request(request: ChatRequest) -> ChatRequest:
    """
    Kullanıcıdan gelen eksik veya 'kolay mod' isteklerini
    standart, tam bir isteğe dönüştürür.
    """
    # 1. Model 'oto' veya boş ise varsayılanı seç
    if not request.model or request.model == "oto":
        request.model = DEFAULT_MODEL

    # 2. 'messages' boş ama 'prompt' doluysa (Kolay Mod), mesaja çevir
    if not request.messages and request.prompt:
        request.messages = [
            Message(role="user", content=request.prompt)
        ]

    # 3. İkisi de yoksa hata ver
    if not request.messages:
        raise HTTPException(
            status_code=400,
            detail="Eksik Parametre: 'messages' listesi veya 'prompt' metni girilmelidir."
        )

    return request

async def handle_chat_request(request: ChatRequest) -> ChatResponse:
    """Tekil yanıt (Non-stream) işlemi."""
    request = normalize_request(request)
    provider = get_provider(request.model)

    if not provider:
        raise HTTPException(status_code=400, detail=f"Desteklenmeyen Model: '{request.model}' için bir sağlayıcı bulunamadı.")

    try:
        # Sağlayıcıya özel formata çevir ve isteği at
        provider_url = provider.get_url(request)
        provider_headers = provider.get_headers()
        provider_payload = provider.convert_request(request)

        response = await provider.client.post(provider_url, json=provider_payload, headers=provider_headers)
        response.raise_for_status()

        # Cevabı standart formata çevir
        return provider.convert_response(response.json(), request.model)

    except httpx.HTTPStatusError as e:
        # Dış API hatalarını temiz bir şekilde göster
        error_detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=f"Sağlayıcı Hatası ({request.model}): {error_detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sunucu İçi Hata: {str(e)}")

async def handle_chat_stream(request: ChatRequest) -> AsyncGenerator[str, None]:
    """Akışlı yanıt (Stream) işlemi - OpenAI uyumlu format."""
    request = normalize_request(request)
    provider = get_provider(request.model)

    stream_id = f"chatcmpl-{int(time.time())}"

    if not provider:
        yield f"data: {json.dumps({'error': f'Model {request.model} bulunamadı'})}\n\n"
        return

    try:
        async for chunk_text in provider.stream_chat(request):
            # OpenAI standart stream formatı
            response_chunk = {
                "id": stream_id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "delta": {"content": chunk_text},
                    "finish_reason": None
                }]
            }
            yield f"data: {json.dumps(response_chunk)}\n\n"

    except Exception as e:
        error_json = {"error": f"Akış Hatası: {str(e)}"}
        yield f"data: {json.dumps(error_json)}\n\n"

    yield "data: [DONE]\n\n"
