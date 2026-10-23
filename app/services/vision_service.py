from app.models.vision import VisionRequest, VisionResponse
from app.providers.vision_registry import get_vision_provider
from fastapi import HTTPException

# Vision için varsayılan model (Gemini 2.5 Flash çok hızlı ve ücretsiz)
DEFAULT_VISION_MODEL = "gemini-2.5-flash"

async def process_vision_request(request: VisionRequest) -> VisionResponse:
    # 1. Oto model seçimi
    if request.model == "oto" or not request.model:
        request.model = DEFAULT_VISION_MODEL

    # 2. Resim URL kontrolü
    if not request.image_url:
        raise HTTPException(status_code=400, detail="Lütfen bir 'image_url' sağlayın.")

    # 3. Sağlayıcıyı bul
    provider = get_vision_provider(request.model)
    if not provider:
        raise HTTPException(status_code=400, detail=f"Desteklenmeyen Vision Modeli: {request.model}")

    # 4. İşlemi yap
    try:
        return await provider.analyze_image(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vision İşleme Hatası: {str(e)}")
