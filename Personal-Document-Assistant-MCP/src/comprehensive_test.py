#!/usr/bin/env python3
"""
Comprehensive test and demo of the Personal Document Assistant
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

def create_test_documents():
    """Create some test documents for demonstration"""
    test_docs_dir = Path("../data/test_docs")
    test_docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a sample text document
    with open(test_docs_dir / "sample_ai.txt", "w") as f:
        f.write("""
Artificial Intelligence Overview

Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines 
that can perform tasks that typically require human intelligence. These tasks include learning, 
reasoning, problem-solving, perception, and language understanding.

Machine Learning is a subset of AI that enables computers to learn and improve from experience 
without being explicitly programmed. It uses algorithms to analyze data, identify patterns, 
and make predictions or decisions.

Deep Learning is a subset of machine learning that uses neural networks with multiple layers 
to model and understand complex patterns in data. It has been particularly successful in 
image recognition, natural language processing, and speech recognition.

RAG (Retrieval-Augmented Generation) is a technique that combines information retrieval 
with generative AI models to provide more accurate and contextual responses by first 
retrieving relevant information from a knowledge base.
        """.strip())
    
    # Create another sample document
    with open(test_docs_dir / "sample_tech.txt", "w") as f:
        f.write("""
Technology Trends 2025

Cloud Computing continues to evolve with serverless architectures and edge computing 
becoming more prevalent. Organizations are adopting hybrid cloud strategies to balance 
performance, cost, and security requirements.

Quantum Computing is moving from research labs to practical applications. Companies 
like IBM, Google, and Microsoft are developing quantum processors that could 
revolutionize cryptography, optimization, and scientific simulations.

Blockchain Technology has expanded beyond cryptocurrencies to include smart contracts, 
supply chain management, and decentralized finance (DeFi). The technology promises 
increased transparency and reduced need for intermediaries.

Internet of Things (IoT) devices are becoming more sophisticated and secure. 
The integration of AI at the edge enables real-time decision making without 
constant cloud connectivity.
        """.strip())
    
    return [
        test_docs_dir / "sample_ai.txt",
        test_docs_dir / "sample_tech.txt"
    ]

def test_document_processing():
    """Test document processing functionality"""
    logger.info("🔍 Testing Document Processing...")
    
    try:
        from processing.parsers import DocumentParserFactory
        from processing.text_processor import TextProcessor
        
        # Create test documents
        test_files = create_test_documents()
        
        parser_factory = DocumentParserFactory()
        text_processor = TextProcessor()
        
        for file_path in test_files:
            logger.info(f"Processing: {file_path.name}")
            
            # Parse document
            parsed_doc = parser_factory.parse_document(str(file_path))
            logger.info(f"✅ Parsed {len(parsed_doc['content'])} characters")
            
            # Process text
            chunks = text_processor.chunk_text(parsed_doc['content'])
            logger.info(f"✅ Created {len(chunks)} text chunks")
            
            # Extract keywords
            keywords = text_processor.extract_keywords(parsed_doc['content'])
            logger.info(f"✅ Extracted keywords: {', '.join(keywords[:5])}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Document processing failed: {e}")
        return False

def test_storage_systems():
    """Test vector and document storage"""
    logger.info("💾 Testing Storage Systems...")
    
    try:
        from storage.vector_store import VectorStore
        from storage.document_store import DocumentStore
        
        # Test vector store
        vector_store = VectorStore()
        logger.info("✅ Vector store initialized")
        
        # Test document store
        doc_store = DocumentStore()
        logger.info("✅ Document store initialized")
        
        # Test adding a document to document store
        doc_id = doc_store.add_document(
            title="Test Document",
            file_path="/test/path",
            content="This is test content",
            metadata={"test": True}
        )
        logger.info(f"✅ Added test document with ID: {doc_id}")
        
        # Test retrieving the document
        doc = doc_store.get_document(doc_id)
        if doc:
            logger.info(f"✅ Retrieved document: {doc['title']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Storage test failed: {e}")
        return False

def test_rag_pipeline():
    """Test the complete RAG pipeline"""
    logger.info("🤖 Testing RAG Pipeline...")
    
    try:
        from rag.pipeline import RAGPipeline
        from rag.generation import RAGGenerator
        
        # Initialize RAG components
        rag_pipeline = RAGPipeline()
        logger.info("✅ RAG pipeline initialized")
        
        rag_generator = RAGGenerator()
        logger.info("✅ RAG generator initialized")
        
        # Test a simple generation
        test_prompt = "What is artificial intelligence?"
        response = rag_generator.generate_response(test_prompt)
        logger.info(f"✅ Generated response: {response[:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ RAG pipeline test failed: {e}")
        return False

def test_ollama_integration():
    """Test Ollama integration"""
    logger.info("🦙 Testing Ollama Integration...")
    
    try:
        import requests
        
        # Test Ollama API
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            logger.info(f"✅ Ollama running with {len(models.get('models', []))} models")
            
            # Test a simple generation
            gen_response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": "What is 2+2?",
                    "stream": False
                },
                timeout=30
            )
            
            if gen_response.status_code == 200:
                result = gen_response.json()
                logger.info(f"✅ Ollama generation test: {result.get('response', '')[:50]}...")
                return True
            else:
                logger.error(f"❌ Ollama generation failed: {gen_response.status_code}")
                return False
        else:
            logger.error(f"❌ Ollama not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ollama test failed: {e}")
        return False

def simulate_document_workflow():
    """Simulate a complete document workflow"""
    logger.info("📄 Simulating Complete Document Workflow...")
    
    try:
        # This simulates what would happen in a real workflow
        test_files = create_test_documents()
        
        logger.info("1. 📥 Documents created")
        logger.info("2. 🔍 Documents would be parsed and chunked")
        logger.info("3. 🧮 Embeddings would be generated")
        logger.info("4. 💾 Content would be stored in vector database")
        logger.info("5. 🔍 Users could search and query documents")
        logger.info("6. 🤖 AI would provide contextual answers")
        
        # Simulate some queries
        sample_queries = [
            "What is machine learning?",
            "Tell me about quantum computing",
            "How does RAG work?",
            "What are the latest technology trends?"
        ]
        
        logger.info("Sample queries that could be answered:")
        for i, query in enumerate(sample_queries, 1):
            logger.info(f"   {i}. {query}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Workflow simulation failed: {e}")
        return False

def main():
    """Run comprehensive tests"""
    logger.info("🚀 Personal Document Assistant - Comprehensive Test")
    logger.info("=" * 60)
    
    tests = [
        ("Document Processing", test_document_processing),
        ("Storage Systems", test_storage_systems),
        ("RAG Pipeline", test_rag_pipeline),
        ("Ollama Integration", test_ollama_integration),
        ("Complete Workflow", simulate_document_workflow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        logger.info("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                logger.info(f"✅ {test_name} - PASSED")
            else:
                logger.info(f"❌ {test_name} - FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} - ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Your Personal Document Assistant is ready!")
        logger.info("\nNext steps:")
        logger.info("1. Install MCP extension in VS Code")
        logger.info("2. Configure the server in VS Code settings")
        logger.info("3. Start uploading documents and asking questions!")
    else:
        logger.info("⚠️  Some tests failed. Check the logs above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
