from fastapi import APIRouter, Depends
from app.models.vision import VisionRequest, VisionResponse
from app.core.security import get_api_key
from app.services import vision_service

router = APIRouter()

@router.post(
    "/v1/vision/analyze",
    dependencies=[Depends(get_api_key)],
    response_model=VisionResponse,
    summary="Görsel Analizi (Vision)",
    description="Bir resim URL'si gönderin, AI size resimde ne olduğunu anlatsın."
)
async def analyze_image(request: VisionRequest):
    return await vision_service.process_vision_request(request)
