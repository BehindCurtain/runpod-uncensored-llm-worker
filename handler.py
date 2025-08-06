"""LLM Worker Handler for RunPod Serverless."""

import logging
import time
from typing import Dict, Any, Optional

import runpod

from config import config
from model_manager import ModelManager
from inference_engine import InferenceEngine

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for model and inference engine
model_manager = None
inference_engine = None
model_loaded = False


def initialize_model():
    """Initialize the model and inference engine."""
    global model_manager, inference_engine, model_loaded
    
    try:
        logger.info("Initializing model...")
        start_time = time.time()
        
        # Initialize model manager
        model_manager = ModelManager()
        
        # Ensure model is available (download if necessary)
        if not model_manager.ensure_model_available():
            raise RuntimeError("Failed to ensure model availability")
        
        # Load the model
        model = model_manager.load_model()
        
        # Initialize inference engine
        inference_engine = InferenceEngine(model)
        
        model_loaded = True
        init_time = time.time() - start_time
        logger.info(f"Model initialized successfully in {init_time:.2f} seconds")
        
        # Log cache status
        cache_status = model_manager.get_cache_status()
        logger.info(f"Cache status: {cache_status}")
        
    except Exception as e:
        logger.error(f"Failed to initialize model: {e}")
        model_loaded = False
        raise


def handler(job):
    """Handler function that will be used to process jobs."""
    global inference_engine, model_loaded
    
    try:
        # Ensure model is loaded
        if not model_loaded or inference_engine is None:
            return {
                "error": "Model not loaded",
                "status": "error"
            }
        
        job_input = job["input"]
        logger.info(f"Processing job with input keys: {list(job_input.keys())}")
        
        # Extract input parameters
        prompt = job_input.get("prompt")
        messages = job_input.get("messages")
        
        if not prompt and not messages:
            return {
                "error": "Either 'prompt' or 'messages' must be provided",
                "status": "error"
            }
        
        # Validate and extract inference parameters
        inference_params = inference_engine.validate_params(job_input)
        
        # Generate response
        start_time = time.time()
        
        if messages:
            # Chat completion mode
            result = inference_engine.chat_completion(messages, inference_params)
        else:
            # Text completion mode
            result = inference_engine.generate(prompt, inference_params)
        
        generation_time = time.time() - start_time
        
        if result["success"]:
            response = {
                "generated_text": result["generated_text"],
                "usage": result["usage"],
                "finish_reason": result.get("finish_reason", "stop"),
                "generation_time": round(generation_time, 3),
                "status": "success"
            }
            
            logger.info(f"Generated {result['usage'].get('completion_tokens', 0)} tokens in {generation_time:.3f}s")
            return response
        else:
            return {
                "error": result["error"],
                "status": "error"
            }
            
    except Exception as e:
        logger.error(f"Error in handler: {e}")
        return {
            "error": str(e),
            "status": "error"
        }


def health_check():
    """Health check endpoint."""
    global model_loaded, model_manager, inference_engine
    
    try:
        status = {
            "status": "healthy" if model_loaded else "unhealthy",
            "model_loaded": model_loaded,
            "timestamp": time.time()
        }
        
        if model_manager:
            status["cache_status"] = model_manager.get_cache_status()
        
        if inference_engine:
            status["model_info"] = inference_engine.get_model_info()
        
        return status
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }


# Initialize model on startup
try:
    initialize_model()
except Exception as e:
    logger.error(f"Failed to initialize on startup: {e}")
    # Continue anyway, handler will return error


# Start the serverless worker
runpod.serverless.start({
    "handler": handler,
    "return_aggregate_stream": True
})
