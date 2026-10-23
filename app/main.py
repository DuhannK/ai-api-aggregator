from fastapi import FastAPI
from app.routers import chat
from app.routers import vision # Yeni router

app = FastAPI(
    title="AI Gateway API (Text + Vision)",
    description="Metin ve Görsel işleme yeteneklerine sahip bütünleşik AI API.",
    version="1.1.0"
)

# Router'ları bağla
app.include_router(chat.router, prefix="/api", tags=["Text Generation"])
app.include_router(vision.router, prefix="/api", tags=["Vision Analysis"])

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "active", "capabilities": ["text", "vision"]}
