"""
Orchestrator Agent for Agentic Finance Workflow

This agent coordinates the execution of multiple agents in a workflow,
handles error recovery, manages agent communication, and provides
human-in-the-loop escalation capabilities.
"""

import asyncio
import yaml
import json
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid

from .. import BaseAgent, AgentType, AgentContext, AgentResult
from ..cleaner import DataCleanerAgent


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class WorkflowStep:
    """Individual step in a workflow"""
    step_id: str
    agent_type: AgentType
    agent_config: Dict[str, Any] = field(default_factory=dict)
    input_mapping: Dict[str, str] = field(default_factory=dict)
    output_mapping: Dict[str, str] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    parallel: bool = False
    retry_on_failure: bool = True
    timeout_seconds: int = 300


@dataclass
class WorkflowDefinition:
    """Complete workflow definition"""
    workflow_id: str
    name: str
    description: str
    version: str = "1.0"
    steps: List[WorkflowStep] = field(default_factory=list)
    global_config: Dict[str, Any] = field(default_factory=dict)
    error_handling: Dict[str, Any] = field(default_factory=dict)
    human_review_required: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """Runtime execution state of a workflow"""
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = ""
    status: WorkflowStatus = WorkflowStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_step: Optional[str] = None
    step_results: Dict[str, Any] = field(default_factory=dict)
    global_context: Dict[str, Any] = field(default_factory=dict)
    error_messages: List[str] = field(default_factory=list)
    human_intervention_required: bool = False
    pause_reason: Optional[str] = None


class OrchestratorAgent(BaseAgent):
    """
    Orchestrator agent that manages workflow execution across multiple agents.
    
    Features:
    - Workflow definition loading and validation
    - Dynamic agent instantiation and configuration
    - Dependency resolution and parallel execution
    - Error handling and recovery strategies
    - Human-in-the-loop intervention
    - Workflow state persistence and recovery
    """

    def __init__(self, **kwargs):
        super().__init__(AgentType.ORCHESTRATOR, **kwargs)
        self.agent_registry: Dict[AgentType, type] = {
            AgentType.CLEANER: DataCleanerAgent,
            # Add other agent types as they are implemented
        }
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        
        # Human intervention callback
        self.human_intervention_callback: Optional[Callable] = None
        
        self.logger.info("Initialized OrchestratorAgent")

    async def _process(self, input_data: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """
        Main orchestration processing logic.
        
        Args:
            input_data: Dictionary containing:
                - workflow_definition: WorkflowDefinition or path to workflow file
                - input_parameters: Parameters to pass to the workflow
                - execution_config: Runtime configuration options
        
        Returns:
            Dictionary containing workflow execution results
        """
        workflow_def = input_data.get('workflow_definition')
        input_parameters = input_data.get('input_parameters', {})
        execution_config = input_data.get('execution_config', {})
        
        # Load workflow definition
        if isinstance(workflow_def, str):
            workflow_def = await self._load_workflow_definition(workflow_def)
        elif isinstance(workflow_def, dict):
            workflow_def = self._dict_to_workflow_definition(workflow_def)
        elif not isinstance(workflow_def, WorkflowDefinition):
            raise ValueError("Invalid workflow definition format")
        
        # Create workflow execution
        execution = WorkflowExecution(
            workflow_id=workflow_def.workflow_id,
            global_context=input_parameters.copy(),
            started_at=datetime.utcnow()
        )
        
        # Store the initial input data specifically for first step access
        execution.global_context['input_data'] = input_parameters
        
        self.active_executions[execution.execution_id] = execution
        
        try:
            # Execute workflow
            execution.status = WorkflowStatus.RUNNING
            result = await self._execute_workflow(workflow_def, execution, execution_config)
            
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            
            self.logger.info(f"Workflow {workflow_def.name} completed successfully")
            
            return {
                'execution_id': execution.execution_id,
                'status': execution.status.value,
                'results': result,
                'execution_summary': self._generate_execution_summary(execution),
                'duration': (execution.completed_at - execution.started_at).total_seconds()
            }
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.completed_at = datetime.utcnow()
            execution.error_messages.append(str(e))
            
            self.logger.error(f"Workflow {workflow_def.name} failed: {str(e)}")
            raise
        finally:
            # Clean up active execution
            if execution.execution_id in self.active_executions:
                del self.active_executions[execution.execution_id]

    async def _load_workflow_definition(self, file_path: str) -> WorkflowDefinition:
        """Load workflow definition from YAML or JSON file"""
        try:
            with open(file_path, 'r') as f:
                if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            return self._dict_to_workflow_definition(data)
            
        except Exception as e:
            self.logger.error(f"Failed to load workflow definition from {file_path}: {str(e)}")
            raise

    def _dict_to_workflow_definition(self, data: Dict[str, Any]) -> WorkflowDefinition:
        """Convert dictionary to WorkflowDefinition object"""
        steps = []
        for step_data in data.get('steps', []):
            step = WorkflowStep(
                step_id=step_data['step_id'],
                agent_type=AgentType(step_data['agent_type']),
                agent_config=step_data.get('agent_config', {}),
                input_mapping=step_data.get('input_mapping', {}),
                output_mapping=step_data.get('output_mapping', {}),
                depends_on=step_data.get('depends_on', []),
                parallel=step_data.get('parallel', False),
                retry_on_failure=step_data.get('retry_on_failure', True),
                timeout_seconds=step_data.get('timeout_seconds', 300)
            )
            steps.append(step)
        
        return WorkflowDefinition(
            workflow_id=data['workflow_id'],
            name=data['name'],
            description=data['description'],
            version=data.get('version', '1.0'),
            steps=steps,
            global_config=data.get('global_config', {}),
            error_handling=data.get('error_handling', {}),
            human_review_required=data.get('human_review_required', False),
            metadata=data.get('metadata', {})
        )

    async def _execute_workflow(
        self,
        workflow_def: WorkflowDefinition,
        execution: WorkflowExecution,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the complete workflow"""
        
        # Build dependency graph
        dependency_graph = self._build_dependency_graph(workflow_def.steps)
        
        # Execute steps in dependency order
        executed_steps = set()
        final_results = {}
        
        while len(executed_steps) < len(workflow_def.steps):
            # Find steps ready to execute
            ready_steps = []
            for step in workflow_def.steps:
                if (step.step_id not in executed_steps and 
                    all(dep in executed_steps for dep in step.depends_on)):
                    ready_steps.append(step)
            
            if not ready_steps:
                raise RuntimeError("Circular dependency detected in workflow")
            
            # Group parallel steps
            parallel_groups = {}
            sequential_steps = []
            
            for step in ready_steps:
                if step.parallel:
                    group_key = tuple(sorted(step.depends_on))
                    if group_key not in parallel_groups:
                        parallel_groups[group_key] = []
                    parallel_groups[group_key].append(step)
                else:
                    sequential_steps.append(step)
            
            # Execute parallel groups
            for group in parallel_groups.values():
                results = await self._execute_parallel_steps(group, execution, workflow_def)
                for step_id, result in results.items():
                    execution.step_results[step_id] = result
                    executed_steps.add(step_id)
                    final_results.update(result.get('data', {}))
            
            # Execute sequential steps
            for step in sequential_steps:
                execution.current_step = step.step_id
                result = await self._execute_single_step(step, execution, workflow_def)
                execution.step_results[step.step_id] = result
                executed_steps.add(step.step_id)
                final_results.update(result.get('data', {}))
                
                # Check for human intervention requirements
                if workflow_def.human_review_required or result.get('human_review_required'):
                    await self._handle_human_intervention(execution, step, result)
        
        return final_results

    def _build_dependency_graph(self, steps: List[WorkflowStep]) -> Dict[str, List[str]]:
        """Build dependency graph for workflow steps"""
        graph = {}
        for step in steps:
            graph[step.step_id] = step.depends_on.copy()
        return graph

    async def _execute_parallel_steps(
        self,
        steps: List[WorkflowStep],
        execution: WorkflowExecution,
        workflow_def: WorkflowDefinition
    ) -> Dict[str, Any]:
        """Execute multiple steps in parallel"""
        tasks = []
        for step in steps:
            task = asyncio.create_task(
                self._execute_single_step(step, execution, workflow_def),
                name=step.step_id
            )
            tasks.append((step.step_id, task))
        
        results = {}
        for step_id, task in tasks:
            try:
                result = await task
                results[step_id] = result
            except Exception as e:
                self.logger.error(f"Parallel step {step_id} failed: {str(e)}")
                results[step_id] = {'success': False, 'error': str(e)}
        
        return results

    async def _execute_single_step(
        self,
        step: WorkflowStep,
        execution: WorkflowExecution,
        workflow_def: WorkflowDefinition
    ) -> Dict[str, Any]:
        """Execute a single workflow step"""
        self.logger.info(f"Executing step: {step.step_id} ({step.agent_type.value})")
        
        try:
            # Create agent instance
            agent = await self._create_agent(step.agent_type, step.agent_config)
            
            # Prepare input data
            input_data = await self._prepare_step_input(step, execution, workflow_def)
            
            # Create agent context
            agent_context = AgentContext(
                workflow_id=execution.workflow_id,
                correlation_id=execution.execution_id,
                timeout_seconds=step.timeout_seconds,
                metadata={
                    'step_id': step.step_id,
                    'workflow_name': workflow_def.name
                }
            )
            
            # Execute agent with timeout
            result = await asyncio.wait_for(
                agent.execute(input_data, agent_context),
                timeout=step.timeout_seconds
            )
            
            if not result.success and step.retry_on_failure:
                # Implement retry logic
                result = await self._retry_step(agent, input_data, agent_context, step)
            
            # Process output mapping
            mapped_output = self._apply_output_mapping(result.data, step.output_mapping)
            
            # Update global context
            execution.global_context.update(mapped_output)
            
            self.logger.info(f"Step {step.step_id} completed successfully")
            
            return {
                'success': result.success,
                'data': mapped_output,
                'metadata': result.metadata,
                'metrics': result.metrics.__dict__ if result.metrics else {},
                'execution_time': (result.completed_at - result.started_at).total_seconds() if result.completed_at else 0
            }
            
        except asyncio.TimeoutError:
            error_msg = f"Step {step.step_id} timed out after {step.timeout_seconds} seconds"
            self.logger.error(error_msg)
            execution.error_messages.append(error_msg)
            return {'success': False, 'error': error_msg}
            
        except Exception as e:
            error_msg = f"Step {step.step_id} failed: {str(e)}"
            self.logger.error(error_msg)
            execution.error_messages.append(error_msg)
            return {'success': False, 'error': error_msg}

    async def _create_agent(self, agent_type: AgentType, config: Dict[str, Any]) -> BaseAgent:
        """Create and configure an agent instance"""
        if agent_type not in self.agent_registry:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = self.agent_registry[agent_type]
        
        # Filter config to only include parameters that the agent expects
        if agent_type == AgentType.CLEANER:
            # For DataCleanerAgent, only pass the cleaning_rules if specified
            if 'cleaning_rules' in config:
                return agent_class(cleaning_rules=config['cleaning_rules'])
            else:
                return agent_class()
        else:
            # For other agent types, pass all config as keyword arguments
            return agent_class(**config)

    async def _prepare_step_input(
        self,
        step: WorkflowStep,
        execution: WorkflowExecution,
        workflow_def: WorkflowDefinition
    ) -> Dict[str, Any]:
        """Prepare input data for a workflow step"""
        input_data = {}
        
        # For the first step or if no input mapping is defined, use the initial workflow input
        if not step.input_mapping and not execution.step_results:
            # This is likely the first step, use the initial workflow input data
            initial_data = execution.global_context.get('input_data')
            if initial_data:
                input_data.update(initial_data)
        
        # Apply input mapping
        for target_key, source_key in step.input_mapping.items():
            if source_key in execution.global_context:
                input_data[target_key] = execution.global_context[source_key]
            elif source_key.startswith('step.'):
                # Reference to previous step output
                step_ref, key = source_key.split('.', 1)
                step_id = step_ref.replace('step.', '')
                if step_id in execution.step_results:
                    step_data = execution.step_results[step_id].get('data', {})
                    if key in step_data:
                        input_data[target_key] = step_data[key]
        
        # Add global configuration
        input_data.update(workflow_def.global_config)
        
        return input_data

    def _apply_output_mapping(self, output_data: Any, mapping: Dict[str, str]) -> Dict[str, Any]:
        """Apply output mapping to step results"""
        if not mapping:
            return output_data if isinstance(output_data, dict) else {'result': output_data}
        
        mapped_output = {}
        for source_key, target_key in mapping.items():
            if isinstance(output_data, dict) and source_key in output_data:
                mapped_output[target_key] = output_data[source_key]
        
        return mapped_output

    async def _retry_step(
        self,
        agent: BaseAgent,
        input_data: Dict[str, Any],
        context: AgentContext,
        step: WorkflowStep
    ) -> AgentResult:
        """Retry a failed step with exponential backoff"""
        max_retries = step.agent_config.get('max_retries', 3)
        
        for attempt in range(max_retries):
            try:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                context.retry_count = attempt + 1
                result = await agent.execute(input_data, context)
                
                if result.success:
                    self.logger.info(f"Step {step.step_id} succeeded on retry {attempt + 1}")
                    return result
                    
            except Exception as e:
                self.logger.warning(f"Retry {attempt + 1} failed for step {step.step_id}: {str(e)}")
        
        # All retries failed
        raise RuntimeError(f"Step {step.step_id} failed after {max_retries} retries")

    async def _handle_human_intervention(
        self,
        execution: WorkflowExecution,
        step: WorkflowStep,
        result: Dict[str, Any]
    ) -> None:
        """Handle human-in-the-loop intervention"""
        execution.human_intervention_required = True
        execution.status = WorkflowStatus.PAUSED
        execution.pause_reason = f"Human review required for step: {step.step_id}"
        
        self.logger.info(f"Human intervention required for step {step.step_id}")
        
        if self.human_intervention_callback:
            intervention_result = await self.human_intervention_callback(execution, step, result)
            
            if intervention_result.get('approved', False):
                execution.human_intervention_required = False
                execution.status = WorkflowStatus.RUNNING
                execution.pause_reason = None
            else:
                execution.status = WorkflowStatus.CANCELLED
                raise RuntimeError("Workflow cancelled by human reviewer")

    def _generate_execution_summary(self, execution: WorkflowExecution) -> Dict[str, Any]:
        """Generate execution summary"""
        total_steps = len(execution.step_results)
        successful_steps = sum(1 for result in execution.step_results.values() if result.get('success', False))
        
        return {
            'execution_id': execution.execution_id,
            'workflow_id': execution.workflow_id,
            'status': execution.status.value,
            'duration': (execution.completed_at - execution.started_at).total_seconds() if execution.completed_at else None,
            'total_steps': total_steps,
            'successful_steps': successful_steps,
            'failed_steps': total_steps - successful_steps,
            'error_count': len(execution.error_messages),
            'human_intervention_required': execution.human_intervention_required
        }

    def register_agent_type(self, agent_type: AgentType, agent_class: type) -> None:
        """Register a new agent type"""
        self.agent_registry[agent_type] = agent_class
        self.logger.info(f"Registered agent type: {agent_type.value}")

    def set_human_intervention_callback(self, callback: Callable) -> None:
        """Set callback for human intervention handling"""
        self.human_intervention_callback = callback

    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a workflow execution"""
        if execution_id in self.active_executions:
            execution = self.active_executions[execution_id]
            return {
                'execution_id': execution_id,
                'status': execution.status.value,
                'current_step': execution.current_step,
                'progress': len(execution.step_results),
                'errors': execution.error_messages,
                'human_intervention_required': execution.human_intervention_required
            }
        return None

    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running workflow execution"""
        if execution_id in self.active_executions:
            execution = self.active_executions[execution_id]
            execution.status = WorkflowStatus.CANCELLED
            execution.completed_at = datetime.utcnow()
            self.logger.info(f"Cancelled workflow execution: {execution_id}")
            return True
        return False
