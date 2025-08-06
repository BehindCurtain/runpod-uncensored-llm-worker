# Modül Haritaları

## Model Management Sistemi Modülleri

### model_manager.py
**Sorumluluk**: Ana model yönetim koordinatörü
**Bağımlılıklar**: 
- huggingface_hub (model indirme)
- llama_cpp (model yükleme)
- os, pathlib (dosya sistemi)

**Sınıflar**:
- `ModelManager`: Ana model yönetim sınıfı
- `ModelConfig`: Model konfigürasyon dataclass'ı

**Temel Metodlar**:
- `ensure_model_available()`: Model varlığını kontrol et ve gerekirse indir
- `load_model()`: Modeli memory'ye yükle
- `get_model_info()`: Model metadata'sını döndür

### cache_manager.py
**Sorumluluk**: Network volume cache yönetimi
**Bağımlılıklar**: 
- pathlib, os (dosya sistemi)
- hashlib (dosya doğrulama)

**Sınıflar**:
- `CacheManager`: Cache işlemlerini yöneten sınıf

**Temel Metodlar**:
- `get_cache_path()`: Model için cache path'i döndür
- `is_cached()`: Model cache'de var mı kontrol et
- `validate_cached_file()`: Cache'deki dosyanın bütünlüğünü kontrol et

## Inference Engine Sistemi Modülleri

### inference_engine.py
**Sorumluluk**: LLM inference işlemleri
**Bağımlılıklar**: 
- llama_cpp (GGUF model inference)
- typing (type hints)

**Sınıflar**:
- `InferenceEngine`: Ana inference sınıfı
- `InferenceParams`: Inference parametreleri dataclass'ı

**Temel Metodlar**:
- `generate()`: Text generation
- `set_parameters()`: Inference parametrelerini ayarla
- `get_model_info()`: Yüklü model bilgilerini döndür

### text_processor.py
**Sorumluluk**: Text preprocessing ve postprocessing
**Bağımlılıklar**: 
- re (regex)
- typing

**Sınıflar**:
- `TextProcessor`: Text işleme sınıfı

**Temel Metodlar**:
- `preprocess_prompt()`: Prompt'u model için hazırla
- `postprocess_response()`: Model çıktısını temizle
- `apply_chat_template()`: Chat formatını uygula

## API Gateway Sistemi Modülleri

### handler.py (mevcut dosya - güncellenecek)
**Sorumluluk**: RunPod job handling
**Bağımlılıklar**: 
- runpod
- model_manager, inference_engine

**Fonksiyonlar**:
- `handler()`: Ana job handler fonksiyonu
- `initialize_model()`: Model initialization
- `process_request()`: Request işleme

### request_validator.py
**Sorumluluk**: Input validation
**Bağımlılıklar**: 
- pydantic (validation)
- typing

**Sınıflar**:
- `RequestValidator`: Input doğrulama sınıfı
- `InferenceRequest`: Request schema

**Temel Metodlar**:
- `validate_request()`: Request'i doğrula
- `sanitize_input()`: Input'u temizle

## Configuration Management Sistemi Modülleri

### config.py
**Sorumluluk**: Sistem konfigürasyonu
**Bağımlılıklar**: 
- os (environment variables)
- dataclasses
- typing

**Sınıflar**:
- `Config`: Ana konfigürasyon sınıfı
- `ModelConfig`: Model-specific konfigürasyon
- `InferenceConfig`: Inference varsayılan parametreleri

**Temel Metodlar**:
- `load_from_env()`: Environment'dan konfigürasyon yükle
- `validate_config()`: Konfigürasyon doğrulama
- `get_model_path()`: Model dosya path'i döndür

## Modüller Arası İlişkiler

```
handler.py
    ├── model_manager.py
    │   ├── cache_manager.py
    │   └── config.py
    ├── inference_engine.py
    │   ├── text_processor.py
    │   └── config.py
    ├── request_validator.py
    └── config.py
```

## Import Hierarchy
1. **config.py** (en alt seviye, bağımlılığı yok)
2. **cache_manager.py** (config'e bağımlı)
3. **text_processor.py** (config'e bağımlı)
4. **model_manager.py** (config ve cache_manager'a bağımlı)
5. **inference_engine.py** (config ve text_processor'a bağımlı)
6. **request_validator.py** (config'e bağımlı)
7. **handler.py** (tüm modülleri kullanır)
