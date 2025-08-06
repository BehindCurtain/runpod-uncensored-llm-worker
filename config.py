"""Configuration management for the LLM worker."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelConfig:
    """Model-specific configuration."""
    repository_id: str = "DavidAU/Llama-3.2-8X3B-MOE-Dark-Champion-Instruct-uncensored-abliterated-18.4B-GGUF"
    filename: str = "L3.2-8X3B-MOE-Dark-Champion-Inst-18.4B-uncen-ablit_D_AU-Q8_0.gguf"
    cache_dir: str = "/runpod-volume"  # Network volume mount point
    n_gpu_layers: int = -1  # Use all GPU layers
    n_ctx: int = 4096  # Context window size
    n_batch: int = 512  # Batch size for processing


@dataclass
class InferenceConfig:
    """Default inference parameters."""
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    stop_sequences: list = None
    
    def __post_init__(self):
        if self.stop_sequences is None:
            self.stop_sequences = ["</s>", "<|im_end|>"]


@dataclass
class Config:
    """Main configuration class."""
    model: ModelConfig
    inference: InferenceConfig
    
    # Environment variables
    hf_token: Optional[str] = None
    log_level: str = "INFO"
    
    @classmethod
    def load_from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        model_config = ModelConfig(
            repository_id=os.getenv("MODEL_REPOSITORY_ID", ModelConfig.repository_id),
            filename=os.getenv("MODEL_FILENAME", ModelConfig.filename),
            cache_dir=os.getenv("MODEL_CACHE_DIR", ModelConfig.cache_dir),
            n_gpu_layers=int(os.getenv("N_GPU_LAYERS", ModelConfig.n_gpu_layers)),
            n_ctx=int(os.getenv("N_CTX", ModelConfig.n_ctx)),
            n_batch=int(os.getenv("N_BATCH", ModelConfig.n_batch))
        )
        
        inference_config = InferenceConfig(
            max_tokens=int(os.getenv("MAX_TOKENS", InferenceConfig.max_tokens)),
            temperature=float(os.getenv("TEMPERATURE", InferenceConfig.temperature)),
            top_p=float(os.getenv("TOP_P", InferenceConfig.top_p)),
            top_k=int(os.getenv("TOP_K", InferenceConfig.top_k)),
            repeat_penalty=float(os.getenv("REPEAT_PENALTY", InferenceConfig.repeat_penalty))
        )
        
        return cls(
            model=model_config,
            inference=inference_config,
            hf_token=os.getenv("HF_TOKEN"),
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )
    
    def validate_config(self) -> bool:
        """Validate configuration parameters."""
        if not self.model.repository_id or not self.model.filename:
            return False
        
        if self.model.n_ctx <= 0 or self.model.n_batch <= 0:
            return False
            
        if self.inference.max_tokens <= 0:
            return False
            
        if not (0.0 <= self.inference.temperature <= 2.0):
            return False
            
        if not (0.0 <= self.inference.top_p <= 1.0):
            return False
            
        return True
    
    def get_model_path(self) -> str:
        """Get the full path to the model file."""
        return os.path.join(self.model.cache_dir, "models", self.model.filename)


# Global configuration instance
config = Config.load_from_env()
