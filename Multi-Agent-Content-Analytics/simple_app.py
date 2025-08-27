"""
Enhanced FastAPI application with functional AI agents for content analysis
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import sys
import os
import re
import json
from datetime import datetime

# Enhanced FastAPI app with functional agents
app = FastAPI(
    title="Multi-Agent Content Analytics API",
    description="Advanced AI system for content analysis with functional agents",
    version="2.0.0"
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
    """Agent that analyzes and summarizes movie scripts"""
    
    def analyze(self, content: str, parameters: Dict = None) -> Dict[str, Any]:
        import time
        start_time = time.time()
        
        # Extract script elements
        scenes = self._extract_scenes(content)
        characters = self._extract_characters(content)
        dialogue_ratio = self._calculate_dialogue_ratio(content)
        
        # Generate summary
        summary = self._generate_summary(content, scenes, characters)
        
        # Extract themes and genres
        themes = self._extract_themes(content)
        suggested_genre = self._classify_genre(content)
        
        processing_time = time.time() - start_time
        
        return {
            "summary": summary,
            "characters": characters,
            "scenes": scenes,
            "dialogue_ratio": dialogue_ratio,
            "themes": themes,
            "suggested_genre": suggested_genre,
            "word_count": len(content.split()),
            "estimated_runtime": f"{len(content.split()) // 250} minutes",
            "processing_time": round(processing_time, 3)
        }
    
    def _extract_scenes(self, content: str) -> List[str]:
        # Find scene headings (INT./EXT.)
        scene_pattern = r'(INT\.|EXT\.)[^\n]*'
        scenes = re.findall(scene_pattern, content, re.IGNORECASE)
        return [scene.strip() for scene in scenes[:10]]  # Limit to first 10
    
    def _extract_characters(self, content: str) -> List[str]:
        # Find character names (all caps followed by dialogue)
        char_pattern = r'^([A-Z][A-Z\s]+)$'
        lines = content.split('\n')
        characters = set()
        
        for line in lines:
            line = line.strip()
            if re.match(char_pattern, line) and len(line) < 30:
                characters.add(line)
        
        return list(characters)[:10]  # Limit to 10 main characters
    
    def _calculate_dialogue_ratio(self, content: str) -> float:
        lines = content.split('\n')
        dialogue_lines = 0
        total_lines = len([l for l in lines if l.strip()])
        
        for line in lines:
            line = line.strip()
            if line and not line.isupper() and not line.startswith(('INT.', 'EXT.', 'FADE')):
                dialogue_lines += 1
                
        return round(dialogue_lines / max(total_lines, 1), 2)
    
    def _generate_summary(self, content: str, scenes: List, characters: List) -> str:
        word_count = len(content.split())
        
        if word_count < 100:
            return "Brief scene or dialogue excerpt"
        elif word_count < 500:
            return f"Short script segment featuring {len(characters)} characters across {len(scenes)} scenes"
        else:
            return f"Full script with {len(characters)} main characters, {len(scenes)} scenes, exploring themes of drama and character development"
    
    def _extract_themes(self, content: str) -> List[str]:
        content_lower = content.lower()
        themes = []
        
        theme_keywords = {
            "love": ["love", "romance", "heart", "kiss", "relationship"],
            "action": ["fight", "chase", "explosion", "battle", "weapon"],
            "sci-fi": ["space", "alien", "robot", "future", "technology"],
            "horror": ["dark", "scary", "fear", "ghost", "monster"],
            "comedy": ["funny", "laugh", "joke", "humor", "silly"],
            "drama": ["emotion", "family", "conflict", "struggle", "pain"],
            "mystery": ["secret", "mystery", "detective", "clue", "investigate"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                themes.append(theme)
        
        return themes[:3]  # Top 3 themes
    
    def _classify_genre(self, content: str) -> str:
        themes = self._extract_themes(content)
        if themes:
            return themes[0].title()
        return "Drama"

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
