"""
Utility functions and helpers for Multi-Agent Content Analytics
"""

import logging
import asyncio
import time
import functools
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime, timedelta
import hashlib
import json
import os
import re
from pathlib import Path
import aiohttp
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Timer:
    """Simple timer for measuring execution time"""
    start_time: float = 0
    end_time: float = 0
    
    def start(self):
        """Start the timer"""
        self.start_time = time.time()
    
    def stop(self) -> float:
        """Stop the timer and return elapsed time"""
        self.end_time = time.time()
        return self.elapsed_time
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        if self.end_time == 0:
            return time.time() - self.start_time
        return self.end_time - self.start_time

def timing_decorator(func):
    """Decorator to measure function execution time"""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        timer = Timer()
        timer.start()
        try:
            result = await func(*args, **kwargs)
            elapsed = timer.stop()
            logger.info(f"{func.__name__} completed in {elapsed:.4f} seconds")
            return result
        except Exception as e:
            elapsed = timer.stop()
            logger.error(f"{func.__name__} failed after {elapsed:.4f} seconds: {str(e)}")
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        timer = Timer()
        timer.start()
        try:
            result = func(*args, **kwargs)
            elapsed = timer.stop()
            logger.info(f"{func.__name__} completed in {elapsed:.4f} seconds")
            return result
        except Exception as e:
            elapsed = timer.stop()
            logger.error(f"{func.__name__} failed after {elapsed:.4f} seconds: {str(e)}")
            raise
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator to retry function on failure"""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logger.error(f"{func.__name__} failed after {max_retries} retries: {str(e)}")
                        raise
                    
                    wait_time = delay * (backoff ** attempt)
                    logger.warning(f"{func.__name__} attempt {attempt + 1} failed, retrying in {wait_time}s: {str(e)}")
                    await asyncio.sleep(wait_time)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logger.error(f"{func.__name__} failed after {max_retries} retries: {str(e)}")
                        raise
                    
                    wait_time = delay * (backoff ** attempt)
                    logger.warning(f"{func.__name__} attempt {attempt + 1} failed, retrying in {wait_time}s: {str(e)}")
                    time.sleep(wait_time)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class TextProcessor:
    """Utility class for text processing"""
    
    @staticmethod
    def clean_text(text: str, remove_html: bool = True, remove_urls: bool = True) -> str:
        """Clean text by removing unwanted characters"""
        if not text:
            return ""
        
        # Remove HTML tags
        if remove_html:
            text = re.sub(r'<[^>]+>', '', text)
        
        # Remove URLs
        if remove_urls:
            text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text (simple implementation)"""
        if not text:
            return []
        
        # Simple keyword extraction using word frequency
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Common stop words to filter out
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'this', 'that', 'these', 'those', 'can', 'may', 'might', 'must'
        }
        
        # Filter stop words and count frequencies
        word_freq = {}
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:max_keywords]]
    
    @staticmethod
    def calculate_readability_score(text: str) -> float:
        """Calculate a simple readability score (0-100, higher is more readable)"""
        if not text:
            return 0.0
        
        # Count sentences, words, and syllables (simplified)
        sentences = len(re.split(r'[.!?]+', text))
        words = len(text.split())
        
        if sentences == 0 or words == 0:
            return 0.0
        
        # Simplified syllable counting
        syllables = sum(max(1, len(re.findall(r'[aeiouAEIOU]', word))) for word in text.split())
        
        # Simplified Flesch Reading Ease score
        if syllables == 0:
            return 100.0
        
        score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
        return max(0, min(100, score))

class CacheManager:
    """Simple in-memory cache manager"""
    
    def __init__(self, default_ttl: int = 3600):  # 1 hour default TTL
        self.cache = {}
        self.expiry_times = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            return None
        
        # Check if expired
        if key in self.expiry_times and time.time() > self.expiry_times[key]:
            self.delete(key)
            return None
        
        return self.cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        self.cache[key] = value
        
        if ttl is None:
            ttl = self.default_ttl
        
        if ttl > 0:
            self.expiry_times[key] = time.time() + ttl
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        deleted = key in self.cache
        self.cache.pop(key, None)
        self.expiry_times.pop(key, None)
        return deleted
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
        self.expiry_times.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count of removed items"""
        current_time = time.time()
        expired_keys = [
            key for key, expiry_time in self.expiry_times.items()
            if current_time > expiry_time
        ]
        
        for key in expired_keys:
            self.delete(key)
        
        return len(expired_keys)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "total_items": len(self.cache),
            "items_with_expiry": len(self.expiry_times),
            "memory_usage_estimate": sum(len(str(v)) for v in self.cache.values())
        }

class ConfigManager:
    """Configuration manager"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config = {}
        self.last_modified = None
        
        if config_path and os.path.exists(config_path):
            self.load_config()
    
    def load_config(self) -> bool:
        """Load configuration from file"""
        try:
            if not self.config_path or not os.path.exists(self.config_path):
                return False
            
            # Check if file was modified
            current_modified = os.path.getmtime(self.config_path)
            if self.last_modified and current_modified <= self.last_modified:
                return True  # No changes
            
            with open(self.config_path, 'r') as f:
                if self.config_path.endswith('.json'):
                    self.config = json.load(f)
                else:
                    # Assume it's a simple key=value format
                    self.config = {}
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                self.config[key.strip()] = value.strip()
            
            self.last_modified = current_modified
            logger.info(f"Configuration loaded from {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            if not self.config_path:
                return False
            
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                if self.config_path.endswith('.json'):
                    json.dump(self.config, f, indent=2)
                else:
                    for key, value in self.config.items():
                        f.write(f"{key}={value}\n")
            
            self.last_modified = os.path.getmtime(self.config_path)
            logger.info(f"Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False

class HttpClient:
    """HTTP client utilities"""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    @retry_on_failure(max_retries=3)
    async def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Async GET request"""
        if not self.session:
            raise RuntimeError("HttpClient must be used as async context manager")
        
        async with self.session.get(url, headers=headers) as response:
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            if 'application/json' in content_type:
                return await response.json()
            else:
                text = await response.text()
                return {"content": text, "status": response.status}
    
    @retry_on_failure(max_retries=3)
    async def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Async POST request"""
        if not self.session:
            raise RuntimeError("HttpClient must be used as async context manager")
        
        kwargs = {"headers": headers}
        if json_data:
            kwargs["json"] = json_data
        elif data:
            kwargs["data"] = data
        
        async with self.session.post(url, **kwargs) as response:
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            if 'application/json' in content_type:
                return await response.json()
            else:
                text = await response.text()
                return {"content": text, "status": response.status}

def generate_content_id(content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
    """Generate a unique content ID based on content and metadata"""
    # Create a hash based on content and metadata
    content_str = content[:1000]  # Use first 1000 chars to avoid huge strings
    metadata_str = json.dumps(metadata or {}, sort_keys=True)
    
    combined = f"{content_str}_{metadata_str}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]

def generate_analysis_id(content_id: str, agent_name: str) -> str:
    """Generate a unique analysis ID"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    combined = f"{content_id}_{agent_name}_{timestamp}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe filesystem operations"""
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'\s+', '_', filename)
    filename = filename.strip('._')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def format_duration(seconds: float) -> str:
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

class ProgressTracker:
    """Simple progress tracker for long-running operations"""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
        self.last_update = 0
    
    def update(self, increment: int = 1) -> None:
        """Update progress"""
        self.current += increment
        current_time = time.time()
        
        # Log progress every 5 seconds or at completion
        if current_time - self.last_update >= 5 or self.current >= self.total:
            self._log_progress()
            self.last_update = current_time
    
    def _log_progress(self) -> None:
        """Log current progress"""
        if self.total > 0:
            percentage = (self.current / self.total) * 100
            elapsed = time.time() - self.start_time
            
            if self.current > 0:
                estimated_total = elapsed * (self.total / self.current)
                remaining = estimated_total - elapsed
                logger.info(
                    f"{self.description}: {self.current}/{self.total} "
                    f"({percentage:.1f}%) - ETA: {format_duration(remaining)}"
                )
            else:
                logger.info(f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%)")
    
    def complete(self) -> None:
        """Mark as complete"""
        self.current = self.total
        elapsed = time.time() - self.start_time
        logger.info(f"{self.description} completed in {format_duration(elapsed)}")

# Global cache instance
global_cache = CacheManager()

# Export commonly used functions
__all__ = [
    'Timer', 'timing_decorator', 'retry_on_failure',
    'TextProcessor', 'CacheManager', 'ConfigManager', 'HttpClient',
    'ProgressTracker', 'generate_content_id', 'generate_analysis_id',
    'sanitize_filename', 'format_file_size', 'format_duration',
    'global_cache'
]
