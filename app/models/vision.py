from pydantic import BaseModel, Field
from typing import List, Optional, Union

class VisionRequest(BaseModel):
    # Kolay Mod: Sadece URL ve soru
    image_url: Optional[str] = Field(None, description="Analiz edilecek resmin linki.")
    prompt: Optional[str] = Field("Bu resimde ne var?", description="Resim hakkında sorulan soru.")

    # Gelişmiş Mod: Model seçimi ve ayarlar
    model: Optional[str] = Field("oto", description="Kullanılacak Vision modeli.")
    max_tokens: Optional[int] = Field(300, description="Cevap uzunluğu.")
    temperature: Optional[float] = Field(0.5, description="Yaratıcılık seviyesi.")

class VisionResponse(BaseModel):
    model_used: str
    description: str
    usage: Optional[dict] = None
