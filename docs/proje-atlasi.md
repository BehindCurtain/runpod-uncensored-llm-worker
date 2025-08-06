# Runpod Uncensored LLM Worker - Proje Atlası

## Proje Amacı
Bu proje, RunPod Serverless platformunda çalışan özelleştirilmiş bir LLM (Large Language Model) worker'ıdır. Temel amacı, uncensored (sansürsüz) LLM modellerini serverless ortamda çalıştırarak API üzerinden erişilebilir hale getirmektir.

## Proje Mimarisi

### Temel Mimari Prensipler
- **Serverless-First**: RunPod Serverless platformuna optimize edilmiş
- **Model Caching**: Network volume kullanarak model dosyalarını cache'leme
- **CUDA Acceleration**: GPU destekli hızlı inference
- **Stateless Design**: Her request bağımsız olarak işlenir

### Teknoloji Stack'i
- **Base Platform**: RunPod Serverless
- **Container**: Docker (runpod/base:0.6.3-cuda11.8.0)
- **Runtime**: Python 3.11
- **GPU Support**: CUDA 11.8.0
- **Model Format**: GGUF (llama.cpp uyumlu)
- **Model Source**: Hugging Face Hub

## Proje Felsefesi

### Performans Odaklı
- Model yükleme süresini minimize etmek için network volume cache kullanımı
- Cold start sürelerini azaltmak için model pre-loading
- GPU memory optimizasyonu

### Esneklik
- Farklı model boyutları için ölçeklenebilir yapı
- Configurable inference parametreleri
- Multiple model support capability

### Güvenilirlik
- Error handling ve graceful degradation
- Health check endpoints
- Logging ve monitoring

## Tercih Edilen Teknolojiler

### Model Handling
- **llama-cpp-python**: GGUF model formatı için optimize edilmiş
- **huggingface-hub**: Model indirme ve cache yönetimi
- **transformers**: Tokenizer ve model metadata

### Infrastructure
- **RunPod SDK**: Platform entegrasyonu
- **Docker**: Containerization
- **Network Volumes**: Persistent model storage

## Deployment Stratejisi
- GitHub integration ile otomatik deployment
- Multi-stage Docker build için optimization
- Environment-based configuration
- Network volume integration for model caching

## Güncel Durum
Proje başarıyla özelleştirildi ve aşağıdaki bileşenler eklendi:
- **Model**: DavidAU/Llama-3.2-8X3B-MOE-Dark-Champion-Instruct-uncensored-abliterated-18.4B-GGUF
- **Cache Sistemi**: Network volume tabanlı model cache'leme
- **Inference Engine**: llama-cpp-python ile GPU destekli inference
- **API**: Hem text completion hem chat completion desteği
- **Error Handling**: Kapsamlı hata yönetimi ve logging
