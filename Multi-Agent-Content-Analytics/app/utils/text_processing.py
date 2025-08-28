"""
Text Processing Utilities - Multi-Agent Content Analytics Platform

This module provides comprehensive text processing utilities for content analysis,
including natural language processing, text cleaning, tokenization, and feature extraction.

Author: Content Analytics Team  
Version: 3.0.0
Last Updated: August 2025
"""

import re
import string
import unicodedata
from typing import List, Dict, Set, Tuple, Optional, Any, Union
from collections import Counter, defaultdict
import logging

# Optional NLP imports with graceful fallbacks
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    from nltk.chunk import ne_chunk
    from nltk.tag import pos_tag
    from nltk.sentiment import SentimentIntensityAnalyzer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from textstat import flesch_reading_ease, flesch_kincaid_grade, automated_readability_index
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)

class TextProcessingError(Exception):
    """Custom exception for text processing errors"""
    pass

class TextProcessor:
    """
    Advanced text processing utility class for content analysis.
    
    Provides comprehensive text processing capabilities including cleaning,
    tokenization, linguistic analysis, and feature extraction.
    """
    
    def __init__(self, language: str = "en"):
        """
        Initialize the text processor with language-specific configurations.
        
        Args:
            language: Target language for processing (default: English)
        """
        self.language = language
        if NLTK_AVAILABLE:
            self._ensure_nltk_data()
        if SPACY_AVAILABLE:
            self._load_language_models()
        
    def _ensure_nltk_data(self) -> None:
        """Ensure required NLTK data is downloaded (only if NLTK is available)"""
        if not NLTK_AVAILABLE:
            return
            
        required_data = [
            'punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger',
            'maxent_ne_chunker', 'words', 'vader_lexicon'
        ]
        
        for data_name in required_data:
            try:
                nltk.data.find(f'tokenizers/{data_name}')
            except LookupError:
                try:
                    nltk.download(data_name, quiet=True)
                except Exception as e:
                    logger.warning(f"Failed to download NLTK data '{data_name}': {e}")
    
    def _load_language_models(self) -> None:
        """Load spaCy language models"""
        try:
            if self.language == "en":
                self.nlp = spacy.load("en_core_web_sm")
            else:
                logger.warning(f"SpaCy model for language '{self.language}' not configured")
                self.nlp = None
        except IOError:
            logger.warning("SpaCy English model not found. Some features may be limited.")
            self.nlp = None
        
        # Initialize NLTK components
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        try:
            self.stop_words = set(stopwords.words('english'))
        except LookupError:
            self.stop_words = set()
            logger.warning("NLTK stopwords not available")
    
    def clean_text(self, text: str, options: Optional[Dict[str, bool]] = None) -> str:
        """
        Clean and normalize text according to specified options.
        
        Args:
            text: Input text to clean
            options: Cleaning options dictionary
        
        Returns:
            Cleaned and normalized text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Default cleaning options
        default_options = {
            'remove_html': True,
            'remove_urls': True,
            'remove_emails': True,
            'remove_phone_numbers': True,
            'normalize_unicode': True,
            'remove_extra_whitespace': True,
            'preserve_sentence_structure': True,
            'fix_encoding': True
        }
        
        if options:
            default_options.update(options)
        
        cleaned_text = text
        
        try:
            # Fix encoding issues
            if default_options['fix_encoding']:
                cleaned_text = self._fix_encoding(cleaned_text)
            
            # Remove HTML tags
            if default_options['remove_html']:
                cleaned_text = re.sub(r'<[^>]+>', ' ', cleaned_text)
            
            # Remove URLs
            if default_options['remove_urls']:
                url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
                cleaned_text = re.sub(url_pattern, ' ', cleaned_text)
            
            # Remove email addresses
            if default_options['remove_emails']:
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                cleaned_text = re.sub(email_pattern, ' ', cleaned_text)
            
            # Remove phone numbers
            if default_options['remove_phone_numbers']:
                phone_pattern = r'(\+?1[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}'
                cleaned_text = re.sub(phone_pattern, ' ', cleaned_text)
            
            # Normalize Unicode characters
            if default_options['normalize_unicode']:
                cleaned_text = unicodedata.normalize('NFKD', cleaned_text)
            
            # Remove extra whitespace
            if default_options['remove_extra_whitespace']:
                cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
                cleaned_text = cleaned_text.strip()
            
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error cleaning text: {e}")
            raise TextProcessingError(f"Text cleaning failed: {e}")
    
    def _fix_encoding(self, text: str) -> str:
        """Fix common encoding issues in text"""
        encoding_fixes = {
            'â€™': "'",
            'â€œ': '"',
            'â€': '"',
            'â€"': '—',
            'â€"': '–',
            'â€¦': '...',
            'Ã©': 'é',
            'Ã¡': 'á',
            'Ã­': 'í',
            'Ã³': 'ó',
            'Ãº': 'ú',
        }
        
        for wrong, correct in encoding_fixes.items():
            text = text.replace(wrong, correct)
        
        return text
    
    def tokenize_text(self, text: str, method: str = "word") -> List[str]:
        """
        Tokenize text into words or sentences.
        
        Args:
            text: Input text to tokenize
            method: Tokenization method ("word" or "sentence")
        
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        try:
            if method == "word":
                return word_tokenize(text.lower())
            elif method == "sentence":
                return sent_tokenize(text)
            else:
                raise ValueError(f"Unknown tokenization method: {method}")
        except Exception as e:
            logger.error(f"Tokenization failed: {e}")
            # Fallback to simple splitting
            if method == "word":
                return text.lower().split()
            else:
                return text.split('.')
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Remove stopwords from token list.
        
        Args:
            tokens: List of word tokens
        
        Returns:
            Filtered token list without stopwords
        """
        return [token for token in tokens if token.lower() not in self.stop_words]
    
    def stem_tokens(self, tokens: List[str]) -> List[str]:
        """
        Apply stemming to tokens.
        
        Args:
            tokens: List of word tokens
        
        Returns:
            List of stemmed tokens
        """
        return [self.stemmer.stem(token) for token in tokens]
    
    def lemmatize_tokens(self, tokens: List[str]) -> List[str]:
        """
        Apply lemmatization to tokens.
        
        Args:
            tokens: List of word tokens
        
        Returns:
            List of lemmatized tokens
        """
        return [self.lemmatizer.lemmatize(token) for token in tokens]
    
    def extract_named_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text.
        
        Args:
            text: Input text
        
        Returns:
            Dictionary mapping entity types to entity lists
        """
        entities = defaultdict(list)
        
        try:
            # Using spaCy if available
            if self.nlp:
                doc = self.nlp(text)
                for ent in doc.ents:
                    entities[ent.label_].append(ent.text)
            else:
                # Fallback to NLTK
                tokens = word_tokenize(text)
                pos_tags = pos_tag(tokens)
                chunks = ne_chunk(pos_tags)
                
                for chunk in chunks:
                    if hasattr(chunk, 'label'):
                        entity_name = ' '.join([token for token, pos in chunk.leaves()])
                        entities[chunk.label()].append(entity_name)
        
        except Exception as e:
            logger.error(f"Named entity extraction failed: {e}")
        
        return dict(entities)
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text.
        
        Args:
            text: Input text
        
        Returns:
            Dictionary with sentiment scores
        """
        try:
            scores = self.sentiment_analyzer.polarity_scores(text)
            return {
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'compound': scores['compound']
            }
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0, 'compound': 0.0}
    
    def calculate_readability_metrics(self, text: str) -> Dict[str, float]:
        """
        Calculate various readability metrics for text.
        
        Args:
            text: Input text
        
        Returns:
            Dictionary with readability scores
        """
        try:
            return {
                'flesch_reading_ease': flesch_reading_ease(text),
                'flesch_kincaid_grade': flesch_kincaid_grade(text),
                'automated_readability_index': automated_readability_index(text)
            }
        except Exception as e:
            logger.error(f"Readability calculation failed: {e}")
            return {
                'flesch_reading_ease': 0.0,
                'flesch_kincaid_grade': 0.0,
                'automated_readability_index': 0.0
            }
    
    def extract_keywords(self, text: str, num_keywords: int = 10) -> List[Tuple[str, int]]:
        """
        Extract keywords from text using frequency analysis.
        
        Args:
            text: Input text
            num_keywords: Number of top keywords to return
        
        Returns:
            List of (keyword, frequency) tuples
        """
        try:
            # Clean and tokenize text
            cleaned_text = self.clean_text(text)
            tokens = self.tokenize_text(cleaned_text, method="word")
            
            # Remove stopwords and punctuation
            filtered_tokens = [
                token for token in tokens 
                if token not in self.stop_words and 
                token not in string.punctuation and 
                len(token) > 2
            ]
            
            # Count word frequencies
            word_freq = Counter(filtered_tokens)
            
            return word_freq.most_common(num_keywords)
        
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []
    
    def analyze_text_statistics(self, text: str) -> Dict[str, Any]:
        """
        Calculate comprehensive text statistics.
        
        Args:
            text: Input text
        
        Returns:
            Dictionary with text statistics
        """
        try:
            sentences = self.tokenize_text(text, method="sentence")
            words = self.tokenize_text(text, method="word")
            
            # Basic counts
            char_count = len(text)
            char_count_no_spaces = len(text.replace(' ', ''))
            word_count = len(words)
            sentence_count = len(sentences)
            paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
            
            # Average metrics
            avg_words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0
            avg_chars_per_word = char_count_no_spaces / word_count if word_count > 0 else 0
            
            # Vocabulary richness
            unique_words = len(set(words))
            vocabulary_richness = unique_words / word_count if word_count > 0 else 0
            
            return {
                'character_count': char_count,
                'character_count_no_spaces': char_count_no_spaces,
                'word_count': word_count,
                'sentence_count': sentence_count,
                'paragraph_count': paragraph_count,
                'average_words_per_sentence': round(avg_words_per_sentence, 2),
                'average_characters_per_word': round(avg_chars_per_word, 2),
                'unique_words': unique_words,
                'vocabulary_richness': round(vocabulary_richness, 3),
                'estimated_reading_time_minutes': round(word_count / 200, 1)  # Assuming 200 WPM
            }
        
        except Exception as e:
            logger.error(f"Text statistics calculation failed: {e}")
            return {}
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of input text.
        
        Args:
            text: Input text
        
        Returns:
            Detected language code
        """
        try:
            if self.nlp:
                doc = self.nlp(text[:1000])  # Use first 1000 chars for detection
                return doc.lang_ if hasattr(doc, 'lang_') else 'en'
            else:
                # Simple heuristic fallback
                return 'en'
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return 'en'
    
    def extract_ngrams(self, text: str, n: int = 2, num_ngrams: int = 10) -> List[Tuple[str, int]]:
        """
        Extract n-grams from text.
        
        Args:
            text: Input text
            n: N-gram size
            num_ngrams: Number of top n-grams to return
        
        Returns:
            List of (n-gram, frequency) tuples
        """
        try:
            tokens = self.tokenize_text(self.clean_text(text), method="word")
            filtered_tokens = self.remove_stopwords(tokens)
            
            # Generate n-grams
            ngrams = []
            for i in range(len(filtered_tokens) - n + 1):
                ngram = ' '.join(filtered_tokens[i:i + n])
                ngrams.append(ngram)
            
            # Count frequencies
            ngram_freq = Counter(ngrams)
            
            return ngram_freq.most_common(num_ngrams)
        
        except Exception as e:
            logger.error(f"N-gram extraction failed: {e}")
            return []

class ScreenplayParser:
    """
    Specialized parser for screenplay and script formats.
    
    Handles various screenplay formats including Final Draft, Fountain,
    and standard industry formats.
    """
    
    def __init__(self):
        """Initialize the screenplay parser"""
        self.text_processor = TextProcessor()
        
        # Screenplay element patterns
        self.patterns = {
            'scene_heading': re.compile(r'^(INT\.|EXT\.|FADE IN:|FADE OUT:)', re.MULTILINE),
            'character_name': re.compile(r'^[A-Z][A-Z\s]+$', re.MULTILINE),
            'dialogue': re.compile(r'^\s{10,}(.+)$', re.MULTILINE),
            'action': re.compile(r'^[A-Z].*[a-z].*$', re.MULTILINE),
            'parenthetical': re.compile(r'^\s*\([^)]+\)\s*$', re.MULTILINE),
            'transition': re.compile(r'^(CUT TO:|FADE TO:|DISSOLVE TO:)', re.MULTILINE)
        }
    
    def parse_screenplay(self, text: str) -> Dict[str, Any]:
        """
        Parse screenplay text and extract structured elements.
        
        Args:
            text: Screenplay text
        
        Returns:
            Dictionary with parsed screenplay elements
        """
        try:
            # Clean the text
            cleaned_text = self.text_processor.clean_text(text, {
                'remove_html': True,
                'preserve_sentence_structure': True,
                'remove_extra_whitespace': True
            })
            
            # Extract elements
            scenes = self._extract_scenes(cleaned_text)
            characters = self._extract_characters(cleaned_text)
            dialogue_analysis = self._analyze_dialogue(cleaned_text)
            action_lines = self._extract_action_lines(cleaned_text)
            
            return {
                'scenes': scenes,
                'characters': characters,
                'dialogue_analysis': dialogue_analysis,
                'action_lines': action_lines,
                'total_pages': self._estimate_page_count(cleaned_text),
                'format_analysis': self._analyze_format(cleaned_text)
            }
        
        except Exception as e:
            logger.error(f"Screenplay parsing failed: {e}")
            return {}
    
    def _extract_scenes(self, text: str) -> List[Dict[str, Any]]:
        """Extract scene information from screenplay"""
        scenes = []
        scene_headings = self.patterns['scene_heading'].findall(text)
        
        for i, heading in enumerate(scene_headings):
            scene_info = {
                'scene_number': i + 1,
                'heading': heading.strip(),
                'location_type': 'interior' if heading.startswith('INT.') else 'exterior',
                'estimated_length': 0  # To be calculated based on content
            }
            scenes.append(scene_info)
        
        return scenes
    
    def _extract_characters(self, text: str) -> Dict[str, Dict[str, Any]]:
        """Extract character information and dialogue statistics"""
        characters = defaultdict(lambda: {
            'dialogue_lines': 0,
            'scene_appearances': 0,
            'first_appearance': None,
            'dialogue_sample': []
        })
        
        # Find character names (simplified pattern)
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if line.isupper() and len(line) < 30 and len(line) > 1:
                # Potential character name
                char_name = line.strip()
                if char_name not in ['INT.', 'EXT.', 'FADE IN:', 'FADE OUT:']:
                    characters[char_name]['dialogue_lines'] += 1
                    if not characters[char_name]['first_appearance']:
                        characters[char_name]['first_appearance'] = i
        
        return dict(characters)
    
    def _analyze_dialogue(self, text: str) -> Dict[str, Any]:
        """Analyze dialogue patterns and characteristics"""
        # Extract dialogue lines (simplified)
        dialogue_lines = []
        lines = text.split('\n')
        
        for line in lines:
            if re.match(r'^\s{10,}', line) and line.strip():
                dialogue_lines.append(line.strip())
        
        if not dialogue_lines:
            return {}
        
        # Analyze dialogue
        total_dialogue = len(dialogue_lines)
        avg_line_length = sum(len(line) for line in dialogue_lines) / total_dialogue
        
        return {
            'total_dialogue_lines': total_dialogue,
            'average_line_length': round(avg_line_length, 2),
            'dialogue_density': round(total_dialogue / len(lines) * 100, 2)
        }
    
    def _extract_action_lines(self, text: str) -> List[str]:
        """Extract action and description lines"""
        action_lines = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Simple heuristic for action lines
            if (line and 
                not line.isupper() and 
                not re.match(r'^\s*\([^)]+\)\s*$', line) and
                not re.match(r'^(INT\.|EXT\.|FADE)', line)):
                action_lines.append(line)
        
        return action_lines
    
    def _estimate_page_count(self, text: str) -> float:
        """Estimate screenplay page count based on industry standards"""
        # Rough estimate: 1 page = ~250 words in screenplay format
        word_count = len(self.text_processor.tokenize_text(text, method="word"))
        return round(word_count / 250, 1)
    
    def _analyze_format(self, text: str) -> Dict[str, Any]:
        """Analyze screenplay format compliance"""
        format_score = 0
        issues = []
        
        # Check for scene headings
        if self.patterns['scene_heading'].search(text):
            format_score += 25
        else:
            issues.append("No scene headings found")
        
        # Check for character names
        if self.patterns['character_name'].search(text):
            format_score += 25
        else:
            issues.append("No character names in proper format")
        
        # Check for dialogue
        if self.patterns['dialogue'].search(text):
            format_score += 25
        else:
            issues.append("No dialogue found")
        
        # Check for action lines
        if self.patterns['action'].search(text):
            format_score += 25
        else:
            issues.append("No action lines found")
        
        return {
            'format_score': format_score,
            'format_issues': issues,
            'likely_screenplay': format_score >= 50
        }

# Utility functions for common text processing tasks

def estimate_reading_time(text: str, words_per_minute: int = 200) -> Dict[str, Union[int, str]]:
    """
    Estimate reading time for given text.
    
    Args:
        text: Input text
        words_per_minute: Average reading speed
    
    Returns:
        Dictionary with reading time estimates
    """
    processor = TextProcessor()
    words = processor.tokenize_text(text, method="word")
    total_minutes = len(words) / words_per_minute
    
    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)
    
    if hours > 0:
        time_str = f"{hours}h {minutes}m"
    else:
        time_str = f"{minutes}m"
    
    return {
        'total_minutes': round(total_minutes, 1),
        'hours': hours,
        'minutes': minutes,
        'formatted_time': time_str
    }

def detect_content_type(text: str) -> str:
    """
    Detect the type of content based on text patterns.
    
    Args:
        text: Input text
    
    Returns:
        Detected content type
    """
    # Simple heuristics for content type detection
    if re.search(r'(INT\.|EXT\.)', text, re.IGNORECASE):
        return "screenplay"
    elif re.search(r'(SCENE|ACT|CHAPTER)', text, re.IGNORECASE):
        return "script"
    elif len(text.split('\n')) < 10 and len(text) < 1000:
        return "synopsis"
    else:
        return "general_text"

def extract_text_features(text: str) -> Dict[str, Any]:
    """
    Extract comprehensive features from text for machine learning.
    
    Args:
        text: Input text
    
    Returns:
        Dictionary with extracted features
    """
    processor = TextProcessor()
    
    # Basic statistics
    stats = processor.analyze_text_statistics(text)
    
    # Linguistic features
    sentiment = processor.analyze_sentiment(text)
    readability = processor.calculate_readability_metrics(text)
    keywords = processor.extract_keywords(text)
    entities = processor.extract_named_entities(text)
    
    return {
        'statistics': stats,
        'sentiment': sentiment,
        'readability': readability,
        'top_keywords': keywords[:10],
        'named_entities': entities,
        'content_type': detect_content_type(text),
        'estimated_reading_time': estimate_reading_time(text)
    }

# Export main classes and functions
__all__ = [
    'TextProcessor',
    'ScreenplayParser', 
    'TextProcessingError',
    'estimate_reading_time',
    'detect_content_type',
    'extract_text_features'
]
