"""
Script Summarizer Agent
Specializes in analyzing and summarizing movie scripts using LLMs
"""

import logging
from typing import Any, Dict, List, Optional
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate

from .base_agent import BaseAgent
from ..config import settings

logger = logging.getLogger(__name__)


class ScriptSummarizerAgent(BaseAgent):
    """Agent specialized in movie script analysis and summarization"""
    
    def __init__(self):
        super().__init__(
            agent_id="script_summarizer",
            name="Script Summarizer Agent",
            description="Analyzes movie scripts and generates comprehensive summaries"
        )
        self.llm = None
        self.summarize_chain = None
        self.text_splitter = None
        
    async def _initialize_dependencies(self) -> None:
        """Initialize LLM and summarization chain"""
        try:
            # Initialize LLM
            self.llm = ChatOpenAI(
                model=settings.DEFAULT_LLM_MODEL,
                openai_api_key=settings.OPENAI_API_KEY,
                temperature=0.3,
                max_tokens=1000
            )
            
            # Initialize text splitter for long scripts
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=4000,
                chunk_overlap=200,
                separators=["\n\nFADE IN:", "\n\nINT.", "\n\nEXT.", "\n\n", "\n", " "]
            )
            
            # Create custom prompt for movie script summarization
            prompt_template = """
            You are an expert film analyst. Analyze the following movie script excerpt and provide insights:

            Script Content:
            {text}

            Please provide:
            1. A concise plot summary (2-3 sentences)
            2. Main characters and their key traits
            3. Central themes and messages
            4. Tone and genre indicators
            5. Key dramatic moments or plot points

            Analysis:
            """
            
            prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
            
            # Initialize summarization chain
            self.summarize_chain = load_summarize_chain(
                self.llm,
                chain_type="map_reduce",
                map_prompt=prompt,
                combine_prompt=prompt
            )
            
            logger.info("Script Summarizer Agent dependencies initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Script Summarizer Agent: {str(e)}")
            raise
    
    async def _custom_validation(self, input_data: Dict[str, Any]) -> None:
        """Validate script input data"""
        if "script_text" not in input_data:
            raise ValueError("'script_text' is required in input data")
        
        script_text = input_data["script_text"]
        if not isinstance(script_text, str) or len(script_text.strip()) == 0:
            raise ValueError("'script_text' must be a non-empty string")
        
        if len(script_text) < 100:
            raise ValueError("Script text too short for meaningful analysis")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process movie script and generate comprehensive summary
        
        Args:
            input_data: Dictionary containing 'script_text' and optional metadata
            
        Returns:
            Dictionary with summary, characters, themes, and analysis
        """
        script_text = input_data["script_text"]
        metadata = input_data.get("metadata", {})
        
        try:
            # Split script into manageable chunks
            docs = self._prepare_documents(script_text)
            
            # Generate summary using LLM chain
            summary_result = await self._generate_summary(docs)
            
            # Extract specific elements
            characters = await self._extract_characters(script_text)
            themes = await self._extract_themes(script_text)
            structure = await self._analyze_structure(script_text)
            
            result = {
                "summary": {
                    "plot": summary_result.get("plot", ""),
                    "overview": summary_result.get("overview", ""),
                    "key_moments": summary_result.get("key_moments", [])
                },
                "characters": characters,
                "themes": themes,
                "structure": structure,
                "analysis": {
                    "word_count": len(script_text.split()),
                    "estimated_runtime": self._estimate_runtime(script_text),
                    "genre_indicators": summary_result.get("genre_indicators", []),
                    "tone": summary_result.get("tone", "")
                },
                "metadata": metadata
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing script: {str(e)}")
            raise
    
    def _prepare_documents(self, script_text: str) -> List[Document]:
        """Split script text into documents for processing"""
        chunks = self.text_splitter.split_text(script_text)
        return [Document(page_content=chunk) for chunk in chunks]
    
    async def _generate_summary(self, docs: List[Document]) -> Dict[str, Any]:
        """Generate summary using LLM chain"""
        try:
            summary_text = self.summarize_chain.run(docs)
            
            # Parse the structured response (this would be more sophisticated in practice)
            return self._parse_summary_response(summary_text)
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return {"plot": "Error generating summary", "overview": "", "key_moments": []}
    
    def _parse_summary_response(self, summary_text: str) -> Dict[str, Any]:
        """Parse structured summary response from LLM"""
        # This is a simplified parser - in practice, you'd use more sophisticated parsing
        lines = summary_text.split('\n')
        
        result = {
            "plot": "",
            "overview": summary_text[:500] + "..." if len(summary_text) > 500 else summary_text,
            "key_moments": [],
            "genre_indicators": [],
            "tone": ""
        }
        
        # Extract plot summary (first few sentences)
        sentences = summary_text.split('. ')
        if len(sentences) >= 2:
            result["plot"] = '. '.join(sentences[:2]) + '.'
        
        return result
    
    async def _extract_characters(self, script_text: str) -> List[Dict[str, Any]]:
        """Extract character information from script"""
        try:
            # Simple character extraction based on script formatting
            character_prompt = f"""
            Extract the main characters from this movie script excerpt.
            For each character, provide their name and a brief description of their role/personality.
            
            Script: {script_text[:2000]}...
            
            Format as a list of characters with names and descriptions.
            """
            
            response = await self.llm.apredict(character_prompt)
            
            # Parse character information (simplified)
            characters = []
            lines = response.split('\n')
            for line in lines:
                if ':' in line and len(line.strip()) > 5:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        characters.append({
                            "name": parts[0].strip(),
                            "description": parts[1].strip()
                        })
            
            return characters[:10]  # Limit to top 10 characters
            
        except Exception as e:
            logger.error(f"Error extracting characters: {str(e)}")
            return []
    
    async def _extract_themes(self, script_text: str) -> List[str]:
        """Extract central themes from script"""
        try:
            theme_prompt = f"""
            Identify the main themes in this movie script.
            List 3-5 central themes or messages.
            
            Script excerpt: {script_text[:1500]}...
            
            Themes:
            """
            
            response = await self.llm.apredict(theme_prompt)
            
            # Extract themes from response
            themes = []
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) > 5:
                    # Remove numbering and bullet points
                    theme = line.lstrip('0123456789.- ')
                    if theme:
                        themes.append(theme)
            
            return themes[:5]  # Limit to 5 themes
            
        except Exception as e:
            logger.error(f"Error extracting themes: {str(e)}")
            return []
    
    async def _analyze_structure(self, script_text: str) -> Dict[str, Any]:
        """Analyze script structure and pacing"""
        try:
            # Basic structure analysis
            lines = script_text.split('\n')
            
            # Count scene headings
            scene_count = sum(1 for line in lines if line.strip().startswith(('INT.', 'EXT.')))
            
            # Estimate acts based on page count (roughly)
            estimated_pages = len(script_text) // 250  # Rough estimate
            
            structure = {
                "estimated_pages": estimated_pages,
                "scene_count": scene_count,
                "act_structure": self._determine_act_structure(estimated_pages),
                "pacing": "Normal" if 90 <= estimated_pages <= 120 else "Fast" if estimated_pages < 90 else "Slow"
            }
            
            return structure
            
        except Exception as e:
            logger.error(f"Error analyzing structure: {str(e)}")
            return {}
    
    def _determine_act_structure(self, pages: int) -> str:
        """Determine likely act structure based on page count"""
        if pages < 60:
            return "Short form"
        elif pages < 90:
            return "Two-act structure"
        elif pages <= 120:
            return "Traditional three-act structure"
        else:
            return "Extended/Epic structure"
    
    def _estimate_runtime(self, script_text: str) -> str:
        """Estimate movie runtime based on script length"""
        # Rule of thumb: 1 page ≈ 1 minute
        estimated_pages = len(script_text) // 250
        runtime_minutes = estimated_pages
        
        hours = runtime_minutes // 60
        minutes = runtime_minutes % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
