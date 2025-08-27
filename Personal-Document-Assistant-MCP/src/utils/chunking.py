"""
Text chunking utilities for document processing.
"""

import logging
from typing import List, Dict, Any, Optional
import re

logger = logging.getLogger(__name__)


class TextChunker:
    """Handles intelligent text chunking for RAG systems."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the text chunker."""
        self.config = config or self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for text chunking."""
        return {
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "min_chunk_size": 100,
            "separators": ["\n\n", "\n", ". ", "! ", "? ", " "],
            "keep_separator": True
        }
    
    def chunk_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Chunk text into overlapping segments.
        
        Args:
            text: The text to chunk
            metadata: Optional metadata to include with each chunk
            
        Returns:
            List of chunk dictionaries with content and metadata
        """
        if not text or not text.strip():
            return []
        
        chunk_size = self.config["chunk_size"]
        chunk_overlap = self.config["chunk_overlap"]
        min_chunk_size = self.config["min_chunk_size"]
        
        # Split text using hierarchical separators
        chunks = self._split_text_hierarchical(text)
        
        # Combine small chunks and split large ones
        processed_chunks = self._process_chunks(chunks, chunk_size, chunk_overlap, min_chunk_size)
        
        # Create chunk objects with metadata
        chunk_objects = []
        for i, chunk_text in enumerate(processed_chunks):
            chunk_obj = {
                "content": chunk_text.strip(),
                "chunk_index": i,
                "character_count": len(chunk_text),
                "metadata": metadata or {}
            }
            chunk_objects.append(chunk_obj)
        
        logger.info(f"Created {len(chunk_objects)} chunks from {len(text)} characters")
        return chunk_objects
    
    def _split_text_hierarchical(self, text: str) -> List[str]:
        """Split text using hierarchical separators."""
        separators = self.config["separators"]
        keep_separator = self.config["keep_separator"]
        
        def split_by_separator(text: str, separator: str) -> List[str]:
            """Split text by separator, optionally keeping the separator."""
            if separator not in text:
                return [text]
            
            parts = text.split(separator)
            if not keep_separator:
                return [part for part in parts if part.strip()]
            
            # Keep separator with the preceding part
            result = []
            for i, part in enumerate(parts[:-1]):
                if part.strip():
                    result.append(part + separator)
            
            # Add the last part if it's not empty
            if parts[-1].strip():
                result.append(parts[-1])
            
            return [part for part in result if part.strip()]
        
        # Start with the full text
        chunks = [text]
        
        # Apply separators in order of preference
        for separator in separators:
            new_chunks = []
            for chunk in chunks:
                if len(chunk) <= self.config["chunk_size"]:
                    new_chunks.append(chunk)
                else:
                    split_chunks = split_by_separator(chunk, separator)
                    new_chunks.extend(split_chunks)
            chunks = new_chunks
        
        return chunks
    
    def _process_chunks(self, chunks: List[str], chunk_size: int, 
                       chunk_overlap: int, min_chunk_size: int) -> List[str]:
        """Process chunks to ensure proper sizing and overlap."""
        processed_chunks = []
        current_chunk = ""
        
        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk:
                continue
            
            # If adding this chunk would exceed the size limit
            if len(current_chunk + chunk) > chunk_size:
                # Save the current chunk if it's large enough
                if len(current_chunk) >= min_chunk_size:
                    processed_chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                if chunk_overlap > 0 and current_chunk:
                    overlap_text = self._get_overlap_text(current_chunk, chunk_overlap)
                    current_chunk = overlap_text + chunk
                else:
                    current_chunk = chunk
            else:
                # Add to current chunk
                if current_chunk:
                    current_chunk += " " + chunk
                else:
                    current_chunk = chunk
        
        # Add the final chunk
        if current_chunk.strip() and len(current_chunk) >= min_chunk_size:
            processed_chunks.append(current_chunk.strip())
        
        # Handle very large single chunks by splitting them
        final_chunks = []
        for chunk in processed_chunks:
            if len(chunk) > chunk_size * 1.5:  # Allow some flexibility
                split_chunks = self._split_large_chunk(chunk, chunk_size, chunk_overlap)
                final_chunks.extend(split_chunks)
            else:
                final_chunks.append(chunk)
        
        return final_chunks
    
    def _get_overlap_text(self, text: str, overlap_size: int) -> str:
        """Get the last part of text for overlap."""
        if len(text) <= overlap_size:
            return text
        
        # Try to break at word boundaries
        overlap_text = text[-overlap_size:]
        
        # Find the first space to avoid cutting words
        space_index = overlap_text.find(' ')
        if space_index > 0:
            overlap_text = overlap_text[space_index + 1:]
        
        return overlap_text
    
    def _split_large_chunk(self, chunk: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """Split a large chunk into smaller pieces."""
        chunks = []
        start = 0
        
        while start < len(chunk):
            end = start + chunk_size
            
            if end >= len(chunk):
                # Last chunk
                chunks.append(chunk[start:])
                break
            
            # Try to break at word boundary
            break_point = end
            for i in range(end, start + chunk_size // 2, -1):
                if chunk[i] in [' ', '\n', '.', '!', '?']:
                    break_point = i + 1
                    break
            
            chunks.append(chunk[start:break_point])
            start = break_point - chunk_overlap
            
            # Ensure we make progress
            if start <= chunks.__len__() * chunk_size // 2:
                start = break_point
        
        return chunks
    
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Chunk multiple documents."""
        all_chunks = []
        
        for doc in documents:
            doc_chunks = self.chunk_text(
                text=doc["content"],
                metadata={
                    **doc.get("metadata", {}),
                    "document_id": doc.get("id"),
                    "document_title": doc.get("title", "Unknown"),
                    "source_file": doc.get("file_path", "Unknown")
                }
            )
            all_chunks.extend(doc_chunks)
        
        return all_chunks
