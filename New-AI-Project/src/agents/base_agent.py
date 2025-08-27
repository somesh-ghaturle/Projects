"""
Base agent class for multi-agent systems
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, name: str, description: str, **kwargs):
        """Initialize the agent"""
        self.name = name
        self.description = description
        self.is_active = False
        self.config = kwargs
        
        logger.info(f"Initialized agent: {name}")
    
    @abstractmethod
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a task"""
        pass
    
    @abstractmethod
    async def process_message(self, message: str, sender: Optional[str] = None) -> str:
        """Process a message from another agent or user"""
        pass
    
    async def start(self):
        """Start the agent"""
        logger.info(f"Starting agent: {self.name}")
        self.is_active = True
        await self._on_start()
    
    async def stop(self):
        """Stop the agent"""
        logger.info(f"Stopping agent: {self.name}")
        self.is_active = False
        await self._on_stop()
    
    async def _on_start(self):
        """Called when the agent starts"""
        pass
    
    async def _on_stop(self):
        """Called when the agent stops"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "config": self.config
        }


class AgentManager:
    """Manages multiple agents"""
    
    def __init__(self):
        """Initialize the agent manager"""
        self.agents: Dict[str, BaseAgent] = {}
        logger.info("Initialized AgentManager")
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent"""
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")
    
    def unregister_agent(self, name: str):
        """Unregister an agent"""
        if name in self.agents:
            del self.agents[name]
            logger.info(f"Unregistered agent: {name}")
    
    async def start_agent(self, name: str):
        """Start a specific agent"""
        if name in self.agents:
            await self.agents[name].start()
    
    async def stop_agent(self, name: str):
        """Stop a specific agent"""
        if name in self.agents:
            await self.agents[name].stop()
    
    async def start_all(self):
        """Start all agents"""
        logger.info("Starting all agents...")
        for agent in self.agents.values():
            await agent.start()
    
    async def stop_all(self):
        """Stop all agents"""
        logger.info("Stopping all agents...")
        for agent in self.agents.values():
            await agent.stop()
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name"""
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        """List all agent names"""
        return list(self.agents.keys())
    
    def get_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all agents"""
        return {name: agent.get_status() for name, agent in self.agents.items()}
