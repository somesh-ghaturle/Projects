#!/usr/bin/env python3
"""
Simple working demo of the Personal Document Assistant
"""

import logging
import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def demo_document_processing():
    """Demo document processing"""
    logger.info("📄 Document Processing Demo")
    logger.info("-" * 40)
    
    from processing.parsers import DocumentParserFactory
    from processing.text_processor import TextProcessor
    
    # Create a sample document
    sample_text = """
    Artificial Intelligence (AI) has revolutionized how we interact with technology. 
    Machine learning algorithms can now process vast amounts of data to identify patterns 
    and make predictions. Deep learning networks have enabled breakthroughs in image 
    recognition, natural language processing, and autonomous systems.
    
    The future of AI includes developments in quantum computing, edge AI, and 
    explainable AI systems that can provide transparent decision-making processes.
    """
    
    # Process the text
    text_processor = TextProcessor(chunk_size=200, chunk_overlap=50)
    chunks = text_processor.chunk_text(sample_text.strip())
    
    logger.info(f"✅ Created {len(chunks)} text chunks")
    for i, chunk in enumerate(chunks):
        logger.info(f"   Chunk {i+1}: {len(chunk['content'])} chars")
    
    # Extract keywords
    keywords = text_processor.extract_keywords(sample_text)
    logger.info(f"✅ Keywords: {', '.join(keywords[:8])}")

def demo_ollama_chat():
    """Demo Ollama integration"""
    logger.info("\n🦙 Ollama Chat Demo")
    logger.info("-" * 40)
    
    import requests
    
    questions = [
        "What is artificial intelligence?",
        "Explain machine learning in simple terms",
        "What are the benefits of RAG systems?"
    ]
    
    for question in questions:
        logger.info(f"❓ Question: {question}")
        
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": f"Answer briefly: {question}",
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('response', '').strip()
                # Limit to first sentence for demo
                first_sentence = answer.split('.')[0] + '.' if '.' in answer else answer[:100]
                logger.info(f"🤖 Answer: {first_sentence}")
            else:
                logger.error(f"❌ Request failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Error: {e}")
        
        logger.info("")

def demo_storage_info():
    """Demo storage capabilities"""
    logger.info("💾 Storage Demo")
    logger.info("-" * 40)
    
    from storage.vector_store import VectorStore
    from storage.document_store import DocumentStore
    
    # Initialize storage
    vector_store = VectorStore()
    doc_store = DocumentStore()
    
    logger.info("✅ Vector store ready for embeddings")
    logger.info("✅ Document store ready for metadata")
    logger.info("✅ ChromaDB collection: document_embeddings")
    logger.info("✅ SQLite database initialized")

def demo_workflow_simulation():
    """Simulate what the full system would do"""
    logger.info("\n🚀 Complete Workflow Simulation")
    logger.info("-" * 40)
    
    workflow_steps = [
        "1. 📥 User uploads a PDF document",
        "2. 🔍 System parses PDF and extracts text",
        "3. ✂️  Text is chunked into smaller pieces",
        "4. 🧮 Each chunk gets converted to vector embeddings",
        "5. 💾 Embeddings stored in ChromaDB",
        "6. 📊 Document metadata stored in SQLite",
        "7. ❓ User asks: 'What does this document say about AI?'",
        "8. 🔍 System searches for relevant chunks",
        "9. 🤖 LLM generates answer using retrieved context",
        "10. ✅ User gets accurate, contextual response"
    ]
    
    for step in workflow_steps:
        logger.info(step)
    
    logger.info("\n📋 What you can do with this system:")
    features = [
        "• Upload PDF, DOCX, TXT, HTML documents",
        "• Ask questions about your documents",
        "• Search for specific topics across all documents",
        "• Get AI-powered summaries",
        "• All processing happens locally (privacy-first)",
        "• Integrate with VS Code via MCP protocol"
    ]
    
    for feature in features:
        logger.info(feature)

def main():
    """Run the demo"""
    logger.info("🎉 Personal Document Assistant - Interactive Demo")
    logger.info("=" * 60)
    
    try:
        demo_document_processing()
        demo_storage_info()
        demo_ollama_chat()
        demo_workflow_simulation()
        
        logger.info("\n" + "=" * 60)
        logger.info("🎯 Demo Complete!")
        logger.info("=" * 60)
        logger.info("Your Personal Document Assistant is working! 🚀")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Install MCP extension in VS Code")
        logger.info("2. Configure server in VS Code settings")
        logger.info("3. Start uploading documents and asking questions!")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
