from .gemini import GeminiProvider
from .openai import OpenAIProvider
import httpx

# Performans için tek bir HTTP istemcisi (Connection Pooling)
client = httpx.AsyncClient(timeout=60.0)

# Model öneklerine (prefix) göre sağlayıcı eşleştirmesi
PROVIDER_MAP = {
    "gemini-": GeminiProvider(client),
    "gpt-": OpenAIProvider(client),
    # "claude-": AnthropicProvider(client), # Gelecekte
}

def get_provider(model_name: str):
    """Model adına bakarak uygun Provider sınıfını döndürür."""
    for prefix, provider in PROVIDER_MAP.items():
        if model_name.startswith(prefix):
            return provider
    return None
