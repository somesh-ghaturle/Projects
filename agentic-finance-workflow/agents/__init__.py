"""
Base Agent Architecture for Agentic Finance Workflow
Provides the foundational framework for all specialized agents
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging
import uuid
import json
from contextlib import asynccontextmanager


class AgentStatus(Enum):
    """Agent execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class AgentType(Enum):
    """Types of agents in the system"""
    CLEANER = "cleaner"
    VALIDATOR = "validator"
    ANALYZER = "analyzer"
    VISUALIZER = "visualizer"
    RECOMMENDER = "recommender"
    ORCHESTRATOR = "orchestrator"


@dataclass
class AgentMetrics:
    """Performance and execution metrics for agents"""
    records_processed: int = 0
    error_count: int = 0
    success_rate: float = 0.0
    processing_speed: float = 0.0  # records per second
    memory_usage: float = 0.0      # MB
    cpu_usage: float = 0.0         # percentage
    execution_time: float = 0.0    # seconds


@dataclass
class AgentContext:
    """Context and metadata for agent execution"""
    agent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: Optional[str] = None
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    environment: str = "development"
    debug_mode: bool = False
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result object returned by agent execution"""
    success: bool
    data: Any = None
    error_message: Optional[str] = None
    metrics: Optional[AgentMetrics] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the agentic finance workflow.
    
    Provides common functionality including:
    - Logging and monitoring
    - Error handling and retries
    - Metrics collection
    - Context management
    - Lifecycle hooks
    """

    def __init__(
        self,
        agent_type: AgentType,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.agent_type = agent_type
        self.name = name or f"{agent_type.value}_agent"
        self.config = config or {}
        self.logger = self._setup_logging()
        self._status = AgentStatus.PENDING
        self._current_context: Optional[AgentContext] = None
        self._metrics = AgentMetrics()

    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging for the agent"""
        logger = logging.getLogger(f"agents.{self.name}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

    @property
    def status(self) -> AgentStatus:
        """Current agent status"""
        return self._status

    @property
    def metrics(self) -> AgentMetrics:
        """Current agent metrics"""
        return self._metrics

    @asynccontextmanager
    async def _execution_context(self, context: AgentContext):
        """Context manager for agent execution"""
        self._current_context = context
        self._status = AgentStatus.RUNNING
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(
                f"Starting agent execution",
                extra={
                    "agent_id": context.agent_id,
                    "workflow_id": context.workflow_id,
                    "agent_type": self.agent_type.value
                }
            )
            
            yield context
            
            self._status = AgentStatus.COMPLETED
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self._metrics.execution_time = execution_time
            
            self.logger.info(
                f"Agent execution completed successfully",
                extra={
                    "agent_id": context.agent_id,
                    "execution_time": execution_time,
                    "records_processed": self._metrics.records_processed
                }
            )
            
        except Exception as e:
            self._status = AgentStatus.FAILED
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self._metrics.execution_time = execution_time
            self._metrics.error_count += 1
            
            self.logger.error(
                f"Agent execution failed: {str(e)}",
                extra={
                    "agent_id": context.agent_id,
                    "error": str(e),
                    "execution_time": execution_time
                },
                exc_info=True
            )
            raise
        finally:
            self._current_context = None

    async def execute(
        self,
        input_data: Any,
        context: Optional[AgentContext] = None
    ) -> AgentResult:
        """
        Execute the agent with given input data and context.
        
        Args:
            input_data: Input data for the agent to process
            context: Execution context and metadata
            
        Returns:
            AgentResult containing execution results and metadata
        """
        if context is None:
            context = AgentContext()
        
        result = AgentResult(
            success=False,
            started_at=datetime.utcnow()
        )
        
        try:
            # Pre-execution validation
            await self._validate_input(input_data, context)
            
            # Execute with context management
            async with self._execution_context(context):
                # Pre-processing hook
                input_data = await self._preprocess(input_data, context)
                
                # Main processing logic
                output_data = await self._process(input_data, context)
                
                # Post-processing hook
                output_data = await self._postprocess(output_data, context)
                
                # Update result
                result.success = True
                result.data = output_data
                result.metrics = self._metrics
                result.completed_at = datetime.utcnow()
                
                return result
                
        except Exception as e:
            result.error_message = str(e)
            result.completed_at = datetime.utcnow()
            
            # Handle retries
            if context.retry_count < context.max_retries:
                context.retry_count += 1
                self._status = AgentStatus.RETRYING
                
                self.logger.warning(
                    f"Retrying agent execution (attempt {context.retry_count}/{context.max_retries})",
                    extra={"agent_id": context.agent_id}
                )
                
                # Exponential backoff
                await asyncio.sleep(2 ** context.retry_count)
                return await self.execute(input_data, context)
            
            return result

    @abstractmethod
    async def _process(self, input_data: Any, context: AgentContext) -> Any:
        """
        Main processing logic - must be implemented by subclasses.
        
        Args:
            input_data: Validated and preprocessed input data
            context: Execution context
            
        Returns:
            Processed output data
        """
        pass

    async def _validate_input(self, input_data: Any, context: AgentContext) -> None:
        """
        Validate input data before processing.
        Override in subclasses for specific validation logic.
        """
        if input_data is None:
            raise ValueError("Input data cannot be None")

    async def _preprocess(self, input_data: Any, context: AgentContext) -> Any:
        """
        Preprocess input data before main processing.
        Override in subclasses for specific preprocessing logic.
        """
        return input_data

    async def _postprocess(self, output_data: Any, context: AgentContext) -> Any:
        """
        Postprocess output data after main processing.
        Override in subclasses for specific postprocessing logic.
        """
        return output_data

    def _update_metrics(self, **kwargs):
        """Update agent metrics"""
        for key, value in kwargs.items():
            if hasattr(self._metrics, key):
                setattr(self._metrics, key, value)

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the agent.
        
        Returns:
            Health status information
        """
        return {
            "agent_type": self.agent_type.value,
            "name": self.name,
            "status": self.status.value,
            "last_execution": getattr(self._metrics, 'last_execution', None),
            "total_executions": getattr(self._metrics, 'total_executions', 0),
            "success_rate": self._metrics.success_rate,
            "average_execution_time": getattr(self._metrics, 'avg_execution_time', 0)
        }

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)

    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, status={self.status.value})"

    def __repr__(self) -> str:
        return self.__str__()


class AgentRegistry:
    """Registry for managing and discovering agents"""
    
    _agents: Dict[str, BaseAgent] = {}
    _types: Dict[AgentType, List[BaseAgent]] = {}

    @classmethod
    def register(cls, agent: BaseAgent) -> None:
        """Register an agent"""
        cls._agents[agent.name] = agent
        
        if agent.agent_type not in cls._types:
            cls._types[agent.agent_type] = []
        cls._types[agent.agent_type].append(agent)

    @classmethod
    def get_agent(cls, name: str) -> Optional[BaseAgent]:
        """Get agent by name"""
        return cls._agents.get(name)

    @classmethod
    def get_agents_by_type(cls, agent_type: AgentType) -> List[BaseAgent]:
        """Get all agents of a specific type"""
        return cls._types.get(agent_type, [])

    @classmethod
    def list_agents(cls) -> List[BaseAgent]:
        """List all registered agents"""
        return list(cls._agents.values())

    @classmethod
    def unregister(cls, name: str) -> bool:
        """Unregister an agent"""
        if name in cls._agents:
            agent = cls._agents.pop(name)
            if agent.agent_type in cls._types:
                cls._types[agent.agent_type].remove(agent)
            return True
        return False


# Utility functions and decorators

def agent_timeout(seconds: int):
    """Decorator to set timeout for agent execution"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                raise TimeoutError(f"Agent execution timed out after {seconds} seconds")
        return wrapper
    return decorator


def agent_retry(max_retries: int = 3, backoff_factor: float = 2.0):
    """Decorator to add retry logic to agent methods"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = backoff_factor ** attempt
                        await asyncio.sleep(wait_time)
                    else:
                        break
            
            raise last_exception
        return wrapper
    return decorator


def validate_agent_input(schema: Dict[str, Any]):
    """Decorator to validate agent input against a schema"""
    def decorator(func):
        async def wrapper(self, input_data, context, *args, **kwargs):
            # Basic schema validation (can be extended with jsonschema)
            if not isinstance(input_data, dict):
                raise ValueError("Input data must be a dictionary")
            
            for required_field in schema.get('required', []):
                if required_field not in input_data:
                    raise ValueError(f"Required field '{required_field}' missing from input")
            
            return await func(self, input_data, context, *args, **kwargs)
        return wrapper
    return decorator
