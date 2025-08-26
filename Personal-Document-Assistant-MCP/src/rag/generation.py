"""
RAG generation component using local LLM.
"""

import logging
from typing import List, Dict, Any, Optional
import requests
import json

logger = logging.getLogger(__name__)


class RAGGenerator:
    """Handles response generation for RAG pipeline using local LLM."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the generator with LLM configuration."""
        self.config = config or self._default_config()
        self.base_url = self.config["llm_base_url"]
        self.model = self.config["llm_model"]
        self.max_tokens = self.config.get("max_tokens", 2048)
        self.temperature = self.config.get("temperature", 0.7)
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for LLM generation."""
        return {
            "llm_base_url": "http://localhost:11434",  # Ollama default
            "llm_model": "llama3",
            "max_tokens": 2048,
            "temperature": 0.7
        }
    
    async def generate_response(self, query: str, retrieved_docs: List[Dict[str, Any]],
                              system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a response based on query and retrieved documents.
        
        Args:
            query: User's question
            retrieved_docs: List of relevant document chunks
            system_prompt: Optional custom system prompt
        
        Returns:
            Generated response with metadata
        """
        try:
            # Prepare context from retrieved documents
            context = self._prepare_context(retrieved_docs)
            
            # Build the prompt
            prompt = self._build_prompt(query, context, system_prompt)
            
            # Generate response using local LLM
            response = await self._call_llm(prompt)
            
            # Package the result
            result = {
                "response": response,
                "query": query,
                "sources": [
                    {
                        "document_title": doc["document"]["title"],
                        "document_id": doc["document"]["id"],
                        "chunk_text": doc["text"][:200] + "...",
                        "relevance_score": doc.get("score", 0)
                    }
                    for doc in retrieved_docs
                ],
                "context_length": len(context),
                "source_count": len(retrieved_docs)
            }
            
            logger.info(f"Generated response for query: {query[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            return {
                "response": f"I apologize, but I encountered an error while generating a response: {str(e)}",
                "error": str(e),
                "query": query,
                "sources": []
            }
    
    def _prepare_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """Prepare context string from retrieved documents."""
        if not retrieved_docs:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            document_title = doc["document"]["title"]
            chunk_text = doc["text"]
            score = doc.get("score", 0)
            
            context_part = f"[Source {i}: {document_title} (Relevance: {score:.2f})]\n{chunk_text}\n"
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, query: str, context: str, system_prompt: Optional[str] = None) -> str:
        """Build the complete prompt for the LLM."""
        if system_prompt is None:
            system_prompt = """You are a helpful AI assistant that answers questions based on provided documents. 
            
Guidelines:
- Base your answers on the provided context documents
- If the context doesn't contain enough information, say so clearly
- Cite specific sources when possible
- Be concise but comprehensive
- If you're uncertain, express that uncertainty"""
        
        prompt = f"""System: {system_prompt}

Context Documents:
{context}

User Question: {query}

Please provide a helpful answer based on the context documents above."""
        
        return prompt
    
    async def _call_llm(self, prompt: str) -> str:
        """Call the local LLM API."""
        try:
            # Prepare the request for Ollama API
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            }
            
            # Make request to Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response generated")
            else:
                logger.error(f"LLM API error: {response.status_code} - {response.text}")
                return f"Error calling LLM: {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to LLM service. Is Ollama running?")
            return "Error: Could not connect to the local LLM service. Please ensure Ollama is running."
        except requests.exceptions.Timeout:
            logger.error("LLM request timed out")
            return "Error: The request to the LLM service timed out."
        except Exception as e:
            logger.error(f"Unexpected error calling LLM: {str(e)}")
            return f"Error: Unexpected error occurred: {str(e)}"
    
    async def generate_summary(self, documents: List[Dict[str, Any]]) -> str:
        """Generate a summary of multiple documents."""
        try:
            if not documents:
                return "No documents provided for summary."
            
            # Prepare content for summarization
            content_parts = []
            for doc in documents:
                title = doc["document"]["title"]
                text = doc["text"][:1000]  # Limit text length
                content_parts.append(f"Document: {title}\n{text}")
            
            combined_content = "\n\n".join(content_parts)
            
            prompt = f"""Please provide a concise summary of the following documents:

{combined_content}

Summary:"""
            
            summary = await self._call_llm(prompt)
            
            logger.info(f"Generated summary for {len(documents)} documents")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            return f"Error generating summary: {str(e)}"
    
    async def extract_key_points(self, document_text: str) -> List[str]:
        """Extract key points from a document."""
        try:
            prompt = f"""Please extract the key points from the following text. 
Return them as a bulleted list:

{document_text[:2000]}

Key Points:"""
            
            response = await self._call_llm(prompt)
            
            # Parse response into list of key points
            lines = response.strip().split('\n')
            key_points = []
            for line in lines:
                line = line.strip()
                if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                    # Remove bullet point markers
                    clean_point = line.lstrip('•-* ').strip()
                    if clean_point:
                        key_points.append(clean_point)
            
            return key_points
            
        except Exception as e:
            logger.error(f"Failed to extract key points: {str(e)}")
            return [f"Error extracting key points: {str(e)}"]
    
    async def answer_question_types(self, query: str, retrieved_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle different types of questions with specialized prompts."""
        # Detect question type
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['summarize', 'summary', 'overview']):
            return await self._handle_summary_question(query, retrieved_docs)
        elif any(word in query_lower for word in ['compare', 'difference', 'versus', 'vs']):
            return await self._handle_comparison_question(query, retrieved_docs)
        elif any(word in query_lower for word in ['how', 'step', 'process', 'procedure']):
            return await self._handle_how_to_question(query, retrieved_docs)
        else:
            return await self.generate_response(query, retrieved_docs)
    
    async def _handle_summary_question(self, query: str, retrieved_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle summary-type questions."""
        system_prompt = """You are summarizing content from documents. 
        Provide a clear, structured summary that captures the main points and key information."""
        
        return await self.generate_response(query, retrieved_docs, system_prompt)
    
    async def _handle_comparison_question(self, query: str, retrieved_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle comparison questions."""
        system_prompt = """You are comparing information from different documents or sections. 
        Highlight similarities, differences, and provide a balanced comparison."""
        
        return await self.generate_response(query, retrieved_docs, system_prompt)
    
    async def _handle_how_to_question(self, query: str, retrieved_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle how-to or procedural questions."""
        system_prompt = """You are providing step-by-step instructions or explanations. 
        Structure your response clearly with numbered steps or logical progression."""
        
        return await self.generate_response(query, retrieved_docs, system_prompt)
