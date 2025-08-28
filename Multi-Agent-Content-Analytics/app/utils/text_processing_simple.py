"""
Text Processing Utilities - Simplified Version

Professional text processing utilities for content analysis without heavy NLP dependencies.
This version provides basic text processing capabilities with graceful fallbacks.
"""

import re
import string
import unicodedata
from typing import List, Dict, Set, Tuple, Optional, Any, Union
from collections import Counter, defaultdict
import logging

# Configure logging
logger = logging.getLogger(__name__)


class TextProcessor:
    """
    Basic text processing utility class for content analysis.
    
    Provides essential text processing capabilities including cleaning,
    tokenization, and basic feature extraction without heavy dependencies.
    """
    
    def __init__(self, language: str = "en"):
        """
        Initialize the text processor with language-specific configurations.
        
        Args:
            language: Target language for processing (default: English)
        """
        self.language = language
        
        # Basic English stop words (simplified list)
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'i', 'you', 'they', 'we', 'this',
            'but', 'have', 'had', 'what', 'said', 'each', 'which', 'their',
            'would', 'there', 'could', 'if', 'do', 'when', 'time', 'about'
        }
        
    def preprocess_text(self, text: str) -> str:
        """
        Clean and normalize text for analysis.
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned and normalized text
        """
        if not text:
            return ""
            
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        
        # Normalize unicode
        text = unicodedata.normalize('NFKD', text)
        
        # Basic cleaning
        text = re.sub(r'[^\w\s\-\.\!\?\,\:\;]', '', text)
        
        return text.strip()
    
    def tokenize_words(self, text: str) -> List[str]:
        """
        Basic word tokenization.
        
        Args:
            text: Input text
            
        Returns:
            List of word tokens
        """
        # Basic word tokenization using regex
        words = re.findall(r'\b\w+\b', text.lower())
        return [word for word in words if len(word) > 1]
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """
        Basic sentence tokenization.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Basic sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """
        Extract top keywords from text using basic frequency analysis.
        
        Args:
            text: Input text
            top_k: Number of top keywords to return
            
        Returns:
            List of top keywords
        """
        words = self.tokenize_words(text)
        
        # Filter out stop words and short words
        filtered_words = [
            word for word in words 
            if word not in self.stop_words and len(word) > 2
        ]
        
        # Count frequencies
        word_counts = Counter(filtered_words)
        
        # Return top keywords
        return [word for word, count in word_counts.most_common(top_k)]
    
    def get_word_count(self, text: str) -> int:
        """Get word count."""
        return len(self.tokenize_words(text))
    
    def get_sentence_count(self, text: str) -> int:
        """Get sentence count."""
        return len(self.tokenize_sentences(text))
    
    def get_character_count(self, text: str) -> int:
        """Get character count (excluding whitespace)."""
        return len(re.sub(r'\s+', '', text))
    
    def get_basic_stats(self, text: str) -> Dict[str, Any]:
        """
        Get basic text statistics.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with basic statistics
        """
        words = self.tokenize_words(text)
        sentences = self.tokenize_sentences(text)
        
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'character_count': self.get_character_count(text),
            'avg_words_per_sentence': len(words) / max(len(sentences), 1),
            'unique_words': len(set(words)),
            'lexical_diversity': len(set(words)) / max(len(words), 1)
        }


class ScreenplayParser:
    """
    Basic screenplay parsing utilities.
    
    Provides simple parsing capabilities for screenplay format detection
    and basic structure analysis.
    """
    
    def __init__(self):
        """Initialize the screenplay parser."""
        self.scene_headers = r'^(INT\.|EXT\.|FADE IN|FADE OUT)'
        self.character_name = r'^[A-Z][A-Z\s]+$'
        
    def is_screenplay_format(self, text: str) -> bool:
        """
        Check if text appears to be in screenplay format.
        
        Args:
            text: Input text
            
        Returns:
            Boolean indicating if text appears to be a screenplay
        """
        lines = text.strip().split('\n')
        screenplay_indicators = 0
        
        for line in lines[:20]:  # Check first 20 lines
            line = line.strip()
            if re.match(self.scene_headers, line, re.IGNORECASE):
                screenplay_indicators += 1
            elif re.match(self.character_name, line):
                screenplay_indicators += 1
                
        return screenplay_indicators >= 2
    
    def extract_characters(self, text: str) -> List[str]:
        """
        Extract character names from screenplay.
        
        Args:
            text: Screenplay text
            
        Returns:
            List of character names
        """
        lines = text.split('\n')
        characters = set()
        
        for line in lines:
            line = line.strip()
            if re.match(self.character_name, line) and len(line) < 30:
                # Basic filtering to avoid false positives
                if not any(word in line.lower() for word in ['fade', 'cut', 'int', 'ext']):
                    characters.add(line)
                    
        return list(characters)
    
    def extract_scenes(self, text: str) -> List[str]:
        """
        Extract scene headers from screenplay.
        
        Args:
            text: Screenplay text
            
        Returns:
            List of scene headers
        """
        lines = text.split('\n')
        scenes = []
        
        for line in lines:
            line = line.strip()
            if re.match(self.scene_headers, line, re.IGNORECASE):
                scenes.append(line)
                
        return scenes


# Export the main classes
__all__ = ['TextProcessor', 'ScreenplayParser']
