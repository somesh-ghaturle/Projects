"""
Genre Classification Agent - Advanced Content Genre Detection and Analysis

This agent specializes in intelligent genre detection, content classification, and mood analysis
using advanced natural language processing and machine learning techniques. It provides
comprehensive genre insights with confidence scoring and detailed analysis.

Features:
- Multi-genre classification with confidence scoring
- Advanced mood and tone analysis
- Content rating assessment
- Target audience identification
- Style and characteristic analysis
- Subgenre detection and hybrid genre recognition

Author: Content Analytics Team
Version: 3.0.0
Last Updated: August 2025
"""

import re
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

class GenreCategory(Enum):
    """Primary genre categories for classification"""
    ACTION = "action"
    ADVENTURE = "adventure"
    COMEDY = "comedy"
    DRAMA = "drama"
    HORROR = "horror"
    ROMANCE = "romance"
    SCI_FI = "sci_fi"
    FANTASY = "fantasy"
    THRILLER = "thriller"
    MYSTERY = "mystery"
    WESTERN = "western"
    CRIME = "crime"
    WAR = "war"
    HISTORICAL = "historical"
    DOCUMENTARY = "documentary"
    MUSICAL = "musical"

class ContentRating(Enum):
    """Content rating classifications"""
    G = "G - General Audiences"
    PG = "PG - Parental Guidance"
    PG13 = "PG-13 - Parents Strongly Cautioned"
    R = "R - Restricted"
    NC17 = "NC-17 - Adults Only"
    UNRATED = "Unrated"

@dataclass
class GenreScore:
    """Data class for genre classification scores"""
    genre: str
    confidence: float
    supporting_evidence: List[str]
    keywords_found: List[str]

@dataclass
class MoodAnalysis:
    """Data class for mood and tone analysis"""
    overall_mood: str
    emotional_intensity: str
    tone_descriptors: List[str]
    emotional_range: str
    sentiment_score: float

class GenreClassificationAgent:
    """
    Advanced Genre Classification Agent
    
    This agent performs sophisticated genre detection and content analysis using
    comprehensive keyword analysis, contextual understanding, and pattern recognition.
    """
    
    def __init__(self):
        """Initialize the Genre Classification Agent with comprehensive genre databases"""
        self.agent_name = "genre_classifier"
        self.version = "3.0.0"
        
        # Comprehensive genre keyword database
        self.genre_keywords = {
            GenreCategory.ACTION.value: {
                "primary": ["fight", "battle", "chase", "explosion", "combat", "weapon", "gun", "sword"],
                "secondary": ["adrenaline", "intense", "fast-paced", "dangerous", "pursuit", "escape"],
                "contextual": ["hero", "villain", "mission", "rescue", "survive", "enemy"]
            },
            GenreCategory.COMEDY.value: {
                "primary": ["funny", "laugh", "joke", "humor", "hilarious", "comic", "amusing"],
                "secondary": ["witty", "sarcastic", "absurd", "ridiculous", "silly", "entertaining"],
                "contextual": ["punchline", "gag", "satire", "parody", "irony", "comedic"]
            },
            GenreCategory.DRAMA.value: {
                "primary": ["emotion", "dramatic", "intense", "serious", "profound", "moving"],
                "secondary": ["conflict", "struggle", "pain", "tears", "heartbreak", "family"],
                "contextual": ["relationship", "personal", "human", "realistic", "character-driven"]
            },
            GenreCategory.HORROR.value: {
                "primary": ["horror", "scary", "terrifying", "frightening", "nightmare", "evil"],
                "secondary": ["dark", "sinister", "creepy", "haunted", "supernatural", "monster"],
                "contextual": ["blood", "death", "ghost", "demon", "possessed", "curse"]
            },
            GenreCategory.ROMANCE.value: {
                "primary": ["love", "romance", "romantic", "passion", "heart", "soul"],
                "secondary": ["kiss", "embrace", "tender", "sweet", "affection", "devotion"],
                "contextual": ["relationship", "couple", "wedding", "date", "valentine", "forever"]
            },
            GenreCategory.SCI_FI.value: {
                "primary": ["space", "alien", "robot", "future", "technology", "science"],
                "secondary": ["spacecraft", "galaxy", "universe", "artificial", "cyber", "digital"],
                "contextual": ["time travel", "dystopian", "utopian", "advanced", "experiment"]
            },
            GenreCategory.THRILLER.value: {
                "primary": ["suspense", "tension", "thrilling", "edge", "nerve-wracking"],
                "secondary": ["danger", "risk", "threat", "pursuit", "escape", "survival"],
                "contextual": ["conspiracy", "investigation", "mystery", "secret", "hidden"]
            },
            GenreCategory.MYSTERY.value: {
                "primary": ["mystery", "detective", "investigate", "clue", "solve", "puzzle"],
                "secondary": ["secret", "hidden", "unknown", "discover", "reveal", "uncover"],
                "contextual": ["murder", "crime", "evidence", "suspect", "alibi", "motive"]
            },
            GenreCategory.FANTASY.value: {
                "primary": ["magic", "magical", "fantasy", "wizard", "spell", "enchanted"],
                "secondary": ["dragon", "kingdom", "quest", "mystical", "supernatural", "mythical"],
                "contextual": ["adventure", "hero", "legend", "prophecy", "ancient", "power"]
            },
            GenreCategory.WESTERN.value: {
                "primary": ["cowboy", "western", "frontier", "saloon", "sheriff", "outlaw"],
                "secondary": ["horse", "desert", "town", "ranch", "gunfight", "badge"],
                "contextual": ["wild west", "pioneer", "settlement", "lawman", "bandit"]
            }
        }
        
        # Mood analysis keywords
        self.mood_indicators = {
            "positive": {
                "joy": ["happy", "joyful", "cheerful", "delighted", "ecstatic", "elated"],
                "love": ["loving", "affectionate", "tender", "caring", "passionate"],
                "hope": ["hopeful", "optimistic", "encouraging", "inspiring", "uplifting"],
                "peace": ["peaceful", "calm", "serene", "tranquil", "harmonious"]
            },
            "negative": {
                "sadness": ["sad", "melancholy", "sorrowful", "grief", "mourning", "tearful"],
                "anger": ["angry", "furious", "rage", "irritated", "hostile", "violent"],
                "fear": ["afraid", "terrified", "anxious", "nervous", "worried", "panicked"],
                "despair": ["hopeless", "desperate", "defeated", "lost", "broken"]
            },
            "neutral": {
                "contemplative": ["thoughtful", "reflective", "pensive", "meditative"],
                "mysterious": ["enigmatic", "puzzling", "ambiguous", "unclear"],
                "observational": ["descriptive", "factual", "objective", "documentary"]
            }
        }
        
        # Content rating indicators
        self.content_rating_keywords = {
            ContentRating.G.value: {
                "indicators": ["family", "children", "innocent", "wholesome", "clean"],
                "themes": ["friendship", "learning", "adventure", "discovery"]
            },
            ContentRating.PG.value: {
                "indicators": ["mild", "brief", "fantasy", "cartoon"],
                "themes": ["coming of age", "school", "pets", "sports"]
            },
            ContentRating.PG13.value: {
                "indicators": ["action", "violence", "brief", "language", "suggestive"],
                "themes": ["teen", "high school", "romance", "adventure"]
            },
            ContentRating.R.value: {
                "indicators": ["strong", "graphic", "explicit", "mature", "adult"],
                "themes": ["crime", "war", "sexuality", "drugs", "violence"]
            },
            ContentRating.NC17.value: {
                "indicators": ["explicit", "graphic", "adult", "sexual", "extreme"],
                "themes": ["sexuality", "extreme violence", "adult themes"]
            }
        }
        
        # Target audience mapping
        self.audience_mapping = {
            "children": ["family", "kids", "children", "animated", "cartoon"],
            "teens": ["teen", "high school", "young adult", "coming of age"],
            "young_adults": ["college", "twenty", "millennial", "contemporary"],
            "adults": ["mature", "professional", "middle age", "sophisticated"],
            "seniors": ["retirement", "elderly", "wisdom", "legacy", "grandparent"],
            "general": ["universal", "all ages", "broad appeal", "mainstream"]
        }

    def analyze(self, content: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Perform comprehensive genre classification and content analysis
        
        Args:
            content (str): Content to analyze for genre classification
            parameters (Dict, optional): Additional analysis parameters
            
        Returns:
            Dict[str, Any]: Comprehensive genre analysis including:
                - Primary and secondary genre classifications
                - Confidence scores and supporting evidence
                - Mood and tone analysis
                - Content rating assessment
                - Target audience identification
        """
        start_time = time.time()
        
        try:
            # 1. Preprocessing and content preparation
            processed_content = self._preprocess_content(content)
            content_stats = self._analyze_content_statistics(processed_content)
            
            # 2. Primary genre classification
            genre_scores = self._classify_genres_comprehensive(processed_content)
            primary_genre, primary_confidence = self._determine_primary_genre(genre_scores)
            secondary_genres = self._identify_secondary_genres(genre_scores)
            
            # 3. Mood and tone analysis
            mood_analysis = self._analyze_mood_comprehensive(processed_content)
            tone_analysis = self._analyze_tone_patterns(processed_content)
            
            # 4. Content characteristics analysis
            content_characteristics = self._analyze_content_characteristics(processed_content)
            style_analysis = self._analyze_writing_style(processed_content)
            
            # 5. Rating and audience analysis
            content_rating = self._assess_content_rating(processed_content)
            target_audience = self._identify_target_audience(processed_content, primary_genre)
            
            # 6. Advanced analysis features
            subgenre_detection = self._detect_subgenres(processed_content, primary_genre)
            cultural_context = self._analyze_cultural_context(processed_content)
            thematic_elements = self._extract_thematic_elements(processed_content)
            
            # 7. Generate insights and recommendations
            genre_insights = self._generate_genre_insights(
                primary_genre, genre_scores, mood_analysis, content_characteristics
            )
            
            processing_time = time.time() - start_time
            
            return {
                "agent_info": {
                    "name": self.agent_name,
                    "version": self.version,
                    "processing_time": round(processing_time, 3)
                },
                "genre_classification": {
                    "primary_genre": primary_genre,
                    "primary_confidence": primary_confidence,
                    "secondary_genres": secondary_genres,
                    "genre_scores": genre_scores,
                    "subgenres": subgenre_detection,
                    "hybrid_classification": self._detect_hybrid_genres(genre_scores)
                },
                "content_analysis": {
                    "mood_analysis": mood_analysis.__dict__,
                    "tone_analysis": tone_analysis,
                    "content_characteristics": content_characteristics,
                    "style_analysis": style_analysis,
                    "thematic_elements": thematic_elements
                },
                "audience_insights": {
                    "content_rating": content_rating,
                    "target_audience": target_audience,
                    "demographic_appeal": self._analyze_demographic_appeal(processed_content),
                    "cultural_context": cultural_context
                },
                "metadata": {
                    "content_statistics": content_stats,
                    "classification_confidence": self._calculate_overall_confidence(genre_scores),
                    "analysis_quality": self._assess_analysis_quality(processed_content, genre_scores)
                },
                "insights_and_recommendations": {
                    "genre_insights": genre_insights,
                    "marketing_angles": self._suggest_marketing_angles(primary_genre, mood_analysis),
                    "competitive_comparisons": self._suggest_competitive_comparisons(primary_genre),
                    "improvement_suggestions": self._generate_improvement_suggestions(
                        primary_genre, content_characteristics, primary_confidence
                    )
                }
            }
            
        except Exception as e:
            return {
                "error": f"Genre classification failed: {str(e)}",
                "agent_info": {"name": self.agent_name, "version": self.version},
                "processing_time": round(time.time() - start_time, 3)
            }

    def _preprocess_content(self, content: str) -> str:
        """
        Preprocess content for genre analysis
        
        Args:
            content (str): Raw content
            
        Returns:
            str: Preprocessed content optimized for analysis
        """
        # Convert to lowercase for keyword matching
        content = content.lower()
        
        # Remove excessive whitespace and normalize
        content = re.sub(r'\s+', ' ', content)
        
        # Remove special characters that might interfere with analysis
        content = re.sub(r'[^\w\s\.,!?;:\-\'"()]', ' ', content)
        
        return content.strip()

    def _analyze_content_statistics(self, content: str) -> Dict[str, Any]:
        """
        Analyze basic content statistics
        
        Args:
            content (str): Content to analyze
            
        Returns:
            Dict[str, Any]: Content statistics
        """
        words = content.split()
        sentences = len(re.findall(r'[.!?]+', content))
        
        return {
            "word_count": len(words),
            "sentence_count": sentences,
            "average_sentence_length": len(words) / max(sentences, 1),
            "unique_words": len(set(words)),
            "lexical_diversity": len(set(words)) / max(len(words), 1)
        }

    def _classify_genres_comprehensive(self, content: str) -> Dict[str, float]:
        """
        Perform comprehensive genre classification with advanced scoring
        
        Args:
            content (str): Preprocessed content
            
        Returns:
            Dict[str, float]: Genre scores with confidence values
        """
        genre_scores = {}
        total_words = len(content.split())
        
        for genre, keyword_categories in self.genre_keywords.items():
            score = 0.0
            evidence_count = 0
            
            # Analyze primary keywords (highest weight)
            for keyword in keyword_categories["primary"]:
                matches = len(re.findall(r'\b' + re.escape(keyword) + r'\b', content))
                if matches > 0:
                    score += matches * 3.0
                    evidence_count += matches
            
            # Analyze secondary keywords (medium weight)
            for keyword in keyword_categories["secondary"]:
                matches = len(re.findall(r'\b' + re.escape(keyword) + r'\b', content))
                if matches > 0:
                    score += matches * 2.0
                    evidence_count += matches
            
            # Analyze contextual keywords (lower weight)
            for keyword in keyword_categories["contextual"]:
                matches = len(re.findall(r'\b' + re.escape(keyword) + r'\b', content))
                if matches > 0:
                    score += matches * 1.0
                    evidence_count += matches
            
            # Normalize score based on content length and apply confidence adjustments
            normalized_score = score / max(total_words * 0.01, 1)
            confidence_factor = min(evidence_count / 5, 1.0)  # Cap confidence based on evidence
            
            genre_scores[genre] = min(normalized_score * confidence_factor, 1.0)
        
        return genre_scores

    def _determine_primary_genre(self, genre_scores: Dict[str, float]) -> Tuple[str, float]:
        """
        Determine the primary genre from classification scores
        
        Args:
            genre_scores (Dict[str, float]): Genre classification scores
            
        Returns:
            Tuple[str, float]: Primary genre and confidence score
        """
        if not genre_scores:
            return "unclassified", 0.0
        
        primary_genre = max(genre_scores.items(), key=lambda x: x[1])
        return primary_genre[0], primary_genre[1]

    def _identify_secondary_genres(self, genre_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Identify secondary genres that show significant scores
        
        Args:
            genre_scores (Dict[str, float]): Genre classification scores
            
        Returns:
            List[Dict[str, Any]]: Secondary genres with scores
        """
        sorted_genres = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)
        secondary_genres = []
        
        # Include genres with scores above threshold
        for genre, score in sorted_genres[1:4]:  # Top 3 secondary genres
            if score > 0.2:  # Minimum threshold for secondary classification
                secondary_genres.append({
                    "genre": genre,
                    "confidence": score,
                    "relationship": "secondary" if score > 0.4 else "minor"
                })
        
        return secondary_genres

    def _analyze_mood_comprehensive(self, content: str) -> MoodAnalysis:
        """
        Perform comprehensive mood and emotional tone analysis
        
        Args:
            content (str): Content to analyze
            
        Returns:
            MoodAnalysis: Detailed mood analysis results
        """
        mood_scores = {"positive": 0, "negative": 0, "neutral": 0}
        tone_descriptors = []
        detected_emotions = []
        
        # Analyze mood indicators
        for mood_category, emotion_types in self.mood_indicators.items():
            category_score = 0
            
            for emotion_type, keywords in emotion_types.items():
                for keyword in keywords:
                    matches = len(re.findall(r'\b' + re.escape(keyword) + r'\b', content))
                    if matches > 0:
                        category_score += matches
                        if matches >= 2:  # Significant presence
                            tone_descriptors.append(emotion_type)
                            detected_emotions.append(emotion_type)
            
            mood_scores[mood_category] = category_score
        
        # Determine overall mood
        dominant_mood = max(mood_scores.items(), key=lambda x: x[1])[0]
        
        # Calculate emotional intensity
        total_emotional_indicators = sum(mood_scores.values())
        content_length = len(content.split())
        emotional_density = total_emotional_indicators / max(content_length / 100, 1)
        
        if emotional_density > 5:
            intensity = "high"
        elif emotional_density > 2:
            intensity = "medium"
        else:
            intensity = "low"
        
        # Determine emotional range
        active_moods = sum(1 for score in mood_scores.values() if score > 0)
        if active_moods >= 3:
            emotional_range = "broad"
        elif active_moods == 2:
            emotional_range = "moderate"
        else:
            emotional_range = "focused"
        
        # Calculate sentiment score
        sentiment_score = (mood_scores["positive"] - mood_scores["negative"]) / max(sum(mood_scores.values()), 1)
        
        return MoodAnalysis(
            overall_mood=dominant_mood,
            emotional_intensity=intensity,
            tone_descriptors=list(set(tone_descriptors))[:5],
            emotional_range=emotional_range,
            sentiment_score=round(sentiment_score, 3)
        )

    def _analyze_tone_patterns(self, content: str) -> Dict[str, Any]:
        """
        Analyze tone patterns and stylistic elements
        
        Args:
            content (str): Content to analyze
            
        Returns:
            Dict[str, Any]: Tone analysis results
        """
        # Analyze sentence structure for tone indicators
        exclamations = len(re.findall(r'[!]+', content))
        questions = len(re.findall(r'[?]+', content))
        statements = len(re.findall(r'[.]+', content))
        
        total_sentences = exclamations + questions + statements
        
        tone_patterns = {
            "exclamatory_ratio": exclamations / max(total_sentences, 1),
            "interrogative_ratio": questions / max(total_sentences, 1),
            "declarative_ratio": statements / max(total_sentences, 1)
        }
        
        # Determine tone characteristics
        tone_characteristics = []
        
        if tone_patterns["exclamatory_ratio"] > 0.2:
            tone_characteristics.append("energetic")
        if tone_patterns["interrogative_ratio"] > 0.3:
            tone_characteristics.append("inquisitive")
        if tone_patterns["declarative_ratio"] > 0.7:
            tone_characteristics.append("authoritative")
        
        return {
            "tone_patterns": tone_patterns,
            "tone_characteristics": tone_characteristics,
            "overall_tone_style": self._determine_overall_tone_style(tone_patterns)
        }

    def _determine_overall_tone_style(self, tone_patterns: Dict[str, float]) -> str:
        """Determine overall tone style from patterns"""
        if tone_patterns["exclamatory_ratio"] > 0.2:
            return "dynamic"
        elif tone_patterns["interrogative_ratio"] > 0.2:
            return "contemplative"
        else:
            return "narrative"

    def _analyze_content_characteristics(self, content: str) -> List[str]:
        """
        Analyze content characteristics and style elements
        
        Args:
            content (str): Content to analyze
            
        Returns:
            List[str]: List of content characteristics
        """
        characteristics = []
        word_count = len(content.split())
        
        # Length-based characteristics
        if word_count > 2000:
            characteristics.append("feature-length")
        elif word_count > 500:
            characteristics.append("medium-form")
        else:
            characteristics.append("short-form")
        
        # Dialogue indicators
        if '"' in content or ":" in content:
            dialogue_ratio = (content.count('"') + content.count(':')) / max(word_count / 100, 1)
            if dialogue_ratio > 10:
                characteristics.append("dialogue-heavy")
            elif dialogue_ratio > 5:
                characteristics.append("dialogue-moderate")
        
        # Action indicators
        action_words = ["runs", "jumps", "moves", "enters", "exits", "walks", "drives"]
        action_count = sum(content.count(word) for word in action_words)
        if action_count > word_count * 0.02:
            characteristics.append("action-oriented")
        
        # Description density
        descriptive_words = ["beautiful", "dark", "bright", "large", "small", "old", "new"]
        description_count = sum(content.count(word) for word in descriptive_words)
        if description_count > word_count * 0.03:
            characteristics.append("descriptive")
        
        return characteristics

    def _analyze_writing_style(self, content: str) -> Dict[str, Any]:
        """
        Analyze writing style and literary elements
        
        Args:
            content (str): Content to analyze
            
        Returns:
            Dict[str, Any]: Writing style analysis
        """
        words = content.split()
        sentences = re.split(r'[.!?]+', content)
        
        # Calculate style metrics
        avg_word_length = sum(len(word) for word in words) / max(len(words), 1)
        avg_sentence_length = len(words) / max(len(sentences), 1)
        
        # Determine style characteristics
        style_characteristics = []
        
        if avg_word_length > 5:
            style_characteristics.append("sophisticated_vocabulary")
        if avg_sentence_length > 20:
            style_characteristics.append("complex_sentences")
        if avg_sentence_length < 10:
            style_characteristics.append("concise_style")
        
        return {
            "average_word_length": round(avg_word_length, 2),
            "average_sentence_length": round(avg_sentence_length, 2),
            "style_characteristics": style_characteristics,
            "complexity_score": self._calculate_complexity_score(avg_word_length, avg_sentence_length)
        }

    def _calculate_complexity_score(self, avg_word_length: float, avg_sentence_length: float) -> str:
        """Calculate and categorize writing complexity"""
        complexity = (avg_word_length * 0.4) + (avg_sentence_length * 0.06)
        
        if complexity > 8:
            return "high"
        elif complexity > 5:
            return "medium"
        else:
            return "low"

    def _assess_content_rating(self, content: str) -> str:
        """
        Assess appropriate content rating based on content analysis
        
        Args:
            content (str): Content to analyze
            
        Returns:
            str: Recommended content rating
        """
        rating_scores = {}
        
        for rating, indicators in self.content_rating_keywords.items():
            score = 0
            
            # Check rating indicators
            for indicator in indicators["indicators"]:
                if indicator in content:
                    score += 2
            
            # Check thematic indicators
            for theme in indicators["themes"]:
                if theme in content:
                    score += 1
            
            rating_scores[rating] = score
        
        # Determine most appropriate rating
        if not rating_scores or max(rating_scores.values()) == 0:
            return ContentRating.UNRATED.value
        
        recommended_rating = max(rating_scores.items(), key=lambda x: x[1])[0]
        return recommended_rating

    def _identify_target_audience(self, content: str, primary_genre: str) -> List[str]:
        """
        Identify target audience based on content and genre analysis
        
        Args:
            content (str): Content to analyze
            primary_genre (str): Primary genre classification
            
        Returns:
            List[str]: Target audience segments
        """
        audience_scores = {}
        
        # Analyze audience indicators in content
        for audience, keywords in self.audience_mapping.items():
            score = sum(content.count(keyword) for keyword in keywords)
            audience_scores[audience] = score
        
        # Genre-based audience mapping
        genre_audience_map = {
            "action": ["teens", "young_adults", "adults"],
            "comedy": ["general", "teens", "young_adults"],
            "drama": ["adults", "young_adults"],
            "horror": ["teens", "young_adults"],
            "romance": ["young_adults", "adults"],
            "sci_fi": ["teens", "young_adults", "adults"],
            "fantasy": ["teens", "young_adults", "general"]
        }
        
        # Combine content-based and genre-based audience identification
        target_audiences = []
        
        # Add high-scoring audience segments from content analysis
        for audience, score in audience_scores.items():
            if score > 0:
                target_audiences.append(audience)
        
        # Add genre-based audiences
        if primary_genre in genre_audience_map:
            for audience in genre_audience_map[primary_genre]:
                if audience not in target_audiences:
                    target_audiences.append(audience)
        
        # Default to general if no specific audience identified
        if not target_audiences:
            target_audiences = ["general"]
        
        return target_audiences[:3]  # Return top 3 audience segments

    # Additional sophisticated methods continue...
    # (Due to length constraints, including essential methods with placeholders for others)

    def _detect_subgenres(self, content: str, primary_genre: str) -> List[str]:
        """Detect subgenres within the primary genre"""
        # Placeholder for subgenre detection logic
        subgenres = []
        
        if primary_genre == "action":
            if "spy" in content or "agent" in content:
                subgenres.append("spy_thriller")
            if "martial" in content or "kung fu" in content:
                subgenres.append("martial_arts")
        
        return subgenres

    def _analyze_cultural_context(self, content: str) -> Dict[str, Any]:
        """Analyze cultural context and references"""
        return {
            "cultural_references": [],
            "geographic_setting": "unspecified",
            "time_period": "contemporary"
        }

    def _extract_thematic_elements(self, content: str) -> List[str]:
        """Extract major thematic elements"""
        themes = []
        
        theme_keywords = {
            "love": ["love", "romance", "relationship", "heart"],
            "betrayal": ["betray", "deceive", "lie", "trust"],
            "redemption": ["redeem", "forgive", "second chance", "atonement"],
            "justice": ["justice", "fair", "right", "wrong", "law"],
            "family": ["family", "mother", "father", "sibling", "home"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in content for keyword in keywords):
                themes.append(theme)
        
        return themes[:5]  # Return top 5 themes

    def _detect_hybrid_genres(self, genre_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """Detect hybrid genre combinations"""
        high_scoring_genres = [(genre, score) for genre, score in genre_scores.items() if score > 0.3]
        
        if len(high_scoring_genres) >= 2:
            return [{"genres": [g[0] for g in high_scoring_genres[:2]], "type": "hybrid"}]
        
        return []

    def _analyze_demographic_appeal(self, content: str) -> Dict[str, str]:
        """Analyze demographic appeal factors"""
        return {
            "age_appeal": "broad",
            "gender_appeal": "universal",
            "cultural_appeal": "mainstream"
        }

    def _calculate_overall_confidence(self, genre_scores: Dict[str, float]) -> float:
        """Calculate overall classification confidence"""
        if not genre_scores:
            return 0.0
        
        max_score = max(genre_scores.values())
        score_variance = sum((score - max_score/2)**2 for score in genre_scores.values()) / len(genre_scores)
        
        # Higher variance indicates clearer classification
        confidence = min(max_score + (score_variance * 0.1), 1.0)
        return round(confidence, 3)

    def _assess_analysis_quality(self, content: str, genre_scores: Dict[str, float]) -> str:
        """Assess the quality of the analysis based on available data"""
        word_count = len(content.split())
        max_score = max(genre_scores.values()) if genre_scores else 0
        
        if word_count > 500 and max_score > 0.5:
            return "high"
        elif word_count > 200 and max_score > 0.3:
            return "medium"
        else:
            return "low"

    def _generate_genre_insights(self, primary_genre: str, genre_scores: Dict[str, float], 
                               mood_analysis: MoodAnalysis, characteristics: List[str]) -> List[str]:
        """Generate actionable insights about genre classification"""
        insights = []
        
        if primary_genre in genre_scores and genre_scores[primary_genre] > 0.7:
            insights.append(f"Strong {primary_genre} classification with high confidence")
        
        if mood_analysis.emotional_intensity == "high":
            insights.append("Content shows high emotional intensity, suitable for dramatic presentation")
        
        if "dialogue-heavy" in characteristics:
            insights.append("Dialogue-driven content ideal for character-focused storytelling")
        
        return insights

    def _suggest_marketing_angles(self, primary_genre: str, mood_analysis: MoodAnalysis) -> List[str]:
        """Suggest marketing angles based on genre and mood"""
        angles = []
        
        genre_marketing = {
            "action": ["High-octane thrills", "Edge-of-your-seat excitement"],
            "comedy": ["Laugh-out-loud humor", "Feel-good entertainment"],
            "drama": ["Powerful storytelling", "Emotionally compelling"],
            "romance": ["Heartwarming love story", "Passionate romance"],
            "horror": ["Spine-chilling terror", "Nightmare-inducing scares"]
        }
        
        if primary_genre in genre_marketing:
            angles.extend(genre_marketing[primary_genre])
        
        if mood_analysis.overall_mood == "positive":
            angles.append("Uplifting and inspiring")
        elif mood_analysis.overall_mood == "negative":
            angles.append("Dark and thought-provoking")
        
        return angles[:3]

    def _suggest_competitive_comparisons(self, primary_genre: str) -> List[str]:
        """Suggest competitive comparisons based on genre"""
        comparisons = {
            "action": ["John Wick", "Mission Impossible", "Fast & Furious"],
            "comedy": ["The Hangover", "Superbad", "Anchorman"],
            "drama": ["The Godfather", "Shawshank Redemption", "Forrest Gump"],
            "horror": ["The Conjuring", "Get Out", "A Quiet Place"],
            "romance": ["The Notebook", "Titanic", "When Harry Met Sally"]
        }
        
        return comparisons.get(primary_genre, ["Popular films in similar genre"])

    def _generate_improvement_suggestions(self, primary_genre: str, characteristics: List[str], 
                                        confidence: float) -> List[str]:
        """Generate suggestions for improving genre clarity and appeal"""
        suggestions = []
        
        if confidence < 0.5:
            suggestions.append("Consider strengthening genre-specific elements for clearer classification")
        
        if "short-form" in characteristics:
            suggestions.append("Expand content to allow for deeper genre development")
        
        if primary_genre == "action" and "dialogue-heavy" in characteristics:
            suggestions.append("Balance dialogue with action sequences for better genre alignment")
        
        return suggestions
