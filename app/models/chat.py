from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

# Standart bir mesaj yapısı
class Message(BaseModel):
    role: str = Field(..., description="Mesajı gönderen: 'user', 'system' veya 'assistant'")
    content: str = Field(..., description="Mesajın metin içeriği")

# Gelen İstek Modeli (Esnek Yapı)
class ChatRequest(BaseModel):
    # Basit mod için tekil prompt (Opsiyonel)
    prompt: Optional[str] = Field(None, description="Hızlı kullanım için tekil metin girişi.")

    # Gelişmiş mod için mesaj geçmişi (Opsiyonel)
    messages: Optional[List[Message]] = Field(None, description="Sohbet geçmişi listesi.")

    # Model seçimi (Opsiyonel - Default: 'oto')
    model: Optional[str] = Field("oto", description="Kullanılacak AI modeli.")

    # Ayarlar (Opsiyonel - Default değerler serviste atanır)
    stream: Optional[bool] = Field(False, description="Yanıtın akış (stream) olarak gelip gelmeyeceği.")
    temperature: Optional[float] = Field(1.0, description="Yaratıcılık seviyesi (0.0 - 2.0).")
    max_tokens: Optional[int] = Field(None, description="Maksimum üretim uzunluğu.")

    # İleri seviye ayarlar (JSON Mode, TopP vb.)
    json_mode: Optional[bool] = Field(False, description="Çıktının JSON formatında olmasını zorlar.")

# Dönüş Modeli (Standartlaştırılmış)
class ChatResponse(BaseModel):
    model_used: str
    content: str
    role: str = "assistant"
    finish_reason: Optional[str] = None
    # usage: Optional[Dict[str, int]] = None # Token kullanımı (İleride eklenecek)
