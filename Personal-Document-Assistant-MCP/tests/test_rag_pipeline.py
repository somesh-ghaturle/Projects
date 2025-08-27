"""
Test the RAG pipeline with sample documents.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag.pipeline import RAGPipeline

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_rag_pipeline():
    """Test the RAG pipeline with sample documents."""
    
    # Initialize pipeline
    config = {
        "vector_store": {
            "persist_directory": "./data/chroma_db",
            "collection_name": "documents"
        },
        "document_store": {
            "database_path": "./data/documents.db"
        },
        "generation": {
            "llm_base_url": "http://localhost:11434",
            "llm_model": "llama3.2"
        }
    }
    
    pipeline = RAGPipeline(config)
    
    # Create test documents
    test_docs = [
        {
            "title": "Python Programming Guide",
            "content": """
            Python is a high-level programming language known for its simplicity and readability.
            It supports multiple programming paradigms including procedural, object-oriented, and functional programming.
            Python has a vast ecosystem of libraries and frameworks that make it suitable for web development,
            data science, machine learning, automation, and more.
            
            Key features of Python:
            - Simple and readable syntax
            - Dynamically typed
            - Interpreted language
            - Extensive standard library
            - Cross-platform compatibility
            """
        },
        {
            "title": "Machine Learning Basics",
            "content": """
            Machine Learning is a subset of artificial intelligence that enables computers to learn
            and make decisions from data without being explicitly programmed.
            
            Types of Machine Learning:
            1. Supervised Learning: Uses labeled data to train models
            2. Unsupervised Learning: Finds patterns in unlabeled data
            3. Reinforcement Learning: Learns through interaction with environment
            
            Common algorithms include linear regression, decision trees, neural networks,
            and support vector machines. Data preprocessing is crucial for model performance.
            """
        },
        {
            "title": "Web Development with Python",
            "content": """
            Python offers several frameworks for web development:
            
            Flask: A lightweight micro-framework for small to medium applications.
            It's minimalistic and gives developers flexibility in choosing components.
            
            Django: A full-featured framework that follows the "batteries included" philosophy.
            It includes ORM, admin interface, authentication, and many other features.
            
            FastAPI: A modern framework for building APIs with automatic documentation
            and type hints support. It's designed for high performance and easy testing.
            """
        }
    ]
    
    try:
        # Add test documents
        document_ids = []
        for doc in test_docs:
            # Create a temporary file
            temp_file = f"./data/temp_{doc['title'].replace(' ', '_')}.txt"
            os.makedirs(os.path.dirname(temp_file), exist_ok=True)
            
            with open(temp_file, 'w') as f:
                f.write(doc['content'])
            
            result = await pipeline.add_document(temp_file, doc['title'])
            if result['success']:
                document_ids.append(result['document_id'])
                logger.info(f"Added document: {doc['title']} (ID: {result['document_id']})")
            else:
                logger.error(f"Failed to add document: {result.get('error')}")
        
        # Test queries
        test_queries = [
            "What is Python?",
            "Explain machine learning types",
            "Which Python web framework should I choose?",
            "How do neural networks work?",
            "Compare Flask and Django"
        ]
        
        for query in test_queries:
            logger.info(f"\n{'='*50}")
            logger.info(f"Query: {query}")
            logger.info(f"{'='*50}")
            
            result = await pipeline.query(query, top_k=3)
            
            if result['success']:
                print(f"\nAnswer: {result['response']}")
                print(f"\nSources ({len(result['sources'])}):")
                for i, source in enumerate(result['sources'], 1):
                    print(f"{i}. {source['document_title']} (Score: {source['relevance_score']:.2f})")
                    print(f"   {source['chunk_text']}")
            else:
                print(f"Error: {result['error']}")
        
        # Test document search
        logger.info(f"\n{'='*50}")
        logger.info("Testing document search")
        logger.info(f"{'='*50}")
        
        search_results = await pipeline.search_documents("Python frameworks", search_type="hybrid")
        print(f"\nFound {len(search_results)} documents for 'Python frameworks':")
        for result in search_results:
            doc = result['document']
            print(f"- {doc['title']} (Score: {result['total_score']:.2f})")
        
        # Test statistics
        logger.info(f"\n{'='*50}")
        logger.info("System Statistics")
        logger.info(f"{'='*50}")
        
        stats = await pipeline.get_statistics()
        print(f"\nSystem Statistics:")
        print(f"Total documents: {stats['documents']['total_documents']}")
        print(f"Total chunks: {stats['documents']['total_chunks']}")
        print(f"Total characters: {stats['documents']['total_characters']}")
        
        # Test health check
        health = await pipeline.health_check()
        print(f"\nHealth Check: {health['overall']}")
        for component, status in health['components'].items():
            print(f"- {component}: {status}")
        
        # Clean up temporary files
        for doc in test_docs:
            temp_file = f"./data/temp_{doc['title'].replace(' ', '_')}.txt"
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        logger.info("\nTest completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(test_rag_pipeline())
