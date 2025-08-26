#!/usr/bin/env python3
"""
Simplified Personal Document Assistant Server for testing
"""

import logging
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test all our imports"""
    try:
        logger.info("Testing imports...")
        
        from processing.parsers import DocumentParserFactory
        logger.info("✅ Document parsers imported")
        
        from processing.text_processor import TextProcessor
        logger.info("✅ Text processor imported")
        
        from storage.vector_store import VectorStore
        logger.info("✅ Vector store imported")
        
        from storage.document_store import DocumentStore
        logger.info("✅ Document store imported")
        
        from rag.generation import RAGGenerator
        logger.info("✅ RAG generator imported")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return False

def test_components():
    """Test component initialization"""
    try:
        logger.info("Testing component initialization...")
        
        from processing.parsers import DocumentParserFactory
        parser = DocumentParserFactory()
        logger.info("✅ Parser factory created")
        
        from processing.text_processor import TextProcessor
        processor = TextProcessor()
        logger.info("✅ Text processor created")
        
        from storage.vector_store import VectorStore
        vector_store = VectorStore()
        logger.info("✅ Vector store created")
        
        from storage.document_store import DocumentStore
        doc_store = DocumentStore()
        logger.info("✅ Document store created")
        
        from rag.generation import RAGGenerator
        generator = RAGGenerator()
        logger.info("✅ RAG generator created")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Component initialization failed: {e}")
        return False

def test_ollama_connection():
    """Test Ollama connection"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Ollama is running and accessible")
            return True
        else:
            logger.error("❌ Ollama returned non-200 status")
            return False
    except Exception as e:
        logger.error(f"❌ Cannot connect to Ollama: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Personal Document Assistant - Component Test")
    logger.info("=" * 50)
    
    # Test imports
    if not test_imports():
        logger.error("Import test failed")
        return False
    
    # Test component initialization
    if not test_components():
        logger.error("Component test failed")
        return False
    
    # Test Ollama connection
    if not test_ollama_connection():
        logger.warning("Ollama connection test failed - server may not be running")
    
    logger.info("=" * 50)
    logger.info("✅ All tests completed successfully!")
    logger.info("")
    logger.info("The server components are ready to use.")
    logger.info("To use with VS Code:")
    logger.info("1. Install MCP extension in VS Code")
    logger.info("2. Add server configuration to settings.json")
    logger.info("3. Start using document upload and query tools")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
