"""
Research Crew - CrewAI configuration for research tasks
"""

import logging
from typing import List, Dict, Any, Optional
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool

logger = logging.getLogger(__name__)


@tool
def web_search_tool(query: str) -> str:
    """Search the web for information on a given query"""
    # Placeholder for actual web search implementation
    return f"Web search results for: {query}"


@tool
def academic_search_tool(query: str) -> str:
    """Search academic databases for scholarly articles"""
    # Placeholder for academic search implementation
    return f"Academic search results for: {query}"


@tool
def news_search_tool(query: str) -> str:
    """Search news sources for current information"""
    # Placeholder for news search implementation
    return f"News search results for: {query}"


class ResearchCrew:
    """CrewAI-based research crew for collaborative research tasks"""
    
    def __init__(self, llm_config: Optional[Dict[str, Any]] = None):
        """Initialize the research crew"""
        self.llm_config = llm_config or {}
        self.crew = None
        self._setup_crew()
    
    def _setup_crew(self):
        """Set up the research crew with agents and tools"""
        
        # Define research specialist agent
        research_specialist = Agent(
            role='Research Specialist',
            goal='Conduct comprehensive research on assigned topics',
            backstory="""You are an expert researcher with years of experience in 
            gathering information from multiple sources, analyzing data, and 
            synthesizing findings into coherent insights.""",
            verbose=True,
            allow_delegation=False,
            tools=[web_search_tool, academic_search_tool, news_search_tool]
        )
        
        # Define information analyst agent
        information_analyst = Agent(
            role='Information Analyst',
            goal='Analyze and synthesize research findings',
            backstory="""You are a skilled analyst who excels at identifying 
            patterns, drawing connections between different pieces of information, 
            and creating structured analysis reports.""",
            verbose=True,
            allow_delegation=False,
            tools=[web_search_tool]
        )
        
        # Define quality reviewer agent
        quality_reviewer = Agent(
            role='Quality Reviewer',
            goal='Review and validate research quality',
            backstory="""You are a meticulous reviewer who ensures research 
            meets high standards of accuracy, completeness, and reliability. 
            You identify gaps and suggest improvements.""",
            verbose=True,
            allow_delegation=False
        )
        
        self.agents = {
            'researcher': research_specialist,
            'analyst': information_analyst,
            'reviewer': quality_reviewer
        }
    
    def create_research_tasks(self, research_query: str, context: Optional[Dict[str, Any]] = None) -> List[Task]:
        """Create research tasks for the crew"""
        
        context = context or {}
        
        # Research task
        research_task = Task(
            description=f"""
            Conduct comprehensive research on: {research_query}
            
            Context: {context}
            
            Requirements:
            1. Search multiple sources (web, academic, news)
            2. Gather relevant and credible information
            3. Document all sources with proper citations
            4. Organize findings by relevance and credibility
            
            Expected Output: Detailed research findings with source citations
            """,
            agent=self.agents['researcher'],
            expected_output="Comprehensive research report with multiple sources"
        )
        
        # Analysis task
        analysis_task = Task(
            description=f"""
            Analyze the research findings from the previous task about: {research_query}
            
            Requirements:
            1. Identify key themes and patterns
            2. Synthesize information from multiple sources
            3. Highlight important insights and conclusions
            4. Note any conflicting information or gaps
            
            Expected Output: Analytical synthesis of research findings
            """,
            agent=self.agents['analyst'],
            expected_output="Structured analysis with key insights and synthesis"
        )
        
        # Quality review task
        review_task = Task(
            description=f"""
            Review the research and analysis for: {research_query}
            
            Requirements:
            1. Assess completeness and accuracy of research
            2. Verify source credibility and citations
            3. Check for logical consistency in analysis
            4. Identify any missing important aspects
            5. Provide recommendations for improvement
            
            Expected Output: Quality assessment report with recommendations
            """,
            agent=self.agents['reviewer'],
            expected_output="Quality review with assessment and recommendations"
        )
        
        return [research_task, analysis_task, review_task]
    
    async def execute_research(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute research using the crew"""
        
        try:
            logger.info(f"Starting crew research for: {query}")
            
            # Create tasks
            tasks = self.create_research_tasks(query, context)
            
            # Create crew
            crew = Crew(
                agents=list(self.agents.values()),
                tasks=tasks,
                process=Process.sequential,
                verbose=True
            )
            
            # Execute the crew
            result = crew.kickoff()
            
            logger.info("Crew research completed successfully")
            
            return {
                "query": query,
                "status": "completed",
                "result": result,
                "agents_used": list(self.agents.keys()),
                "tasks_completed": len(tasks)
            }
            
        except Exception as e:
            logger.error(f"Crew research failed: {e}")
            return {
                "query": query,
                "status": "failed", 
                "error": str(e)
            }
    
    def get_crew_status(self) -> Dict[str, Any]:
        """Get the current status of the crew"""
        return {
            "agents": {
                name: {
                    "role": agent.role,
                    "goal": agent.goal,
                    "tools": [tool.name for tool in agent.tools] if agent.tools else []
                }
                for name, agent in self.agents.items()
            },
            "crew_ready": self.crew is not None,
            "process_type": "sequential"
        }


# Factory function for easy crew creation
def create_research_crew(llm_config: Optional[Dict[str, Any]] = None) -> ResearchCrew:
    """Factory function to create a research crew"""
    return ResearchCrew(llm_config)
