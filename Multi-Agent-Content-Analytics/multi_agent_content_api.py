"""
Enhanced FastAPI application with advanced AI agents for content analysis
Features: Sophisticated NLP, sentiment analysis, character development tracking,
plot structure analysis, and comprehensive marketing intelligence
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import sys
import os
import re
import json
from datetime import datetime
import logging
from collections import Counter
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced FastAPI app with advanced AI agents
app = FastAPI(
    title="Multi-Agent Content Analytics Platform",
    description="Advanced AI system with sophisticated agents for movie script analysis, genre classification, and marketing intelligence",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware to allow web browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

class HealthResponse(BaseModel):
    status: str
    message: str
    version: str

class ContentAnalysisRequest(BaseModel):
    content: str
    analysis_type: str = "basic"
    agent: Optional[str] = None  # Specify which agent to use

class AgentRequest(BaseModel):
    content: str
    agent_name: str
    parameters: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    agent: str
    content: str
    results: Dict[str, Any]
    timestamp: str
    processing_time: float

class ContentAnalysisRequest(BaseModel):
    content: str
    analysis_type: str = "basic"
    agent: Optional[str] = None  # Specify which agent to use

class ContentAnalysisResponse(BaseModel):
    content: str
    analysis_type: str
    results: Dict[str, Any]

class AgentRequest(BaseModel):
    content: str
    agent_name: str
    parameters: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    agent: str
    content: str
    results: Dict[str, Any]
    timestamp: str
    processing_time: float

# ============================================================================
# FUNCTIONAL AI AGENTS - These actually process your content!
# ============================================================================

class ScriptSummarizerAgent:
    """Advanced agent that analyzes movie scripts with sophisticated NLP and structure analysis"""
    
    def analyze(self, content: str, parameters: Dict = None) -> Dict[str, Any]:
        import time
        start_time = time.time()
        
        # Enhanced script analysis
        scenes = self._extract_scenes_detailed(content)
        characters = self._extract_characters_advanced(content)
        dialogue_analysis = self._analyze_dialogue_comprehensive(content)
        plot_structure = self._analyze_plot_structure(content)
        character_development = self._analyze_character_development(content)
        
        # Generate sophisticated summary
        summary = self._generate_detailed_summary(content, scenes, characters, plot_structure)
        
        # Extract themes with confidence scores
        themes_analysis = self._extract_themes_advanced(content)
        
        # Advanced genre classification
        genre_analysis = self._classify_genre_advanced(content)
        
        # Emotional arc analysis
        emotional_arc = self._analyze_emotional_arc(content)
        
        # Pacing analysis
        pacing_analysis = self._analyze_pacing(content)
        
        processing_time = time.time() - start_time
        
        return {
            "summary": summary,
            "characters": characters,
            "character_development": character_development,
            "scenes": scenes,
            "plot_structure": plot_structure,
            "dialogue_analysis": dialogue_analysis,
            "themes_analysis": themes_analysis,
            "genre_analysis": genre_analysis,
            "emotional_arc": emotional_arc,
            "pacing_analysis": pacing_analysis,
            "word_count": len(content.split()),
            "estimated_runtime": self._calculate_runtime_advanced(content),
            "script_quality_score": self._calculate_quality_score(content, characters, scenes),
            "processing_time": round(processing_time, 3)
        }
    
    def _extract_scenes_detailed(self, content: str) -> Dict[str, Any]:
        """Extract scenes with detailed location and time information"""
        scene_pattern = r'((?:INT\.|EXT\.)\s*[^\n]*)'
        scenes = re.findall(scene_pattern, content, re.IGNORECASE)
        
        scene_details = []
        for scene in scenes[:15]:  # Analyze up to 15 scenes
            location_type = "INTERIOR" if scene.upper().startswith("INT.") else "EXTERIOR"
            location_name = re.sub(r'^(INT\.|EXT\.)\s*', '', scene, flags=re.IGNORECASE).strip()
            
            # Extract time indicators
            time_indicators = ["DAY", "NIGHT", "MORNING", "EVENING", "DAWN", "DUSK"]
            time_of_day = "UNSPECIFIED"
            for time_ind in time_indicators:
                if time_ind in scene.upper():
                    time_of_day = time_ind
                    break
            
            scene_details.append({
                "heading": scene.strip(),
                "location_type": location_type,
                "location_name": location_name,
                "time_of_day": time_of_day
            })
        
        # Scene statistics
        total_int = sum(1 for s in scene_details if s["location_type"] == "INTERIOR")
        total_ext = sum(1 for s in scene_details if s["location_type"] == "EXTERIOR")
        
        return {
            "scene_list": scene_details,
            "total_scenes": len(scene_details),
            "interior_scenes": total_int,
            "exterior_scenes": total_ext,
            "scene_variety": len(set(s["location_name"] for s in scene_details)),
            "time_distribution": Counter(s["time_of_day"] for s in scene_details)
        }
    
    def _extract_characters_advanced(self, content: str) -> Dict[str, Any]:
        """Advanced character extraction with dialogue analysis"""
        # Enhanced character pattern matching
        char_pattern = r'^([A-Z][A-Z\s\(\)\.]{2,30})(?:\s*\([^)]*\))?\s*$'
        lines = content.split('\n')
        character_data = {}
        
        current_character = None
        for i, line in enumerate(lines):
            line = line.strip()
            # Character name detection
            char_match = re.match(char_pattern, line)
            if char_match:
                char_name = char_match.group(1).strip()
                if len(char_name) > 2 and len(char_name) < 30:
                    current_character = char_name
                    if char_name not in character_data:
                        character_data[char_name] = {
                            "dialogue_lines": 0,
                            "first_appearance": i,
                            "scenes_present": 0,
                            "emotional_range": [],
                            "key_phrases": []
                        }
            
            # Dialogue tracking
            elif current_character and line and not line.isupper():
                character_data[current_character]["dialogue_lines"] += 1
                
                # Simple emotion detection in dialogue
                emotions = self._detect_emotions_in_text(line)
                character_data[current_character]["emotional_range"].extend(emotions)
                
                # Extract key phrases (questions, exclamations)
                if line.endswith(('!', '?')):
                    character_data[current_character]["key_phrases"].append(line[:50])
        
        # Character analysis
        main_characters = []
        for char, data in sorted(character_data.items(), 
                               key=lambda x: x[1]["dialogue_lines"], reverse=True)[:8]:
            main_characters.append({
                "name": char,
                "dialogue_lines": data["dialogue_lines"],
                "emotional_range": list(set(data["emotional_range"])),
                "character_importance": self._calculate_character_importance(data),
                "key_phrases": data["key_phrases"][:3]
            })
        
        return {
            "main_characters": main_characters,
            "total_characters": len(character_data),
            "protagonist_candidate": main_characters[0]["name"] if main_characters else "Unknown",
            "ensemble_cast": len(main_characters) > 4
        }
    
    def _analyze_dialogue_comprehensive(self, content: str) -> Dict[str, Any]:
        """Comprehensive dialogue analysis"""
        lines = content.split('\n')
        total_lines = len([l for l in lines if l.strip()])
        
        dialogue_lines = []
        action_lines = []
        scene_descriptions = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.isupper() and any(scene_word in line for scene_word in ['INT.', 'EXT.', 'FADE']):
                scene_descriptions.append(line)
            elif re.match(r'^[A-Z][A-Z\s]+$', line) and len(line) < 30:
                continue  # Character names
            elif line and not line.isupper():
                dialogue_lines.append(line)
            else:
                action_lines.append(line)
        
        # Dialogue complexity analysis
        avg_dialogue_length = sum(len(line.split()) for line in dialogue_lines) / max(len(dialogue_lines), 1)
        
        # Conversation flow analysis
        question_count = sum(1 for line in dialogue_lines if '?' in line)
        exclamation_count = sum(1 for line in dialogue_lines if '!' in line)
        
        return {
            "dialogue_ratio": round(len(dialogue_lines) / max(total_lines, 1), 3),
            "action_ratio": round(len(action_lines) / max(total_lines, 1), 3),
            "average_dialogue_length": round(avg_dialogue_length, 2),
            "conversation_dynamics": {
                "questions": question_count,
                "exclamations": exclamation_count,
                "statements": len(dialogue_lines) - question_count - exclamation_count
            },
            "dialogue_complexity": "High" if avg_dialogue_length > 15 else "Medium" if avg_dialogue_length > 8 else "Simple"
        }
    
    def _analyze_plot_structure(self, content: str) -> Dict[str, Any]:
        """Analyze three-act structure and plot points"""
        word_count = len(content.split())
        scenes = re.findall(r'(INT\.|EXT\.)[^\n]*', content, re.IGNORECASE)
        
        # Estimate act breaks
        act1_end = int(word_count * 0.25)
        act2_end = int(word_count * 0.75)
        
        # Plot point detection
        plot_keywords = {
            "inciting_incident": ["discovers", "learns", "realizes", "finds", "meets"],
            "climax": ["confronts", "faces", "battles", "decides", "chooses"],
            "resolution": ["returns", "ends", "concludes", "finally", "resolves"]
        }
        
        structure_analysis = {
            "estimated_structure": "Three-Act" if len(scenes) > 5 else "Short Form",
            "act_breaks": {
                "act1_end": f"~{act1_end} words",
                "act2_end": f"~{act2_end} words"
            },
            "scene_distribution": {
                "setup_scenes": len(scenes[:len(scenes)//3]) if scenes else 0,
                "development_scenes": len(scenes[len(scenes)//3:2*len(scenes)//3]) if scenes else 0,
                "resolution_scenes": len(scenes[2*len(scenes)//3:]) if scenes else 0
            },
            "pacing_rhythm": "Fast" if len(scenes) > word_count/500 else "Standard"
        }
        
        return structure_analysis
    
    def _analyze_character_development(self, content: str) -> Dict[str, Any]:
        """Analyze character arcs and development"""
        # Character growth indicators
        growth_keywords = ["learns", "realizes", "changes", "becomes", "transforms", "grows"]
        relationship_keywords = ["loves", "hates", "befriends", "betrays", "trusts", "forgives"]
        
        content_lower = content.lower()
        growth_indicators = sum(content_lower.count(word) for word in growth_keywords)
        relationship_changes = sum(content_lower.count(word) for word in relationship_keywords)
        
        return {
            "character_growth_indicators": growth_indicators,
            "relationship_dynamics": relationship_changes,
            "development_complexity": "High" if growth_indicators > 3 else "Medium" if growth_indicators > 1 else "Low",
            "interpersonal_focus": relationship_changes > growth_indicators
        }
    
    def _extract_themes_advanced(self, content: str) -> Dict[str, Any]:
        """Advanced theme extraction with confidence scoring"""
        content_lower = content.lower()
        
        theme_keywords = {
            "love_romance": ["love", "romance", "heart", "kiss", "relationship", "wedding", "marriage"],
            "action_adventure": ["fight", "chase", "explosion", "battle", "weapon", "adventure", "quest"],
            "science_fiction": ["space", "alien", "robot", "future", "technology", "spaceship", "mars", "galaxy"],
            "horror_thriller": ["dark", "scary", "fear", "ghost", "monster", "terror", "nightmare", "danger"],
            "comedy_humor": ["funny", "laugh", "joke", "humor", "silly", "comedy", "hilarious", "amusing"],
            "drama_emotion": ["emotion", "family", "conflict", "struggle", "pain", "tears", "heart", "loss"],
            "mystery_crime": ["secret", "mystery", "detective", "clue", "investigate", "solve", "murder", "crime"],
            "fantasy_magic": ["magic", "wizard", "dragon", "kingdom", "spell", "enchanted", "mystical"],
            "coming_of_age": ["grows", "learns", "matures", "discovers", "realizes", "becomes", "youth"],
            "redemption": ["forgive", "redeem", "second chance", "atone", "mercy", "salvation"]
        }
        
        theme_scores = {}
        total_words = len(content.split())
        
        for theme, keywords in theme_keywords.items():
            matches = sum(content_lower.count(keyword) for keyword in keywords)
            confidence = min(matches / max(total_words * 0.005, 1), 1.0)
            theme_scores[theme] = round(confidence, 3)
        
        # Get top themes
        top_themes = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "primary_themes": [{"theme": theme.replace("_", " ").title(), "confidence": score} 
                             for theme, score in top_themes if score > 0.1],
            "theme_distribution": theme_scores,
            "thematic_complexity": len([s for s in theme_scores.values() if s > 0.1])
        }
    
    def _detect_emotions_in_text(self, text: str) -> List[str]:
        """Simple emotion detection in dialogue"""
        emotions = []
        text_lower = text.lower()
        
        emotion_indicators = {
            "anger": ["angry", "mad", "furious", "rage", "hate"],
            "joy": ["happy", "joy", "excited", "love", "wonderful"],
            "sadness": ["sad", "cry", "tears", "mourn", "grief"],
            "fear": ["afraid", "scared", "terrified", "worried", "anxious"],
            "surprise": ["wow", "amazing", "incredible", "unbelievable"]
        }
        
        for emotion, keywords in emotion_indicators.items():
            if any(keyword in text_lower for keyword in keywords):
                emotions.append(emotion)
        
        return emotions
    
    def _calculate_character_importance(self, char_data: Dict) -> str:
        """Calculate character importance based on dialogue and presence"""
        dialogue_lines = char_data["dialogue_lines"]
        if dialogue_lines > 20:
            return "Major"
        elif dialogue_lines > 10:
            return "Supporting"
        elif dialogue_lines > 5:
            return "Minor"
        else:
            return "Background"
    
    def _analyze_emotional_arc(self, content: str) -> Dict[str, Any]:
        """Analyze the emotional journey of the story"""
        content_lower = content.lower()
        
        positive_emotions = ["happy", "joy", "love", "hope", "triumph", "success", "victory"]
        negative_emotions = ["sad", "angry", "fear", "despair", "loss", "defeat", "tragedy"]
        neutral_emotions = ["calm", "peaceful", "ordinary", "normal", "routine"]
        
        positive_count = sum(content_lower.count(word) for word in positive_emotions)
        negative_count = sum(content_lower.count(word) for word in negative_emotions)
        neutral_count = sum(content_lower.count(word) for word in neutral_emotions)
        
        total_emotional_words = positive_count + negative_count + neutral_count
        
        if total_emotional_words == 0:
            emotional_tone = "Neutral"
        else:
            if positive_count > negative_count and positive_count > neutral_count:
                emotional_tone = "Positive"
            elif negative_count > positive_count and negative_count > neutral_count:
                emotional_tone = "Negative"
            else:
                emotional_tone = "Mixed"
        
        return {
            "overall_tone": emotional_tone,
            "emotional_intensity": "High" if total_emotional_words > 10 else "Medium" if total_emotional_words > 5 else "Low",
            "emotional_distribution": {
                "positive": round(positive_count / max(total_emotional_words, 1), 2),
                "negative": round(negative_count / max(total_emotional_words, 1), 2),
                "neutral": round(neutral_count / max(total_emotional_words, 1), 2)
            }
        }
    
    def _analyze_pacing(self, content: str) -> Dict[str, Any]:
        """Analyze story pacing and rhythm"""
        scenes = re.findall(r'(INT\.|EXT\.)[^\n]*', content, re.IGNORECASE)
        word_count = len(content.split())
        
        if len(scenes) == 0:
            return {"pacing": "Unable to determine", "rhythm": "Unknown"}
        
        words_per_scene = word_count / len(scenes)
        
        if words_per_scene > 500:
            pacing = "Slow"
        elif words_per_scene > 200:
            pacing = "Medium"
        else:
            pacing = "Fast"
        
        action_words = ["runs", "fights", "chases", "explodes", "crashes", "jumps"]
        action_count = sum(content.lower().count(word) for word in action_words)
        
        rhythm = "Action-packed" if action_count > 5 else "Contemplative" if action_count < 2 else "Balanced"
        
        return {
            "pacing": pacing,
            "rhythm": rhythm,
            "words_per_scene": round(words_per_scene, 1),
            "scene_density": "High" if len(scenes) > word_count/300 else "Low"
        }
    
    def _calculate_runtime_advanced(self, content: str) -> str:
        """Advanced runtime calculation based on industry standards"""
        word_count = len(content.split())
        
        # Industry standard: 1 page ≈ 250 words ≈ 1 minute screen time
        # But adjust for dialogue density and action sequences
        
        dialogue_lines = len([line for line in content.split('\n') 
                            if line.strip() and not line.strip().isupper() 
                            and not line.strip().startswith(('INT.', 'EXT.'))])
        
        action_lines = len([line for line in content.split('\n') 
                          if line.strip().isupper() and not line.strip().startswith(('INT.', 'EXT.'))])
        
        # Dialogue typically takes longer, action sequences can be faster
        estimated_minutes = (word_count / 250) + (dialogue_lines * 0.1) - (action_lines * 0.05)
        estimated_minutes = max(1, estimated_minutes)  # Minimum 1 minute
        
        if estimated_minutes < 5:
            return f"{estimated_minutes:.1f} minutes (Short scene)"
        elif estimated_minutes < 30:
            return f"{estimated_minutes:.1f} minutes (Short film)"
        elif estimated_minutes < 90:
            return f"{estimated_minutes:.1f} minutes (Feature length)"
        else:
            return f"{estimated_minutes:.1f} minutes (Epic length)"
    
    def _calculate_quality_score(self, content: str, characters: Dict, scenes: Dict) -> Dict[str, Any]:
        """Calculate overall script quality score"""
        score = 0
        factors = []
        
        # Character development (0-25 points)
        char_score = min(len(characters.get("main_characters", [])) * 3, 25)
        score += char_score
        factors.append(f"Character development: {char_score}/25")
        
        # Scene variety (0-20 points)
        scene_variety = scenes.get("scene_variety", 0)
        scene_score = min(scene_variety * 2, 20)
        score += scene_score
        factors.append(f"Scene variety: {scene_score}/20")
        
        # Dialogue quality (0-25 points)
        word_count = len(content.split())
        dialogue_score = min(word_count / 100, 25)
        score += dialogue_score
        factors.append(f"Content depth: {dialogue_score:.1f}/25")
        
        # Structure (0-30 points)
        has_structure = len(re.findall(r'(INT\.|EXT\.)', content, re.IGNORECASE)) > 2
        structure_score = 30 if has_structure else 10
        score += structure_score
        factors.append(f"Structure: {structure_score}/30")
        
        return {
            "overall_score": f"{score:.1f}/100",
            "grade": self._get_quality_grade(score),
            "scoring_factors": factors,
            "recommendations": self._get_quality_recommendations(score)
        }
    
    def _get_quality_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return "A (Excellent)"
        elif score >= 80:
            return "B (Good)"
        elif score >= 70:
            return "C (Average)"
        elif score >= 60:
            return "D (Below Average)"
        else:
            return "F (Needs Improvement)"
    
    def _get_quality_recommendations(self, score: float) -> List[str]:
        """Provide improvement recommendations based on score"""
        recommendations = []
        
        if score < 60:
            recommendations.extend([
                "Develop more distinct characters with unique voices",
                "Add more scene variety and locations",
                "Expand dialogue and character interactions",
                "Improve story structure with clear acts"
            ])
        elif score < 80:
            recommendations.extend([
                "Enhance character development and backstories",
                "Add more emotional depth to scenes",
                "Consider subplot development"
            ])
        else:
            recommendations.extend([
                "Fine-tune dialogue for authenticity",
                "Polish scene transitions",
                "Consider professional script formatting"
            ])
        
        return recommendations[:3]
    
    def _generate_detailed_summary(self, content: str, scenes: Dict, characters: Dict, plot_structure: Dict) -> str:
        """Generate a comprehensive summary of the script content"""
        word_count = len(content.split())
        main_chars = characters.get("main_characters", [])
        scene_count = scenes.get("total_scenes", 0)
        
        # Determine content type
        if word_count < 100:
            content_type = "brief scene excerpt"
        elif word_count < 500:
            content_type = "short script segment"
        elif word_count < 2000:
            content_type = "substantial script section"
        else:
            content_type = "full-length screenplay"
        
        # Character summary
        if len(main_chars) > 0:
            protagonist = main_chars[0]["name"]
            char_summary = f"featuring {len(main_chars)} main characters led by {protagonist}"
        else:
            char_summary = "with character development to be determined"
        
        # Scene summary
        if scene_count > 0:
            scene_summary = f"across {scene_count} scenes"
            if scenes.get("scene_variety", 0) > scene_count // 2:
                scene_summary += " with diverse locations"
        else:
            scene_summary = "in a single setting"
        
        # Structure summary
        structure_type = plot_structure.get("estimated_structure", "Unknown")
        
        return f"A {content_type} {char_summary} {scene_summary}. The narrative follows a {structure_type} structure with {word_count} words of content, indicating {'professional screenplay formatting' if scene_count > 3 else 'developing script structure'}."
    
    def _classify_genre_advanced(self, content: str) -> Dict[str, Any]:
        """Advanced genre classification with confidence scoring"""
        content_lower = content.lower()
        
        genre_indicators = {
            "sci-fi": ["space", "alien", "robot", "future", "technology", "spaceship", "mars", "galaxy"],
            "action": ["fight", "chase", "explosion", "battle", "weapon", "combat", "war"],
            "drama": ["emotion", "family", "conflict", "struggle", "pain", "tears", "heart"],
            "thriller": ["danger", "suspense", "chase", "escape", "pursuit", "tension"],
            "romance": ["love", "heart", "kiss", "relationship", "wedding", "marriage"],
            "comedy": ["funny", "laugh", "joke", "humor", "silly", "hilarious"],
            "horror": ["dark", "scary", "fear", "ghost", "monster", "terror"],
            "mystery": ["secret", "detective", "clue", "investigate", "solve", "murder"]
        }
        
        scores = {}
        total_words = len(content.split())
        
        for genre, keywords in genre_indicators.items():
            matches = sum(content_lower.count(keyword) for keyword in keywords)
            scores[genre] = min(matches / max(total_words * 0.01, 1), 1.0)
        
        primary_genre = max(scores.items(), key=lambda x: x[1])
        
        return {
            "primary_genre": primary_genre[0],
            "confidence": round(primary_genre[1], 3),
            "all_scores": {k: round(v, 3) for k, v in scores.items()}
        }

class GenreClassifierAgent:
    """Agent that classifies content by genre with confidence scores"""
    
    def analyze(self, content: str, parameters: Dict = None) -> Dict[str, Any]:
        import time
        start_time = time.time()
        
        # Analyze content for genre indicators
        genre_scores = self._calculate_genre_scores(content)
        primary_genre = max(genre_scores.items(), key=lambda x: x[1])
        
        # Analyze mood and tone
        mood_analysis = self._analyze_mood(content)
        
        # Get content characteristics
        characteristics = self._get_content_characteristics(content)
        
        processing_time = time.time() - start_time
        
        return {
            "primary_genre": primary_genre[0],
            "confidence": round(primary_genre[1], 2),
            "genre_scores": {k: round(v, 2) for k, v in genre_scores.items()},
            "mood": mood_analysis,
            "characteristics": characteristics,
            "content_rating": self._suggest_rating(content),
            "target_audience": self._identify_audience(genre_scores, mood_analysis),
            "processing_time": round(processing_time, 3)
        }
    
    def _calculate_genre_scores(self, content: str) -> Dict[str, float]:
        content_lower = content.lower()
        
        genre_keywords = {
            "action": ["fight", "chase", "explosion", "battle", "weapon", "combat", "war"],
            "comedy": ["funny", "laugh", "joke", "humor", "silly", "comedy", "hilarious"],
            "drama": ["emotion", "family", "conflict", "struggle", "pain", "tears", "heart"],
            "horror": ["dark", "scary", "fear", "ghost", "monster", "terror", "nightmare"],
            "romance": ["love", "romance", "heart", "kiss", "relationship", "wedding", "date"],
            "sci-fi": ["space", "alien", "robot", "future", "technology", "spaceship", "mars"],
            "thriller": ["suspense", "tension", "danger", "chase", "escape", "pursuit"],
            "mystery": ["secret", "mystery", "detective", "clue", "investigate", "solve"],
            "fantasy": ["magic", "wizard", "dragon", "kingdom", "spell", "enchanted"],
            "western": ["cowboy", "sheriff", "saloon", "horse", "desert", "frontier"]
        }
        
        scores = {}
        total_words = len(content.split())
        
        for genre, keywords in genre_keywords.items():
            matches = sum(content_lower.count(keyword) for keyword in keywords)
            scores[genre] = min(matches / max(total_words * 0.01, 1), 1.0)
        
        return scores
    
    def _analyze_mood(self, content: str) -> Dict[str, Any]:
        content_lower = content.lower()
        
        positive_words = ["happy", "joy", "love", "smile", "laugh", "wonderful", "amazing"]
        negative_words = ["sad", "angry", "fear", "dark", "pain", "terrible", "awful"]
        intense_words = ["intense", "dramatic", "powerful", "strong", "extreme"]
        
        positive_score = sum(content_lower.count(word) for word in positive_words)
        negative_score = sum(content_lower.count(word) for word in negative_words)
        intensity_score = sum(content_lower.count(word) for word in intense_words)
        
        if positive_score > negative_score:
            overall_mood = "positive"
        elif negative_score > positive_score:
            overall_mood = "negative"
        else:
            overall_mood = "neutral"
        
        return {
            "overall": overall_mood,
            "intensity": "high" if intensity_score > 2 else "medium" if intensity_score > 0 else "low",
            "emotional_range": "broad" if (positive_score > 0 and negative_score > 0) else "focused"
        }
    
    def _get_content_characteristics(self, content: str) -> List[str]:
        characteristics = []
        
        if "dialogue" in content.lower() or ":" in content:
            characteristics.append("dialogue-heavy")
        
        if len(re.findall(r'(INT\.|EXT\.)', content, re.IGNORECASE)) > 3:
            characteristics.append("multi-location")
        
        if len(content.split()) > 1000:
            characteristics.append("feature-length")
        elif len(content.split()) > 300:
            characteristics.append("short-form")
        else:
            characteristics.append("scene-excerpt")
        
        return characteristics
    
    def _suggest_rating(self, content: str) -> str:
        content_lower = content.lower()
        
        mature_content = ["violence", "blood", "kill", "murder", "weapon", "fight"]
        mild_content = ["damn", "hell", "kiss", "romance"]
        
        if any(word in content_lower for word in mature_content):
            return "PG-13 / R"
        elif any(word in content_lower for word in mild_content):
            return "PG"
        else:
            return "G / PG"
    
    def _identify_audience(self, genre_scores: Dict, mood: Dict) -> List[str]:
        audiences = []
        
        top_genre = max(genre_scores.items(), key=lambda x: x[1])[0]
        
        age_mapping = {
            "comedy": ["family", "young_adult", "adult"],
            "action": ["teen", "adult"],
            "romance": ["teen", "young_adult", "adult"],
            "horror": ["teen", "adult"],
            "sci-fi": ["teen", "adult", "geek_culture"],
            "drama": ["adult", "mature"],
            "fantasy": ["family", "young_adult"],
        }
        
        return age_mapping.get(top_genre, ["general_audience"])

class MarketingAgent:
    """Agent that generates marketing recommendations and audience insights"""
    
    def analyze(self, content: str, parameters: Dict = None) -> Dict[str, Any]:
        import time
        start_time = time.time()
        
        # Analyze target demographics
        demographics = self._analyze_demographics(content)
        
        # Generate marketing hooks
        hooks = self._generate_marketing_hooks(content)
        
        # Suggest marketing channels
        channels = self._suggest_marketing_channels(content, demographics)
        
        # Competitive analysis
        similar_content = self._find_similar_content(content)
        
        # Budget recommendations
        budget_recs = self._suggest_budget_allocation(content)
        
        processing_time = time.time() - start_time
        
        return {
            "target_demographics": demographics,
            "marketing_hooks": hooks,
            "recommended_channels": channels,
            "similar_content": similar_content,
            "budget_allocation": budget_recs,
            "taglines": self._generate_taglines(content),
            "release_strategy": self._suggest_release_strategy(content),
            "processing_time": round(processing_time, 3)
        }
    
    def _analyze_demographics(self, content: str) -> Dict[str, Any]:
        content_lower = content.lower()
        
        # Age group indicators
        young_indicators = ["teen", "school", "college", "young", "party"]
        adult_indicators = ["work", "career", "marriage", "family", "responsibility"]
        mature_indicators = ["retirement", "wisdom", "legacy", "grandchild"]
        
        # Gender appeal indicators
        male_indicators = ["action", "fight", "car", "sports", "war", "technology"]
        female_indicators = ["romance", "emotion", "relationship", "family", "fashion"]
        
        young_score = sum(content_lower.count(word) for word in young_indicators)
        adult_score = sum(content_lower.count(word) for word in adult_indicators)
        mature_score = sum(content_lower.count(word) for word in mature_indicators)
        
        primary_age = "young_adult" if young_score > adult_score and young_score > mature_score else \
                     "mature" if mature_score > adult_score else "adult"
        
        male_score = sum(content_lower.count(word) for word in male_indicators)
        female_score = sum(content_lower.count(word) for word in female_indicators)
        
        gender_appeal = "male" if male_score > female_score * 1.5 else \
                       "female" if female_score > male_score * 1.5 else "universal"
        
        return {
            "primary_age_group": primary_age,
            "gender_appeal": gender_appeal,
            "appeal_scores": {
                "young": young_score,
                "adult": adult_score,
                "mature": mature_score
            }
        }
    
    def _generate_marketing_hooks(self, content: str) -> List[str]:
        hooks = []
        content_lower = content.lower()
        
        # Emotional hooks
        if any(word in content_lower for word in ["love", "heart", "romance"]):
            hooks.append("A heart-stopping romance that will leave you breathless")
        
        if any(word in content_lower for word in ["action", "fight", "chase"]):
            hooks.append("Edge-of-your-seat action that never stops")
        
        if any(word in content_lower for word in ["mystery", "secret", "detective"]):
            hooks.append("A mystery that will keep you guessing until the very end")
        
        if any(word in content_lower for word in ["space", "future", "alien"]):
            hooks.append("A mind-bending journey to the edge of the universe")
        
        # Default hooks
        if not hooks:
            hooks.extend([
                "A compelling story that will captivate audiences",
                "An unforgettable cinematic experience",
                "Drama that speaks to the human condition"
            ])
        
        return hooks[:3]
    
    def _suggest_marketing_channels(self, content: str, demographics: Dict) -> List[Dict]:
        channels = []
        
        age_group = demographics["primary_age_group"]
        gender_appeal = demographics["gender_appeal"]
        
        if age_group == "young_adult":
            channels.extend([
                {"platform": "TikTok", "priority": "high", "content_type": "short_videos"},
                {"platform": "Instagram", "priority": "high", "content_type": "stories_reels"},
                {"platform": "YouTube", "priority": "medium", "content_type": "trailers"}
            ])
        elif age_group == "adult":
            channels.extend([
                {"platform": "Facebook", "priority": "high", "content_type": "targeted_ads"},
                {"platform": "Twitter", "priority": "medium", "content_type": "discussions"},
                {"platform": "Traditional TV", "priority": "high", "content_type": "commercials"}
            ])
        else:  # mature
            channels.extend([
                {"platform": "Facebook", "priority": "high", "content_type": "community_groups"},
                {"platform": "Traditional Media", "priority": "high", "content_type": "print_radio"},
                {"platform": "Email", "priority": "medium", "content_type": "newsletters"}
            ])
        
        return channels
    
    def _find_similar_content(self, content: str) -> List[str]:
        content_lower = content.lower()
        
        similar_content = []
        
        if any(word in content_lower for word in ["space", "alien", "mars"]):
            similar_content.extend(["Interstellar", "The Martian", "Arrival"])
        
        if any(word in content_lower for word in ["love", "romance", "heart"]):
            similar_content.extend(["The Notebook", "Titanic", "La La Land"])
        
        if any(word in content_lower for word in ["action", "fight", "chase"]):
            similar_content.extend(["John Wick", "Mission Impossible", "Fast & Furious"])
        
        if not similar_content:
            similar_content = ["Popular drama films", "Character-driven stories", "Independent cinema"]
        
        return similar_content[:3]
    
    def _suggest_budget_allocation(self, content: str) -> Dict[str, str]:
        return {
            "digital_marketing": "40%",
            "traditional_advertising": "25%",
            "influencer_partnerships": "15%",
            "public_relations": "10%",
            "events_premieres": "10%"
        }
    
    def _generate_taglines(self, content: str) -> List[str]:
        content_lower = content.lower()
        taglines = []
        
        if "space" in content_lower:
            taglines.append("The universe has never been closer")
        if "love" in content_lower:
            taglines.append("Love knows no boundaries")
        if "action" in content_lower:
            taglines.append("Action speaks louder than words")
        
        taglines.extend([
            "Experience the story",
            "Beyond ordinary",
            "This changes everything"
        ])
        
        return taglines[:3]
    
    def _suggest_release_strategy(self, content: str) -> Dict[str, str]:
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["action", "adventure", "sci-fi"]):
            return {
                "recommended_season": "Summer blockbuster season",
                "platform_strategy": "Wide theatrical release followed by streaming",
                "international_strategy": "Global simultaneous release"
            }
        else:
            return {
                "recommended_season": "Awards season (Fall/Winter)",
                "platform_strategy": "Limited theatrical then wide release",
                "international_strategy": "Festival circuit then international rollout"
            }

# Initialize agents
script_summarizer = ScriptSummarizerAgent()
genre_classifier = GenreClassifierAgent()
marketing_agent = MarketingAgent()

AGENTS = {
    "script_summarizer": script_summarizer,
    "genre_classifier": genre_classifier,
    "marketing_agent": marketing_agent
}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="API is running successfully",
        version="1.0.0"
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Multi-Agent Content Analytics API", "status": "running", "version": "2.0.0"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="API is running successfully with functional agents",
        version="2.0.0"
    )

@app.get("/web")
async def web_interface():
    """Serve the web interface"""
    try:
        with open("content_analytics_ui.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Web interface not found</h1><p>Please ensure content_analytics_ui.html exists.</p>")

@app.get("/ui")
async def ui_redirect():
    """Redirect /ui to /web for convenience"""
    return HTMLResponse(content='<script>window.location.href="/web";</script>')

@app.post("/analyze", response_model=ContentAnalysisResponse)
async def analyze_content(request: ContentAnalysisRequest):
    """Enhanced content analysis with optional agent specification"""
    
    if request.agent and request.agent in AGENTS:
        # Use specific agent
        agent = AGENTS[request.agent]
        results = agent.analyze(request.content)
        
        return ContentAnalysisResponse(
            content=request.content[:100] + "..." if len(request.content) > 100 else request.content,
            analysis_type=f"{request.analysis_type} (using {request.agent})",
            results=results
        )
    else:
        # Default general analysis
        mock_results = {
            "word_count": len(request.content.split()),
            "character_count": len(request.content),
            "sentiment": "positive",
            "keywords": ["content", "analysis"],
            "summary": f"Analysis of {request.analysis_type} content with {len(request.content.split())} words",
            "suggestion": "Use the '/agent/{agent_name}' endpoint for detailed analysis"
        }
        
        return ContentAnalysisResponse(
            content=request.content[:100] + "..." if len(request.content) > 100 else request.content,
            analysis_type=request.analysis_type,
            results=mock_results
        )

@app.post("/agent/{agent_name}", response_model=AgentResponse)
async def use_agent(agent_name: str, request: AgentRequest):
    """Use a specific agent to analyze content"""
    
    if agent_name not in AGENTS:
        raise HTTPException(
            status_code=404, 
            detail=f"Agent '{agent_name}' not found. Available agents: {list(AGENTS.keys())}"
        )
    
    agent = AGENTS[agent_name]
    
    try:
        results = agent.analyze(
            request.content, 
            request.parameters or {}
        )
        
        return AgentResponse(
            agent=agent_name,
            content=request.content[:100] + "..." if len(request.content) > 100 else request.content,
            results=results,
            timestamp=datetime.now().isoformat(),
            processing_time=results.get("processing_time", 0.0)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")

@app.get("/agents")
async def list_agents():
    """List available agents with their current status"""
    return {
        "agents": [
            {
                "name": "script_summarizer",
                "description": "Analyzes and summarizes movie scripts with character/scene extraction",
                "status": "active",
                "capabilities": ["scene_extraction", "character_analysis", "theme_detection", "genre_suggestion"],
                "endpoint": "/agent/script_summarizer"
            },
            {
                "name": "genre_classifier", 
                "description": "Classifies content by genre with confidence scores and mood analysis",
                "status": "active",
                "capabilities": ["genre_classification", "mood_analysis", "audience_targeting", "content_rating"],
                "endpoint": "/agent/genre_classifier"
            },
            {
                "name": "marketing_agent",
                "description": "Generates comprehensive marketing strategies and audience insights",
                "status": "active", 
                "capabilities": ["demographic_analysis", "marketing_hooks", "channel_strategy", "budget_planning"],
                "endpoint": "/agent/marketing_agent"
            }
        ],
        "total_agents": 3,
        "all_active": True
    }

@app.get("/agents/{agent_name}")
async def get_agent_info(agent_name: str):
    """Get information about a specific agent"""
    agents_info = {
        "script_summarizer": {
            "name": "Script Summarizer Agent",
            "capabilities": ["text_summarization", "key_themes", "character_analysis"],
            "models": ["gpt-4", "claude-3"],
            "status": "ready"
        },
        "genre_classifier": {
            "name": "Genre Classification Agent", 
            "capabilities": ["genre_prediction", "mood_analysis", "style_detection"],
            "models": ["bert-classifier", "custom-cnn"],
            "status": "ready"
        },
        "marketing_agent": {
            "name": "Marketing Strategy Agent",
            "capabilities": ["audience_targeting", "campaign_strategy", "market_analysis"],
            "models": ["gpt-4", "market-llm"],
            "status": "ready"
        }
    }
    
    if agent_name not in agents_info:
        return JSONResponse(
            status_code=404,
            content={"error": f"Agent '{agent_name}' not found"}
        )
    
    return agents_info[agent_name]

# Application startup logging
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Multi-Agent Content Analytics Platform starting up...")
    logger.info("📊 Initializing AI agents...")
    logger.info("✅ System ready for content analysis!")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Multi-Agent Content Analytics Platform shutting down...")
    logger.info("✅ Cleanup completed!")
