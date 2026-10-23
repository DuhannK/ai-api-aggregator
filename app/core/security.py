from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

# Header'da 'Authorization: Bearer <key>' beklenir
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

async def get_api_key(key: str = Security(api_key_header)):
    """
    Kullanıcının gönderdiği API anahtarını doğrular.
    """
    if not key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kimlik doğrulama hatası: 'Authorization' başlığı eksik."
        )

    # 'Bearer ' öneki kontrolü
    parts = key.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Format hatası: Anahtar 'Bearer <API_KEY>' formatında olmalıdır."
        )

    # Anahtar kontrolü (Gerçek senaryoda veritabanından bakılır)
    if parts[1] == settings.INTERNAL_API_KEY:
        return True
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yetkisiz erişim: Geçersiz API Anahtarı."
        )
