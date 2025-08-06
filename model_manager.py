"""Model management for downloading and loading LLM models."""

import os
import logging
from pathlib import Path
from typing import Optional
import time

from huggingface_hub import hf_hub_download, repo_info
from huggingface_hub.utils import RepositoryNotFoundError, RevisionNotFoundError

from config import config
from cache_manager import CacheManager

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages model downloading, caching, and loading."""
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.model_config = config.model
        self.hf_token = config.hf_token
        
    def get_model_info(self) -> Optional[dict]:
        """Get model information from Hugging Face Hub."""
        try:
            info = repo_info(
                repo_id=self.model_config.repository_id,
                token=self.hf_token,
                repo_type="model"
            )
            
            # Find the specific file we need
            target_file = None
            for sibling in info.siblings:
                if sibling.rfilename == self.model_config.filename:
                    target_file = sibling
                    break
            
            if not target_file:
                logger.error(f"File {self.model_config.filename} not found in repository")
                return None
            
            return {
                "repository_id": self.model_config.repository_id,
                "filename": self.model_config.filename,
                "file_size": target_file.size,
                "last_modified": target_file.last_modified,
                "download_url": f"https://huggingface.co/{self.model_config.repository_id}/resolve/main/{self.model_config.filename}"
            }
            
        except (RepositoryNotFoundError, RevisionNotFoundError) as e:
            logger.error(f"Repository or file not found: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return None
    
    def download_model(self) -> Optional[str]:
        """Download model file to cache if not already present."""
        filename = self.model_config.filename
        
        # Check if already cached and valid
        if self.cache_manager.is_cached(filename):
            logger.info(f"Model {filename} already cached")
            if self.cache_manager.validate_cached_file(filename):
                logger.info(f"Cached model {filename} is valid")
                return str(self.cache_manager.get_cache_path(filename))
            else:
                logger.warning(f"Cached model {filename} is invalid, removing...")
                self.cache_manager.remove_cached_file(filename)
        
        # Get model info for validation
        model_info = self.get_model_info()
        if not model_info:
            logger.error("Could not get model information")
            return None
        
        logger.info(f"Downloading model {filename} ({model_info['file_size']} bytes)...")
        
        try:
            start_time = time.time()
            
            # Download to cache directory
            downloaded_path = hf_hub_download(
                repo_id=self.model_config.repository_id,
                filename=filename,
                cache_dir=str(self.cache_manager.cache_dir.parent),
                local_dir=str(self.cache_manager.cache_dir),
                local_dir_use_symlinks=False,
                token=self.hf_token
            )
            
            download_time = time.time() - start_time
            logger.info(f"Model downloaded successfully in {download_time:.2f} seconds")
            
            # Validate downloaded file
            if self.cache_manager.validate_cached_file(filename, model_info['file_size']):
                logger.info(f"Downloaded model {filename} validated successfully")
                return downloaded_path
            else:
                logger.error(f"Downloaded model {filename} validation failed")
                self.cache_manager.remove_cached_file(filename)
                return None
                
        except Exception as e:
            logger.error(f"Error downloading model: {e}")
            return None
    
    def ensure_model_available(self) -> bool:
        """Ensure model is available in cache, download if necessary."""
        filename = self.model_config.filename
        
        # Check if model is already cached and valid
        if self.cache_manager.is_cached(filename):
            if self.cache_manager.validate_cached_file(filename):
                logger.info(f"Model {filename} is available and valid")
                return True
            else:
                logger.warning(f"Cached model {filename} is invalid")
        
        # Download model
        downloaded_path = self.download_model()
        return downloaded_path is not None
    
    def get_model_path(self) -> Optional[str]:
        """Get the path to the model file."""
        if not self.ensure_model_available():
            return None
        
        return str(self.cache_manager.get_cache_path(self.model_config.filename))
    
    def load_model(self):
        """Load the model using llama-cpp-python."""
        model_path = self.get_model_path()
        if not model_path:
            raise RuntimeError("Model not available")
        
        try:
            # Import here to avoid issues if llama-cpp-python is not installed
            from llama_cpp import Llama
            
            logger.info(f"Loading model from {model_path}")
            start_time = time.time()
            
            model = Llama(
                model_path=model_path,
                n_gpu_layers=self.model_config.n_gpu_layers,
                n_ctx=self.model_config.n_ctx,
                n_batch=self.model_config.n_batch,
                verbose=False
            )
            
            load_time = time.time() - start_time
            logger.info(f"Model loaded successfully in {load_time:.2f} seconds")
            
            return model
            
        except ImportError:
            logger.error("llama-cpp-python not installed")
            raise
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def get_cache_status(self) -> dict:
        """Get cache status information."""
        filename = self.model_config.filename
        
        status = {
            "model_filename": filename,
            "is_cached": self.cache_manager.is_cached(filename),
            "cache_path": str(self.cache_manager.get_cache_path(filename)),
            "cache_info": self.cache_manager.get_cache_info()
        }
        
        if status["is_cached"]:
            status["file_size"] = self.cache_manager.get_file_size(filename)
            status["is_valid"] = self.cache_manager.validate_cached_file(filename)
        
        return status
