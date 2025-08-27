"""
RAG retrieval component.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from ..storage.vector_store import VectorStore
from ..storage.document_store import DocumentStore

logger = logging.getLogger(__name__)


class DocumentRetriever:
    """Handles document retrieval for RAG pipeline."""
    
    def __init__(self, vector_store: VectorStore, document_store: DocumentStore):
        """Initialize the retriever with vector and document stores."""
        self.vector_store = vector_store
        self.document_store = document_store
    
    async def retrieve_documents(self, query: str, top_k: int = 5,
                               similarity_threshold: float = 0.7,
                               filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            top_k: Number of documents to retrieve
            similarity_threshold: Minimum similarity score
            filters: Optional metadata filters
        
        Returns:
            List of relevant document chunks with metadata
        """
        try:
            # Search vector store for similar chunks
            search_results = await self.vector_store.search(
                query=query,
                top_k=top_k * 2,  # Get more results to filter
                filters=filters
            )
            
            # Filter by similarity threshold
            filtered_results = [
                result for result in search_results
                if result["score"] >= similarity_threshold
            ]
            
            # Limit to top_k results
            filtered_results = filtered_results[:top_k]
            
            # Enrich with document metadata
            enriched_results = []
            for result in filtered_results:
                document_id = result["metadata"].get("document_id")
                if document_id:
                    doc_metadata = await self.document_store.get_document(document_id)
                    if doc_metadata:
                        enriched_result = {
                            "chunk_id": result["id"],
                            "text": result["text"],
                            "score": result["score"],
                            "chunk_metadata": result["metadata"],
                            "document": {
                                "id": doc_metadata["id"],
                                "title": doc_metadata["title"],
                                "file_path": doc_metadata["file_path"],
                                "created_at": doc_metadata["created_at"]
                            }
                        }
                        enriched_results.append(enriched_result)
            
            logger.info(f"Retrieved {len(enriched_results)} documents for query: {query[:50]}...")
            return enriched_results
            
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {str(e)}")
            return []
    
    async def retrieve_by_document(self, document_id: str, query: str,
                                 top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks from a specific document.
        
        Args:
            document_id: ID of the document to search within
            query: Search query
            top_k: Number of chunks to retrieve
        
        Returns:
            List of relevant chunks from the specified document
        """
        try:
            # Use document filter
            filters = {"document_id": document_id}
            
            search_results = await self.vector_store.search(
                query=query,
                top_k=top_k,
                filters=filters
            )
            
            # Enrich with document metadata
            document_metadata = await self.document_store.get_document(document_id)
            
            enriched_results = []
            for result in search_results:
                enriched_result = {
                    "chunk_id": result["id"],
                    "text": result["text"],
                    "score": result["score"],
                    "chunk_metadata": result["metadata"],
                    "document": document_metadata
                }
                enriched_results.append(enriched_result)
            
            logger.info(f"Retrieved {len(enriched_results)} chunks from document {document_id}")
            return enriched_results
            
        except Exception as e:
            logger.error(f"Failed to retrieve from document {document_id}: {str(e)}")
            return []
    
    async def get_similar_documents(self, document_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find documents similar to a given document.
        
        Args:
            document_id: ID of the reference document
            top_k: Number of similar documents to find
        
        Returns:
            List of similar documents
        """
        try:
            # Get a representative chunk from the document
            filters = {"document_id": document_id}
            chunks = await self.vector_store.search(
                query="",  # Empty query to get chunks by filter
                top_k=1,
                filters=filters
            )
            
            if not chunks:
                return []
            
            # Use the first chunk's text as query
            representative_text = chunks[0]["text"]
            
            # Search for similar documents (excluding the original)
            all_results = await self.vector_store.search(
                query=representative_text,
                top_k=top_k * 3  # Get more to ensure diversity
            )
            
            # Group by document and select diverse results
            document_groups = {}
            for result in all_results:
                doc_id = result["metadata"].get("document_id")
                if doc_id and doc_id != document_id:  # Exclude original document
                    if doc_id not in document_groups:
                        document_groups[doc_id] = result
            
            # Get top_k most similar documents
            similar_docs = list(document_groups.values())[:top_k]
            
            # Enrich with document metadata
            enriched_results = []
            for result in similar_docs:
                doc_id = result["metadata"].get("document_id")
                doc_metadata = await self.document_store.get_document(doc_id)
                if doc_metadata:
                    enriched_result = {
                        "document": doc_metadata,
                        "similarity_score": result["score"],
                        "representative_chunk": result["text"][:200] + "..."
                    }
                    enriched_results.append(enriched_result)
            
            logger.info(f"Found {len(enriched_results)} similar documents to {document_id}")
            return enriched_results
            
        except Exception as e:
            logger.error(f"Failed to find similar documents: {str(e)}")
            return []
    
    async def hybrid_search(self, query: str, document_filters: Optional[Dict[str, Any]] = None,
                          semantic_weight: float = 0.7, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining semantic and keyword search.
        
        Args:
            query: Search query
            document_filters: Optional filters for document metadata
            semantic_weight: Weight for semantic search (0-1)
            top_k: Number of results to return
        
        Returns:
            List of hybrid search results
        """
        try:
            # Get semantic search results
            semantic_results = await self.vector_store.search(
                query=query,
                top_k=top_k * 2,
                filters=document_filters
            )
            
            # Get keyword search results from document store
            keyword_results = await self.document_store.list_documents(
                search_term=query,
                limit=top_k * 2
            )
            
            # Combine and rank results
            combined_results = {}
            
            # Add semantic results with weights
            for i, result in enumerate(semantic_results):
                doc_id = result["metadata"].get("document_id")
                if doc_id:
                    score = result["score"] * semantic_weight
                    # Boost score based on ranking position
                    position_boost = (len(semantic_results) - i) / len(semantic_results) * 0.1
                    combined_results[doc_id] = {
                        "document_id": doc_id,
                        "semantic_score": result["score"],
                        "semantic_chunk": result["text"],
                        "total_score": score + position_boost,
                        "chunk_metadata": result["metadata"]
                    }
            
            # Add keyword results with weights
            keyword_weight = 1.0 - semantic_weight
            for i, doc in enumerate(keyword_results):
                doc_id = doc["id"]
                if doc_id in combined_results:
                    # Boost existing entry
                    position_boost = (len(keyword_results) - i) / len(keyword_results) * keyword_weight
                    combined_results[doc_id]["total_score"] += position_boost
                    combined_results[doc_id]["keyword_match"] = True
                else:
                    # Add new entry
                    position_boost = (len(keyword_results) - i) / len(keyword_results) * keyword_weight
                    combined_results[doc_id] = {
                        "document_id": doc_id,
                        "total_score": position_boost,
                        "keyword_match": True,
                        "document_metadata": doc
                    }
            
            # Sort by total score and get top results
            sorted_results = sorted(
                combined_results.values(),
                key=lambda x: x["total_score"],
                reverse=True
            )[:top_k]
            
            # Enrich with full document metadata
            enriched_results = []
            for result in sorted_results:
                doc_id = result["document_id"]
                if "document_metadata" not in result:
                    doc_metadata = await self.document_store.get_document(doc_id)
                else:
                    doc_metadata = result["document_metadata"]
                
                if doc_metadata:
                    enriched_result = {
                        "document": doc_metadata,
                        "total_score": result["total_score"],
                        "semantic_score": result.get("semantic_score", 0),
                        "keyword_match": result.get("keyword_match", False),
                        "semantic_chunk": result.get("semantic_chunk", ""),
                        "chunk_metadata": result.get("chunk_metadata", {})
                    }
                    enriched_results.append(enriched_result)
            
            logger.info(f"Hybrid search returned {len(enriched_results)} results for: {query[:50]}...")
            return enriched_results
            
        except Exception as e:
            logger.error(f"Failed to perform hybrid search: {str(e)}")
            return []
