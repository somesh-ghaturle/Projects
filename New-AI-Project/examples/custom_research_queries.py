"""
Example: How to add research queries programmatically in your code
"""

import asyncio
from agents.researcher_agent import ResearcherAgent


async def custom_research_example():
    """Example of how to add research queries in your code"""
    
    # Initialize the research agent
    researcher = ResearcherAgent()
    await researcher.start()
    
    # Your custom research queries
    my_research_queries = [
        "What are the latest breakthroughs in renewable energy?",
        "How is AI being used in medical diagnosis?", 
        "What are the economic impacts of remote work?",
        "Future trends in electric vehicle technology",
        "Cybersecurity challenges in IoT devices"
    ]
    
    results = []
    
    for query in my_research_queries:
        print(f"🔍 Researching: {query}")
        
        # Execute research
        result = await researcher.execute(query)
        
        if result["status"] == "completed":
            print(f"✅ Found {result['sources_found']} sources")
            print(f"📊 Quality Score: {result['research_quality']['quality_score']:.2f}")
            print(f"📝 Summary: {result['synthesis'][:150]}...\n")
            
            results.append({
                "query": query,
                "sources": result['sources_found'],
                "quality": result['research_quality']['quality_score'],
                "summary": result['synthesis']
            })
    
    # Stop the agent
    await researcher.stop()
    
    return results


async def single_query_example():
    """Example of researching a single query"""
    
    researcher = ResearcherAgent()
    await researcher.start()
    
    # Your specific research query
    my_query = "What are the environmental benefits of vertical farming?"
    
    result = await researcher.execute(my_query)
    
    await researcher.stop()
    
    return result


# Configuration-based queries
class ResearchConfig:
    """Configuration class for organizing research queries"""
    
    TECHNOLOGY_QUERIES = [
        "Latest developments in quantum computing",
        "AI ethics and responsible development",
        "Blockchain applications beyond cryptocurrency"
    ]
    
    HEALTH_QUERIES = [
        "Personalized medicine and genomics",
        "Mental health technology solutions",
        "Telemedicine adoption and effectiveness"
    ]
    
    ENVIRONMENT_QUERIES = [
        "Carbon capture technology advances",
        "Sustainable agriculture practices",
        "Ocean cleanup and marine conservation"
    ]


async def research_by_category(category: str):
    """Research queries organized by category"""
    
    config = ResearchConfig()
    
    query_map = {
        "technology": config.TECHNOLOGY_QUERIES,
        "health": config.HEALTH_QUERIES, 
        "environment": config.ENVIRONMENT_QUERIES
    }
    
    if category not in query_map:
        raise ValueError(f"Unknown category: {category}")
    
    researcher = ResearcherAgent()
    await researcher.start()
    
    results = []
    for query in query_map[category]:
        result = await researcher.execute(query)
        results.append(result)
    
    await researcher.stop()
    return results


if __name__ == "__main__":
    # Run custom research
    asyncio.run(custom_research_example())
