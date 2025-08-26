"""
Multi-Agent AI Research Assistant - Main Entry Point
"""

import asyncio
import logging
from dotenv import load_dotenv

from config.settings import settings
from core.base import Application
from agents.researcher_agent import ResearcherAgent
from workflows.research_workflow import create_research_workflow
from crews.research_crew import create_research_crew

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def demo_agentic_research():
    """Demonstrate the agentic AI research capabilities"""
    logger.info("🤖 Starting Multi-Agent AI Research Assistant Demo")
    print("\n" + "="*60)
    print("🚀 AGENTECH RESEARCH HUB")
    print("="*60)
    
    try:
        # Initialize components
        
        # Create research agent
        researcher = ResearcherAgent()
        await researcher.start()
        
        # Create research workflow
        workflow = create_research_workflow()
        
        # Create research crew
        crew = create_research_crew()
        
        # Demo research queries
        research_queries = [
            "Latest developments in artificial intelligence and machine learning",
            "Impact of quantum computing on cybersecurity", 
            "Sustainable energy solutions for 2024",
            # Add your custom research queries here:
            "Future of blockchain technology in finance",
            "Climate change adaptation strategies for coastal cities",
            "Advances in gene therapy for rare diseases",
            "The role of AI in space exploration missions"
        ]
        
        print(f"\n🔍 Conducting research on {len(research_queries)} topics...")
        
        for i, query in enumerate(research_queries, 1):
            print(f"\n--- Research Query {i}/{len(research_queries)} ---")
            print(f"📋 Topic: {query}")
            
            # Method 1: Individual Agent Research
            print("\n🤖 Individual Agent Research:")
            agent_result = await researcher.execute(query)
            if agent_result["status"] == "completed":
                print(f"✅ Sources found: {agent_result['sources_found']}")
                print(f"📊 Quality: {agent_result['research_quality']['quality_score']:.2f}")
                
                # Show first source in demo mode
                sources = agent_result.get('sources', [])
                if sources:
                    first_source = sources[0]
                    source_type = first_source.get('source', 'unknown')
                    title = first_source.get('title', 'No title')
                    url = first_source.get('url', 'No URL')
                    print(f"🔗 Sample Source: [{source_type.upper()}] {title}")
                    if url != 'No URL':
                        print(f"    🌐 {url}")
                
                print(f"📝 Synthesis: {agent_result['synthesis'][:100]}...")
            
            # Method 2: Workflow-based Research
            print("\n🔄 Workflow-based Research:")
            workflow_result = await workflow.execute_workflow(query)
            if workflow_result["status"] == "completed":
                final_state = workflow_result["results"]
                print(f"✅ Quality Score: {final_state['quality_score']:.2f}")
                print(f"⏱️  Processing Time: {final_state['metadata'].get('processing_duration_seconds', 0):.1f}s")
                print(f"📝 Synthesis: {final_state['synthesis'][:100]}...")
            
            # Method 3: Crew-based Research (if available)
            print("\n👥 Crew-based Research:")
            try:
                crew_result = await crew.execute_research(query)
                if crew_result["status"] == "completed":
                    print(f"✅ Crew completed with {crew_result['agents_used']} agents")
                    print(f"📋 Tasks completed: {crew_result['tasks_completed']}")
                else:
                    print(f"⚠️  Crew research: {crew_result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"⚠️  Crew functionality requires full installation: {str(e)[:50]}...")
            
            if i < len(research_queries):
                print("\n⏳ Waiting before next query...")
                await asyncio.sleep(1)
        
        # Display system capabilities
        print(f"\n" + "="*60)
        print("📊 SYSTEM CAPABILITIES SUMMARY")
        print("="*60)
        
        # Agent capabilities
        agent_caps = await researcher.get_capabilities()
        print(f"\n🤖 Research Agent:")
        print(f"  • Function: {agent_caps['primary_function']}")
        print(f"  • Sessions: {agent_caps['performance_metrics']['research_sessions']}")
        print(f"  • Avg Sources: {agent_caps['performance_metrics']['average_sources_per_task']:.1f}")
        
        # Workflow status
        workflow_status = workflow.get_workflow_status()
        print(f"\n🔄 Research Workflow:")
        print(f"  • LangGraph Available: {workflow_status['langgraph_available']}")
        print(f"  • Executions: {workflow_status['executions_completed']}")
        print(f"  • Avg Quality: {workflow_status['average_quality_score']:.2f}")
        print(f"  • Avg Time: {workflow_status['average_processing_time']:.1f}s")
        
        # Crew status
        crew_status = crew.get_crew_status()
        print(f"\n👥 Research Crew:")
        print(f"  • Agents: {len(crew_status['agents'])}")
        print(f"  • Process: {crew_status['process_type']}")
        print(f"  • Ready: {crew_status['crew_ready']}")
        
        print(f"\n✅ Demo completed successfully!")
        
        # Stop agent
        await researcher.stop()
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n❌ Demo failed: {e}")


async def interactive_research_mode():
    """Interactive mode for custom research queries"""
    print(f"\n" + "="*60)
    print("🎯 INTERACTIVE RESEARCH MODE")
    print("="*60)
    print("Enter research queries (type 'quit' to exit)")
    print("💡 Powered by AgenTech Research Hub")
    
    # Initialize research agent
    researcher = ResearcherAgent()
    await researcher.start()
    
    try:
        while True:
            query = input("\n🔍 Research Query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            print(f"\n🤖 Researching: {query}")
            print("⏳ Processing...")
            
            result = await researcher.execute(query)
            
            if result["status"] == "completed":
                print(f"\n✅ Research Complete!")
                print(f"📊 Sources: {result['sources_found']}")
                print(f"🎯 Quality: {result['research_quality']['quality_score']:.2f}")
                
                # Display source links
                sources = result.get('sources', [])
                if sources:
                    print(f"\n🔗 Sources Found:")
                    for i, source in enumerate(sources, 1):
                        source_type = source.get('source', 'unknown')
                        title = source.get('title', 'No title available')
                        url = source.get('url', 'No URL available')
                        
                        print(f"   {i}. [{source_type.upper()}] {title}")
                        if url != 'No URL available':
                            print(f"      🌐 {url}")
                        
                        # Add snippet if available
                        if 'snippet' in source:
                            snippet = source['snippet'][:100] + "..." if len(source['snippet']) > 100 else source['snippet']
                            print(f"      📄 {snippet}")
                        elif 'abstract' in source:
                            abstract = source['abstract'][:100] + "..." if len(source['abstract']) > 100 else source['abstract']
                            print(f"      📄 {abstract}")
                        print()  # Empty line for spacing
                
                print(f"📝 Summary:")
                print(result['synthesis'])
            else:
                print(f"\n❌ Research failed: {result.get('error', 'Unknown error')}")
    
    except KeyboardInterrupt:
        print(f"\n\n👋 Research session ended by user")
    finally:
        await researcher.stop()


async def main():
    """Main application entry point"""
    try:
        # Load settings
        logger.info(f"Starting AgenTech Research Hub v1.0.0")
        
        print(f"\n🤖 AGENTECH RESEARCH HUB")
        print("Choose mode:")
        print("1. Demo Mode - Automated research examples")
        print("2. Interactive Mode - Custom research queries")
        print("3. API Mode - Start REST API server")
        
        while True:
            try:
                choice = input("\nSelect mode (1-3, or 'q' to quit): ").strip()
                
                if choice.lower() in ['q', 'quit', 'exit']:
                    break
                elif choice == '1':
                    await demo_agentic_research()
                    break
                elif choice == '2':
                    await interactive_research_mode()
                    break
                elif choice == '3':
                    print("\n🌐 Starting API server...")
                    print("Run: uvicorn src.api.routes:router --reload --host 0.0.0.0 --port 8000")
                    break
                else:
                    print("❌ Invalid choice. Please select 1, 2, 3, or 'q'")
            except KeyboardInterrupt:
                print(f"\n\n👋 Goodbye!")
                break
        
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        print(f"❌ Application error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
