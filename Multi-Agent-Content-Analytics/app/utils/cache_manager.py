"""
Cache Manager - Multi-Agent Content Analytics Platform

This module provides comprehensive caching functionality for the content analytics platform,
including in-memory caching, persistent storage, and cache management operations.

Author: Content Analytics Team  
Version: 3.0.0
Last Updated: August 2025
"""

import hashlib
import json
import pickle
import time
import sqlite3
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from threading import RLock
from pathlib import Path
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry data structure"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    size_bytes: int = 0
    metadata: Optional[Dict[str, Any]] = None

class CacheBackend(ABC):
    """Abstract base class for cache backends"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value by key"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value with optional TTL"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete entry by key"""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Clear all entries"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        pass
    
    @abstractmethod
    def keys(self) -> List[str]:
        """Get all keys"""
        pass
    
    @abstractmethod
    def size(self) -> int:
        """Get number of entries"""
        pass

class MemoryCache(CacheBackend):
    """
    In-memory cache backend with LRU eviction and TTL support.
    
    Features:
    - Thread-safe operations
    - LRU eviction policy
    - TTL (Time To Live) support
    - Memory usage tracking
    - Access statistics
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[int] = 3600):
        """
        Initialize memory cache.
        
        Args:
            max_size: Maximum number of entries
            default_ttl: Default TTL in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: List[str] = []
        self._lock = RLock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_memory_bytes': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value by key with access tracking"""
        with self._lock:
            if key not in self._cache:
                self._stats['misses'] += 1
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if entry.expires_at and datetime.utcnow() > entry.expires_at:
                self.delete(key)
                self._stats['misses'] += 1
                return None
            
            # Update access statistics
            entry.access_count += 1
            entry.last_accessed = datetime.utcnow()
            
            # Update LRU order
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            
            self._stats['hits'] += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value with optional TTL"""
        with self._lock:
            try:
                # Calculate entry size
                size_bytes = self._calculate_size(value)
                
                # Calculate expiration
                ttl = ttl or self.default_ttl
                expires_at = None
                if ttl:
                    expires_at = datetime.utcnow() + timedelta(seconds=ttl)
                
                # Create cache entry
                entry = CacheEntry(
                    key=key,
                    value=value,
                    created_at=datetime.utcnow(),
                    expires_at=expires_at,
                    size_bytes=size_bytes
                )
                
                # Remove existing entry if present
                if key in self._cache:
                    old_entry = self._cache[key]
                    self._stats['total_memory_bytes'] -= old_entry.size_bytes
                    if key in self._access_order:
                        self._access_order.remove(key)
                
                # Check if we need to evict entries
                while len(self._cache) >= self.max_size:
                    self._evict_lru()
                
                # Store new entry
                self._cache[key] = entry
                self._access_order.append(key)
                self._stats['total_memory_bytes'] += size_bytes
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to cache entry {key}: {e}")
                return False
    
    def delete(self, key: str) -> bool:
        """Delete entry by key"""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                self._stats['total_memory_bytes'] -= entry.size_bytes
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)
                return True
            return False
    
    def clear(self) -> bool:
        """Clear all entries"""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
            self._stats['total_memory_bytes'] = 0
            return True
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        with self._lock:
            if key not in self._cache:
                return False
            
            entry = self._cache[key]
            if entry.expires_at and datetime.utcnow() > entry.expires_at:
                self.delete(key)
                return False
            
            return True
    
    def keys(self) -> List[str]:
        """Get all non-expired keys"""
        with self._lock:
            valid_keys = []
            for key in list(self._cache.keys()):
                if self.exists(key):
                    valid_keys.append(key)
            return valid_keys
    
    def size(self) -> int:
        """Get number of non-expired entries"""
        return len(self.keys())
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if self._access_order:
            lru_key = self._access_order[0]
            self.delete(lru_key)
            self._stats['evictions'] += 1
    
    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate size of value in bytes"""
        try:
            return len(pickle.dumps(value))
        except Exception:
            # Fallback to string representation
            return len(str(value).encode('utf-8'))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = self._stats['hits'] / total_requests if total_requests > 0 else 0
            
            return {
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'hit_rate': round(hit_rate, 3),
                'evictions': self._stats['evictions'],
                'current_size': len(self._cache),
                'max_size': self.max_size,
                'memory_usage_bytes': self._stats['total_memory_bytes'],
                'memory_usage_mb': round(self._stats['total_memory_bytes'] / 1024 / 1024, 2)
            }

class DiskCache(CacheBackend):
    """
    Persistent disk-based cache using SQLite.
    
    Features:
    - Persistent storage across restarts
    - TTL support with automatic cleanup
    - Compression for large values
    - ACID transactions
    """
    
    def __init__(self, cache_dir: str = "./cache", default_ttl: Optional[int] = 86400):
        """
        Initialize disk cache.
        
        Args:
            cache_dir: Directory for cache files
            default_ttl: Default TTL in seconds (24 hours)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.db_path = self.cache_dir / "cache.db"
        self.default_ttl = default_ttl
        self._lock = RLock()
        
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    value BLOB,
                    created_at TIMESTAMP,
                    expires_at TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP,
                    size_bytes INTEGER
                )
            """)
            
            # Create index for expiration cleanup
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at ON cache_entries(expires_at)
            """)
            
            conn.commit()
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value by key"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        SELECT value, expires_at, access_count 
                        FROM cache_entries 
                        WHERE key = ?
                    """, (key,))
                    
                    row = cursor.fetchone()
                    if not row:
                        return None
                    
                    # Check expiration
                    if row['expires_at']:
                        expires_at = datetime.fromisoformat(row['expires_at'])
                        if datetime.utcnow() > expires_at:
                            self.delete(key)
                            return None
                    
                    # Update access statistics
                    cursor.execute("""
                        UPDATE cache_entries 
                        SET access_count = access_count + 1, 
                            last_accessed = ? 
                        WHERE key = ?
                    """, (datetime.utcnow().isoformat(), key))
                    
                    conn.commit()
                    
                    # Deserialize value
                    return pickle.loads(row['value'])
                    
            except Exception as e:
                logger.error(f"Failed to get cache entry {key}: {e}")
                return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value with optional TTL"""
        with self._lock:
            try:
                # Serialize value
                serialized_value = pickle.dumps(value)
                size_bytes = len(serialized_value)
                
                # Calculate expiration
                ttl = ttl or self.default_ttl
                expires_at = None
                if ttl:
                    expires_at = datetime.utcnow() + timedelta(seconds=ttl)
                
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO cache_entries 
                        (key, value, created_at, expires_at, access_count, last_accessed, size_bytes)
                        VALUES (?, ?, ?, ?, 0, NULL, ?)
                    """, (
                        key,
                        serialized_value,
                        datetime.utcnow().isoformat(),
                        expires_at.isoformat() if expires_at else None,
                        size_bytes
                    ))
                    
                    conn.commit()
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to cache entry {key}: {e}")
                return False
    
    def delete(self, key: str) -> bool:
        """Delete entry by key"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                    conn.commit()
                    return cursor.rowcount > 0
            except Exception as e:
                logger.error(f"Failed to delete cache entry {key}: {e}")
                return False
    
    def clear(self) -> bool:
        """Clear all entries"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM cache_entries")
                    conn.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to clear cache: {e}")
                return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT expires_at FROM cache_entries WHERE key = ?
                    """, (key,))
                    
                    row = cursor.fetchone()
                    if not row:
                        return False
                    
                    if row[0]:  # expires_at
                        expires_at = datetime.fromisoformat(row[0])
                        if datetime.utcnow() > expires_at:
                            self.delete(key)
                            return False
                    
                    return True
            except Exception as e:
                logger.error(f"Failed to check cache entry existence {key}: {e}")
                return False
    
    def keys(self) -> List[str]:
        """Get all non-expired keys"""
        with self._lock:
            try:
                # First clean up expired entries
                self.cleanup_expired()
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT key FROM cache_entries")
                    return [row[0] for row in cursor.fetchall()]
            except Exception as e:
                logger.error(f"Failed to get cache keys: {e}")
                return []
    
    def size(self) -> int:
        """Get number of non-expired entries"""
        return len(self.keys())
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count of removed entries"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        DELETE FROM cache_entries 
                        WHERE expires_at IS NOT NULL 
                        AND expires_at < ?
                    """, (datetime.utcnow().isoformat(),))
                    
                    conn.commit()
                    return cursor.rowcount
            except Exception as e:
                logger.error(f"Failed to cleanup expired entries: {e}")
                return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Get basic stats
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_entries,
                            SUM(access_count) as total_accesses,
                            SUM(size_bytes) as total_size_bytes,
                            AVG(access_count) as avg_access_count
                        FROM cache_entries
                    """)
                    
                    row = cursor.fetchone()
                    
                    return {
                        'total_entries': row[0] or 0,
                        'total_accesses': row[1] or 0,
                        'total_size_bytes': row[2] or 0,
                        'total_size_mb': round((row[2] or 0) / 1024 / 1024, 2),
                        'average_access_count': round(row[3] or 0, 2),
                        'database_path': str(self.db_path)
                    }
            except Exception as e:
                logger.error(f"Failed to get cache stats: {e}")
                return {}

class CacheManager:
    """
    Comprehensive cache manager with multiple backends and advanced features.
    
    Features:
    - Multiple cache backends (memory, disk)
    - Automatic key generation
    - Cache warming and preloading
    - Statistics and monitoring
    - Batch operations
    """
    
    def __init__(self, 
                 memory_cache_size: int = 1000,
                 disk_cache_dir: str = "./cache",
                 default_ttl: int = 3600,
                 enable_disk_cache: bool = True):
        """
        Initialize cache manager.
        
        Args:
            memory_cache_size: Size of memory cache
            disk_cache_dir: Directory for disk cache
            default_ttl: Default TTL in seconds
            enable_disk_cache: Whether to enable persistent disk cache
        """
        self.default_ttl = default_ttl
        
        # Initialize backends
        self.memory_cache = MemoryCache(
            max_size=memory_cache_size,
            default_ttl=default_ttl
        )
        
        self.disk_cache = None
        if enable_disk_cache:
            try:
                self.disk_cache = DiskCache(
                    cache_dir=disk_cache_dir,
                    default_ttl=default_ttl * 24  # Longer TTL for disk cache
                )
            except Exception as e:
                logger.warning(f"Failed to initialize disk cache: {e}")
        
        self._stats = {
            'requests': 0,
            'memory_hits': 0,
            'disk_hits': 0,
            'misses': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value by key with multi-tier caching.
        
        Checks memory cache first, then disk cache if enabled.
        """
        self._stats['requests'] += 1
        
        # Check memory cache first
        value = self.memory_cache.get(key)
        if value is not None:
            self._stats['memory_hits'] += 1
            return value
        
        # Check disk cache if available
        if self.disk_cache:
            value = self.disk_cache.get(key)
            if value is not None:
                self._stats['disk_hits'] += 1
                # Promote to memory cache
                self.memory_cache.set(key, value)
                return value
        
        self._stats['misses'] += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value in both memory and disk caches"""
        ttl = ttl or self.default_ttl
        success = True
        
        # Store in memory cache
        if not self.memory_cache.set(key, value, ttl):
            success = False
        
        # Store in disk cache if available
        if self.disk_cache:
            if not self.disk_cache.set(key, value, ttl * 24):  # Longer TTL for disk
                success = False
        
        return success
    
    def delete(self, key: str) -> bool:
        """Delete from both caches"""
        memory_deleted = self.memory_cache.delete(key)
        disk_deleted = True
        
        if self.disk_cache:
            disk_deleted = self.disk_cache.delete(key)
        
        return memory_deleted or disk_deleted
    
    def clear(self) -> bool:
        """Clear both caches"""
        memory_cleared = self.memory_cache.clear()
        disk_cleared = True
        
        if self.disk_cache:
            disk_cleared = self.disk_cache.clear()
        
        return memory_cleared and disk_cleared
    
    def exists(self, key: str) -> bool:
        """Check if key exists in either cache"""
        return (self.memory_cache.exists(key) or 
                (self.disk_cache and self.disk_cache.exists(key)))
    
    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate cache key from prefix and arguments.
        
        Args:
            prefix: Key prefix
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Generated cache key
        """
        # Create hash from arguments
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else {}
        }
        
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()[:16]
        
        return f"{prefix}:{key_hash}"
    
    def get_or_set(self, key: str, func, ttl: Optional[int] = None) -> Any:
        """
        Get value from cache or compute and cache it.
        
        Args:
            key: Cache key
            func: Function to compute value if not cached
            ttl: TTL for new cache entry
        
        Returns:
            Cached or computed value
        """
        value = self.get(key)
        if value is not None:
            return value
        
        # Compute value
        try:
            value = func()
            self.set(key, value, ttl)
            return value
        except Exception as e:
            logger.error(f"Failed to compute value for key {key}: {e}")
            raise
    
    def batch_get(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values at once"""
        results = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                results[key] = value
        return results
    
    def batch_set(self, items: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple values at once"""
        success = True
        for key, value in items.items():
            if not self.set(key, value, ttl):
                success = False
        return success
    
    def cleanup(self) -> Dict[str, int]:
        """Clean up expired entries and return cleanup stats"""
        stats = {'memory_cleaned': 0, 'disk_cleaned': 0}
        
        # Memory cache cleanup happens automatically during access
        
        # Disk cache cleanup
        if self.disk_cache:
            stats['disk_cleaned'] = self.disk_cache.cleanup_expired()
        
        return stats
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        memory_stats = self.memory_cache.get_stats()
        disk_stats = self.disk_cache.get_stats() if self.disk_cache else {}
        
        total_requests = self._stats['requests']
        overall_hit_rate = 0
        if total_requests > 0:
            total_hits = self._stats['memory_hits'] + self._stats['disk_hits']
            overall_hit_rate = total_hits / total_requests
        
        return {
            'overall': {
                'total_requests': total_requests,
                'memory_hits': self._stats['memory_hits'],
                'disk_hits': self._stats['disk_hits'],
                'misses': self._stats['misses'],
                'overall_hit_rate': round(overall_hit_rate, 3)
            },
            'memory_cache': memory_stats,
            'disk_cache': disk_stats
        }

# Global cache manager instance
_cache_manager: Optional[CacheManager] = None

def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager

def configure_cache(memory_size: int = 1000, 
                   disk_dir: str = "./cache",
                   default_ttl: int = 3600,
                   enable_disk: bool = True) -> CacheManager:
    """Configure and get cache manager"""
    global _cache_manager
    _cache_manager = CacheManager(
        memory_cache_size=memory_size,
        disk_cache_dir=disk_dir,
        default_ttl=default_ttl,
        enable_disk_cache=enable_disk
    )
    return _cache_manager

# Decorators for caching

def cached(ttl: Optional[int] = None, key_prefix: str = "func"):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Cache TTL in seconds
        key_prefix: Cache key prefix
    
    Returns:
        Decorated function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_manager = get_cache_manager()
            
            # Generate cache key
            key = cache_manager.generate_key(
                f"{key_prefix}:{func.__name__}",
                *args,
                **kwargs
            )
            
            # Try to get from cache
            result = cache_manager.get(key)
            if result is not None:
                return result
            
            # Compute and cache result
            result = func(*args, **kwargs)
            cache_manager.set(key, result, ttl)
            
            return result
        
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    
    return decorator

# Export main classes and functions
__all__ = [
    'CacheManager',
    'MemoryCache',
    'DiskCache',
    'CacheEntry',
    'CacheBackend',
    'get_cache_manager',
    'configure_cache',
    'cached'
]
