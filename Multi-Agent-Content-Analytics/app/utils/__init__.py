"""
Utils Package - Multi-Agent Content Analytics Platform

This package contains utility modules for text processing, caching, and other
common operations used throughout the platform.

Author: Content Analytics Team  
Version: 3.0.0
Last Updated: August 2025
"""

from .text_processing_simple import (
    TextProcessor,
    ScreenplayParser
)

# Stub functions for compatibility
class TextProcessingError(Exception):
    """Text processing error."""
    pass

def estimate_reading_time(text: str) -> int:
    """Estimate reading time in minutes (basic calculation)."""
    words = len(text.split())
    return max(1, words // 200)  # Assume 200 words per minute

def detect_content_type(text: str) -> str:
    """Basic content type detection."""
    parser = ScreenplayParser()
    if parser.is_screenplay_format(text):
        return "screenplay"
    return "general"

def extract_text_features(text: str) -> dict:
    """Extract basic text features."""
    processor = TextProcessor()
    return processor.get_basic_stats(text)

from .cache_manager import (
    CacheManager,
    MemoryCache,
    DiskCache,
    CacheEntry,
    CacheBackend,
    get_cache_manager,
    configure_cache,
    cached
)

__version__ = "3.0.0"
__author__ = "Content Analytics Team"

# Utility registry for dynamic access
UTILITY_REGISTRY = {
    "text_processor": TextProcessor,
    "screenplay_parser": ScreenplayParser,
    "cache_manager": CacheManager,
    "memory_cache": MemoryCache,
    "disk_cache": DiskCache
}

# Global instances for commonly used utilities
_text_processor = None
_cache_manager = None

def get_text_processor(language: str = "en") -> TextProcessor:
    """
    Get global text processor instance.
    
    Args:
        language: Language for text processing
    
    Returns:
        TextProcessor instance
    """
    global _text_processor
    if _text_processor is None or _text_processor.language != language:
        _text_processor = TextProcessor(language=language)
    return _text_processor

def get_screenplay_parser() -> ScreenplayParser:
    """
    Get screenplay parser instance.
    
    Returns:
        ScreenplayParser instance
    """
    return ScreenplayParser()

def initialize_utils(config: dict = None) -> dict:
    """
    Initialize utility modules with configuration.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Dictionary with initialization status
    """
    if config is None:
        config = {}
    
    status = {}
    
    try:
        # Initialize cache manager
        cache_config = config.get('cache', {})
        cache_manager = configure_cache(
            memory_size=cache_config.get('memory_size', 1000),
            disk_dir=cache_config.get('disk_dir', './cache'),
            default_ttl=cache_config.get('default_ttl', 3600),
            enable_disk=cache_config.get('enable_disk', True)
        )
        status['cache_manager'] = True
        
        # Initialize text processor
        text_config = config.get('text_processing', {})
        language = text_config.get('language', 'en')
        text_processor = get_text_processor(language)
        status['text_processor'] = True
        
        return status
        
    except Exception as e:
        status['error'] = str(e)
        return status

def cleanup_utils() -> dict:
    """
    Cleanup utility resources.
    
    Returns:
        Dictionary with cleanup status
    """
    status = {}
    
    try:
        # Cleanup cache
        cache_manager = get_cache_manager()
        cleanup_stats = cache_manager.cleanup()
        status['cache_cleanup'] = cleanup_stats
        
        # Reset global instances
        global _text_processor, _cache_manager
        _text_processor = None
        _cache_manager = None
        
        status['cleanup_complete'] = True
        
    except Exception as e:
        status['error'] = str(e)
    
    return status

def get_utility_stats() -> dict:
    """
    Get statistics from all utility modules.
    
    Returns:
        Dictionary with utility statistics
    """
    stats = {}
    
    try:
        # Cache statistics
        cache_manager = get_cache_manager()
        stats['cache'] = cache_manager.get_comprehensive_stats()
        
        # Text processor statistics (if available)
        if _text_processor:
            stats['text_processor'] = {
                'language': _text_processor.language,
                'stopwords_count': len(_text_processor.stop_words),
                'nlp_model_loaded': _text_processor.nlp is not None
            }
        
    except Exception as e:
        stats['error'] = str(e)
    
    return stats

# Convenience functions for common operations

def process_text_content(content: str, 
                        language: str = "en",
                        clean_options: dict = None) -> dict:
    """
    Process text content with default options.
    
    Args:
        content: Text content to process
        language: Language for processing
        clean_options: Text cleaning options
    
    Returns:
        Dictionary with processed text and features
    """
    processor = get_text_processor(language)
    
    # Clean text
    cleaned_text = processor.clean_text(content, clean_options)
    
    # Extract features
    features = extract_text_features(cleaned_text)
    
    return {
        'original_content': content,
        'cleaned_content': cleaned_text,
        'features': features,
        'processing_language': language
    }

def parse_screenplay_content(content: str) -> dict:
    """
    Parse screenplay content with default options.
    
    Args:
        content: Screenplay content
    
    Returns:
        Dictionary with parsed screenplay elements
    """
    parser = get_screenplay_parser()
    return parser.parse_screenplay(content)

def cache_analysis_result(key: str, 
                         result: dict, 
                         ttl: int = None) -> bool:
    """
    Cache analysis result with default TTL.
    
    Args:
        key: Cache key
        result: Analysis result to cache
        ttl: Time to live in seconds
    
    Returns:
        True if cached successfully
    """
    cache_manager = get_cache_manager()
    return cache_manager.set(key, result, ttl)

def get_cached_analysis_result(key: str) -> dict:
    """
    Get cached analysis result.
    
    Args:
        key: Cache key
    
    Returns:
        Cached result or None
    """
    cache_manager = get_cache_manager()
    return cache_manager.get(key)

__all__ = [
    # Text Processing
    "TextProcessor", "ScreenplayParser", "TextProcessingError",
    "estimate_reading_time", "detect_content_type", "extract_text_features",
    
    # Cache Management
    "CacheManager", "MemoryCache", "DiskCache", "CacheEntry", "CacheBackend",
    "get_cache_manager", "configure_cache", "cached",
    
    # Utility Functions
    "get_text_processor", "get_screenplay_parser", "initialize_utils",
    "cleanup_utils", "get_utility_stats",
    
    # Convenience Functions
    "process_text_content", "parse_screenplay_content",
    "cache_analysis_result", "get_cached_analysis_result",
    
    # Registry
    "UTILITY_REGISTRY"
]
