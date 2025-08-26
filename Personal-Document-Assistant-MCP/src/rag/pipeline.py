"""
Main RAG pipeline that orchestrates all components.
"""

import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from processing.parsers import DocumentParserFactory
from processing.text_processor import TextProcessor
from storage.vector_store import VectorStore
from storage.document_store import DocumentStore
from rag.generation import RAGGenerator

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Main RAG pipeline that orchestrates document processing and query answering."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the RAG pipeline with all components."""
        self.config = config or {}
        
        # Initialize components
        self.parser = DocumentParserFactory()
        self.text_processor = TextProcessor()
        self.vector_store = VectorStore()
        self.document_store = DocumentStore()
        self.generator = RAGGenerator(self.config.get("generation", {}))
        
        logger.info("RAG pipeline initialized")
    
    async def add_document(self, file_path: str, title: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a document to the RAG system.
        
        Args:
            file_path: Path to the document file
            title: Optional title (will be inferred if not provided)
        
        Returns:
            Document processing result
        """
        try:
            logger.info(f"Adding document: {file_path}")
            
            # Step 1: Parse the document
            parsed_content = await self.parser.parse_file(file_path)
            if not parsed_content["success"]:
                return {
                    "success": False,
                    "error": f"Failed to parse document: {parsed_content.get('error', 'Unknown error')}"
                }
            
            content = parsed_content["content"]
            metadata = parsed_content["metadata"]
            
            # Use provided title or extract from metadata
            document_title = title or metadata.get("title", file_path.split("/")[-1])
            
            # Check if document already exists
            content_hash = str(hash(content))
            existing_doc_id = await self.document_store.document_exists(file_path, content_hash)
            if existing_doc_id:
                logger.info(f"Document already exists: {existing_doc_id}")
                return {
                    "success": True,
                    "document_id": existing_doc_id,
                    "message": "Document already exists",
                    "chunks_added": 0
                }
            
            # Step 2: Store document metadata
            document_id = await self.document_store.add_document(
                title=document_title,
                file_path=file_path,
                content=content,
                metadata=metadata
            )
            
            # Step 3: Chunk the content
            chunks = await self.chunker.chunk_text(content, metadata={"document_id": document_id})
            
            # Step 4: Generate embeddings and store in vector database
            chunk_ids = []
            for chunk in chunks:
                # Generate embedding
                embedding = await self.embedding_generator.generate_embedding(chunk["text"])
                
                # Store in vector database
                chunk_id = await self.vector_store.add_document(
                    text=chunk["text"],
                    embedding=embedding,
                    metadata={
                        **chunk["metadata"],
                        "document_id": document_id,
                        "document_title": document_title
                    }
                )
                chunk_ids.append(chunk_id)
            
            # Step 5: Update document with chunk count
            await self.document_store.update_document(
                document_id,
                chunk_count=len(chunks)
            )
            
            logger.info(f"Successfully added document {document_id} with {len(chunks)} chunks")
            
            return {
                "success": True,
                "document_id": document_id,
                "title": document_title,
                "chunks_added": len(chunks),
                "chunk_ids": chunk_ids,
                "character_count": len(content)
            }
            
        except Exception as e:
            logger.error(f"Failed to add document: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def query(self, question: str, top_k: int = 5, 
                   filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Answer a question using the RAG pipeline.
        
        Args:
            question: User's question
            top_k: Number of relevant documents to retrieve
            filters: Optional filters for document search
        
        Returns:
            Generated answer with sources
        """
        try:
            logger.info(f"Processing query: {question[:100]}...")
            
            # Step 1: Retrieve relevant documents
            relevant_docs = await self.retriever.retrieve_documents(
                query=question,
                top_k=top_k,
                filters=filters
            )
            
            if not relevant_docs:
                return {
                    "success": True,
                    "response": "I couldn't find any relevant documents to answer your question.",
                    "sources": [],
                    "query": question
                }
            
            # Step 2: Generate response
            result = await self.generator.answer_question_types(question, relevant_docs)
            
            return {
                "success": True,
                **result
            }
            
        except Exception as e:
            logger.error(f"Failed to process query: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": question
            }
    
    async def search_documents(self, query: str, search_type: str = "hybrid",
                             top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents using various methods.
        
        Args:
            query: Search query
            search_type: Type of search ('semantic', 'keyword', 'hybrid')
            top_k: Number of results to return
        
        Returns:
            List of matching documents
        """
        try:
            if search_type == "semantic":
                return await self.retriever.retrieve_documents(query, top_k)
            elif search_type == "keyword":
                docs = await self.document_store.list_documents(
                    search_term=query,
                    limit=top_k
                )
                return [{"document": doc, "score": 1.0} for doc in docs]
            elif search_type == "hybrid":
                return await self.retriever.hybrid_search(query, top_k=top_k)
            else:
                raise ValueError(f"Unknown search type: {search_type}")
                
        except Exception as e:
            logger.error(f"Failed to search documents: {str(e)}")
            return []
    
    async def get_document_info(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a document."""
        try:
            doc_info = await self.document_store.get_document(document_id)
            if not doc_info:
                return None
            
            # Get document chunks
            chunks = await self.vector_store.search(
                query="",
                filters={"document_id": document_id},
                top_k=1000  # Get all chunks
            )
            
            return {
                **doc_info,
                "chunks": len(chunks),
                "sample_chunks": [chunk["text"][:200] + "..." for chunk in chunks[:3]]
            }
            
        except Exception as e:
            logger.error(f"Failed to get document info: {str(e)}")
            return None
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and all its chunks."""
        try:
            # Delete from vector store
            await self.vector_store.delete_by_filter({"document_id": document_id})
            
            # Delete from document store
            success = await self.document_store.delete_document(document_id)
            
            logger.info(f"Deleted document: {document_id}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
            return False
    
    async def get_similar_documents(self, document_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find documents similar to a given document."""
        return await self.retriever.get_similar_documents(document_id, top_k)
    
    async def generate_summary(self, document_ids: List[str]) -> str:
        """Generate a summary of multiple documents."""
        try:
            # Get sample chunks from each document
            all_chunks = []
            for doc_id in document_ids:
                chunks = await self.vector_store.search(
                    query="",
                    filters={"document_id": doc_id},
                    top_k=3  # Get first few chunks
                )
                
                # Get document metadata
                doc_info = await self.document_store.get_document(doc_id)
                
                for chunk in chunks:
                    all_chunks.append({
                        "text": chunk["text"],
                        "document": doc_info
                    })
            
            return await self.generator.generate_summary(all_chunks)
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            return f"Error generating summary: {str(e)}"
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics."""
        try:
            doc_stats = await self.document_store.get_stats()
            vector_stats = await self.vector_store.get_collection_info()
            
            return {
                "documents": doc_stats,
                "vector_store": vector_stats,
                "pipeline_status": "operational"
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {str(e)}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of all pipeline components."""
        health = {
            "overall": "healthy",
            "components": {}
        }
        
        try:
            # Check document store
            doc_stats = await self.document_store.get_stats()
            health["components"]["document_store"] = "healthy" if doc_stats else "error"
            
            # Check vector store
            vector_info = await self.vector_store.get_collection_info()
            health["components"]["vector_store"] = "healthy" if vector_info else "error"
            
            # Check embedding generator
            test_embedding = await self.embedding_generator.generate_embedding("test")
            health["components"]["embeddings"] = "healthy" if test_embedding else "error"
            
            # Check LLM
            test_response = await self.generator._call_llm("Say 'OK' if you can respond.")
            health["components"]["llm"] = "healthy" if "ok" in test_response.lower() else "error"
            
            # Overall health
            if any(status == "error" for status in health["components"].values()):
                health["overall"] = "degraded"
            
        except Exception as e:
            health["overall"] = "error"
            health["error"] = str(e)
        
        return health
