"""
Research Agent - Specialized in web research and information gathering
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ResearcherAgent(BaseAgent):
    """Agent specialized in research and information gathering"""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="Researcher",
            description="Expert in web research, academic papers, and information synthesis",
            **kwargs
        )
        self.research_history = []
        self.sources_cache = {}
    
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a research task"""
        logger.info(f"Researcher executing task: {task}")
        
        try:
            # Parse the research request
            research_query = self._parse_research_query(task, context)
            
            # Conduct multi-source research
            research_results = await self._conduct_research(research_query)
            
            # Synthesize findings
            synthesis = await self._synthesize_findings(research_results)
            
            # Store research history
            self._store_research_record(task, research_results, synthesis)
            
            return {
                "task": task,
                "agent": self.name,
                "query": research_query,
                "sources_found": len(research_results.get("sources", [])),
                "sources": research_results.get("sources", []),  # Include actual sources
                "synthesis": synthesis,
                "research_quality": self._assess_research_quality(research_results),
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Research task failed: {e}")
            return {
                "task": task,
                "agent": self.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "failed"
            }
    
    async def process_message(self, message: str, sender: Optional[str] = None) -> str:
        """Process research requests from other agents"""
        logger.info(f"Researcher received message from {sender}: {message}")
        
        if "research" in message.lower() or "find" in message.lower():
            result = await self.execute(message)
            if result["status"] == "completed":
                return f"Research completed: {result['synthesis'][:200]}..."
            else:
                return f"Research failed: {result.get('error', 'Unknown error')}"
        
        return "I specialize in research tasks. Please provide a research query."
    
    def _parse_research_query(self, task: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse and structure the research query"""
        return {
            "main_query": task,
            "context": context or {},
            "search_terms": self._extract_search_terms(task),
            "research_scope": self._determine_research_scope(task),
            "priority_sources": self._identify_priority_sources(task)
        }
    
    def _extract_search_terms(self, task: str) -> List[str]:
        """Extract relevant search terms from the task"""
        # Simple keyword extraction (can be enhanced with NLP)
        import re
        
        # Remove common words and extract meaningful terms
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        words = re.findall(r'\b\w+\b', task.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:10]  # Limit to top 10 keywords
    
    def _determine_research_scope(self, task: str) -> str:
        """Determine the scope of research needed"""
        if any(term in task.lower() for term in ["comprehensive", "detailed", "thorough"]):
            return "comprehensive"
        elif any(term in task.lower() for term in ["quick", "brief", "summary"]):
            return "brief"
        else:
            return "standard"
    
    def _identify_priority_sources(self, task: str) -> List[str]:
        """Identify priority sources based on the task"""
        sources = []
        
        if "academic" in task.lower() or "research" in task.lower():
            sources.extend(["arxiv", "pubmed", "google_scholar"])
        if "news" in task.lower() or "current" in task.lower():
            sources.extend(["news_apis", "reuters", "bloomberg"])
        if "technology" in task.lower():
            sources.extend(["tech_blogs", "github", "stack_overflow"])
        
        # Default sources
        if not sources:
            sources = ["web_search", "wikipedia", "general_sources"]
        
        return sources
    
    async def _conduct_research(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct the actual research using various sources"""
        results = {
            "sources": [],
            "raw_data": [],
            "metadata": {
                "search_terms": query["search_terms"],
                "scope": query["research_scope"],
                "timestamp": datetime.now().isoformat()
            }
        }
        
        try:
            # Web search
            web_results = await self._web_search(query["search_terms"])
            results["sources"].extend(web_results)
            
            # Academic search (if applicable)
            if "academic" in query.get("priority_sources", []):
                academic_results = await self._academic_search(query["search_terms"])
                results["sources"].extend(academic_results)
            
            # News search (if applicable)
            if any(source in query.get("priority_sources", []) for source in ["news_apis", "reuters"]):
                news_results = await self._news_search(query["search_terms"])
                results["sources"].extend(news_results)
            
            logger.info(f"Research completed: {len(results['sources'])} sources found")
            
        except Exception as e:
            logger.error(f"Research execution failed: {e}")
            results["error"] = str(e)
        
        return results
    
    async def _web_search(self, search_terms: List[str]) -> List[Dict[str, Any]]:
        """Simulate web search (implement with actual search APIs)"""
        # Placeholder for web search implementation
        # In reality, you'd integrate with Google Search API, Bing API, etc.
        
        await asyncio.sleep(1)  # Simulate API call
        
        return [
            {
                "source": "web_search",
                "title": f"Search result for {', '.join(search_terms[:3])}",
                "url": "https://example.com/search-result",
                "snippet": f"Relevant information about {search_terms[0]} and related topics...",
                "relevance_score": 0.85,
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    async def _academic_search(self, search_terms: List[str]) -> List[Dict[str, Any]]:
        """Simulate academic paper search"""
        await asyncio.sleep(1.5)  # Simulate API call
        
        return [
            {
                "source": "academic",
                "title": f"Academic paper on {search_terms[0]}",
                "authors": ["Dr. Smith", "Prof. Johnson"],
                "journal": "Journal of Advanced Research",
                "year": 2024,
                "abstract": f"This paper explores {search_terms[0]} and its implications...",
                "relevance_score": 0.92,
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    async def _news_search(self, search_terms: List[str]) -> List[Dict[str, Any]]:
        """Simulate news search"""
        await asyncio.sleep(0.8)  # Simulate API call
        
        return [
            {
                "source": "news",
                "title": f"Latest news on {search_terms[0]}",
                "publication": "Tech News Daily",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "summary": f"Recent developments in {search_terms[0]} show promising trends...",
                "relevance_score": 0.78,
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    async def _synthesize_findings(self, research_results: Dict[str, Any]) -> str:
        """Synthesize research findings into a coherent summary"""
        sources = research_results.get("sources", [])
        
        if not sources:
            return "No relevant sources found for the research query."
        
        # Simple synthesis (can be enhanced with LLM)
        synthesis_parts = []
        
        # Group sources by type
        web_sources = [s for s in sources if s.get("source") == "web_search"]
        academic_sources = [s for s in sources if s.get("source") == "academic"]
        news_sources = [s for s in sources if s.get("source") == "news"]
        
        if web_sources:
            synthesis_parts.append(f"Web research reveals {len(web_sources)} relevant sources with key insights.")
        
        if academic_sources:
            synthesis_parts.append(f"Academic literature provides {len(academic_sources)} scholarly perspectives.")
        
        if news_sources:
            synthesis_parts.append(f"Current news coverage includes {len(news_sources)} recent developments.")
        
        # Calculate average relevance
        avg_relevance = sum(s.get("relevance_score", 0) for s in sources) / len(sources) if sources else 0
        
        synthesis_parts.append(f"Overall research quality score: {avg_relevance:.2f}")
        
        return " ".join(synthesis_parts)
    
    def _assess_research_quality(self, research_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality of research results"""
        sources = research_results.get("sources", [])
        
        return {
            "total_sources": len(sources),
            "source_diversity": len(set(s.get("source") for s in sources)),
            "average_relevance": sum(s.get("relevance_score", 0) for s in sources) / len(sources) if sources else 0,
            "quality_score": min(len(sources) / 5, 1.0),  # Normalized quality score
            "completeness": "high" if len(sources) >= 5 else "medium" if len(sources) >= 2 else "low"
        }
    
    def _store_research_record(self, task: str, results: Dict[str, Any], synthesis: str):
        """Store research record for future reference"""
        record = {
            "task": task,
            "timestamp": datetime.now().isoformat(),
            "results_summary": {
                "total_sources": len(results.get("sources", [])),
                "synthesis": synthesis[:100] + "..." if len(synthesis) > 100 else synthesis
            }
        }
        
        self.research_history.append(record)
        
        # Keep only last 50 records
        if len(self.research_history) > 50:
            self.research_history = self.research_history[-50:]
    
    def get_research_history(self) -> List[Dict[str, Any]]:
        """Get research history"""
        return self.research_history.copy()
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities"""
        return {
            "primary_function": "Research and information gathering",
            "specializations": [
                "Web search and scraping",
                "Academic paper analysis", 
                "News and current events research",
                "Data synthesis and summarization"
            ],
            "tools": [
                "Multi-source search",
                "Content extraction",
                "Relevance scoring",
                "Information synthesis"
            ],
            "performance_metrics": {
                "research_sessions": len(self.research_history),
                "average_sources_per_task": sum(r.get("results_summary", {}).get("total_sources", 0) 
                                               for r in self.research_history) / max(len(self.research_history), 1)
            }
        }
