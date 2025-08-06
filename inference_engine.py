"""Inference engine for LLM text generation."""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from config import config

logger = logging.getLogger(__name__)


@dataclass
class InferenceParams:
    """Parameters for text generation."""
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    stop_sequences: List[str] = None
    stream: bool = False
    
    def __post_init__(self):
        if self.stop_sequences is None:
            self.stop_sequences = ["</s>", "<|im_end|>"]


class InferenceEngine:
    """Handles LLM inference operations."""
    
    def __init__(self, model):
        """Initialize with a loaded model."""
        self.model = model
        self.default_params = InferenceParams(
            max_tokens=config.inference.max_tokens,
            temperature=config.inference.temperature,
            top_p=config.inference.top_p,
            top_k=config.inference.top_k,
            repeat_penalty=config.inference.repeat_penalty,
            stop_sequences=config.inference.stop_sequences
        )
        
    def generate(self, prompt: str, params: Optional[InferenceParams] = None) -> Dict[str, Any]:
        """Generate text from a prompt."""
        if params is None:
            params = self.default_params
        
        try:
            logger.info(f"Generating text with prompt length: {len(prompt)}")
            
            # Prepare generation parameters
            generation_kwargs = {
                "prompt": prompt,
                "max_tokens": params.max_tokens,
                "temperature": params.temperature,
                "top_p": params.top_p,
                "top_k": params.top_k,
                "repeat_penalty": params.repeat_penalty,
                "stop": params.stop_sequences,
                "stream": params.stream,
                "echo": False  # Don't include prompt in output
            }
            
            # Generate text
            if params.stream:
                return self._generate_stream(generation_kwargs)
            else:
                return self._generate_complete(generation_kwargs)
                
        except Exception as e:
            logger.error(f"Error during text generation: {e}")
            return {
                "success": False,
                "error": str(e),
                "generated_text": "",
                "usage": {}
            }
    
    def _generate_complete(self, generation_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete text response."""
        try:
            response = self.model(**generation_kwargs)
            
            generated_text = response["choices"][0]["text"]
            
            # Extract usage information
            usage = {
                "prompt_tokens": response.get("usage", {}).get("prompt_tokens", 0),
                "completion_tokens": response.get("usage", {}).get("completion_tokens", 0),
                "total_tokens": response.get("usage", {}).get("total_tokens", 0)
            }
            
            return {
                "success": True,
                "generated_text": generated_text,
                "usage": usage,
                "finish_reason": response["choices"][0].get("finish_reason", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Error in complete generation: {e}")
            raise
    
    def _generate_stream(self, generation_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate streaming text response."""
        try:
            generated_text = ""
            tokens_generated = 0
            
            for chunk in self.model(**generation_kwargs):
                if chunk["choices"][0]["text"]:
                    generated_text += chunk["choices"][0]["text"]
                    tokens_generated += 1
            
            return {
                "success": True,
                "generated_text": generated_text,
                "usage": {
                    "completion_tokens": tokens_generated,
                    "total_tokens": tokens_generated  # Approximate
                },
                "finish_reason": "stop"
            }
            
        except Exception as e:
            logger.error(f"Error in streaming generation: {e}")
            raise
    
    def chat_completion(self, messages: List[Dict[str, str]], params: Optional[InferenceParams] = None) -> Dict[str, Any]:
        """Generate chat completion response."""
        try:
            # Convert messages to prompt format
            prompt = self._format_chat_messages(messages)
            return self.generate(prompt, params)
            
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            return {
                "success": False,
                "error": str(e),
                "generated_text": "",
                "usage": {}
            }
    
    def _format_chat_messages(self, messages: List[Dict[str, str]]) -> str:
        """Format chat messages into a prompt."""
        # Basic chat template for Llama models
        formatted_prompt = ""
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                formatted_prompt += f"<|im_start|>system\n{content}<|im_end|>\n"
            elif role == "user":
                formatted_prompt += f"<|im_start|>user\n{content}<|im_end|>\n"
            elif role == "assistant":
                formatted_prompt += f"<|im_start|>assistant\n{content}<|im_end|>\n"
        
        # Add assistant start token for response
        formatted_prompt += "<|im_start|>assistant\n"
        
        return formatted_prompt
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        try:
            # Get basic model information
            info = {
                "model_loaded": self.model is not None,
                "context_length": config.model.n_ctx,
                "gpu_layers": config.model.n_gpu_layers,
                "batch_size": config.model.n_batch
            }
            
            # Try to get additional model metadata if available
            if hasattr(self.model, 'metadata'):
                info.update(self.model.metadata)
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {"error": str(e)}
    
    def validate_params(self, params: Dict[str, Any]) -> InferenceParams:
        """Validate and convert parameters to InferenceParams."""
        try:
            # Extract and validate parameters
            max_tokens = min(max(int(params.get("max_tokens", self.default_params.max_tokens)), 1), 4096)
            temperature = max(min(float(params.get("temperature", self.default_params.temperature)), 2.0), 0.0)
            top_p = max(min(float(params.get("top_p", self.default_params.top_p)), 1.0), 0.0)
            top_k = max(int(params.get("top_k", self.default_params.top_k)), 1)
            repeat_penalty = max(float(params.get("repeat_penalty", self.default_params.repeat_penalty)), 0.1)
            
            stop_sequences = params.get("stop", self.default_params.stop_sequences)
            if isinstance(stop_sequences, str):
                stop_sequences = [stop_sequences]
            elif not isinstance(stop_sequences, list):
                stop_sequences = self.default_params.stop_sequences
            
            stream = bool(params.get("stream", False))
            
            return InferenceParams(
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repeat_penalty=repeat_penalty,
                stop_sequences=stop_sequences,
                stream=stream
            )
            
        except Exception as e:
            logger.warning(f"Error validating parameters, using defaults: {e}")
            return self.default_params
