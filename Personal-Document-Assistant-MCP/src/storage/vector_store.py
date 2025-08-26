"""
Vector storage using ChromaDB for semantic search.
"""

import logging
from typing import List, Dict, Any, Optional
import uuid
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages vector storage and retrieval using ChromaDB."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the vector store."""
        self.config = config or self._default_config()
        self.client = None
        self.collection = None
        self._initialize_store()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for vector storage."""
        return {
            "persist_directory": "./data/vectordb",
            "collection_name": "document_embeddings"
        }
    
    def _initialize_store(self):
        """Initialize ChromaDB client and collection."""
        try:
            # Initialize ChromaDB client with persistence
            self.client = chromadb.PersistentClient(
                path=self.config["persist_directory"],
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.config["collection_name"],
                metadata={"description": "Document chunks for RAG"}
            )
            
            logger.info(f"Vector store initialized. Collection: {self.config['collection_name']}")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {str(e)}")
            raise
    
    async def add_chunks(self, document_id: str, chunks: List[Dict[str, Any]]) -> List[str]:
        """Add document chunks to the vector store."""
        if not chunks:
            return []
        
        try:
            # Prepare data for ChromaDB
            chunk_ids = []
            documents = []
            metadatas = []
            embeddings = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{document_id}_chunk_{i}"
                chunk_ids.append(chunk_id)
                documents.append(chunk["content"])
                
                # Prepare metadata
                metadata = {
                    "document_id": document_id,
                    "chunk_index": i,
                    "character_count": len(chunk["content"]),
                    **chunk.get("metadata", {})
                }
                metadatas.append(metadata)
                
                # Get embedding if available
                if "embedding" in chunk:
                    embeddings.append(chunk["embedding"])
            
            # Add to collection
            if embeddings:
                self.collection.add(
                    ids=chunk_ids,
                    documents=documents,
                    metadatas=metadatas,
                    embeddings=embeddings
                )
            else:
                # Let ChromaDB generate embeddings
                self.collection.add(
                    ids=chunk_ids,
                    documents=documents,
                    metadatas=metadatas
                )
            
            logger.info(f"Added {len(chunk_ids)} chunks for document {document_id}")
            return chunk_ids
            
        except Exception as e:
            logger.error(f"Failed to add chunks to vector store: {str(e)}")
            raise
    
    async def search(self, query: str, limit: int = 5, 
                    filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar chunks using semantic similarity."""
        try:
            # Prepare where clause for filtering
            where_clause = filter_metadata if filter_metadata else None
            
            # Perform similarity search
            results = self.collection.query(
                query_texts=[query],
                n_results=min(limit, 100),  # ChromaDB limit
                where=where_clause
            )
            
            # Format results
            formatted_results = []
            if results and results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    result = {
                        "id": results['ids'][0][i],
                        "content": results['documents'][0][i],
                        "score": 1 - results['distances'][0][i],  # Convert distance to similarity
                        "metadata": results['metadatas'][0][i] if results['metadatas'][0] else {}
                    }
                    formatted_results.append(result)
            
            logger.info(f"Found {len(formatted_results)} results for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete all chunks for a document."""
        try:
            # Find chunks belonging to the document
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            if results and results['ids']:
                # Delete the chunks
                self.collection.delete(
                    ids=results['ids']
                )
                logger.info(f"Deleted {len(results['ids'])} chunks for document {document_id}")
                return True
            else:
                logger.warning(f"No chunks found for document {document_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {str(e)}")
            raise
    
    async def get_chunk(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific chunk by ID."""
        try:
            results = self.collection.get(
                ids=[chunk_id],
                include=["documents", "metadatas"]
            )
            
            if results and results['documents'] and results['documents'][0]:
                return {
                    "id": chunk_id,
                    "content": results['documents'][0],
                    "metadata": results['metadatas'][0] if results['metadatas'] else {}
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get chunk {chunk_id}: {str(e)}")
            return None
    
    async def list_documents(self) -> List[str]:
        """List all unique document IDs in the vector store."""
        try:
            # Get all metadatas to extract document IDs
            results = self.collection.get(
                include=["metadatas"]
            )
            
            document_ids = set()
            if results and results['metadatas']:
                for metadata in results['metadatas']:
                    if metadata and 'document_id' in metadata:
                        document_ids.add(metadata['document_id'])
            
            return list(document_ids)
            
        except Exception as e:
            logger.error(f"Failed to list documents: {str(e)}")
            return []
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        try:
            collection_info = self.collection.count()
            document_ids = await self.list_documents()
            
            return {
                "total_chunks": collection_info,
                "total_documents": len(document_ids),
                "collection_name": self.config["collection_name"]
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {str(e)}")
            return {"error": str(e)}
    
    def reset_collection(self):
        """Reset the collection (delete all data)."""
        try:
            self.client.delete_collection(self.config["collection_name"])
            self.collection = self.client.create_collection(
                name=self.config["collection_name"],
                metadata={"description": "Document chunks for RAG"}
            )
            logger.info("Collection reset successfully")
            
        except Exception as e:
            logger.error(f"Failed to reset collection: {str(e)}")
            raise
