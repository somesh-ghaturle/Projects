"""
Agent Orchestrator
Coordinates multiple agents and manages their interactions
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json

from .base_agent import BaseAgent
from .script_summarizer import ScriptSummarizerAgent
from .genre_classifier import GenreClassificationAgent
from .marketing_agent import MarketingRecommendationAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates multiple content analysis agents"""
    
    def __init__(self):
        self.agents = {}
        self.is_initialized = False
        self.task_queue = asyncio.Queue()
        self.results_cache = {}
        self.active_tasks = {}
        
    async def initialize(self) -> None:
        """Initialize all agents"""
        if self.is_initialized:
            return
        
        logger.info("Initializing Agent Orchestrator")
        
        try:
            # Initialize individual agents
            self.agents = {
                "script_summarizer": ScriptSummarizerAgent(),
                "genre_classifier": GenreClassificationAgent(),
                "marketing_agent": MarketingRecommendationAgent()
            }
            
            # Initialize all agents concurrently
            initialization_tasks = [
                agent.initialize() for agent in self.agents.values()
            ]
            
            await asyncio.gather(*initialization_tasks)
            
            self.is_initialized = True
            logger.info("Agent Orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Agent Orchestrator: {str(e)}")
            raise
    
    async def analyze_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze content using multiple agents
        
        Args:
            content_data: Dictionary containing content to analyze
            
        Returns:
            Combined analysis results from all agents
        """
        if not self.is_initialized:
            await self.initialize()
        
        analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        logger.info(f"Starting content analysis: {analysis_id}")
        
        try:
            # Prepare agent tasks
            agent_tasks = {}
            
            # Script analysis task
            if "script_text" in content_data:
                agent_tasks["script_analysis"] = self._run_script_analysis(
                    content_data["script_text"],
                    content_data.get("metadata", {})
                )
            
            # Genre classification task
            if "text_content" in content_data or "script_text" in content_data:
                text_for_genre = content_data.get("text_content") or content_data.get("script_text", "")
                agent_tasks["genre_classification"] = self._run_genre_classification(
                    text_for_genre,
                    content_data.get("metadata", {})
                )
            
            # Marketing analysis task
            if "social_media_data" in content_data:
                agent_tasks["marketing_analysis"] = self._run_marketing_analysis(
                    content_data["social_media_data"],
                    content_data.get("metadata", {})
                )
            
            # Execute all tasks concurrently
            results = {}
            if agent_tasks:
                completed_tasks = await asyncio.gather(
                    *agent_tasks.values(),
                    return_exceptions=True
                )
                
                # Map results back to agent names
                for i, (task_name, _) in enumerate(agent_tasks.items()):
                    result = completed_tasks[i]
                    if isinstance(result, Exception):
                        logger.error(f"Agent task {task_name} failed: {str(result)}")
                        results[task_name] = {"error": str(result)}
                    else:
                        results[task_name] = result
            
            # Combine and enrich results
            combined_results = await self._combine_results(results, content_data)
            
            # Cache results
            self.results_cache[analysis_id] = combined_results
            
            logger.info(f"Content analysis completed: {analysis_id}")
            return combined_results
            
        except Exception as e:
            logger.error(f"Error in content analysis: {str(e)}")
            raise
    
    async def _run_script_analysis(self, script_text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Run script summarizer agent"""
        agent = self.agents["script_summarizer"]
        input_data = {
            "script_text": script_text,
            "metadata": metadata
        }
        return await agent.execute(input_data)
    
    async def _run_genre_classification(self, text_content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Run genre classification agent"""
        agent = self.agents["genre_classifier"]
        input_data = {
            "text_content": text_content,
            "metadata": metadata
        }
        return await agent.execute(input_data)
    
    async def _run_marketing_analysis(self, social_media_data: List[str], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Run marketing recommendation agent"""
        agent = self.agents["marketing_agent"]
        input_data = {
            "social_media_data": social_media_data,
            "metadata": metadata
        }
        return await agent.execute(input_data)
    
    async def _combine_results(self, agent_results: Dict[str, Any], original_data: Dict[str, Any]) -> Dict[str, Any]:
        """Combine results from multiple agents"""
        combined = {
            "analysis_id": f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            "timestamp": datetime.now().isoformat(),
            "content_summary": await self._generate_content_summary(agent_results, original_data),
            "agents_used": list(agent_results.keys()),
            "individual_results": agent_results,
            "cross_agent_insights": await self._generate_cross_agent_insights(agent_results),
            "confidence_scores": await self._calculate_confidence_scores(agent_results),
            "recommendations": await self._generate_combined_recommendations(agent_results)
        }
        
        return combined
    
    async def _generate_content_summary(self, agent_results: Dict[str, Any], original_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a high-level content summary"""
        summary = {
            "content_type": "movie_content",
            "analysis_scope": [],
            "key_findings": []
        }
        
        # Determine analysis scope
        if "script_analysis" in agent_results:
            summary["analysis_scope"].append("script_analysis")
        if "genre_classification" in agent_results:
            summary["analysis_scope"].append("genre_classification")
        if "marketing_analysis" in agent_results:
            summary["analysis_scope"].append("marketing_analysis")
        
        # Extract key findings
        script_result = agent_results.get("script_analysis", {})
        if "summary" in script_result:
            plot = script_result["summary"].get("plot", "")
            if plot:
                summary["key_findings"].append(f"Plot: {plot[:200]}...")
        
        genre_result = agent_results.get("genre_classification", {})
        if "primary_genre" in genre_result:
            genre_info = genre_result["primary_genre"]
            genre = genre_info.get("genre", "Unknown")
            confidence = genre_info.get("confidence", 0)
            summary["key_findings"].append(f"Primary Genre: {genre} (confidence: {confidence:.2f})")
        
        marketing_result = agent_results.get("marketing_analysis", {})
        if "sentiment_analysis" in marketing_result:
            overall_sentiment = marketing_result["sentiment_analysis"].get("overall_sentiment", "neutral")
            summary["key_findings"].append(f"Social Sentiment: {overall_sentiment}")
        
        return summary
    
    async def _generate_cross_agent_insights(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights by combining data from multiple agents"""
        insights = {
            "genre_sentiment_alignment": {},
            "marketing_genre_fit": {},
            "content_market_readiness": {}
        }
        
        try:
            # Genre-Sentiment Alignment
            genre_result = agent_results.get("genre_classification", {})
            marketing_result = agent_results.get("marketing_analysis", {})
            
            if genre_result and marketing_result:
                primary_genre = genre_result.get("primary_genre", {}).get("genre", "")
                sentiment = marketing_result.get("sentiment_analysis", {}).get("overall_sentiment", "neutral")
                
                insights["genre_sentiment_alignment"] = {
                    "genre": primary_genre,
                    "sentiment": sentiment,
                    "alignment": self._assess_genre_sentiment_fit(primary_genre, sentiment)
                }
            
            # Marketing-Genre Fit
            if genre_result and marketing_result:
                genre_confidence = genre_result.get("primary_genre", {}).get("confidence", 0)
                positive_sentiment = marketing_result.get("sentiment_analysis", {}).get("percentages", {}).get("positive_percent", 0)
                
                insights["marketing_genre_fit"] = {
                    "genre_confidence": genre_confidence,
                    "positive_sentiment_percent": positive_sentiment,
                    "market_fit_score": (genre_confidence * positive_sentiment) / 100
                }
            
            # Content Market Readiness
            script_result = agent_results.get("script_analysis", {})
            readiness_factors = []
            
            if script_result and "analysis" in script_result:
                runtime = script_result["analysis"].get("estimated_runtime", "")
                if runtime:
                    readiness_factors.append(f"Runtime: {runtime}")
            
            if genre_result:
                confidence = genre_result.get("primary_genre", {}).get("confidence", 0)
                if confidence > 0.7:
                    readiness_factors.append("Strong genre identity")
            
            if marketing_result:
                positive_percent = marketing_result.get("sentiment_analysis", {}).get("percentages", {}).get("positive_percent", 0)
                if positive_percent > 60:
                    readiness_factors.append("Positive audience reception")
            
            insights["content_market_readiness"] = {
                "readiness_factors": readiness_factors,
                "overall_readiness": "high" if len(readiness_factors) >= 2 else "medium" if len(readiness_factors) == 1 else "low"
            }
            
        except Exception as e:
            logger.error(f"Error generating cross-agent insights: {str(e)}")
            insights["error"] = str(e)
        
        return insights
    
    def _assess_genre_sentiment_fit(self, genre: str, sentiment: str) -> str:
        """Assess how well genre and sentiment align"""
        # Define expected sentiment patterns for genres
        genre_sentiment_map = {
            "Comedy": ["positive", "very_positive"],
            "Horror": ["negative", "neutral"],  # Horror can have negative sentiment but still be successful
            "Drama": ["neutral", "positive", "negative"],  # Drama is flexible
            "Action": ["positive", "neutral"],
            "Romance": ["positive", "very_positive"],
            "Thriller": ["neutral", "negative"]
        }
        
        expected_sentiments = genre_sentiment_map.get(genre, ["neutral"])
        
        if sentiment in expected_sentiments:
            return "well_aligned"
        elif sentiment in ["positive", "very_positive"] and genre not in ["Horror"]:
            return "positively_aligned"
        else:
            return "misaligned"
    
    async def _calculate_confidence_scores(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate confidence scores for each analysis"""
        confidence_scores = {}
        
        try:
            # Script analysis confidence
            script_result = agent_results.get("script_analysis", {})
            if script_result and not script_result.get("error"):
                # Base confidence on presence of key elements
                score = 0.5  # Base score
                
                if script_result.get("summary", {}).get("plot"):
                    score += 0.2
                if script_result.get("characters"):
                    score += 0.2
                if script_result.get("themes"):
                    score += 0.1
                
                confidence_scores["script_analysis"] = min(1.0, score)
            
            # Genre classification confidence
            genre_result = agent_results.get("genre_classification", {})
            if genre_result and not genre_result.get("error"):
                confidence = genre_result.get("primary_genre", {}).get("confidence", 0)
                confidence_scores["genre_classification"] = confidence
            
            # Marketing analysis confidence
            marketing_result = agent_results.get("marketing_analysis", {})
            if marketing_result and not marketing_result.get("error"):
                data_summary = marketing_result.get("data_summary", {})
                processed_posts = data_summary.get("processed_posts", 0)
                
                # Confidence based on data volume
                if processed_posts >= 100:
                    confidence_scores["marketing_analysis"] = 0.9
                elif processed_posts >= 50:
                    confidence_scores["marketing_analysis"] = 0.7
                elif processed_posts >= 20:
                    confidence_scores["marketing_analysis"] = 0.5
                else:
                    confidence_scores["marketing_analysis"] = 0.3
            
            # Overall confidence
            if confidence_scores:
                overall_confidence = sum(confidence_scores.values()) / len(confidence_scores)
                confidence_scores["overall"] = overall_confidence
            
        except Exception as e:
            logger.error(f"Error calculating confidence scores: {str(e)}")
            confidence_scores["error"] = str(e)
        
        return confidence_scores
    
    async def _generate_combined_recommendations(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate combined recommendations from all agents"""
        recommendations = {
            "content_improvements": [],
            "marketing_strategies": [],
            "genre_positioning": [],
            "overall_strategy": []
        }
        
        try:
            # Extract recommendations from individual agents
            script_result = agent_results.get("script_analysis", {})
            genre_result = agent_results.get("genre_classification", {})
            marketing_result = agent_results.get("marketing_analysis", {})
            
            # Content improvements from script analysis
            if script_result and "structure" in script_result:
                pacing = script_result["structure"].get("pacing", "")
                if pacing == "Slow":
                    recommendations["content_improvements"].append("Consider tightening pacing for better audience engagement")
                elif pacing == "Fast":
                    recommendations["content_improvements"].append("Consider adding character development moments")
            
            # Genre positioning
            if genre_result:
                primary_genre = genre_result.get("primary_genre", {}).get("genre", "")
                confidence = genre_result.get("primary_genre", {}).get("confidence", 0)
                
                if confidence < 0.5:
                    recommendations["genre_positioning"].append("Strengthen genre-specific elements for clearer positioning")
                else:
                    recommendations["genre_positioning"].append(f"Strong {primary_genre} identity - leverage in marketing")
            
            # Marketing strategies from marketing agent
            if marketing_result and "recommendations" in marketing_result:
                marketing_recs = marketing_result["recommendations"]
                
                immediate_actions = marketing_recs.get("immediate_actions", [])
                recommendations["marketing_strategies"].extend(immediate_actions[:3])
                
                campaign_themes = marketing_recs.get("campaign_themes", [])
                if campaign_themes:
                    recommendations["marketing_strategies"].append(f"Focus campaigns on: {', '.join(campaign_themes[:2])}")
            
            # Overall strategy
            recommendations["overall_strategy"] = [
                "Align content positioning with audience sentiment",
                "Leverage strongest analysis results in marketing",
                "Monitor social sentiment throughout campaign",
                "Continuously refine messaging based on feedback"
            ]
            
        except Exception as e:
            logger.error(f"Error generating combined recommendations: {str(e)}")
            recommendations["error"] = str(e)
        
        return recommendations
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        status = {
            "orchestrator_initialized": self.is_initialized,
            "agents": {},
            "cache_size": len(self.results_cache),
            "active_tasks": len(self.active_tasks)
        }
        
        for agent_name, agent in self.agents.items():
            status["agents"][agent_name] = agent.get_status()
        
        return status
    
    async def cleanup(self) -> None:
        """Cleanup all agents and resources"""
        logger.info("Cleaning up Agent Orchestrator")
        
        try:
            # Cleanup all agents
            cleanup_tasks = [agent.cleanup() for agent in self.agents.values()]
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
            
            # Clear caches
            self.results_cache.clear()
            self.active_tasks.clear()
            
            self.is_initialized = False
            logger.info("Agent Orchestrator cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        if self.is_initialized:
            try:
                asyncio.create_task(self.cleanup())
            except Exception:
                pass  # Best effort cleanup
