"""
Base Agent Abstract Class
Defines the interface for all specialized agents
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all content analysis agents"""
    
    def __init__(self, agent_id: str, name: str, description: str = ""):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.is_initialized = False
        self.created_at = datetime.now()
        self.last_used = None
        self.usage_count = 0
        
    async def initialize(self) -> None:
        """Initialize the agent and its dependencies"""
        if self.is_initialized:
            return
            
        logger.info(f"Initializing agent: {self.name}")
        await self._initialize_dependencies()
        self.is_initialized = True
        logger.info(f"Agent {self.name} initialized successfully")
    
    @abstractmethod
    async def _initialize_dependencies(self) -> None:
        """Initialize agent-specific dependencies"""
        pass
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results
        
        Args:
            input_data: Dictionary containing input data for processing
            
        Returns:
            Dictionary containing processing results
        """
        pass
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent with input validation and error handling
        
        Args:
            input_data: Input data for processing
            
        Returns:
            Processing results with metadata
        """
        if not self.is_initialized:
            await self.initialize()
        
        self.last_used = datetime.now()
        self.usage_count += 1
        
        try:
            # Validate input
            await self._validate_input(input_data)
            
            # Process data
            logger.info(f"Agent {self.name} processing request")
            start_time = datetime.now()
            
            result = await self.process(input_data)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Add metadata to result
            result["metadata"] = {
                "agent_id": self.agent_id,
                "agent_name": self.name,
                "processing_time": processing_time,
                "timestamp": end_time.isoformat(),
                "usage_count": self.usage_count
            }
            
            logger.info(f"Agent {self.name} completed processing in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Agent {self.name} processing failed: {str(e)}")
            return {
                "error": str(e),
                "agent_id": self.agent_id,
                "agent_name": self.name,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _validate_input(self, input_data: Dict[str, Any]) -> None:
        """
        Validate input data
        
        Args:
            input_data: Input data to validate
            
        Raises:
            ValueError: If input data is invalid
        """
        if not isinstance(input_data, dict):
            raise ValueError("Input data must be a dictionary")
        
        # Agent-specific validation can be implemented in subclasses
        await self._custom_validation(input_data)
    
    async def _custom_validation(self, input_data: Dict[str, Any]) -> None:
        """Override this method for agent-specific validation"""
        pass
    
    async def cleanup(self) -> None:
        """Cleanup agent resources"""
        logger.info(f"Cleaning up agent: {self.name}")
        self.is_initialized = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "is_initialized": self.is_initialized,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "usage_count": self.usage_count
        }
    
    def __str__(self) -> str:
        return f"Agent({self.name})"
    
    def __repr__(self) -> str:
        return f"Agent(id={self.agent_id}, name={self.name}, initialized={self.is_initialized})"
