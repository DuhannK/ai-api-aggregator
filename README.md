# AI API Aggregator

OpenAI ve Google Gemini API'lerini tek bir REST API arkasında birleştiren, FastAPI tabanlı bir AI gateway.
İstemci hangi sağlayıcıyı kullanırsa kullansın aynı istek ve cevap formatıyla çalışır. Model adı değiştirilerek sağlayıcı değiştirilebilir.

## Özellikler

- **Tek endpoint, çok sağlayıcı:** model adına göre otomatik yönlendirme (`gpt-*` → OpenAI, `gemini-*` → Gemini)
- **OpenAI uyumlu sohbet endpoint'i:** `POST /api/v1/chat/completions`
- **Streaming (SSE):** her iki sağlayıcının akışı da OpenAI `chat.completion.chunk` formatında döner
- **Kolay mod:** `messages` listesi yerine yalnızca `prompt` gönderilebilir
- **`"oto"` model:** model belirtilmezse varsayılan modele düşer (`gemini-2.5-flash`)
- **JSON mode:** `json_mode: true` ile çıktıyı JSON'a zorlar
- **Görsel analiz (Vision):** `POST /api/v1/vision/analyze` ile bir resim URL'si analiz edilir (Gemini için resim otomatik Base64'e çevrilir)
- **Kimlik doğrulama:** `Authorization: Bearer <INTERNAL_API_KEY>`
- **Hata yönetimi:** sağlayıcı hataları ve Gemini güvenlik filtresi tek formatta döner
- **Otomatik dokümantasyon:** Swagger UI `/docs` adresinde

## Mimari

```
app/
├── main.py              # FastAPI uygulaması, router'ları bağlar
├── core/
│   ├── config.py        # .env okuma (pydantic-settings)
│   └── security.py      # Bearer token doğrulama
├── models/              # Pydantic istek/cevap şemaları (chat, vision)
├── providers/
│   ├── base.py          # BaseProvider: her sağlayıcının uyduğu soyut sınıf
│   ├── openai.py        # OpenAI ↔ ortak format dönüşümü
│   ├── gemini.py        # Gemini ↔ ortak format dönüşümü
│   ├── __init__.py      # PROVIDER_MAP: model öneki → sağlayıcı
│   └── *_vision.py      # Vision sağlayıcıları ve kayıt defteri
├── services/            # İş mantığı: istek normalizasyonu, yönlendirme, streaming
└── routers/             # HTTP endpoint'leri
```

Tüm sağlayıcılar tek bir paylaşılan `httpx.AsyncClient` kullanır (connection pooling); sunucu tamamen async ve stateless'tır.

## Kurulum

```bash
pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
# .env içine kendi anahtarlarınızı girin
uvicorn app.main:app --reload
```

Sunucu açıldıktan sonra `http://localhost:8000/docs` adresinden tüm endpoint'leri deneyebilirsiniz.

Colab'da çalıştırmak için [`notebooks/colab_demo.ipynb`](notebooks/colab_demo.ipynb) dosyasını kullanın; anahtarlar Colab'ın 🔑 Secrets bölümünden okunur.

## Örnek istekler

**Sohbet (kolay mod):**

```bash
curl -X POST http://localhost:8000/api/v1/chat/completions \
  -H "Authorization: Bearer <INTERNAL_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"model": "oto", "prompt": "Merhaba!"}'
```

```json
{"model_used": "gemini-2.5-flash", "content": "Merhaba! Size nasıl yardımcı olabilirim?", "role": "assistant", "finish_reason": "STOP"}
```

**Sohbet (mesaj geçmişi + streaming):**

```bash
curl -N -X POST http://localhost:8000/api/v1/chat/completions \
  -H "Authorization: Bearer <INTERNAL_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o-mini", "stream": true, "messages": [{"role": "system", "content": "Kısa cevap ver."}, {"role": "user", "content": "FastAPI nedir?"}]}'
```

**Görsel analiz:**

```bash
curl -X POST http://localhost:8000/api/v1/vision/analyze \
  -H "Authorization: Bearer <INTERNAL_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://upload.wikimedia.org/wikipedia/commons/3/3a/Cat03.jpg", "prompt": "Bu resimde ne var?"}'
```

## Yeni sağlayıcı eklemek

1. `app/providers/` altında `BaseProvider`'dan türeyen bir sınıf yazın (`get_url`, `get_headers`, `convert_request`, `convert_response`, `stream_chat`).
2. `app/providers/__init__.py` içindeki `PROVIDER_MAP`'e model önekiyle ekleyin, örneğin `"claude-": AnthropicProvider(client)`.

Servis ve router katmanında değişiklik gerekmez.

## Yol haritası

- [ ] Anthropic, Ollama vb. sağlayıcıların eklenmesi / çoğaltılması
- [ ] Sağlayıcılar arası fallback (bir sağlayıcı hata verirse diğerine geçme)
- [ ] `"oto"` modunda göreve/maliyete göre model seçimi
- [ ] Rate limiting ve önbellek
- [ ] Token kullanım takibi
- [ ] Ses üretimi (TTS) endpoint'i
- [ ] Dockerfile ve testler

## Teknolojiler

Python · FastAPI · Uvicorn · Pydantic / pydantic-settings · httpx (async, HTTP/2) · Google Colab + ngrok
