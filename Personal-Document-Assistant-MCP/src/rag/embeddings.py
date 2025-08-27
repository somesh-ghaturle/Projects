"""
Embedding management for document processing and retrieval.
"""

import logging
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import openai
from pathlib import Path

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Manages document embeddings using various embedding models."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the embedding manager."""
        self.config = config or self._default_config()
        self.model = None
        self.embedding_dimension = None
        self._initialize_model()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for embeddings."""
        return {
            "provider": "sentence_transformers",  # or "openai"
            "model": "all-MiniLM-L6-v2",  # or "text-embedding-3-small"
            "api_key": None,
            "batch_size": 32
        }
    
    def _initialize_model(self):
        """Initialize the embedding model based on configuration."""
        provider = self.config["provider"]
        model_name = self.config["model"]
        
        try:
            if provider == "sentence_transformers":
                logger.info(f"Loading Sentence Transformer model: {model_name}")
                self.model = SentenceTransformer(model_name)
                self.embedding_dimension = self.model.get_sentence_embedding_dimension()
                
            elif provider == "openai":
                logger.info(f"Using OpenAI embeddings: {model_name}")
                if self.config.get("api_key"):
                    openai.api_key = self.config["api_key"]
                self.embedding_dimension = 1536  # OpenAI embedding dimension
                
            else:
                raise ValueError(f"Unsupported embedding provider: {provider}")
                
            logger.info(f"Embedding model initialized. Dimension: {self.embedding_dimension}")
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {str(e)}")
            raise
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        return await self.embed_texts([text])[0]
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        if not texts:
            return []
        
        try:
            provider = self.config["provider"]
            
            if provider == "sentence_transformers":
                embeddings = self.model.encode(texts, convert_to_tensor=False)
                return embeddings.tolist()
                
            elif provider == "openai":
                embeddings = []
                batch_size = self.config["batch_size"]
                
                for i in range(0, len(texts), batch_size):
                    batch = texts[i:i + batch_size]
                    response = openai.embeddings.create(
                        input=batch,
                        model=self.config["model"]
                    )
                    batch_embeddings = [item.embedding for item in response.data]
                    embeddings.extend(batch_embeddings)
                
                return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            raise
    
    async def embed_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Embed a list of document chunks."""
        if not documents:
            return []
        
        texts = [doc["content"] for doc in documents]
        embeddings = await self.embed_texts(texts)
        
        # Add embeddings to documents
        for doc, embedding in zip(documents, embeddings):
            doc["embedding"] = embedding
            doc["embedding_model"] = f"{self.config['provider']}/{self.config['model']}"
        
        return documents
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model."""
        return self.embedding_dimension
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
