"""Cache management for model files."""

import os
import hashlib
from pathlib import Path
from typing import Optional
import logging

from config import config

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages model file caching on network volume."""
    
    def __init__(self):
        self.cache_dir = Path(config.model.cache_dir) / "models"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def get_cache_path(self, filename: str) -> Path:
        """Get the cache path for a model file."""
        return self.cache_dir / filename
    
    def is_cached(self, filename: str) -> bool:
        """Check if a model file is cached."""
        cache_path = self.get_cache_path(filename)
        return cache_path.exists() and cache_path.is_file()
    
    def get_file_size(self, filename: str) -> Optional[int]:
        """Get the size of a cached file."""
        if not self.is_cached(filename):
            return None
        
        cache_path = self.get_cache_path(filename)
        return cache_path.stat().st_size
    
    def validate_cached_file(self, filename: str, expected_size: Optional[int] = None) -> bool:
        """Validate the integrity of a cached file."""
        if not self.is_cached(filename):
            return False
        
        cache_path = self.get_cache_path(filename)
        
        try:
            # Check file size if provided
            if expected_size is not None:
                actual_size = cache_path.stat().st_size
                if actual_size != expected_size:
                    logger.warning(f"File size mismatch for {filename}: expected {expected_size}, got {actual_size}")
                    return False
            
            # Basic file integrity check - ensure file is readable
            with open(cache_path, 'rb') as f:
                # Read first few bytes to ensure file is not corrupted
                f.read(1024)
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating cached file {filename}: {e}")
            return False
    
    def calculate_file_hash(self, filename: str, algorithm: str = "sha256") -> Optional[str]:
        """Calculate hash of a cached file."""
        if not self.is_cached(filename):
            return None
        
        cache_path = self.get_cache_path(filename)
        
        try:
            hash_obj = hashlib.new(algorithm)
            with open(cache_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {filename}: {e}")
            return None
    
    def remove_cached_file(self, filename: str) -> bool:
        """Remove a cached file."""
        if not self.is_cached(filename):
            return True
        
        cache_path = self.get_cache_path(filename)
        
        try:
            cache_path.unlink()
            logger.info(f"Removed cached file: {filename}")
            return True
        except Exception as e:
            logger.error(f"Error removing cached file {filename}: {e}")
            return False
    
    def get_cache_info(self) -> dict:
        """Get information about the cache directory."""
        try:
            total_size = 0
            file_count = 0
            
            for file_path in self.cache_dir.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    file_count += 1
            
            return {
                "cache_dir": str(self.cache_dir),
                "total_files": file_count,
                "total_size_bytes": total_size,
                "total_size_gb": round(total_size / (1024**3), 2)
            }
        except Exception as e:
            logger.error(f"Error getting cache info: {e}")
            return {}
    
    def cleanup_cache(self, keep_current_model: bool = True) -> int:
        """Clean up old cached files."""
        removed_count = 0
        current_filename = config.model.filename
        
        try:
            for file_path in self.cache_dir.iterdir():
                if file_path.is_file():
                    if keep_current_model and file_path.name == current_filename:
                        continue
                    
                    # Remove files that are not the current model
                    file_path.unlink()
                    removed_count += 1
                    logger.info(f"Cleaned up cached file: {file_path.name}")
                    
        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")
        
        return removed_count
