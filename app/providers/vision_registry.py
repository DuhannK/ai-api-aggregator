from .gemini_vision import GeminiVisionProvider
from .openai_vision import OpenAIVisionProvider
import httpx

client = httpx.AsyncClient(timeout=60.0)

VISION_PROVIDER_MAP = {
    "gemini-": GeminiVisionProvider(client),
    "gpt-": OpenAIVisionProvider(client),
}

def get_vision_provider(model_name: str):
    for prefix, provider in VISION_PROVIDER_MAP.items():
        if model_name.startswith(prefix):
            return provider
    return None
