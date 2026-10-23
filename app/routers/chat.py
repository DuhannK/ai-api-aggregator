from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from app.models.chat import ChatRequest, ChatResponse
from app.core.security import get_api_key
from app.services import router_service

router = APIRouter()

@router.post(
    "/v1/chat/completions",
    dependencies=[Depends(get_api_key)],
    summary="Metin Üretimi (Chat)",
    description="Metin veya sohbet geçmişi göndererek AI yanıtı alın. 'stream=True' ile anlık akış destekler.",
    response_model=None # Union dönüş tipi hatasını önlemek için
)
async def generate_chat(request: ChatRequest):
    # İsteği servise ilet
    if request.stream:
        return StreamingResponse(
            router_service.handle_chat_stream(request),
            media_type="text/event-stream"
        )
    else:
        response = await router_service.handle_chat_request(request)
        return JSONResponse(content=response.model_dump())

# --- YER TUTUCULAR (Gelecek Özellikler) ---
# @router.post("/v1/audio/speech") -> TTS eklenecek
# @router.post("/v1/images/generations") -> Resim üretimi eklenecek
# @router.post("/v1/audio/transcriptions") -> Ses-Metin (Whisper) eklenecek
