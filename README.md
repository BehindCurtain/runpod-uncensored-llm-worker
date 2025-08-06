# RunPod Uncensored LLM Worker

![RunPod Worker Template](https://cpjrphpz3t5wbwfe.public.blob.vercel-storage.com/worker-template_banner-zUuCAjwDuvfsINR6vKBhYvvm3TnZFB.jpeg)

---

Bu proje, RunPod Serverless platformunda çalışan özelleştirilmiş bir LLM (Large Language Model) worker'ıdır. Uncensored (sansürsüz) LLM modellerini serverless ortamda çalıştırarak API üzerinden erişilebilir hale getirir.

---

[![RunPod](https://api.runpod.io/badge/runpod-workers/worker-template)](https://www.runpod.io/console/hub/runpod-workers/worker-template)

---

## Özellikler

- **Otomatik Model İndirme**: Hugging Face Hub'dan model dosyalarını otomatik indirir
- **Network Volume Cache**: Model dosyalarını network volume'da cache'ler
- **GPU Acceleration**: CUDA destekli hızlı inference
- **Chat & Text Completion**: Hem chat hem de text completion modları
- **Configurable Parameters**: Esnek inference parametreleri
- **Error Handling**: Kapsamlı hata yönetimi ve logging

## Desteklenen Model

Bu worker şu anda aşağıdaki modeli desteklemektedir:
- **Model**: Llama-3.2-8X3B-MOE-Dark-Champion-Instruct-uncensored-abliterated-18.4B
- **Format**: GGUF (Q8_0 quantization)
- **Boyut**: ~18.4B parametreler

## Kurulum ve Deployment

### 1. Environment Variables

Aşağıdaki environment variable'ları ayarlayabilirsiniz:

```bash
# Model Configuration
MODEL_REPOSITORY_ID="DavidAU/Llama-3.2-8X3B-MOE-Dark-Champion-Instruct-uncensored-abliterated-18.4B-GGUF"
MODEL_FILENAME="L3.2-8X3B-MOE-Dark-Champion-Inst-18.4B-uncen-ablit_D_AU-Q8_0.gguf"
MODEL_CACHE_DIR="/runpod-volume"

# Model Parameters
N_GPU_LAYERS=-1
N_CTX=4096
N_BATCH=512

# Inference Defaults
MAX_TOKENS=512
TEMPERATURE=0.7
TOP_P=0.9
TOP_K=40
REPEAT_PENALTY=1.1

# Optional
HF_TOKEN="your_huggingface_token"
LOG_LEVEL="INFO"
```

### 2. Network Volume

RunPod'da bir network volume oluşturun ve `/runpod-volume` path'ine mount edin. Model dosyaları bu volume'da cache'lenecektir.

### 3. GitHub Integration ile Deploy

1. Bu repository'yi fork edin veya clone edin
2. RunPod Console'da yeni bir Serverless Endpoint oluşturun
3. GitHub integration'ı kullanarak repository'nizi bağlayın
4. Network volume'ı endpoint'e attach edin

### 4. Manuel Docker Build

```bash
docker build -t your-registry/llm-worker .
docker push your-registry/llm-worker
```

## API Kullanımı

### Text Completion

```json
{
  "input": {
    "prompt": "What is the meaning of life?",
    "max_tokens": 256,
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40
  }
}
```

### Chat Completion

```json
{
  "input": {
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful AI assistant."
      },
      {
        "role": "user",
        "content": "Explain quantum computing in simple terms."
      }
    ],
    "max_tokens": 512,
    "temperature": 0.7,
    "top_p": 0.9
  }
}
```

### Response Format

```json
{
  "generated_text": "Generated response text...",
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 128,
    "total_tokens": 143
  },
  "finish_reason": "stop",
  "generation_time": 2.345,
  "status": "success"
}
```

## Parametreler

| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|------------|----------|
| `prompt` | string | - | Text completion için prompt |
| `messages` | array | - | Chat completion için mesaj listesi |
| `max_tokens` | integer | 512 | Maksimum token sayısı |
| `temperature` | float | 0.7 | Yaratıcılık seviyesi (0.0-2.0) |
| `top_p` | float | 0.9 | Nucleus sampling (0.0-1.0) |
| `top_k` | integer | 40 | Top-k sampling |
| `repeat_penalty` | float | 1.1 | Tekrar cezası |
| `stop` | array | ["</s>", "<\|im_end\|>"] | Durma token'ları |

## Local Testing

```bash
# Test input ile
python handler.py

# Chat completion test ile
cp test_chat_input.json test_input.json
python handler.py
```

## Proje Yapısı

```
├── docs/                    # Dokümantasyon
├── config.py               # Konfigürasyon yönetimi
├── cache_manager.py        # Cache yönetimi
├── model_manager.py        # Model indirme ve yükleme
├── inference_engine.py     # LLM inference
├── handler.py              # Ana RunPod handler
├── requirements.txt        # Python bağımlılıkları
├── Dockerfile             # Container tanımı
├── test_input.json        # Test verisi
└── test_chat_input.json   # Chat test verisi
```

## Known Issues

- İlk çalıştırmada model indirme süresi uzun olabilir (~18GB dosya)
- GPU memory yetersizse model yükleme başarısız olabilir
- Network volume mount edilmemişse cache çalışmaz

## Troubleshooting

### Model İndirme Sorunları
- Network volume'ın doğru mount edildiğini kontrol edin
- HF_TOKEN environment variable'ını ayarlayın (private model'ler için)
- Disk alanının yeterli olduğunu kontrol edin

### Memory Sorunları
- N_GPU_LAYERS değerini azaltın
- Daha küçük context window (N_CTX) kullanın
- Batch size'ı (N_BATCH) azaltın

### Performance Optimizasyonu
- Model cache'lendiğinde cold start süreleri azalır
- GPU instance'ları CPU instance'larından çok daha hızlıdır
- Network volume SSD kullanın

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.
